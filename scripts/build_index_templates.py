#!/usr/bin/env python3
"""Generate the template section for index.html from resolved templates.

Usage:
    python3 scripts/build_index_templates.py <sdrf-templates-dir> <index-html-path>

The script resolves all templates, classifies them into display groups,
renders a Jinja2 snippet, and replaces the content inside
<section id="templates"...>...</section> in the target HTML file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Allow importing resolve_templates from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_templates import resolve_all  # noqa: E402

# Organism template names (sample-layer but displayed as primary cards)
ORGANISM_NAMES = {"human", "vertebrates", "invertebrates", "plants"}


def classify_templates(
    all_resolved: dict[str, dict],
) -> dict[str, list[dict]]:
    """Classify resolved templates into display groups.

    Returns dict with keys:
        organism_templates, technology_templates,
        experiment_templates, sample_clinical_templates
    """
    organism: list[dict] = []
    technology: list[dict] = []
    experiment: list[dict] = []
    sample_clinical: list[dict] = []

    for name, tpl in sorted(all_resolved.items()):
        layer = tpl.get("layer")
        usable_alone = tpl.get("usable_alone", False)

        # Exclude internal templates (layer is None and not usable alone)
        if layer is None and not usable_alone:
            continue

        if name in ORGANISM_NAMES:
            organism.append(tpl)
        elif layer == "technology":
            technology.append(tpl)
        elif layer == "experiment":
            experiment.append(tpl)
        elif layer == "sample" and name not in ORGANISM_NAMES:
            sample_clinical.append(tpl)

    # Sort organism templates in a sensible fixed order
    organism_order = {n: i for i, n in enumerate(
        ["human", "vertebrates", "invertebrates", "plants"]
    )}
    organism.sort(key=lambda t: organism_order.get(t["name"], 99))

    return {
        "organism_templates": organism,
        "technology_templates": technology,
        "experiment_templates": experiment,
        "sample_clinical_templates": sample_clinical,
    }


def render_section(groups: dict[str, list[dict]]) -> str:
    """Render the index-templates Jinja2 snippet with the given groups."""
    templates_dir = Path(__file__).resolve().parent.parent / "site" / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("index-templates.html.j2")
    return template.render(**groups)


def inject_section(html: str, section_html: str) -> str:
    """Replace content inside <section id="templates"...>...</section>."""
    pattern = r'(<section\s+id="templates"[^>]*>)(.*?)(</section>)'
    replacement = rf"\1\n{section_html}\n        \3"
    result, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
    if count == 0:
        raise ValueError("Could not find <section id=\"templates\"> in HTML")
    return result


def main() -> None:
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} <sdrf-templates-dir> <index-html-path>",
            file=sys.stderr,
        )
        sys.exit(1)

    templates_dir = Path(sys.argv[1])
    index_path = Path(sys.argv[2])

    # Resolve all templates
    all_resolved = resolve_all(templates_dir)

    # Classify into groups
    groups = classify_templates(all_resolved)

    # Render the Jinja2 snippet
    section_html = render_section(groups)

    # Read, inject, write
    html = index_path.read_text()
    html = inject_section(html, section_html)
    index_path.write_text(html)

    # Summary
    total = sum(len(v) for v in groups.values())
    print(f"Injected {total} templates into {index_path}")
    for group_name, templates in groups.items():
        print(f"  {group_name}: {len(templates)}")


if __name__ == "__main__":
    main()
