#!/usr/bin/env python3
"""
Fix column order in SDRF files.
Moves all 'factor value[*]' columns to the end of the file.
Also strips trailing whitespace from all cells.
"""

import os
import pandas as pd
from pathlib import Path


def fix_sdrf_file(file_path: Path) -> dict:
    """
    Fix column order and whitespace in a single SDRF file.

    Returns dict with info about changes made.
    """
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    changes = {
        "column_order_fixed": False,
        "whitespace_fixed": False,
        "factor_columns_moved": [],
    }

    # 1. Strip trailing whitespace from all cells
    df_stripped = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    if not df.equals(df_stripped):
        changes["whitespace_fixed"] = True
        df = df_stripped

    # 2. Reorder columns - factor value columns should be last
    columns = df.columns.tolist()

    # Separate factor value columns from others
    factor_cols = [c for c in columns if c.lower().startswith("factor value[")]
    non_factor_cols = [c for c in columns if not c.lower().startswith("factor value[")]

    # Check if reordering is needed
    if factor_cols:
        # Find the position of first factor column in original
        first_factor_idx = min(columns.index(c) for c in factor_cols)
        # Check if any non-factor column comes after the first factor column
        non_factor_after_factor = [c for c in non_factor_cols if columns.index(c) > first_factor_idx]

        if non_factor_after_factor:
            # Reordering needed
            new_order = non_factor_cols + factor_cols
            df = df[new_order]
            changes["column_order_fixed"] = True
            changes["factor_columns_moved"] = factor_cols

    # Save if any changes were made
    if changes["column_order_fixed"] or changes["whitespace_fixed"]:
        df.to_csv(file_path, sep="\t", index=False)

    return changes


def main():
    base_dir = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects")

    stats = {
        "total_files": 0,
        "files_with_column_order_fixed": 0,
        "files_with_whitespace_fixed": 0,
        "unchanged_files": 0,
    }

    fixed_files = []

    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".sdrf.tsv"):
                file_path = Path(root) / f
                stats["total_files"] += 1

                try:
                    changes = fix_sdrf_file(file_path)

                    if changes["column_order_fixed"] or changes["whitespace_fixed"]:
                        project = file_path.parent.name
                        fixed_files.append((project, changes))

                        if changes["column_order_fixed"]:
                            stats["files_with_column_order_fixed"] += 1
                        if changes["whitespace_fixed"]:
                            stats["files_with_whitespace_fixed"] += 1
                    else:
                        stats["unchanged_files"] += 1

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Print summary
    print("=" * 60)
    print("SDRF FIX SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files with column order fixed: {stats['files_with_column_order_fixed']}")
    print(f"Files with whitespace fixed: {stats['files_with_whitespace_fixed']}")
    print(f"Unchanged files: {stats['unchanged_files']}")

    if fixed_files:
        print("\n" + "=" * 60)
        print("FIXED FILES:")
        print("=" * 60)
        for project, changes in fixed_files:
            fixes = []
            if changes["column_order_fixed"]:
                fixes.append(f"column order (moved: {', '.join(changes['factor_columns_moved'])})")
            if changes["whitespace_fixed"]:
                fixes.append("whitespace")
            print(f"  {project}: {', '.join(fixes)}")


if __name__ == "__main__":
    main()
