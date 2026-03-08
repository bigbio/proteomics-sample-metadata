"""
Template inheritance resolver module.

Loads YAML templates from the sdrf-templates directory, walks the extends: chain,
and produces resolved template dicts with own, inherited, and merged columns.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def load_manifest(templates_dir: Path) -> dict[str, dict]:
    """Load templates.yaml manifest and return the templates dict.

    Args:
        templates_dir: Path to the sdrf-templates directory.

    Returns:
        Dict mapping template name -> manifest entry (latest, versions, extends, etc.).
    """
    manifest_path = templates_dir / "templates.yaml"
    with open(manifest_path) as f:
        data = yaml.safe_load(f)
    return data["templates"]


def load_template_yaml(
    templates_dir: Path, name: str, version: str
) -> dict[str, Any]:
    """Load a single template YAML file.

    Args:
        templates_dir: Path to the sdrf-templates directory.
        name: Template name (e.g. 'base', 'human').
        version: Exact version string (e.g. '1.1.0').

    Returns:
        Parsed YAML dict for the template.
    """
    yaml_path = templates_dir / name / version / f"{name}.yaml"
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def _parse_extends(extends_str: str | None) -> str | None:
    """Extract parent template name from an extends string like 'base@>=1.1.0'.

    Returns None if extends_str is None.
    """
    if extends_str is None:
        return None
    # Split on '@' to get the template name
    return extends_str.split("@")[0]


def build_inheritance_chain(
    name: str,
    manifest: dict[str, dict],
    templates_dir: Path,
) -> list[str]:
    """Build the full inheritance chain for a template, root first.

    Args:
        name: Template name.
        manifest: The loaded manifest dict.
        templates_dir: Path to sdrf-templates directory.

    Returns:
        List of template names from root ancestor to this template.
        E.g. ['base', 'sample-metadata', 'human'] for human.
    """
    chain: list[str] = []
    current = name
    while current is not None:
        chain.append(current)
        entry = manifest[current]
        parent_name = _parse_extends(entry.get("extends"))
        current = parent_name
    chain.reverse()
    return chain


def _merge_single_column(
    parent_col: dict[str, Any], child_col: dict[str, Any]
) -> dict[str, Any]:
    """Merge a child column override onto a parent column.

    Child inherits ALL parent properties via copy, then overrides only
    the fields explicitly specified in child_col.
    """
    merged = copy.deepcopy(parent_col)
    for key, value in child_col.items():
        if key == "name":
            continue  # name is the join key, always keep
        merged[key] = copy.deepcopy(value)
    return merged


def merge_columns(
    chain: list[str],
    manifest: dict[str, dict],
    templates_dir: Path,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Walk the inheritance chain and merge columns.

    Returns:
        Tuple of (own_columns, inherited_columns, all_columns).
        Each column dict includes a 'source_template' annotation.
    """
    if not chain:
        return [], [], []

    # Load all templates in the chain
    loaded: dict[str, dict] = {}
    for tname in chain:
        entry = manifest[tname]
        version = entry["latest"]
        loaded[tname] = load_template_yaml(templates_dir, tname, version)

    # Build merged column list by walking chain from root to leaf
    # merged_columns: ordered dict of name -> column dict
    merged_columns: dict[str, dict[str, Any]] = {}

    # Track which template originally defined or last overrode each column
    for tname in chain:
        tpl = loaded[tname]
        tpl_columns = tpl.get("columns", [])
        for col in tpl_columns:
            col_name = col["name"]
            if col_name in merged_columns:
                # Merge: child overrides parent
                merged_columns[col_name] = _merge_single_column(
                    merged_columns[col_name], col
                )
            else:
                # New column
                merged_columns[col_name] = copy.deepcopy(col)
            # Update source_template to this template (last one to define/override)
            merged_columns[col_name]["source_template"] = tname

    # The leaf template is the last in the chain
    leaf_name = chain[-1]
    leaf_col_names = {
        col["name"] for col in loaded[leaf_name].get("columns", [])
    }

    # Separate own vs inherited
    own_columns: list[dict] = []
    inherited_columns: list[dict] = []
    for col_name, col in merged_columns.items():
        if col_name in leaf_col_names:
            own_columns.append(col)
        else:
            inherited_columns.append(col)

    # all_columns: inherited order first, then own additions
    # "own" columns that override a parent column keep their inherited position
    all_columns: list[dict] = []
    own_addition_names = leaf_col_names - {
        col["name"]
        for tname in chain[:-1]
        for col in loaded[tname].get("columns", [])
    }
    for col_name, col in merged_columns.items():
        if col_name not in own_addition_names:
            all_columns.append(col)
    # Then append own additions (new columns not in any parent)
    for col_name, col in merged_columns.items():
        if col_name in own_addition_names:
            all_columns.append(col)

    return own_columns, inherited_columns, all_columns


def resolve_template(
    name: str,
    templates_dir: Path,
    manifest: dict[str, dict] | None = None,
) -> dict[str, Any]:
    """Resolve a single template with full inheritance.

    Args:
        name: Template name.
        templates_dir: Path to sdrf-templates directory.
        manifest: Optional pre-loaded manifest (loaded if None).

    Returns:
        Resolved template dict with all metadata and merged columns.
    """
    if manifest is None:
        manifest = load_manifest(templates_dir)

    entry = manifest[name]
    version = entry["latest"]
    tpl = load_template_yaml(templates_dir, name, version)
    chain = build_inheritance_chain(name, manifest, templates_dir)
    own_columns, inherited_columns, all_columns = merge_columns(
        chain, manifest, templates_dir
    )

    return {
        "name": tpl["name"],
        "description": tpl.get("description", ""),
        "documentation": tpl.get("documentation", ""),
        "contributors": tpl.get("contributors", []),
        "version": tpl.get("version", version),
        "layer": tpl.get("layer", entry.get("layer")),
        "extends": tpl.get("extends", entry.get("extends")),
        "usable_alone": tpl.get("usable_alone", entry.get("usable_alone", False)),
        "mutually_exclusive_with": tpl.get("mutually_exclusive_with", []),
        "requires": entry.get("requires"),
        "excludes": entry.get("excludes"),
        "inheritance_chain": chain,
        "own_columns": own_columns,
        "inherited_columns": inherited_columns,
        "all_columns": all_columns,
    }


def resolve_all(
    templates_dir: Path,
) -> dict[str, dict[str, Any]]:
    """Resolve all templates from the manifest.

    Returns:
        Dict mapping template name -> resolved template dict.
    """
    manifest = load_manifest(templates_dir)
    result: dict[str, dict[str, Any]] = {}
    for name in manifest:
        result[name] = resolve_template(name, templates_dir, manifest=manifest)
    return result
