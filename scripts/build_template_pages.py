#!/usr/bin/env python3
"""Generate per-template HTML pages from YAML definitions."""

import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).parent))
from resolve_templates import resolve_all

REQUIREMENT_ORDER = {"required": 0, "recommended": 1, "optional": 2}


def process_documentation(doc_text: str) -> str:
    """Convert documentation text to HTML.

    Handles mixed blocks where paragraphs and list items can coexist:
    - Backtick-wrapped text (`text`) becomes <code>text</code>
    - Lines starting with '- ' become HTML list items
    - Consecutive list lines are grouped into a single <ul>
    - Other lines become paragraphs
    - Double newlines separate blocks
    """
    if not doc_text:
        return ""
    # Convert backtick-wrapped text to <code>
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", doc_text.strip())

    blocks = html.split("\n\n")
    result = []
    for block in blocks:
        lines = [line for line in block.strip().split("\n") if line.strip()]
        if not lines:
            continue

        # Process line by line, grouping consecutive list items
        current_list: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                current_list.append(stripped[2:])
            else:
                # Flush any pending list
                if current_list:
                    items = "".join(f"<li>{item}</li>" for item in current_list)
                    result.append(f"<ul>{items}</ul>")
                    current_list = []
                result.append(f"<p>{stripped}</p>")

        # Flush trailing list
        if current_list:
            items = "".join(f"<li>{item}</li>" for item in current_list)
            result.append(f"<ul>{items}</ul>")

    return "\n".join(result)


def sort_columns(columns: list[dict]) -> list[dict]:
    """Sort columns by requirement level: required, recommended, optional."""
    return sorted(
        columns,
        key=lambda c: REQUIREMENT_ORDER.get(c.get("requirement", "optional"), 2),
    )


def fix_jinja_reserved_keys(columns: list[dict]) -> list[dict]:
    """Rename 'values' key in validator params to avoid Jinja2 dict.values() conflict."""
    for col in columns:
        if col.get("validators"):
            for v in col["validators"]:
                if v.get("params") and "values" in v["params"]:
                    v["params"]["allowed_values"] = v["params"].pop("values")
    return columns


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
        # Sort columns by requirement level
        resolved["all_columns"] = sort_columns(resolved["all_columns"])
        resolved["own_columns"] = sort_columns(resolved["own_columns"])
        resolved["inherited_columns"] = sort_columns(resolved["inherited_columns"])
        # Fix Jinja2 reserved key conflicts
        fix_jinja_reserved_keys(resolved["all_columns"])

        html = page_template.render(template=resolved)
        out_path = output_dir / f"{name}.html"
        with open(out_path, "w") as f:
            f.write(html)
        print(f"  Generated: {out_path}")

    print(f"Generated {len(all_templates)} template pages in {output_dir}")


if __name__ == "__main__":
    main()
