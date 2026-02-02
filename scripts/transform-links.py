#!/usr/bin/env python3
"""
Transform links in built HTML files for the SDRF-Proteomics website.

Usage: python3 transform-links.py <html_file_or_directory>

This script performs two types of transformations:

1. GitHub annotated-projects links to SDRF Explorer viewer links:
   https://github.com/bigbio/proteomics-metadata-standard/tree/master/annotated-projects/PXD123456
   -> ./sdrf-explorer.html?view=PXD123456

2. AsciiDoc links (.adoc) to HTML links (.html):
   - README.adoc -> specification.html (for main spec)
   - ../templates/human/README.adoc -> human.html (from templates)
   - ../../README.adoc -> ../specification.html (from templates)
   - metadata-guidelines/sample-metadata.adoc -> metadata-guidelines/sample-metadata.html
"""

import sys
import re
from pathlib import Path


def transform_sdrf_explorer_links(content: str) -> tuple[str, int]:
    """Transform GitHub annotated-projects links to SDRF Explorer links."""
    pattern = r'href="https://github\.com/bigbio/proteomics-metadata-standard/tree/master/annotated-projects/(PXD\d+)"'
    replacement = r'href="./sdrf-explorer.html?view=\1"'
    return re.subn(pattern, replacement, content)


def transform_adoc_links(content: str, filepath: str) -> tuple[str, int]:
    """Transform .adoc links to .html links based on file location."""
    count = 0

    # Determine if this file is in templates/ or metadata-guidelines/ directory
    is_template = '/templates/' in filepath
    is_metadata_guidelines = '/metadata-guidelines/' in filepath

    # Pattern 1: ../../README.adoc -> ../specification.html (from templates)
    pattern1 = r'href="\.\.\/\.\.\/README\.adoc([^"]*)"'
    replacement1 = r'href="../specification.html\1"'
    content, c = re.subn(pattern1, replacement1, content)
    count += c

    # Pattern 2: ../templates/XXXX/README.adoc -> ../templates/XXXX.html (from metadata-guidelines)
    pattern2 = r'href="\.\.\/templates\/([^/]+)\/README\.adoc([^"]*)"'
    replacement2 = r'href="../templates/\1.html\2"'
    content, c = re.subn(pattern2, replacement2, content)
    count += c

    # Pattern 3: ../XXXX/README.adoc -> XXXX.html (from templates - sibling template)
    pattern3 = r'href="\.\.\/([^/]+)\/README\.adoc([^"]*)"'
    replacement3 = r'href="\1.html\2"'
    content, c = re.subn(pattern3, replacement3, content)
    count += c

    # Pattern 4: templates/XXXX/README.adoc -> templates/XXXX.html (from root)
    pattern4 = r'href="templates\/([^/]+)\/README\.adoc([^"]*)"'
    replacement4 = r'href="templates/\1.html\2"'
    content, c = re.subn(pattern4, replacement4, content)
    count += c

    # Pattern 5: metadata-guidelines/XXXX.adoc -> metadata-guidelines/XXXX.html
    pattern5 = r'href="(\.\.\/)?metadata-guidelines\/([^"]+)\.adoc([^"]*)"'
    replacement5 = r'href="\1metadata-guidelines/\2.html\3"'
    content, c = re.subn(pattern5, replacement5, content)
    count += c

    # Pattern 6: README.adoc -> specification.html (from same directory as spec)
    pattern6 = r'href="README\.adoc([^"]*)"'
    replacement6 = r'href="specification.html\1"'
    content, c = re.subn(pattern6, replacement6, content)
    count += c

    # Pattern 7: tool-support.adoc -> tool-support.html
    pattern7 = r'href="(\.\.\/)?tool-support\.adoc([^"]*)"'
    replacement7 = r'href="\1tool-support.html\2"'
    content, c = re.subn(pattern7, replacement7, content)
    count += c

    # Pattern 8: Any remaining .adoc links - generic transformation
    pattern8 = r'href="([^"]*?)\.adoc([^"]*)"'
    replacement8 = r'href="\1.html\2"'
    content, c = re.subn(pattern8, replacement8, content)
    count += c

    return content, count


def transform_file(filepath: str) -> dict:
    """Transform all links in a single HTML file.

    Returns dict with counts of each transformation type.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply transformations
    content, sdrf_count = transform_sdrf_explorer_links(content)
    content, adoc_count = transform_adoc_links(content, filepath)

    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return {
        'sdrf_explorer': sdrf_count,
        'adoc_to_html': adoc_count,
        'total': sdrf_count + adoc_count
    }


def transform_directory(dirpath: str) -> dict:
    """Transform all HTML files in a directory recursively."""
    total_counts = {'sdrf_explorer': 0, 'adoc_to_html': 0, 'total': 0, 'files': 0}

    for html_file in Path(dirpath).rglob('*.html'):
        counts = transform_file(str(html_file))
        if counts['total'] > 0:
            total_counts['files'] += 1
            total_counts['sdrf_explorer'] += counts['sdrf_explorer']
            total_counts['adoc_to_html'] += counts['adoc_to_html']
            total_counts['total'] += counts['total']
            print(f"  {html_file}: {counts['total']} links transformed")

    return total_counts


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transform-links.py <html_file_or_directory>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if not target.exists():
        print(f"Error: Path not found: {target}")
        sys.exit(1)

    if target.is_file():
        counts = transform_file(str(target))
        print(f"Transformed {counts['total']} links in {target}")
        print(f"  - SDRF Explorer links: {counts['sdrf_explorer']}")
        print(f"  - AsciiDoc to HTML links: {counts['adoc_to_html']}")
    else:
        counts = transform_directory(str(target))
        print(f"\nTotal: Transformed {counts['total']} links in {counts['files']} files")
        print(f"  - SDRF Explorer links: {counts['sdrf_explorer']}")
        print(f"  - AsciiDoc to HTML links: {counts['adoc_to_html']}")


if __name__ == "__main__":
    main()
