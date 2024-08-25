Additional information
=========================

Ontologies/Controlled Vocabularies Supported
---------------------------------------------

The list of ontologies/controlled vocabularies (CV) supported are:

-	PSI Mass Spectrometry CV (`PSI-MS <https://www.ebi.ac.uk/ols/ontologies/ms>`_)
-	Experimental Factor Ontology (`EFO <https://www.ebi.ac.uk/ols/ontologies/efo>`_).
-	Unimod protein modification database for mass spectrometry (`UNIMOD <https://www.ebi.ac.uk/ols/ontologies/unimod>`_)
-	PSI-MOD CV (`PSI-MOD <https://www.ebi.ac.uk/ols/ontologies/mod>`_)
-	Cell line ontology (`CLO <https://www.ebi.ac.uk/ols/ontologies/clo>`_)
-	Drosophila anatomy ontology (`FBBT <https://www.ebi.ac.uk/ols/ontologies/fbbt>`_)
-	Cell ontology (`CL <https://www.ebi.ac.uk/ols/ontologies/cl>`_)
-	Plant ontology (`PO <https://www.ebi.ac.uk/ols/ontologies/po>`_)
-	Uber-anatomy ontology (`UBERON <https://www.ebi.ac.uk/ols/ontologies/uberon>`_)
-	Zebrafish anatomy and development ontology (`ZFA <https://www.ebi.ac.uk/ols/ontologies/zfa>`_)
-	Zebrafish developmental stages ontology (`ZFS <https://www.ebi.ac.uk/ols/ontologies/zfs>`_)
-	Plant Environment Ontology (`PEO <https://www.ebi.ac.uk/ols/ontologies/peo>`_)
-	FlyBase Developmental Ontology (`FBdv <https://www.ebi.ac.uk/ols/ontologies/fbdv>`_)
-	Rat Strain Ontology (`RSO <https://www.ebi.ac.uk/ols/ontologies/rso>`_)
-	Chemical Entities of Biological Interest Ontology (`CHEBI <https://www.ebi.ac.uk/ols/ontologies/chebi>`_)
-	NCBI organismal classification (`NCBITaxon <https://www.ebi.ac.uk/ols/ontologies/ncbitaxon>`_)
-	PATO - the Phenotype and Trait Ontology (`PATO <https://www.ebi.ac.uk/ols/ontologies/pato>`_)
-	PRIDE Controlled Vocabulary (`PRIDE <https://www.ebi.ac.uk/ols/ontologies/pride>`_)

Relations with other formats
-----------------------------------------------

SDRF-Proteomics is fully compatible with the SDRF file format part of `MAGE-TAB <https://www.ebi.ac.uk/arrayexpress/help/magetab_spec.html>`_. The MAGE-TAB is the file format to store the metadata and sample information on transcriptomics experiments.
MAGE-TAB (MicroArray Gene Expression Tabular) is a standard format for storing and exchanging microarray and other high-throughput genomics data. It consists of two spreadsheets for each experiment: the Investigation Description Format (IDF) file and the Sample and Data Relationship Format (SDRF) file.

The IDF file contains general information about the experiment, such as the project title, description, and funding sources, as well as details about the experimental design, such as the type of technology used, the organism studied, and the experimental conditions.
The SDRF file contains detailed information about the samples and the data generated from them, including sample annotations, data file locations, and data processing parameters. It also defines the relationships between samples, such as replicates or time-course experiments. Together, the IDF and SDRF files provide a complete description of the experiment and the data generated from it, allowing researchers to share and compare their data with others in a standardized and interoperable format.

SDRF-Proteomics sample information can be embedded into mzTab metadata files.   The mzTab (Mass Spectrometry Tabular) format is a standard format for reporting the results of proteomics and metabolomics experiments. It can be used to store information such as protein identification, peptide sequences, and quantitation results.
The mzTab format allows for the embedding of sample metadata into the file, which includes information about the samples and the experimental conditions. This metadata can be derived from the Sample and Data Relationship Format (SDRF) file in a proteomics experiment.
In the mzTab format, sample metadata is stored in a separate section called the "metadata section," which contains a list of key-value pairs that describe the samples. The keys in the metadata section correspond to the column names in the SDRF file, and the values correspond to the values in the Sample cells.
By embedding sample metadata into the mzTab file, researchers can ensure that all relevant information about the experiment is stored in a single file, making it easier to share and compare data with others.


Documentation
-----------------------------

The official website for SDRF-Proteomics project is https://github.com/bigbio/proteomics-sample-metadata. New use cases, changes to the specification and examples can be added by using Pull requests or issues in GitHub (see introduction to `GitHub <https://lab.github.com/githubtraining/introduction-to-github>`_).

A set of examples and annotated projects from ProteomeXchange can be `found here <https://github.com/bigbio/proteomics-sample-metadata/tree/master/annotated-projects>`_

Multiple tools have been implemented to validate SDRF-Proteomics files:

- `sdrf-pipelines <https://github.com/bigbio/sdrf-pipelines>`_ (Python): This tool allows a user to validate an SDRF-Proteomics file. In addition, it allows a user to convert SDRF to other popular pipelines and software configuration files such as: MaxQuant or OpenMS.

- `jsdrf <https://github.com/bigbio/jsdrf>`_ (Java): This Java library and tool allows a user to validate SDRF-Proteomics files. It also includes a generic data model that can be used by Java applications.
