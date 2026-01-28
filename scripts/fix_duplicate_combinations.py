#!/usr/bin/env python3
"""
Fix duplicate row combinations in SDRF files.

The validator checks that (source name, assay name, comment[label]) combinations are unique.
When duplicates exist, this script:
1. If fraction identifiers differ: append fraction to source name
2. If technical replicates differ: append tech rep to assay name
3. If data files differ: append sequence number to source name
"""

import os
import pandas as pd
from pathlib import Path
from collections import Counter


def fix_duplicates(file_path: Path) -> dict:
    """Fix duplicate combinations in a single SDRF file.

    Runs multiple passes to handle nested duplicates (e.g., same sample+fraction
    run multiple times).
    """
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")
    original_df = df.copy()

    changes = {
        "duplicates_fixed": 0,
        "methods": [],
    }

    key_cols = ["source name", "assay name", "comment[label]"]

    # Check if all key columns exist
    missing = [c for c in key_cols if c not in df.columns]
    if missing:
        return changes

    # Run multiple passes until no more duplicates
    max_passes = 5
    for pass_num in range(max_passes):
        # Find duplicates
        dup_mask = df.duplicated(subset=key_cols, keep=False)
        if not dup_mask.any():
            break

        pass_fixed = 0

        # Group duplicates and analyze what differs
        for key_tuple, group in df[dup_mask].groupby(key_cols):
            if len(group) <= 1:
                continue

            indices = group.index.tolist()

            # Check what differs between duplicates
            fraction_col = "comment[fraction identifier]"
            tech_rep_col = "comment[technical replicate]"
            data_file_col = "comment[data file]"

            fixed_this_group = False

            # Option 1: Different fractions - append fraction to source name
            if not fixed_this_group and fraction_col in df.columns:
                fractions = df.loc[indices, fraction_col].tolist()
                unique_fractions = set(fractions)
                if len(unique_fractions) > 1:
                    for idx in indices:
                        frac = df.loc[idx, fraction_col]
                        if frac and frac.strip():
                            old_source = df.loc[idx, "source name"]
                            if f"_frac_{frac}" not in old_source:
                                df.loc[idx, "source name"] = f"{old_source}_frac_{frac}"
                                pass_fixed += 1
                                if "fraction" not in changes["methods"]:
                                    changes["methods"].append("fraction")
                    fixed_this_group = True

            # Option 2: Different technical replicates - append to assay name
            if not fixed_this_group and tech_rep_col in df.columns:
                tech_reps = df.loc[indices, tech_rep_col].tolist()
                unique_tech_reps = set(tech_reps)
                if len(unique_tech_reps) > 1:
                    for idx in indices:
                        tech_rep = df.loc[idx, tech_rep_col]
                        if tech_rep and tech_rep.strip():
                            old_assay = df.loc[idx, "assay name"]
                            if f"_tech_{tech_rep}" not in old_assay:
                                df.loc[idx, "assay name"] = f"{old_assay}_tech_{tech_rep}"
                                pass_fixed += 1
                                if "tech_rep" not in changes["methods"]:
                                    changes["methods"].append("tech_rep")
                    fixed_this_group = True

            # Option 3: Different data files - append run number
            if not fixed_this_group and data_file_col in df.columns:
                data_files = df.loc[indices, data_file_col].tolist()
                unique_files = set(data_files)
                if len(unique_files) > 1:
                    for i, idx in enumerate(indices):
                        old_source = df.loc[idx, "source name"]
                        if "_run_" not in old_source:
                            df.loc[idx, "source name"] = f"{old_source}_run_{i+1}"
                            pass_fixed += 1
                            if "data_file" not in changes["methods"]:
                                changes["methods"].append("data_file")
                    fixed_this_group = True

            # Option 4: Last resort - add sequence number
            if not fixed_this_group:
                for i, idx in enumerate(indices):
                    if i > 0:  # Keep first one unchanged
                        old_source = df.loc[idx, "source name"]
                        df.loc[idx, "source name"] = f"{old_source}_{i+1}"
                        pass_fixed += 1
                        if "sequence" not in changes["methods"]:
                            changes["methods"].append("sequence")

        changes["duplicates_fixed"] += pass_fixed
        if pass_fixed == 0:
            break

    # Save if changes were made
    if not df.equals(original_df):
        df.to_csv(file_path, sep="\t", index=False)

    return changes


def main():
    base_dir = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects")

    stats = {
        "total_files": 0,
        "files_modified": 0,
        "total_duplicates_fixed": 0,
    }

    modified_files = []

    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".sdrf.tsv"):
                file_path = Path(root) / f
                stats["total_files"] += 1

                try:
                    changes = fix_duplicates(file_path)

                    if changes["duplicates_fixed"] > 0:
                        project = file_path.parent.name
                        modified_files.append((project, f, changes))
                        stats["files_modified"] += 1
                        stats["total_duplicates_fixed"] += changes["duplicates_fixed"]

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Print summary
    print("=" * 60)
    print("DUPLICATE COMBINATION FIX SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Total duplicates fixed: {stats['total_duplicates_fixed']}")

    if modified_files:
        print("\n" + "=" * 60)
        print("MODIFIED FILES:")
        print("=" * 60)
        for project, filename, changes in modified_files:
            methods = ", ".join(changes.get("methods", [])) or "unknown"
            print(f"  {project}/{filename}: {changes['duplicates_fixed']} rows fixed (methods: {methods})")


if __name__ == "__main__":
    main()
