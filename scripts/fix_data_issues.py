#!/usr/bin/env python3
"""
Fix specific data issues in SDRF files:
1. comment[fraction identifier] with 'not applicable' -> '1'
2. Age with spaces ('30Y 6M' -> '30Y6M')
3. 'adult' in characteristics[age] -> move to characteristics[developmental stage]
"""

import os
import re
import pandas as pd
from pathlib import Path


def fix_sdrf_file(file_path: Path) -> dict:
    """Fix data issues in a single SDRF file."""
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")
    original_df = df.copy()

    changes = {
        "fraction_identifier_fixed": 0,
        "age_space_fixed": 0,
        "adult_moved_to_developmental_stage": 0,
    }

    # 1. Fix fraction identifier: 'not applicable' -> '1'
    fraction_cols = [c for c in df.columns if "fraction identifier" in c.lower()]
    for col in fraction_cols:
        mask = df[col].str.lower().str.strip() == "not applicable"
        if mask.any():
            changes["fraction_identifier_fixed"] += mask.sum()
            df.loc[mask, col] = "1"

    # 2. Fix age with spaces: '30Y 6M' -> '30Y6M', '3Y 11M' -> '3Y11M'
    age_cols = [c for c in df.columns if c.lower() == "characteristics[age]"]
    for col in age_cols:
        # Pattern to match ages with spaces like "30Y 6M" or "3Y 11M"
        def fix_age_space(val):
            if pd.isna(val) or val.strip() == "":
                return val
            # Remove spaces between number+unit combinations
            fixed = re.sub(r"(\d+[yYmMwWdD])\s+(\d+[mMwWdD])", r"\1\2", val)
            return fixed

        original_values = df[col].copy()
        df[col] = df[col].apply(fix_age_space)
        changes["age_space_fixed"] += (original_values != df[col]).sum()

    # 3. Move 'adult' from age to developmental stage
    age_cols = [c for c in df.columns if c.lower() == "characteristics[age]"]
    for col in age_cols:
        mask = df[col].str.lower().str.strip() == "adult"
        if mask.any():
            changes["adult_moved_to_developmental_stage"] += mask.sum()

            # Find or create developmental stage column
            dev_stage_cols = [c for c in df.columns if "developmental stage" in c.lower()]
            if dev_stage_cols:
                dev_col = dev_stage_cols[0]
            else:
                # Insert developmental stage column after age column
                age_idx = df.columns.get_loc(col)
                dev_col = "characteristics[developmental stage]"
                df.insert(age_idx + 1, dev_col, "")

            # Move 'adult' to developmental stage and set age to 'not available'
            df.loc[mask, dev_col] = "adult"
            df.loc[mask, col] = "not available"

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
        "fraction_identifier_fixed": 0,
        "age_space_fixed": 0,
        "adult_moved": 0,
    }

    modified_files = []

    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".sdrf.tsv"):
                file_path = Path(root) / f
                stats["total_files"] += 1

                try:
                    changes = fix_sdrf_file(file_path)

                    total_changes = sum(changes.values())
                    if total_changes > 0:
                        project = file_path.parent.name
                        modified_files.append((project, f, changes))
                        stats["files_modified"] += 1
                        stats["fraction_identifier_fixed"] += changes["fraction_identifier_fixed"]
                        stats["age_space_fixed"] += changes["age_space_fixed"]
                        stats["adult_moved"] += changes["adult_moved_to_developmental_stage"]

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Print summary
    print("=" * 60)
    print("DATA FIX SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Fraction identifier 'not applicable' -> '1': {stats['fraction_identifier_fixed']} cells")
    print(f"Age spaces removed: {stats['age_space_fixed']} cells")
    print(f"'adult' moved to developmental stage: {stats['adult_moved']} cells")

    if modified_files:
        print("\n" + "=" * 60)
        print("MODIFIED FILES:")
        print("=" * 60)
        for project, filename, changes in modified_files:
            fixes = []
            if changes["fraction_identifier_fixed"]:
                fixes.append(f"fraction_id: {changes['fraction_identifier_fixed']}")
            if changes["age_space_fixed"]:
                fixes.append(f"age_space: {changes['age_space_fixed']}")
            if changes["adult_moved_to_developmental_stage"]:
                fixes.append(f"adult_moved: {changes['adult_moved_to_developmental_stage']}")
            print(f"  {project}/{filename}: {', '.join(fixes)}")


if __name__ == "__main__":
    main()
