# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Multi-file vendor format annotation** (`comment[associated data file]`, `comment[associated file uri]`): new sidecar columns to describe auxiliary files that must be downloaded alongside a primary raw file (e.g. AB Sciex `.wiff.scan` companion to a `.wiff`). `comment[data file]` and `comment[file uri]` continue to reference the primary/canonical file; the auxiliary columns are repeated positionally when more than one auxiliary file is needed. New specification section (`Vendor formats that ship multiple files`) and AB Sciex example (`examples/PXD073289`). Resolves https://github.com/bigbio/proteomics-sample-metadata/issues/761.
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
- **Core templates in YAML format** for validation: ms-proteomics, human, vertebrates, invertebrates, plants.
- **Metadata guidelines documentation**:
  - Sample metadata guidelines (sample-metadata.adoc)
  - Human-specific metadata guidelines (templates/human/README.adoc)
  - MS data file metadata (in ms-proteomics template)
  - SDRF terms reference (sdrf-terms.tsv)
- **Template Builder page** (site/sdrf-builder.html): dedicated interactive wizard for building customized SDRF templates by selecting technology, organism, and experiment type.
- **Metaproteomics examples**: PXD005969 (human gut, extraction methods), PXD003572 (soil, Mediterranean dryland), PXD009712 (ocean, Pacific depth profiles).
- **Website infrastructure** (site/): homepage, SDRF explorer, terms reference, search functionality, CSS styling.
- **PDF generation workflow** with custom theme for specification documents.
- File-level metadata support using dedicated columns (`comment[sdrf version]`, `comment[sdrf template]`, `comment[sdrf annotation tool]`) for capturing SDRF version, template, and provenance information.
- Row uniqueness requirements documentation (renamed to "Additional SDRF Rules"):
  - Error-level: source name + assay name + comment[label] must be unique.
  - Warning-level: source name + assay name should be unique.
- Validation of 256+ annotated projects.
- Abbreviated SDRF examples use `...` columns to indicate omitted columns.

### Changed

- **Template architecture refactoring**: Introduced `sample-metadata` intermediate template between `base` and technology/organism templates. Columns `organism`, `organism part`, `cell type`, `biological replicate`, and `pooled sample` moved from `base` to `sample-metadata`. Columns `disease` and `biosample accession number` consolidated from organism templates into `sample-metadata` (RECOMMENDED and OPTIONAL respectively; organism templates override disease to REQUIRED). All technology templates (`ms-proteomics`, `affinity-proteomics`) and organism templates (`human`, `vertebrates`, `invertebrates`, `plants`) now extend `sample-metadata` instead of `base`. No change to effective validation for any template combination.
- **Version bump to v1.1.0**.
- **BREAKING: `comment[technical replicate]`** changed from RECOMMENDED to REQUIRED in base template. All inheriting templates now require a technical replicate column. Existing SDRF files without this column will fail validation -- add the column with value `1` for single-run samples.
- **BREAKING: Immunopeptidomics field renames**: `characteristics[MHC class]` → `characteristics[MHC protein complex]` (GO:0042611), `characteristics[MHC allele]`/`characteristics[HLA typing]` → `characteristics[MHC typing]` (PRIDE:0000893), `characteristics[HLA typing method]` → `characteristics[MHC typing method]` (PRIDE:0000894). Values updated to use MRO/GO ontology terms. Existing datasets must update column names and values.
- **Organism templates**: `developmental stage` and `strain/breed` changed to REQUIRED in invertebrates, vertebrates, and plants. `sex` changed to RECOMMENDED in vertebrates. `growth conditions` and `treatment` changed to RECOMMENDED in plants.
- **Human template**: `age` and `sex` changed to REQUIRED. Age pattern now allows standalone month/week/day values (e.g. `6M`, `3W`, `14D`).
- **BioSample accession**: regex fixed from `^SAM[NED]A?\d+$` to `^SAM(N|EA|D)\d+$` to reject invalid prefixes.
- **Affinity proteomics**: version set to 1.0.0. `comment[instrument]` renamed to `comment[platform]` (REQUIRED); new `comment[instrument]` added as OPTIONAL for actual sequencer/reader. Sample type values normalized to use spaces (`sample control`, `negative control`, etc.).
- **Cell-lines**: added PATO ontology to disease field for `normal` (PATO:0000461). Added `characteristics[culture medium]` (RECOMMENDED) and `characteristics[storage temperature]` (RECOMMENDED).
- **MS-proteomics/DDA**: mass tolerance patterns updated to accept `not available`/`not applicable` when those flags are set. DDA mass tolerance kept as RECOMMENDED.
- **Quick Start page** refactored as an educational concepts guide (column types, ontology usage, common patterns, validation) with CTA linking to the new Template Builder.
- **Navigation** updated across all pages to include Template Builder link.
- **CI/CD link checker** optimized with concurrency limits, retries, and GITHUB_TOKEN to avoid 429 rate-limit failures. Fixed stale repository URLs (proteomics-sample-metadata → proteomics-metadata-standard).
- **Dev/Stable version links** now use a placeholder system in inject-headers.py, resolved at build time based on `--dev` flag.
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

