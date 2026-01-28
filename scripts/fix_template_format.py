#!/usr/bin/env python3
"""
Fix template format in already-migrated SDRF files.
Converts from: template_name,version=vX.Y.Z
To: NT=template_name;version=vX.Y.Z

Both formats are now valid:
- NT=name;version=vX.Y.Z (key=value format)
- name vX.Y.Z (simple format)
"""

import os
import re
from pathlib import Path


def fix_template_format(file_path: Path) -> bool:
    """Fix template format in a single SDRF file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern to match comma format: word,version=vX.Y.Z -> NT=word;version=vX.Y.Z
    old_pattern = r'\b([\w-]+),version=(v[\d.]+[\w.-]*)'
    new_format = r'NT=\1;version=\2'

    new_content = re.sub(old_pattern, new_format, content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    base_dir = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects")

    fixed = 0
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".sdrf.tsv"):
                file_path = Path(root) / f
                if fix_template_format(file_path):
                    print(f"Fixed: {file_path.relative_to(base_dir)}")
                    fixed += 1

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
