#!/usr/bin/env python3
"""Build JSON data file for the interactive SDRF builder UI.

Compiles YAML template definitions into a single JSON file containing
resolved templates, combination rules, and term definitions.

Usage:
    python3 build_sdrf_builder_data.py <sdrf-templates-dir> <output-json-path>
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from resolve_templates import resolve_all

# Fallback example values for well-known column names
FALLBACK_EXAMPLES: dict[str, str] = {
    "source name": "sample_1",
    "assay name": "run_1",
    "comment[data file]": "sample1.raw",
    "comment[fraction identifier]": "1",
    "comment[technical replicate]": "1",
    "comment[label]": "label free sample",
}


def _compact_validators(validators: list[dict] | None) -> list[dict]:
    """Return a compact representation of validators."""
    if not validators:
        return []
    result = []
    for v in validators:
        compact: dict[str, Any] = {"type": v.get("validator_name", "")}
        params = v.get("params", {})
        if params:
            compact["params"] = params
        result.append(compact)
    return result


def _example_value(column: dict) -> str:
    """Derive an example value for a column from validators or fallbacks."""
    validators = column.get("validators") or []
    for v in validators:
        params = v.get("params", {})
        if params.get("examples"):
            return str(params["examples"][0])
        if params.get("values"):
            return str(params["values"][0])
    return FALLBACK_EXAMPLES.get(column.get("name", ""), "")


def _serialize_column(col: dict) -> dict:
    """Serialize a single column dict for JSON output."""
    return {
        "name": col.get("name", ""),
        "requirement": col.get("requirement", "optional"),
        "description": col.get("description", ""),
        "ontology_accession": col.get("ontology_accession", ""),
        "cardinality": col.get("cardinality", "single"),
        "allow_not_applicable": col.get("allow_not_applicable", False),
        "allow_not_available": col.get("allow_not_available", False),
        "source_template": col.get("source_template", ""),
        "validators": _compact_validators(col.get("validators")),
        "example_value": _example_value(col),
    }


def _extract_combination_rules(
    all_templates: dict[str, dict],
) -> dict[str, Any]:
    """Extract combination rules from all resolved templates."""
    # Deduplicate mutually_exclusive groups (stored as frozensets)
    exclusive_groups: set[frozenset[str]] = set()
    requires: dict[str, list[str]] = {}
    excludes: dict[str, list[str]] = {}

    for name, tpl in all_templates.items():
        me = tpl.get("mutually_exclusive_with") or []
        if me:
            group = frozenset([name] + list(me))
            exclusive_groups.add(group)

        req = tpl.get("requires")
        if req:
            requires[name] = list(req) if isinstance(req, list) else [req]

        exc = tpl.get("excludes")
        if exc:
            excludes[name] = list(exc) if isinstance(exc, list) else [exc]

    return {
        "mutually_exclusive": [sorted(g) for g in exclusive_groups],
        "requires": requires,
        "excludes": excludes,
    }


def _load_terms(repo_root: Path) -> list[dict]:
    """Load sdrf-terms.tsv from known locations."""
    candidates = [
        repo_root / "sdrf-proteomics" / "metadata-guidelines" / "sdrf-terms.tsv",
        repo_root / "local-info" / "demo_web" / "sdrf-terms.tsv",
    ]
    terms_path = None
    for p in candidates:
        if p.exists():
            terms_path = p
            break

    if terms_path is None:
        print("Warning: sdrf-terms.tsv not found, terms list will be empty.")
        return []

    terms: list[dict] = []
    with open(terms_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            terms.append(
                {
                    "term": row.get("term", ""),
                    "type": row.get("type", ""),
                    "description": row.get("description", ""),
                    "values": row.get("values", ""),
                    "ontology_accession": row.get("ontology_term_accession", ""),
                    "allow_not_available": row.get("allow_not_available", "false")
                    == "true",
                    "allow_not_applicable": row.get("allow_not_applicable", "false")
                    == "true",
                }
            )
    print(f"Loaded {len(terms)} terms from {terms_path}")
    return terms


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "Usage: python3 build_sdrf_builder_data.py "
            "<sdrf-templates-dir> <output-json-path>"
        )
        sys.exit(1)

    templates_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parent.parent

    # Resolve all templates
    all_templates = resolve_all(templates_dir)
    print(f"Resolved {len(all_templates)} templates")

    # Serialize templates
    templates_json: dict[str, dict] = {}
    for name, tpl in all_templates.items():
        templates_json[name] = {
            "description": tpl.get("description", ""),
            "layer": tpl.get("layer"),
            "usable_alone": tpl.get("usable_alone", False),
            "extends": tpl.get("extends"),
            "inheritance_chain": tpl.get("inheritance_chain", []),
            "columns": [_serialize_column(c) for c in tpl["all_columns"]],
            "own_columns": [_serialize_column(c) for c in tpl["own_columns"]],
        }

    # Extract combination rules
    combination_rules = _extract_combination_rules(all_templates)

    # Load terms
    terms = _load_terms(repo_root)

    # Write output
    output = {
        "templates": templates_json,
        "combination_rules": combination_rules,
        "terms": terms,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote builder data to {output_path}")


if __name__ == "__main__":
    main()
