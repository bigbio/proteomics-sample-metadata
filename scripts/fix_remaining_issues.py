#!/usr/bin/env python3
"""
Fix remaining validation issues in specific SDRF files.

1. PXD004242 - source name has "not applicable" in pattern -> PXD004242-Sample-{number}
2. PXD005445 - source name "not available" -> PXD005445-Sample-{number}
3. PXD005780 - assay name "not available" -> create from source name
4. PXD011153 - missing comment[proteomics data acquisition method] -> add column
5. PXD012986 - technology type "not available" -> "proteomic profiling by mass spectrometry"
6. PXD025706 - technology type case inconsistency -> normalize to lowercase
7. PXD042173 - missing characteristics[disease] -> add column with "not applicable"
"""

import pandas as pd
from pathlib import Path


def fix_pxd004242():
    """Fix source names containing 'not applicable'."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD004242/PXD004242.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    # Find rows where source name contains "not applicable"
    mask = df["source name"].str.contains("not applicable", case=False)

    if mask.any():
        # Create a counter for unique sample numbers
        sample_counter = 1
        for idx in df[mask].index:
            old_name = df.loc[idx, "source name"]
            # Extract any identifying info from the old name (e.g., F1, F2)
            prefix = old_name.split()[0] if old_name.split() else ""
            df.loc[idx, "source name"] = f"PXD004242-{prefix}-Sample-{sample_counter}"
            sample_counter += 1

        df.to_csv(file_path, sep="\t", index=False)
        print(f"PXD004242: Fixed {mask.sum()} source names with 'not applicable'")
    return mask.sum()


def fix_pxd005445():
    """Fix source names that are 'not available'."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD005445/PXD005445.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    mask = df["source name"].str.lower().str.strip() == "not available"

    if mask.any():
        sample_counter = 1
        for idx in df[mask].index:
            df.loc[idx, "source name"] = f"PXD005445-Sample-{sample_counter}"
            sample_counter += 1

        df.to_csv(file_path, sep="\t", index=False)
        print(f"PXD005445: Fixed {mask.sum()} source names with 'not available'")
    return mask.sum()


def fix_pxd005780():
    """Fix assay names that are 'not available'."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD005780/PXD005780.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    mask = df["assay name"].str.lower().str.strip() == "not available"

    if mask.any():
        # Create assay names from source name + row number
        for idx in df[mask].index:
            source = df.loc[idx, "source name"]
            # Use data file name as base for assay name if available
            data_file = df.loc[idx, "comment[data file]"] if "comment[data file]" in df.columns else ""
            if data_file:
                # Remove extension and use as assay name
                assay_name = data_file.replace(".raw", "").replace(".RAW", "")
            else:
                assay_name = f"{source}_run_{idx+1}"
            df.loc[idx, "assay name"] = assay_name

        df.to_csv(file_path, sep="\t", index=False)
        print(f"PXD005780: Fixed {mask.sum()} assay names with 'not available'")
    return mask.sum()


def fix_pxd011153():
    """Add missing comment[proteomics data acquisition method] column."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD011153/PXD011153.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    if "comment[proteomics data acquisition method]" not in df.columns:
        # Find the position to insert (after technology type if exists)
        if "technology type" in df.columns:
            idx = df.columns.get_loc("technology type") + 1
        else:
            idx = len(df.columns)

        # Add column with DDA as default
        df.insert(idx, "comment[proteomics data acquisition method]", "NT=Data-dependent acquisition;AC=PRIDE:0000627")
        df.to_csv(file_path, sep="\t", index=False)
        print(f"PXD011153: Added comment[proteomics data acquisition method] column")
        return 1
    return 0


def fix_pxd012986():
    """Fix technology type 'not available'."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD012986/PXD012986.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    if "technology type" in df.columns:
        mask = df["technology type"].str.lower().str.strip() == "not available"
        if mask.any():
            df.loc[mask, "technology type"] = "proteomic profiling by mass spectrometry"
            df.to_csv(file_path, sep="\t", index=False)
            print(f"PXD012986: Fixed {mask.sum()} rows with technology type 'not available'")
            return mask.sum()
    return 0


def fix_pxd025706():
    """Normalize technology type case."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD025706/PXD025706.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    if "technology type" in df.columns:
        # Find rows with uppercase "Proteomic"
        mask = df["technology type"].str.startswith("Proteomic")
        if mask.any():
            df.loc[mask, "technology type"] = "proteomic profiling by mass spectrometry"
            df.to_csv(file_path, sep="\t", index=False)
            print(f"PXD025706: Normalized {mask.sum()} technology type values to lowercase")
            return mask.sum()
    return 0


def fix_pxd042173():
    """Add missing characteristics[disease] column."""
    file_path = Path("/Users/yperez/work/proteomics-metadata-standard/annotated-projects/PXD042173/PXD042173.sdrf.tsv")
    df = pd.read_csv(file_path, sep="\t", dtype=str).fillna("")

    if "characteristics[disease]" not in df.columns:
        # Find the position to insert (after organism part or cell type)
        if "characteristics[cell type]" in df.columns:
            idx = df.columns.get_loc("characteristics[cell type]") + 1
        elif "characteristics[organism part]" in df.columns:
            idx = df.columns.get_loc("characteristics[organism part]") + 1
        else:
            idx = 3

        # Add column with "not applicable" for recombinant protein samples
        df.insert(idx, "characteristics[disease]", "not applicable")
        df.to_csv(file_path, sep="\t", index=False)
        print(f"PXD042173: Added characteristics[disease] column with 'not applicable'")
        return 1
    return 0


def main():
    print("=" * 60)
    print("FIXING REMAINING VALIDATION ISSUES")
    print("=" * 60)

    fixes = {
        "PXD004242": fix_pxd004242(),
        "PXD005445": fix_pxd005445(),
        "PXD005780": fix_pxd005780(),
        "PXD011153": fix_pxd011153(),
        "PXD012986": fix_pxd012986(),
        "PXD025706": fix_pxd025706(),
        "PXD042173": fix_pxd042173(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for project, count in fixes.items():
        if count > 0:
            print(f"  {project}: {count} fixes applied")


if __name__ == "__main__":
    main()
