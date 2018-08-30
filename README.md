PRIDE Metadata Project: “Crowd-sourcing the annotation of public proteomics datasets to improve data reusability”
======

Description of Work
===================

Public proteomics data reuse is currently constrained by the limited technical and biological annotations available in PRIDE datasets (as it also happens in the other PX resources). The current annotation requirements for proteomics datasets in PX are lower than in analogous bioinformatics resources for other data types (e.g. ArrayExpress, for transcriptomics data). These requirements were defined in 2011 (with minor updates in 2013), during the establishment of ProteomeXchange, reflecting the discussions at the time, involving many key stakeholders. In fact, the main priority at the time was to make data sharing popular in the field.

Nevertheless, the situation can be dramatically improved by pursuing a “divide and conquer” approach involving the four objectives (and four work packages) included in this proposal.

**i)** First, we will develop a posteriori annotation system for PRIDE, for both technical as well as biological metadata, which will leverage the unique synergies of already existing tools and pipelines developed by different ELIXIR nodes.

**ii)** We will develop a set of standards for metadata representation: technical and biological (experimental design).

**iii)** We will create data structures that can capture the most-frequently used experimental designs in proteomics studies. Third, an appropriate API will be built to allow annotation tools to be developed easily. Fourth, we will reach out to actively involve the whole proteomics community in the annotation process.


First Goal: Implementation of automatic data pipelines to extract technical metadata.
=====================================================================================

This involves extraction of search parameters in Task 1.1, and raw data information in Task 1.2. All pipelines will be adapted to run in, and will be tested on, existing EMBL-EBI IT infrastructure, bringing the code to the data. All extracted information will be made available to all PRIDE users.

**Task 1.1**: Extraction of search parameters for search engine use. The availability of a community standard format for the output of search engines identification results (mzIdentML) enables this information to be extracted using tools such as pride-asap6 (developed by ELIXIR-BE). In those cases where mzIdentML is not available, the alternatives at present are to estimate those parameters, using tools such as Param-Medic, or to parse specific output files from popular tools (e.g. MaxQuant).

**Task 1.2**: Additional information gathering from raw MS files. ELIXIR-NE will use their existing pipeline that enables automatic spectrum recalibration based on the technical metadata extracted in Task 1.1, including ion source, mass analyzer and search parameter information. ELIXIR-ES will provide the OpenMS based pipelines available in the QCloud resource. Finally, ELIXIR-EBI and ELIXIR-DE will provide the QC pipelines from the ongoing “Mining the proteome” ELIXIR implementation study.

Second Goal: Create standard representation for technical and biological metadata representation.
=================================================================================================

In all cases, the extracted information will be made available in a simple and computer-readable file format (e.g. _JSON-based_). This will in turn facilitate data reuse by providing parameter settings for PRIDE datasets that can be used directly by popular tools such as OpenMS (ELIXIR-DE), SearchGUI/PeptideShaker (ELIXIR-NO), Proteios Software Environment (ELIXIR-SE) and Proline (ELIXIR-FR).

**Task 2.1**: Development of data structures to capture the thecnical metadata at the level of RAW data and Result files (MzIdentML) in proteomics datasets. Please see [Thenical Metadata Discussion](/technical-metadata)

**Task 2.2**: Development of data strcutures and metadata format for for a more thorough biological annotation of datasets. With the aim of not “reinventing the wheel”, in our kick-off meeting, different approaches and file formats used by analogous resources at EMBL-EBI (e.g. ArrayExpress, Unified Submission Interface, Human Cell Atlas), will be presented and openly discussed. We will also take advantage of the experience of ELIXIR-DEN in the context of wrapper formats, as already used in bio.tools. In addition, relevant ontologies/controlled vocabularies need to be agreed to provide the actual annotations. We anticipate that, logically, some refinements in existing data structures will be needed to accommodate proteomics specific information. After the initial meeting, and using our collective experience in the context of the activities of the Proteomics Standards Initiative (PSI), the data structure/file formats will be agreed over the following months, through periodical calls. We anticipate that this task will have an even wider impact, since we envision that the same data structures/formats could be re-used by existing open proteomics data tools/pipelines to analyse whole datasets, rather than only individual MS runs as it is now the case. This would also benefit directly those pipelines being deployed in a cloud environment (work performed in the above-mentioned ELIXIR Implementation study “Mining the proteome”).

Third Goal: Development of APIs for automatic annotation of PRIDE experiments.
==============================================================================

**Task 3.1**: Development of an Application Programming Interface (API) to enable annotation of biological metadata.

**Task 3.2**: A read-and-write API will be developed by EMBL-EBI (with the feedback from all partners) to enable this functionality, implementing the data structure/file format developed in Task 2.1. The annotation interface will be made accessible for private (for the original submitters only) and public datasets (for everyone in the community, e.g. labs wanted to re-use data). It will be possible to import annotation from tables in a predefined format (e.g. Microsoft Excel spreadsheets). A crowd-sourced mechanism for annotation will then be available, so that datasets will be re-annotated just once by third parties (usually by reading the corresponding paper and/or contacting the original authors), avoiding the duplication of efforts that happens today. This is particularly relevant since there are high-profile datasets that are much more reused than others, and these can be prioritized. The resulting re-annotation will be made available in PRIDE, with proper acknowledgment and recognition for the responsible persons. As a pilot study, at least two relevant high-profile datasets will be curated and re-annotated using the developed framework by the neXtProt team (ELIXIR-CH) and ELIXIR-DE. It is important to highlight that, as soon as the API is functional, we plan to prototype and build a user-friendly web interface on top of the API, so that dataset annotation functionality can be extended to proteomics researchers that are not able to interact directly with an API. However, we believe it is not realistic to include this aim in the time frame of this project.

**Task 3.3**: Community engagement to rapidly increase the amount of manually re-annotated datasets.
