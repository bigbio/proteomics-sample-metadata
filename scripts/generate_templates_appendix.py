#!/usr/bin/env python3
"""Generate AsciiDoc template definitions and inject into README.adoc.

Reads all YAML templates from sdrf-templates/ and injects a "Template Definitions"
section directly into README.adoc, before the "Intellectual Property Statement"
section. This keeps the PDF in sync with YAML templates without a separate file.

Usage:
    python scripts/generate_templates_appendix.py [--templates-dir PATH] [--readme PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Add scripts dir to path so we can import resolve_templates
sys.path.insert(0, str(Path(__file__).parent))

from resolve_templates import load_manifest, load_template_yaml

# Marker used to identify the injected section
MARKER_START = "// AUTO-GENERATED: Template Definitions (do not edit below this line)"
MARKER_END = "// AUTO-GENERATED: End of Template Definitions"

# Injection point: insert before this heading
INJECT_BEFORE = "== Intellectual Property Statement"

# Ordered template groups for the appendix
TEMPLATE_ORDER: list[list[str]] = [
    # Infrastructure
    ["base", "sample-metadata"],
    # Technology
    ["ms-proteomics", "affinity-proteomics"],
    # Sample (organism)
    ["human", "vertebrates", "invertebrates", "plants"],
    # Sample (study type)
    ["clinical-metadata", "oncology-metadata"],
    # Experiment (MS)
    ["dia-acquisition", "single-cell", "immunopeptidomics", "crosslinking", "cell-lines"],
    # Experiment (affinity)
    ["olink", "somascan"],
    # Metaproteomics branch
    ["metaproteomics", "human-gut", "soil", "water"],
]


def _escape_adoc(text: str) -> str:
    """Escape special AsciiDoc characters in table cells."""
    return text.replace("|", "\\|")


def _summarize_validators(validators: list[dict[str, Any]]) -> str:
    """Produce a short human-readable summary of column validators."""
    if not validators:
        return ""

    parts: list[str] = []
    for v in validators:
        vname = v.get("validator_name", "")
        params = v.get("params") or {}

        if vname == "ontology":
            ontologies = params.get("ontologies", [])
            parts.append(f"ontology: {', '.join(ontologies)}")
        elif vname == "pattern":
            desc = params.get("description", "")
            if desc:
                parts.append(f"pattern: {desc}")
            else:
                pat = params.get("pattern", "")
                parts.append(f"pattern: `{pat}`")
        elif vname == "values":
            values = params.get("values", [])
            if len(values) <= 5:
                parts.append(f"values: {', '.join(str(v) for v in values)}")
            else:
                shown = ", ".join(str(v) for v in values[:4])
                parts.append(f"values: {shown}, ...")
        elif vname == "number_with_unit":
            units = params.get("units", [])
            parts.append(f"number with unit ({', '.join(units)})")
        elif vname == "single_cardinality_validator":
            parts.append("single value only")
        elif vname == "accession":
            fmt = params.get("format", "")
            parts.append(f"accession: {fmt}")
        elif vname == "mz_value":
            parts.append("m/z value")
        elif vname == "mz_range_interval":
            parts.append("m/z range interval")
        elif vname == "identifier":
            parts.append("identifier")
        else:
            parts.append(vname)

    return "; ".join(parts)


def _collect_examples(validators: list[dict[str, Any]]) -> str:
    """Collect example values from validators."""
    examples: list[str] = []
    for v in validators:
        params = v.get("params") or {}
        for ex in params.get("examples", []):
            ex_str = str(ex)
            if ex_str not in examples:
                examples.append(ex_str)

    if not examples:
        return ""
    shown = examples[:4]
    result = ", ".join(shown)
    if len(examples) > 4:
        result += ", ..."
    return result


def _format_extends(extends: str | None) -> str:
    """Format the extends field, stripping version constraint."""
    if not extends:
        return "none"
    return extends.split("@")[0]


def generate_template_section(
    name: str,
    tpl: dict[str, Any],
    manifest_entry: dict[str, Any],
) -> str:
    """Generate AsciiDoc for a single template."""
    lines: list[str] = []

    # Heading
    lines.append(f"=== {name}")
    lines.append("")

    # Metadata line
    version = tpl.get("version", manifest_entry.get("latest", ""))
    layer = tpl.get("layer") or manifest_entry.get("layer") or "internal"
    extends = _format_extends(
        tpl.get("extends") or manifest_entry.get("extends")
    )
    usable_alone = tpl.get("usable_alone", manifest_entry.get("usable_alone", False))

    lines.append(
        f"**Version:** {version} | "
        f"**Layer:** {layer} | "
        f"**Extends:** {extends} | "
        f"**Usable alone:** {'Yes' if usable_alone else 'No'}"
    )
    lines.append("")

    # Description
    desc = tpl.get("description", "")
    if desc:
        lines.append(_escape_adoc(desc.strip()))
        lines.append("")

    # Columns table
    columns = tpl.get("columns", [])
    if not columns:
        lines.append("_No own columns defined (inherits all from parent)._")
        lines.append("")
        return "\n".join(lines)

    lines.append('[cols="2,1,3,2,2", options="header"]')
    lines.append("|===")
    lines.append("| Column Name | Req. | Description | Validators | Examples")
    lines.append("")

    for col in columns:
        col_name = col.get("name", "")
        requirement = col.get("requirement", "")
        col_desc = col.get("description", "")
        validators = col.get("validators", [])

        validator_summary = _summarize_validators(validators)
        examples = _collect_examples(validators)

        # If column is a minimal override (only name + requirement, no description),
        # note it as an override
        if not col_desc and requirement:
            col_desc = f"_(override: requirement set to {requirement})_"

        lines.append(f"| `{_escape_adoc(col_name)}`")
        lines.append(f"| {requirement}")
        lines.append(f"| {_escape_adoc(col_desc)}")
        lines.append(f"| {_escape_adoc(validator_summary)}")
        lines.append(f"| {_escape_adoc(examples)}")
        lines.append("")

    lines.append("|===")
    lines.append("")

    return "\n".join(lines)


def generate_appendix(templates_dir: Path) -> str:
    """Generate the full AsciiDoc appendix content."""
    manifest = load_manifest(templates_dir)

    lines: list[str] = []
    lines.append(MARKER_START)
    lines.append("")
    lines.append("[[template-definitions]]")
    lines.append("== Template Definitions")
    lines.append("")
    lines.append(
        "This section provides the column definitions for each SDRF-Proteomics template. "
        "Each template shows only its *own* columns (not inherited ones). "
        'See the "Extends" field to identify which parent template\'s columns are also included.'
    )
    lines.append("")

    # Flatten ordered list, skipping templates not in manifest
    ordered_names: list[str] = []
    for group in TEMPLATE_ORDER:
        for name in group:
            if name in manifest:
                ordered_names.append(name)

    # Add any templates from manifest not in our explicit order
    for name in manifest:
        if name not in ordered_names:
            ordered_names.append(name)

    for name in ordered_names:
        entry = manifest[name]
        version = entry["latest"]
        tpl = load_template_yaml(templates_dir, name, version)
        section = generate_template_section(name, tpl, entry)
        lines.append(section)

    lines.append(MARKER_END)
    return "\n".join(lines)


def inject_into_readme(readme_path: Path, appendix_content: str) -> None:
    """Inject template definitions into README.adoc.

    If markers from a previous run exist, replace that section.
    Otherwise, insert before the 'Intellectual Property Statement' heading.
    """
    readme_text = readme_path.read_text()

    # Check if markers from a previous run exist
    if MARKER_START in readme_text:
        # Replace existing auto-generated section
        pattern = re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END)
        readme_text = re.sub(pattern, appendix_content, readme_text, flags=re.DOTALL)
    else:
        # Insert before the injection point
        if INJECT_BEFORE not in readme_text:
            raise ValueError(
                f"Could not find '{INJECT_BEFORE}' in {readme_path}. "
                "Cannot determine where to inject template definitions."
            )
        readme_text = readme_text.replace(
            INJECT_BEFORE,
            appendix_content + "\n\n" + INJECT_BEFORE,
        )

    readme_path.write_text(readme_text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and inject template definitions into README.adoc."
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "sdrf-templates",
        help="Path to sdrf-templates directory (default: ../../sdrf-templates)",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=Path(__file__).parent.parent / "sdrf-proteomics" / "README.adoc",
        help="Path to README.adoc to inject into",
    )
    args = parser.parse_args()

    appendix_content = generate_appendix(args.templates_dir)
    inject_into_readme(args.readme, appendix_content)
    print(f"Injected template definitions into {args.readme} ({len(appendix_content)} bytes)")


if __name__ == "__main__":
    main()
