#!/usr/bin/env python3
"""
Fix 'not available' values for replicate and fraction columns.

These are identifiers that every experiment has (at least 1), so 'not available'
should be changed to '1'.

Fixes:
1. characteristics[biological replicate] = 'not available' -> '1'
2. comment[technical replicate] = 'not available' -> '1'
3. comment[fraction identifier] = 'not available' -> '1'
"""

import os
import pandas as pd
from pathlib import Path


def fix_not_available(file_path: Path) -> dict:
    """Fix 'not available' values in replicate/fraction columns."""
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")
    original_df = df.copy()

    changes = {
        "biological_replicate_fixed": 0,
        "technical_replicate_fixed": 0,
        "fraction_identifier_fixed": 0,
    }

    # 1. Fix characteristics[biological replicate]: 'not available' -> '1'
    bio_rep_cols = [c for c in df.columns if "biological replicate" in c.lower()]
    for col in bio_rep_cols:
        mask = df[col].str.lower().str.strip() == "not available"
        if mask.any():
            changes["biological_replicate_fixed"] += mask.sum()
            df.loc[mask, col] = "1"

    # 2. Fix comment[technical replicate]: 'not available' -> '1'
    tech_rep_cols = [c for c in df.columns if "technical replicate" in c.lower()]
    for col in tech_rep_cols:
        mask = df[col].str.lower().str.strip() == "not available"
        if mask.any():
            changes["technical_replicate_fixed"] += mask.sum()
            df.loc[mask, col] = "1"

    # 3. Fix comment[fraction identifier]: 'not available' -> '1'
    frac_cols = [c for c in df.columns if "fraction identifier" in c.lower()]
    for col in frac_cols:
        mask = df[col].str.lower().str.strip() == "not available"
        if mask.any():
            changes["fraction_identifier_fixed"] += mask.sum()
            df.loc[mask, col] = "1"

    # Save if any changes were made
    if not df.equals(original_df):
        df.to_csv(file_path, sep="\t", index=False)
        return changes

    return changes


def main():
    base_dir = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects")

    stats = {
        "total_files": 0,
        "files_modified": 0,
        "biological_replicate_fixed": 0,
        "technical_replicate_fixed": 0,
        "fraction_identifier_fixed": 0,
    }

    modified_files = []

    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".sdrf.tsv"):
                file_path = Path(root) / f
                stats["total_files"] += 1

                try:
                    changes = fix_not_available(file_path)

                    total_changes = sum(changes.values())
                    if total_changes > 0:
                        project = file_path.parent.name
                        modified_files.append((project, f, changes))
                        stats["files_modified"] += 1
                        stats["biological_replicate_fixed"] += changes["biological_replicate_fixed"]
                        stats["technical_replicate_fixed"] += changes["technical_replicate_fixed"]
                        stats["fraction_identifier_fixed"] += changes["fraction_identifier_fixed"]

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Print summary
    print("=" * 60)
    print("NOT AVAILABLE REPLICATE/FRACTION FIX SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Biological replicate 'not available' -> '1': {stats['biological_replicate_fixed']} cells")
    print(f"Technical replicate 'not available' -> '1': {stats['technical_replicate_fixed']} cells")
    print(f"Fraction identifier 'not available' -> '1': {stats['fraction_identifier_fixed']} cells")

    if modified_files:
        print("\n" + "=" * 60)
        print("MODIFIED FILES:")
        print("=" * 60)
        for project, filename, changes in modified_files:
            fixes = []
            if changes["biological_replicate_fixed"]:
                fixes.append(f"bio_rep: {changes['biological_replicate_fixed']}")
            if changes["technical_replicate_fixed"]:
                fixes.append(f"tech_rep: {changes['technical_replicate_fixed']}")
            if changes["fraction_identifier_fixed"]:
                fixes.append(f"frac_id: {changes['fraction_identifier_fixed']}")
            print(f"  {project}/{filename}: {', '.join(fixes)}")


if __name__ == "__main__":
    main()
