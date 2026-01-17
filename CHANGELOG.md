# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01 (Unreleased)

### Added

- **Quick Start section** with minimal example, key concepts, format requirements, and scope clarification.
- **Format Requirements** documenting core SDRF rules (tab-delimited, column structure, row semantics).
- **Scope clarification**: SDRF captures sample-to-data relationships but not downstream analysis parameters (FDR, p-values, etc.).
- **Styled HTML tables** for SDRF examples with color-coded columns (blue=sample, green=data, orange=factor values) and PDF fallback.
- **Ontology table** with direct links to OLS for each ontology, organized by category.
- **Disease annotation guidelines** (link:metadata-guidelines/sample-metadata.adoc#disease-annotation): clarifying `normal` vs `healthy` vs `control` terminology.
- **Pooled reference sample handling**: use `pooled` value for biological replicate, age, sex, and other individual-specific fields.
- **DEVELOPMENT.md**: documentation for building the website locally and contributing.
- **Experiment-specific templates** with YAML validation schemas:
  - Affinity proteomics (Olink, SomaScan)
  - Cell lines (Cellosaurus integration)
  - Crosslinking mass spectrometry (XL-MS)
  - DDA acquisition parameters
  - DIA acquisition parameters
  - Immunopeptidomics (MHC/HLA)
  - Metaproteomics (environmental samples)
  - Single-cell proteomics
- **Core templates in YAML format** for validation: default, human, vertebrates, invertebrates, plants.
- **Metadata guidelines documentation**:
  - Sample metadata guidelines (sample-metadata.adoc)
  - Human-specific metadata guidelines (human-sample-metadata.adoc)
  - Data file metadata guidelines (data-file-metadata.adoc)
  - SDRF terms reference (sdrf-terms.tsv)
- **Website infrastructure** (site/): homepage, SDRF explorer, terms reference, search functionality, CSS styling.
- **PDF generation workflow** with custom theme for specification documents.
- File-level metadata support using header comments (#key=value format) for capturing SDRF version, template, and provenance information.
- Row uniqueness requirements documentation (renamed to "Additional SDRF Rules"):
  - Error-level: source name + assay name + comment[label] must be unique.
  - Warning-level: source name + assay name should be unique.
- Validation of 256+ annotated projects.
- Abbreviated SDRF examples use `...` columns to indicate omitted columns.

### Changed

- **Version bump to v1.1.0**.
- **Specification restructured** with clearer organization: Quick Start → Validation → Specification Structure → Notational Conventions → Sample Metadata → Data File Metadata → Templates → Factor Values.
- **Column naming**: `fileformat` changed to `file_format` for consistency with underscore convention.
- **Ontology recommendations**: added NCIT and PRIDE to general purpose; added PATO for healthy samples (`normal` = PATO:0000461).
- **BioSamples section** shortened with citation added.
- **Replicates section** simplified with clearer examples.
- **Pooled samples section** simplified; added simple `pooled` value option alongside detailed `SN=` format.
- Standardized proteomics data acquisition method terms across all annotated projects.
- Updated enzyme.tsv file; removed enzyme regular expression requirement.
- Small changes in typos and grammar throughout the specification.

### Removed

- Outdated readthedocs link and configuration (.readthedocs.yaml).
- Verbose/redundant sections consolidated into metadata guidelines documents.

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

