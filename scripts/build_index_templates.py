#!/usr/bin/env python3
"""Generate the template section for index.html from resolved templates.

Usage:
    python3 scripts/build_index_templates.py <sdrf-templates-dir> <index-html-path>

The script resolves all templates, filters out internal ones,
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

# Display order for layers
LAYER_ORDER = {"technology": 0, "sample": 1, "experiment": 2}


def filter_and_sort_templates(all_resolved: dict[str, dict]) -> list[dict]:
    """Filter out internal templates and sort by layer then name."""
    templates = []
    for name, tpl in all_resolved.items():
        layer = tpl.get("layer")
        usable_alone = tpl.get("usable_alone", False)
        # Exclude internal templates (layer is None and not usable alone)
        if layer is None and not usable_alone:
            continue
        templates.append(tpl)

    templates.sort(
        key=lambda t: (
            LAYER_ORDER.get(t.get("layer") or "", 99),
            t["name"],
        )
    )
    return templates


def render_section(templates: list[dict]) -> str:
    """Render the index-templates Jinja2 snippet."""
    templates_dir = Path(__file__).resolve().parent.parent / "site" / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("index-templates.html.j2")
    return template.render(all_templates=templates)


def inject_section(html: str, section_html: str) -> str:
    """Replace content inside <section id="templates"...>...</section>."""
    pattern = r'(<section\s+id="templates"[^>]*>)(.*?)(</section>)'
    replacement = rf"\1\n{section_html}\n        \3"
    result, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
    if count == 0:
        raise ValueError('Could not find <section id="templates"> in HTML')
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

    # Filter and sort
    templates = filter_and_sort_templates(all_resolved)

    # Render the Jinja2 snippet
    section_html = render_section(templates)

    # Read, inject, clean up, write
    html = index_path.read_text()
    html = inject_section(html, section_html)
    index_path.write_text(html)

    print(f"Injected {len(templates)} templates into {index_path}")


if __name__ == "__main__":
    main()
