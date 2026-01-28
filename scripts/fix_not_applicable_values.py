#!/usr/bin/env python3
"""
Fix 'not applicable' values that are not allowed by the schema.

Fixes:
1. characteristics[age] = 'not applicable' -> 'not available'
   (cell lines don't have a meaningful age, schema allows 'not available')
2. characteristics[biological replicate] = 'not applicable' -> '1'
   (every sample is at least replicate 1)
3. comment[technical replicate] = 'not applicable' -> '1'
   (every run is at least technical replicate 1)
"""

import os
import pandas as pd
from pathlib import Path


def fix_not_applicable(file_path: Path) -> dict:
    """Fix 'not applicable' values in a single SDRF file."""
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")
    original_df = df.copy()

    changes = {
        "age_fixed": 0,
        "biological_replicate_fixed": 0,
        "technical_replicate_fixed": 0,
    }

    # 1. Fix characteristics[age]: 'not applicable' -> 'not available'
    age_cols = [c for c in df.columns if c.lower() == "characteristics[age]"]
    for col in age_cols:
        mask = df[col].str.lower().str.strip() == "not applicable"
        if mask.any():
            changes["age_fixed"] += mask.sum()
            df.loc[mask, col] = "not available"

    # 2. Fix characteristics[biological replicate]: 'not applicable' -> '1'
    bio_rep_cols = [c for c in df.columns if "biological replicate" in c.lower()]
    for col in bio_rep_cols:
        mask = df[col].str.lower().str.strip() == "not applicable"
        if mask.any():
            changes["biological_replicate_fixed"] += mask.sum()
            df.loc[mask, col] = "1"

    # 3. Fix comment[technical replicate]: 'not applicable' -> '1'
    tech_rep_cols = [c for c in df.columns if "technical replicate" in c.lower()]
    for col in tech_rep_cols:
        mask = df[col].str.lower().str.strip() == "not applicable"
        if mask.any():
            changes["technical_replicate_fixed"] += mask.sum()
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
        "age_fixed": 0,
        "biological_replicate_fixed": 0,
        "technical_replicate_fixed": 0,
    }

    modified_files = []

    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".sdrf.tsv"):
                file_path = Path(root) / f
                stats["total_files"] += 1

                try:
                    changes = fix_not_applicable(file_path)

                    total_changes = sum(changes.values())
                    if total_changes > 0:
                        project = file_path.parent.name
                        modified_files.append((project, f, changes))
                        stats["files_modified"] += 1
                        stats["age_fixed"] += changes["age_fixed"]
                        stats["biological_replicate_fixed"] += changes["biological_replicate_fixed"]
                        stats["technical_replicate_fixed"] += changes["technical_replicate_fixed"]

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Print summary
    print("=" * 60)
    print("NOT APPLICABLE FIX SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Age 'not applicable' -> 'not available': {stats['age_fixed']} cells")
    print(f"Biological replicate 'not applicable' -> '1': {stats['biological_replicate_fixed']} cells")
    print(f"Technical replicate 'not applicable' -> '1': {stats['technical_replicate_fixed']} cells")

    if modified_files:
        print("\n" + "=" * 60)
        print("MODIFIED FILES:")
        print("=" * 60)
        for project, filename, changes in modified_files:
            fixes = []
            if changes["age_fixed"]:
                fixes.append(f"age: {changes['age_fixed']}")
            if changes["biological_replicate_fixed"]:
                fixes.append(f"bio_rep: {changes['biological_replicate_fixed']}")
            if changes["technical_replicate_fixed"]:
                fixes.append(f"tech_rep: {changes['technical_replicate_fixed']}")
            print(f"  {project}/{filename}: {', '.join(fixes)}")


if __name__ == "__main__":
    main()
