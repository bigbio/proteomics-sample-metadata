# Annotated projects migration notice

The annotated SDRF datasets were moved to a dedicated repository:

- https://github.com/bigbio/sdrf-annotated-datasets

## Why this was moved

The SDRF specification and annotated datasets now evolve on separate lifecycles:

- `bigbio/proteomics-sample-metadata` focuses on specification, docs, and tooling.
- `bigbio/sdrf-annotated-datasets` focuses on curated dataset annotations that can be updated frequently.

This split was discussed in:
- https://github.com/bigbio/proteomics-sample-metadata/issues/817

## New canonical location

Annotated files are now expected in:

`datasets/{ACCESSION}/{ACCESSION}.sdrf.tsv`

Example:

`datasets/PXD000070/PXD000070.sdrf.tsv`

## How to contribute annotated datasets

1. Fork `bigbio/sdrf-annotated-datasets`.
2. Add or update files in `datasets/{ACCESSION}/`.
3. Validate with `parse_sdrf validate-sdrf`.
4. Open a pull request in `bigbio/sdrf-annotated-datasets`.
