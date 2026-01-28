#!/usr/bin/env python3
"""
Migrate SDRF files from header-based to column-based metadata.

This script:
1. Reads SDRF files with header comments (#file_format, #version, #template, etc.)
2. Extracts metadata from headers
3. Adds metadata columns to the TSV
4. Removes header comment lines
5. Writes updated SDRF files

Usage:
    python migrate_sdrf_to_columns.py [--dry-run] [path_to_sdrf_or_directory]
"""

import argparse
import os
import re
import sys
from pathlib import Path


def parse_header_metadata(content: str) -> dict:
    """Parse metadata from header comment lines."""
    metadata = {
        "file_format": None,
        "version": None,
        "templates": [],
        "source": None,
        "validation_hash": None,
    }

    lines = content.split("\n")
    for line in lines:
        if not line.startswith("#"):
            break

        # Parse #key=value or #key=value1,key2=value2 format
        line = line[1:].strip()  # Remove leading #

        # Handle template format: template=name,version=vX.Y.Z
        if line.startswith("template="):
            # Extract everything after "template="
            template_value = line[9:]  # len("template=") = 9
            # Convert from old format (name,version=vX.Y.Z) to new format (NT=name;version=vX.Y.Z)
            if ",version=" in template_value:
                parts = template_value.split(",version=")
                template_value = f"NT={parts[0]};version={parts[1]}"
            else:
                template_value = f"NT={template_value}"
            metadata["templates"].append(template_value)
        elif line.startswith("file_format="):
            metadata["file_format"] = line[12:]
        elif line.startswith("version="):
            metadata["version"] = line[8:]
        elif line.startswith("source="):
            # Convert source to new format (NT=name;version=vX.Y.Z)
            source_value = line[7:]
            # Try to parse "tool vX.Y.Z" format
            if " v" in source_value:
                parts = source_value.rsplit(" v", 1)
                source_value = f"NT={parts[0]};version=v{parts[1]}"
            elif " " not in source_value:
                source_value = f"NT={source_value}"
            metadata["source"] = source_value
        elif line.startswith("validation_hash="):
            metadata["validation_hash"] = line[16:]

    return metadata


def find_data_start(lines: list[str]) -> int:
    """Find the index of the first non-header, non-empty line."""
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith("#"):
            return i
    return -1


def migrate_sdrf_file(file_path: Path, dry_run: bool = False) -> dict:
    """Migrate a single SDRF file from headers to columns.

    Returns dict with migration info.
    """
    result = {
        "file": str(file_path),
        "status": "skipped",
        "headers_found": [],
        "columns_added": [],
        "error": None,
    }

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Could not read file: {e}"
        return result

    lines = content.split("\n")

    # Check if file has header comments
    has_headers = any(line.startswith("#") for line in lines if line.strip())
    if not has_headers:
        result["status"] = "no_headers"
        return result

    # Parse existing metadata from headers
    metadata = parse_header_metadata(content)
    result["headers_found"] = [k for k, v in metadata.items() if v and (v if isinstance(v, list) else True)]

    # Find the header row (first non-comment line)
    header_idx = find_data_start(lines)
    if header_idx < 0:
        result["status"] = "error"
        result["error"] = "No data header row found"
        return result

    header_line = lines[header_idx]
    columns = header_line.split("\t")

    # Check if already has metadata columns
    has_version_col = any("comment[sdrf version]" in col for col in columns)
    has_template_col = any("comment[sdrf template]" in col for col in columns)
    has_tool_col = any("comment[sdrf annotation tool]" in col for col in columns)

    if has_version_col and has_template_col:
        result["status"] = "already_migrated"
        return result

    # Prepare new columns
    new_columns = columns.copy()
    columns_to_add = []

    if not has_version_col and metadata["version"]:
        new_columns.append("comment[sdrf version]")
        columns_to_add.append(("comment[sdrf version]", metadata["version"]))

    if not has_template_col and metadata["templates"]:
        for template in metadata["templates"]:
            new_columns.append("comment[sdrf template]")
            columns_to_add.append(("comment[sdrf template]", template))

    if not has_tool_col and metadata["source"]:
        new_columns.append("comment[sdrf annotation tool]")
        columns_to_add.append(("comment[sdrf annotation tool]", metadata["source"]))

    result["columns_added"] = [c[0] for c in columns_to_add]

    if dry_run:
        result["status"] = "would_migrate"
        return result

    # Build new content
    new_lines = []

    # New header row
    new_lines.append("\t".join(new_columns))

    # Data rows (skip header comments and old header)
    for i, line in enumerate(lines):
        if i <= header_idx:
            continue
        if not line.strip():
            continue

        # Add metadata values to each data row
        row_values = line.split("\t")
        for col_name, col_value in columns_to_add:
            row_values.append(col_value)
        new_lines.append("\t".join(row_values))

    # Write updated file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
            if new_lines:
                f.write("\n")
        result["status"] = "migrated"
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Could not write file: {e}"

    return result


def find_sdrf_files(path: Path) -> list[Path]:
    """Find all SDRF files in a directory or return the file itself."""
    if path.is_file():
        return [path]

    sdrf_files = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".sdrf.tsv") or f == "sdrf.tsv":
                sdrf_files.append(Path(root) / f)

    return sorted(sdrf_files)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate SDRF files from header-based to column-based metadata"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to SDRF file or directory containing SDRF files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    sdrf_files = find_sdrf_files(path)
    if not sdrf_files:
        print(f"No SDRF files found in {path}")
        sys.exit(0)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Migrating {len(sdrf_files)} SDRF files...")
    print("-" * 60)

    stats = {
        "migrated": 0,
        "would_migrate": 0,
        "already_migrated": 0,
        "no_headers": 0,
        "skipped": 0,
        "error": 0,
    }

    for sdrf_file in sdrf_files:
        result = migrate_sdrf_file(sdrf_file, dry_run=args.dry_run)
        stats[result["status"]] = stats.get(result["status"], 0) + 1

        if result["status"] in ("migrated", "would_migrate"):
            rel_path = sdrf_file.relative_to(path) if sdrf_file.is_relative_to(path) else sdrf_file
            cols = ", ".join(result["columns_added"]) if result["columns_added"] else "none"
            action = "Would migrate" if args.dry_run else "Migrated"
            print(f"{action}: {rel_path} (added: {cols})")
        elif result["status"] == "error":
            print(f"ERROR: {sdrf_file}: {result['error']}")

    print("-" * 60)
    print("Summary:")
    if args.dry_run:
        print(f"  Would migrate: {stats['would_migrate']}")
    else:
        print(f"  Migrated: {stats['migrated']}")
    print(f"  Already migrated: {stats['already_migrated']}")
    print(f"  No headers (skipped): {stats['no_headers']}")
    print(f"  Errors: {stats['error']}")


if __name__ == "__main__":
    main()
