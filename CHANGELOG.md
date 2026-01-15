# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Validation of 256 annotated projects.
- Introduction of the ChangeLog file to the project.
- File-level metadata support using header comments (#key=value format) for capturing SDRF version, template, and provenance information (Issue #758).
- Row uniqueness requirements documentation in the specification (Issues #749, #750, #767):
  - Error-level: source name + assay name + comment[label] must be unique.
  - Warning-level: source name + assay name should be unique.
  - Assay name uniqueness guidance for multiplexed experiments.

### Changed

- Small changes in typos and grammar in the SDRF specification document (sdrf-proteomics/README.adoc).
- Update of the enzyme.tsv file in the SDRF specification document (sdrf-proteomics/enzymes.tsv).
- Remove enzyme regular expression as recommended in the SDRF specification document (sdrf-proteomics/README.adoc).
- Standardized proteomics data acquisition method terms across all annotated projects:
  - DDA: `Data-dependent acquisition` with accession `PRIDE:0000627`.
  - DIA: `Data-independent acquisition` with accession `PRIDE:0000450`.

### Removed

- Outdated readthedocs link, main documentation is the SDRF specification document (sdrf-proteomics/README.adoc).

## [1.0.0] - 2023-05-24

### Added

- First release of the project.
- First version of the SDRF specification document (psi-document/SDRF_Proteomics_Specification_v1.0.0.docx).
- First projects annotated in the SDRF format.

### Fixed

- Nothing fixed.

### Changed

- Nothing changed. 

### Removed

- Nothing removed.

