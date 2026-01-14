# Proteomics Sample Metadata Format

[![Version](https://flat.badgen.net/static/sdrf-proteomics/1.0.1/orange)](CHANGELOG.md)
[![License](https://flat.badgen.net/github/license/bigbio/proteomics-metadata-standard)](https://github.com/bigbio/proteomics-metadata-standard/blob/master/LICENSE)
[![Open Issues](https://flat.badgen.net/github/open-issues/HUPO-PSI/mzSpecLib)](https://github.com/bigbio/proteomics-metadata-standard/issues)
[![Open PRs](https://flat.badgen.net/github/open-prs/bigbio/proteomics-metadata-standard)](https://github.com/bigbio/proteomics-metadata-standard/pulls)
![Contributors](https://flat.badgen.net/github/contributors/bigbio/proteomics-metadata-standard)
![Watchers](https://flat.badgen.net/github/watchers/bigbio/proteomics-metadata-standard)
![Stars](https://flat.badgen.net/github/stars/bigbio/proteomics-metadata-standard)

## Improving metadata annotation of Proteomics datasets

Metadata is essential in proteomics data repositories and is crucial to interpret and reanalyze the deposited data sets. While the dataset general description and standard data file formats are supported and captured for every dataset by ProteomeXchange partners, the information regarding the sample to data files is mostly missing. Members of the European Bioinformatics Community for Mass Spectrometry (EuBIC - https://eubic-ms.org/) have created this open-source project to enable the standardization of sample metadata of public proteomics data sets.

The **SDRF-Proteomics** (Sample and Data Relationship Format for Proteomics) is a tab-delimited file format that captures the relationship between samples and data files in proteomics experiments. It defines the minimum information required to report the experimental design of proteomics experiments, enabling automated re-processing and reuse of deposited data by the proteomics community.

SDRF-Proteomics is fully compatible with the SDRF component of [MAGE-TAB v1.1](https://www.fged.org/projects/mage-tab/), the file format used in transcriptomics. This compatibility enables future multiomics experiments submissions and better integration with other omics data.

Our goal is to ensure maximum reusability of the deposited data. The following design principles guide the SDRF-Proteomics specification:

- The SDRF-Proteomics captures the Sample to Data relationships for proteomics experiments.
- The format is fully compatible with MAGE-TAB SDRF used in transcriptomics.
- The format enables data submitters and curators to annotate a proteomics dataset at different levels, including the sample metadata (e.g. organism and tissues), technical metadata (e.g. instrument model) and the experimental design.
- The format facilitates the automatic reanalysis of public proteomics datasets, by providing a better representation of quantitative datasets in public repositories.

### SDRF-Proteomics

The SDRF-Proteomics file captures the Sample to Data information that is missing (or not standardized) in ProteomeXchange datasets. The standardization of sample metadata for proteomics is the main objective of this project ([Read more about SDRF-Proteomics](sdrf-proteomics/README.adoc))

## Final PSI specification

The final HUPO-PSI specification is: [SDRF HUPO-PSI](psi-document/SDRF_Proteomics_Specification_v1.0.0.pdf)

## How to contribute

External contributors, researchers and the proteomics community are more than welcome to contribute to this project.

Contribute with the specification: you can contribute to the specification with ideas or refinements by adding an issue into the [issue tracker](https://github.com/bigbio/proteomics-metadata-standard/issues) or performing a PR.

In the [annotated projects](https://github.com/bigbio/proteomics-metadata-standard/tree/master/annotated-projects) folder, users can see different public datasets that have been annotated so far by the contributors. If you would like to join these efforts, make a Fork of this repo and perform a pull request (PR) with your annotated project. If you don't have a project in mind, you can take one project from the [issues](https://github.com/bigbio/proteomics-metadata-standard/issues) and perform the annotation.

Annotate a dataset in 5 steps:

- Read the [SDRF-Proteomics specification](https://github.com/bigbio/proteomics-metadata-standard/tree/master/sdrf-proteomics).
- Depending on the type of dataset, choose the appropriate [sample template](https://github.com/bigbio/proteomics-metadata-standard/tree/master/sdrf-proteomics#sdrf-templates).
- Annotate the corresponding ProteomeXchange PXD dataset following the guidelines.
- Validate your SDRF file:

In order to validate your SDRF, you can install the sdrf-pipelines tool in Python

```bash
pip install sdrf-pipelines
```

validate the SDRF file

```bash
parse_sdrf validate-sdrf --sdrf_file PXD020294.sdrf.tsv
```

You can read more about the validator [here](https://github.com/bigbio/sdrf-pipelines).

- Fork the current repository, add a folder with the ProteomeXchange accession and the annotated sdrf.tsv

## 30 Minutes Guide to SDRF-Proteomics

We have created a 30-minute Guide to the file format in [the github repository](https://github.com/bigbio/proteomics-metadata-standard/wiki). Additionally, the following materials are relevant for new users:

- [Introduction to SDRF-Proteomics - Slides](https://github.com/bigbio/proteomics-metadata-standard/raw/master/additional-documentation/presentation-20200313.pptx)
- [Introduction to SDRF-Proteomics - YouTube Video](https://www.youtube.com/watch?v=TMDu_yTzYQM)


## Core contributors and collaborators

The project is run by different groups:

- Yasset Perez-Riverol (PRIDE Team, European Bioinformatics Institute - EMBL-EBI, U.K.)
- Timo Sachsenberg (OpenMS Team, Tübingen University, Germany)
- Anja Fullgrabe (Expression Atlas Team, European Bioinformatics Institute - EMBL-EBI, U.K.)
- Nancy George (Expression Atlas Team, European Bioinformatics Institute - EMBL-EBI, U.K.)
- Mathias Walzer (PRIDE Team, European Bioinformatics Institute - EMBL-EBI, U.K.)
- Pablo Moreno (Expression Atlas Team, European Bioinformatics Institute - EMBL-EBI, U.K.)
- Juan Antonio Vizcaíno (PRIDE Team, European Bioinformatics Institute - EMBL-EBI, U.K.)
- Oliver Alka (OpenMS Team, Tübingen University, Germany)
- Julianus Pfeuffer (OpenMS Team, Tübingen University, Germany)
- Marc Vaudel (University of Bergen, Norway)
- Harald Barsnes (University of Bergen, Norway)
- Niels Hulstaert (Compomics, University of Gent, Belgium)
- Lennart Martens (Compomics, University of Gent, Belgium)
- Expression Atlas Team (European Bioinformatics Institute - EMBL-EBI, U.K.)
- Lev Levitsky (INEP team, INEPCP RAS, Moscow, Russia)
- Elizaveta Solovyeva (INEP team, INEPCP RAS, Moscow, Russia)
- Stefan Schulze (University of Pennsylvania, USA)
- Veit Schwämmle (Protein Research Group, University of Southern Denmark, Denmark)
- ProteomicsDB Team (Technical University of Munich, Germany)
- David Bouyssié (ProFI/IPBS, University of Toulouse, CNRS, Toulouse, France)
- Nicholas Carruthers (Wayne State University, USA)
- Paul Rudnick (NCI, Proteomic Data Commons, USA)
- Enrique Audain (University Medical Center Schleswig-Holstein, Germany)
- Marie Locard-Paulet (Novo Nordisk Foundation Center for Protein Research, University of Copenhagen, Denmark)
- Johannes Griss (Department of Dermatology, Medical University of Vienna, Austria)
- Chengxin Dai (Chongqing Key Laboratory on Big Data for Bio Intelligence, Chongqing University of Posts and telecommunications, Chongqing, China)
- Julian Uszkoreit ( Medical Faculty, Medizinisches Proteom-Center and Center for Protein Diagnostics (PRODI), Medical Proteome Analysis, Ruhr-University Bochum, Germany)
- Dirk Winkelhardt ( Medical Faculty, Medizinisches Proteom-Center and Center for Protein Diagnostics (PRODI), Medical Proteome Analysis, Ruhr-University Bochum, Germany)
- Kanami Arima (Toyama University of International Studies, Toyama Japan)
- Shin Kawano (Toyama University of International Studies, Toyama Japan)
- Ruri Okamoto (Toyama University of International Studies, Toyama Japan)
- Alexandra Naba (Department of Physiology and Biophysics, University of Illinois Chicago, USA)
- Jonas Scheid (Department of Peptide-based Immunotherapy, University of Tübingen, Germany)
- Joshua Klein (Program for Computational Biology, Boston University, USA)

IMPORTANT: If you contribute with the following specification, please make sure to add your name to the list of contributors.

## Code of Conduct

As part of our efforts toward delivering open and inclusive science, we follow the [Contributor Covenant Code of Conduct for Open Source Projects](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## How to cite

- Dai C, Füllgrabe A, Pfeuffer J, Solovyeva EM, Deng J, Moreno P, Kamatchinathan S, Kundu DJ, George N, Fexova S, Grüning B, Föll MC, Griss J, Vaudel M, Audain E, Locard-Paulet M, Turewicz M, Eisenacher M, Uszkoreit J, Van Den Bossche T, Schwämmle V, Webel H, Schulze S, Bouyssié D, Jayaram S, Duggineni VK, Samaras P, Wilhelm M, Choi M, Wang M, Kohlbacher O, Brazma A, Papatheodorou I, Bandeira N, Deutsch EW, Vizcaíno JA, Bai M, Sachsenberg T, Levitsky LI, Perez-Riverol Y. A proteomics sample metadata representation for multiomics integration and big data analysis. Nat Commun. 2021 Oct 6;12(1):5854. doi: 10.1038/s41467-021-26111-3. PMID: 34615866; PMCID: PMC8494749. [Manuscript](https://www.nature.com/articles/s41467-021-26111-3)
- Perez-Riverol, Yasset, European Bioinformatics Community for Mass Spectrometry. "Towards a sample metadata standard in public proteomics repositories." Journal of Proteome Research (2020) [Manuscript](https://pubs.acs.org/doi/abs/10.1021/acs.jproteome.0c00376).


## Copyright notice


    This information is free; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This information is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this work; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
