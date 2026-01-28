#!/usr/bin/env python3
"""
Transform SDRF example tables in HTML documentation to add colored column styling.

Usage: python3 transform-sdrf-tables.py <output_dir>

This script finds tables that look like SDRF examples (with source name, characteristics,
comment, factor value columns) and transforms them to use the colored column styling
with a legend below.
"""

import sys
import re
from pathlib import Path
from html.parser import HTMLParser


def classify_column(header_text: str) -> str:
    """Classify a column based on its header text."""
    header_lower = header_text.lower().strip()

    # Factor value columns (yellow/orange) - check FIRST to avoid matching "disease" etc
    if 'factor value' in header_lower:
        return 'factor-col'

    # Sample/characteristics columns (blue)
    if any(x in header_lower for x in ['source name', 'characteristics[']):
        return 'sample-col'

    # Data/comment columns (green) - assay name, technology type, comments
    if any(x in header_lower for x in ['assay name', 'technology type', 'comment[', 'data file', '.raw', '.mzml']):
        return 'data-col'

    # Default - no special class
    return ''


def is_sdrf_table(headers: list) -> bool:
    """Check if a table looks like an SDRF example table."""
    header_text = ' '.join(headers).lower()

    # Must have source name and at least one of: characteristics, comment, or factor value
    has_source = 'source name' in header_text
    has_characteristics = 'characteristics[' in header_text
    has_comment = 'comment[' in header_text
    has_factor = 'factor value' in header_text
    has_assay = 'assay name' in header_text

    return has_source and (has_characteristics or has_comment or has_factor or has_assay)


def transform_table(table_html: str) -> str:
    """Transform a table to add SDRF column styling."""

    # Extract headers
    header_match = re.search(r'<thead[^>]*>(.*?)</thead>', table_html, re.DOTALL)
    if not header_match:
        # Try finding th elements directly
        header_match = re.search(r'<tr[^>]*>\s*(<th.*?</th>.*?)</tr>', table_html, re.DOTALL)
        if not header_match:
            return table_html

    header_content = header_match.group(1)
    headers = re.findall(r'<th[^>]*>(.*?)</th>', header_content, re.DOTALL)

    if not headers:
        return table_html

    # Check if this is an SDRF table
    if not is_sdrf_table(headers):
        return table_html

    # Classify each column
    column_classes = [classify_column(h) for h in headers]

    # Check if we have at least 1 classified column type
    unique_classes = set(c for c in column_classes if c)
    if len(unique_classes) < 1:
        return table_html

    # Transform header cells
    def replace_header(match):
        idx = replace_header.counter
        replace_header.counter += 1
        col_class = column_classes[idx] if idx < len(column_classes) else ''

        original_tag = match.group(0)
        if col_class:
            # Add class to th
            if 'class="' in original_tag:
                return original_tag.replace('class="', f'class="{col_class} ')
            else:
                return original_tag.replace('<th', f'<th class="{col_class}"')
        return original_tag

    replace_header.counter = 0
    # Match <th> but not <thead>
    transformed = re.sub(r'<th\b[^>]*>', replace_header, table_html)

    # Transform body cells - only modify the <td> tag, not nested elements
    def replace_td_tag(match):
        idx = replace_td_tag.counter
        replace_td_tag.counter += 1
        col_class = column_classes[idx % len(column_classes)] if column_classes else ''

        original_tag = match.group(0)
        if col_class:
            if 'class="' in original_tag:
                return original_tag.replace('class="', f'class="{col_class} ')
            else:
                return original_tag.replace('<td', f'<td class="{col_class}"')
        return original_tag

    replace_td_tag.counter = 0
    # Only match opening <td> tags, not content inside
    transformed = re.sub(r'<td\b[^>]*>', replace_td_tag, transformed)

    # Wrap in sdrf-example-table div and add legend
    has_sample = 'sample-col' in column_classes
    has_data = 'data-col' in column_classes
    has_factor = 'factor-col' in column_classes

    legend_items = []
    if has_sample:
        legend_items.append('<div class="legend-item"><span class="legend-color sample"></span>Sample metadata</div>')
    if has_data:
        legend_items.append('<div class="legend-item"><span class="legend-color data"></span>Data file metadata</div>')
    if has_factor:
        legend_items.append('<div class="legend-item"><span class="legend-color factor"></span>Factor values</div>')

    legend_html = f'<div class="sdrf-legend">{"".join(legend_items)}</div>'

    return f'<div class="sdrf-example-table">{transformed}{legend_html}</div>'


def process_html_file(filepath: Path) -> None:
    """Process an HTML file to transform SDRF tables."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all tables
    table_pattern = r'<table[^>]*class="[^"]*tableblock[^"]*"[^>]*>.*?</table>'

    def replace_table(match):
        table_html = match.group(0)
        return transform_table(table_html)

    new_content = re.sub(table_pattern, replace_table, content, flags=re.DOTALL)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Transformed SDRF tables in: {filepath}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transform-sdrf-tables.py <output_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])

    # Process all HTML files
    html_files = list(output_dir.glob("**/*.html"))

    for html_file in html_files:
        process_html_file(html_file)

    print("SDRF table transformation complete!")


if __name__ == "__main__":
    main()
