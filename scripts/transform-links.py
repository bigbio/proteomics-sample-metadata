#!/usr/bin/env python3
"""
Transform GitHub annotated-projects links to SDRF Explorer viewer links.

Usage: python3 transform-links.py <html_file>

This script replaces links like:
  https://github.com/bigbio/proteomics-metadata-standard/tree/master/annotated-projects/PXD123456
with:
  ./sdrf-explorer.html?view=PXD123456
"""

import sys
import re
from pathlib import Path


def transform_links(filepath: str) -> int:
    """Transform GitHub annotated-projects links to SDRF Explorer links.

    Returns the number of links transformed.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match GitHub annotated-projects links
    pattern = r'href="https://github\.com/bigbio/proteomics-metadata-standard/tree/master/annotated-projects/(PXD\d+)"'
    replacement = r'href="./sdrf-explorer.html?view=\1"'

    new_content, count = re.subn(pattern, replacement, content)

    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transform-links.py <html_file>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    count = transform_links(str(filepath))
    print(f"Transformed {count} SDRF links in {filepath}")


if __name__ == "__main__":
    main()
