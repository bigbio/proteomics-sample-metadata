#!/usr/bin/env python3
"""Generate per-template HTML pages from YAML definitions."""

import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).parent))
from resolve_templates import resolve_all


def process_documentation(doc_text: str) -> str:
    """Convert documentation text to HTML.

    - Backtick-wrapped text (`text`) becomes <code>text</code>
    - Lines starting with '- ' become HTML list items
    - Double newlines separate paragraphs
    """
    if not doc_text:
        return ""
    # Convert backtick-wrapped text to <code>
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", doc_text.strip())

    paragraphs = html.split("\n\n")
    result = []
    for para in paragraphs:
        lines = para.strip().split("\n")
        # Check if this paragraph is a list
        if all(line.strip().startswith("- ") for line in lines if line.strip()):
            items = [
                f"<li>{line.strip()[2:]}</li>" for line in lines if line.strip()
            ]
            result.append(f'<ul>{"".join(items)}</ul>')
        else:
            result.append(
                f'<p>{" ".join(line.strip() for line in lines)}</p>'
            )
    return "\n".join(result)


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python3 build_template_pages.py <sdrf-templates-dir> <output-dir>"
        )
        sys.exit(1)

    templates_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).parent.parent
    jinja_dir = repo_root / "site" / "templates"

    env = Environment(loader=FileSystemLoader(str(jinja_dir)))
    page_template = env.get_template("template-page.html.j2")

    all_templates = resolve_all(templates_dir)

    for name, resolved in all_templates.items():
        resolved["documentation_html"] = process_documentation(
            resolved.get("documentation", "")
        )
        html = page_template.render(template=resolved)
        out_path = output_dir / f"{name}.html"
        with open(out_path, "w") as f:
            f.write(html)
        print(f"  Generated: {out_path}")

    print(f"Generated {len(all_templates)} template pages in {output_dir}")


if __name__ == "__main__":
    main()
