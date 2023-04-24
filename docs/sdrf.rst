SDRF-Proteomics Format
########################################

The SDRF-Proteomics file format describes the sample characteristics and the relationships between samples and data files. The file format is a tab-delimited one where each ROW corresponds to a relationship between a Sample and a Data file (and MS signal corresponding to labelling in the context of multiplexed experiments), each column corresponds to an attribute/property of the Sample and the value in each cell is the specific value of the property for a given Sample (**Figure 1**).

.. image:: images/sdrf-nutshell.png
   :width: 600
   :align: center


**Figure 2**: SDRF-Proteomics in a nutshell. The file format is a tab-delimited one where columns are properties of the sample, the data file or the variables under study. The rows are the samples of origin and the cells are the values for one property in a specific sample.

Rules
******************************

There are general scenarios/use cases that are addressed by the following rules:

- **Unknown values**: In some cases, the column is mandatory in the format but for some samples the corresponding value is unknown. In those cases, users SHOULD use :guilabel:`not available`.
- **Not Applicable values**: In some cases, the column is mandatory but for some samples the corresponding value is not applicable. In those cases, users SHOULD use :guilabel:`not applicable`.
- **Case sensitivity**: By specification the SDRF is case insensitive, but we RECOMMEND using lowercase characters throughout all the text (Column names and values).
- **Spaces**: By specification the SDRF is case sensitive to spaces (sourcename != source name).
- **Column order**: The SDRF MUST start with the source name column (accession/name of the sample of origin), then all the sample characteristics; followed by the assay name corresponding to the MS run. Finally, after the assay name all the comments (properties of the data file generated).
- **Extension**: The extension of the SDRF should be .tsv or .txt.

Values
******************************

The value for each property (e.g. characteristics, comment) corresponding to each sample can be represented in multiple ways.

- Free Text (Human readable): In the free text representation, the value is provided as text without Ontology support (e.g. colon or providing accession numbers). This is only RECOMMENDED when the text inserted in the table is the exact name of an ontology/CV term in EFO. If the term is not in EFO, other ontologies can be used.

.. list-table:: SDRF values annotated in free text
   :widths: 50 50
   :header-rows: 1

   * - source name
     - characteristics[organism]
   * - sample 1
     - homo sapiens
   * - sample 2
     - homo sapiens

- Ontology url (Computer readable): Users can provide the corresponding URI (Uniform Resource Identifier) of the ontology/CV term as a value. This is recommended for enriched files where the user does not want to use intermediate tools to map from free text to ontology/CV terms.

.. list-table:: SDRF with ontology terms
   :widths: 50 50
   :header-rows: 1

   * - source name
     - characteristics[organism]
   * - sample 1
     - http://purl.obolibrary.org/obo/NCBITaxon_9606
   * - sample 2
     - http://purl.obolibrary.org/obo/NCBITaxon_9606

- Key=value representation (Human and Computer readable): The current representation aims to provide a mechanism to represent the complete information of the ontology/CV term including Accession, Name and other additional properties. In the key=value pair representation the Value of the property is represented as an Object with multiple properties, where the key is one of the properties of the object and the value is the corresponding value for the particular key. An example of key value pairs is post-translational modification (see :ref:`ptms`)

`NT=Glu->pyro-Glu; MT=fixed; PP=Anywhere; AC=Unimod:27; TA=E`

Samples metadata
***********************************

The Sample metadata has different Categories/Headings to organize all the attributes/ column headers of a given sample. Each Sample contains a :guilabel:`source name` (accession) and a set of :guilabel:`characteristics`. Any proteomics sample MUST contain the following characteristics:

- :guilabel:`source name`: Unique sample name (it can be present multiple times if the same sample is used several times in the same dataset).
- :guilabel:`characteristics[organism]`: The organism of the Sample of origin.
- :guilabel:`characteristics[disease]`: The disease under study in the Sample.
- :guilabel:`characteristics[organism part]`: The part of organism's anatomy or substance arising from an organism from which the biomaterial was derived (e.g. liver).
- :guilabel:`characteristics[cell type]`: A cell type is a distinct morphological or functional form of cell. Examples are epithelial, glial etc.

Example:

.. list-table:: Minimum sample metadata for any proteomics dataset
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - source name
     - characteristics[organism]
     - characteristics[organism part]
     - characteristics[disease]
     - characteristics[cell type]
   * - sample_treat
     - homo sapiens
     - liver
     - liver cancer
     - liver cancer cell
   * - sample_control
     - homo sapiens
     - liver
     - liver cancer
     - liver

.. note:: Additional characteristics can be added depending on the type of the experiment and sample. The `SDRF-Proteomics templates <https://github.com/bigbio/proteomics-metadata-standard/tree/master/templates>`_ defines a set of templates and checklists of properties that should be provided depending on the proteomics experiment.

Some important notes:

- Each characteristics name in the column header SHOULD be a CV term from the EFO ontology. For example, the header :guilabel:`characteristics[organism]` corresponds to the ontology term Organism.

- Multiple values (columns) for the same characteristics term are allowed in SDRF-Proteomics. However, it is RECOMMENDED not to use the same column in the same file. If you have multiple phenotypes, you can specify what it refers to or use another more specific term, e.g. "immunophenotype".

Data files metadata
************************************

The connection between the Samples to the Data files is done by using a series of properties and attributes. All the properties referring to the MS run (file) itself are annotated with the category/prefix :guilabel:`comment`. The use of comment is mainly aimed at differentiating sample properties from the data properties. It matches a given sample to the corresponding file(s). The word comment is used for backwards-compatibility with gene expression experiments (RNA-Seq and Microarrays experiments).

The order of the columns is important, :guilabel:`assay name` MUST always be located before the comments. It is RECOMMENDED to put the last column as :guilabel:`comment[data file]`. The following properties MUST be provided for each data file (ms run) file:

- :guilabel:`assay name`: assay name is an accession for each msrun. Because of back-compatibility with SDRF in transcriptomics we don't use the term ms run but the more generic term :guilabel:`assay name`. Examples of assay names are: “run 1”, “run_fraction_1_2”, it must be a unique accession for every msrun.
- :guilabel:`comment[fraction identifier]`: The fraction identifier allows to record the number of a given fraction. The fraction identifier corresponds to this ontology term. It MUST start from `1` and if the experiment is not fractionated, 1 MUST be used for each MSRun (assay).
- :guilabel:`comment[label]`: label describes the label applied to each Sample (if any). In case of multiplex experiments such as TMT, SILAC, and/or ITRAQ the corresponding label SHOULD be added. For Label-free experiments the label free sample term MUST be used :ref:`label-annotations`.
- :guilabel:`comment[data file]`: The data file provides the name of the raw file generated  by the instrument. The data files can be instrument raw files but also converted peak lists such as mzML, MGF or result files like mzIdentML.
- :guilabel:`comment[instrument]`: Instrument model used to capture the sample :ref:`instrument-information`.

Example:

.. list-table:: Minimum data metadata for any proteomics dataset
   :widths: 14 14 14 14 14 14 14
   :header-rows: 1

   * - source name
     - ....
     - assay name
     - comment[label]
     - comment[fraction identifier]
     - comment[instrument]
     - comment[data file]
   * - sample 1
     - ....
     - run 1
     - label free sample
     - 1
     - NT=LTQ Orbitrap XL
     - 000261_C05_P0001563_A00_B00K_R1.RAW
   * - sample 1
     - ....
     - run 2
     - label free sample
     - 2
     - NT=LTQ Orbitrap XL
     - 000261_C05_P0001563_A00_B00K_R2.RAW

.. note:: All the possible _label_ values can be seen in the in the PRIDE CV under `labels <https://www.ebi.ac.uk/ols/ontologies/pride/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPRIDE_0000514&lang=en&viewMode=All&siblings=false>`_ node.

.. _label-annotations:

Label annotations
====================

In order to annotate quantitative datasets, the SDRF file format uses tags for each channel associated with the sample in :guilabel:`comment[label]`. The label values are organized under the following ontology term Label. Some of the most popular labels are:

- For label-free experiments the value SHOULD be: label free sample or the corresponding key value pair term: `AC=MS:1002038;NT=label free sample`
- For TMT experiments the SDRF uses the PRIDE ontology terms under sample label. Here some examples of TMT channels:

  TMT126, TMT127, TMT127C, TMT127N, TMT128 , TMT128C, TMT128N, TMT129, TMT129C, TMT129N, TMT130, TMT130C, TMT130N, TMT131

In order to achieve a clear relationship between the label and the sample characteristics, each channel of each sample (in multiplex experiments) SHOULD be defined in a separate row: one row per channel used (annotated with the corresponding :guilabel:`comment[label]` per file.

Examples:

- `PXD000612 <https://github.com/bigbio/proteomics-sample-metadata/blob/master/annotated-projects/PXD000612/PXD000612.sdrf.tsv>`_
- `PXD011799 <https://github.com/bigbio/proteomics-sample-metadata/blob/master/annotated-projects/PXD011799/PXD011799.sdrf.tsv>`_

.. _instrument-information:

Instrument information
====================================

The model of the mass spectrometer SHOULD be specified as :guilabel:`comment[instrument]`. Possible values are listed in `PSI-MS <https://www.ebi.ac.uk/ols/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1000031&viewMode=All&siblings=false>`_

Additionally, it is strongly RECOMMENDED to include :guilabel:`comment[MS2 analyzer type]`. This is important e.g. for Orbitrap models where MS2 scans can be acquired either in the Orbitrap or in the ion trap. Setting this value allows to differentiate high-resolution MS/MS data. Possible values of :guilabel:`comment[MS2 analyzer type]` are mass analyzer types.

Additional Data files technical properties
===========================================

It is RECOMMENDED to encode some of the technical parameters of the MS experiment as comments including the following parameters:

- Protein Modifications
- Precursor and Fragment ion mass tolerances
- Digestion Enzymes

.. _ptms:
Protein Modifications
---------------------------------

Sample modifications (including both chemical modifications and post translational modifications, PTMs) are originated from multiple sources: artifact modifications, isotope labeling, adducts that are encoded as PTMs (e.g. sodium) or the most biologically relevant PTMs. It is RECOMMENDED to provide the modifications expected in the sample including the amino acid affected, whether it is Variable or Fixed (also Custom and Annotated modifications are supported) and included other properties such as mass shift/delta mass and the position (e.g. anywhere in the sequence). The RECOMMENDED name of the column for sample modification parameters is: :guilabel:`comment[modification parameters]`. The modification parameters are the name of the ontology term MS:1001055. For each modification, different properties are captured using a key=value pair structure including name, position, etc. All the possible (optional) features available for modification parameters are:

.. list-table:: Minimum data metadata for any proteomics dataset
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - Property
     - Key
     - Example
     - Required
     - comment
   * - Name of the Modification
     - NT
     - NT=Acetylation
     - Yes
     - Name of the Term in this particular case Modification, for custom modifications can be a name defined by the user.
   * - Modification Accession
     - AC
     - AC=UNIMOD:1
     - Yes
     - Accession in an external database UNIMOD or PSI-MOD supported.
   * - Chemical Formula
     - CF
     - CF=H(2)C(2)O
     - No
     - This is the chemical formula of the added or removed atoms. For the formula composition please follow the `guidelines <http://www.unimod.org/names.html>`_
   * - Modification Type
     - MT
     - MT=Fixed
     - No
     - This specifies which modification group the modification should be included with. Choose from the following options: [Fixed, Variable, Annotated]. Annotated is used to search for all the occurrences of the modification into an annotated protein database file like UNIPROT XML or PEFF.
   * - Position of the modification in the Polypeptide
     - PP
     - PP=Any N-term
     - No
     - Choose from the following options: [Anywhere, Protein N-term, Protein C-term, Any N-term, Any C-term]. Default is **Anywhere**.
   * - Target Amino acid
     - TA
     - TA=S,T,Y
     - No
     - The target amino acid letter. If the modification targets multiple sites, it can be separated by `,`.
   * - Monoisotopic Mass
     - MM
     - MM=42.010565
     - No
     - The exact atomic mass shift produced by the modification. Please use at least 5 decimal places of accuracy. This should only be used if the chemical formula of the modification is not known. If the chemical formula is specified, the monoisotopic mass will be overwritten by the calculated monoisotopic mass.
   * - Target Site
     - TS
     - TS=N[^P][ST]
     - No
     - For some software, it is important to capture complex rules for modification sites as regular expressions. These use cases should be specified as regular expressions.

.. note:: We RECOMMEND for indicating the modification name, to use the UNIMOD interim name or the PSI-MOD name. For custom modifications, we RECOMMEND using an intuitive name. If the PTM is unknown (custom), the Chemical Formula or Monoisotopic Mass MUST be annotated.

An example of an SDRF-Proteomics file with sample modifications annotated, where each modification needs an extra column:

.. list-table:: Example about how to annotated two modifications in SDRF-Proteomics
   :widths: 25 25 25 25
   :header-rows: 1

   * - source name
     - ...
     - comment[modification parameters]
     - comment[modification parameters]
   * - Sample 1
     - ...
     - NT=Glu->pyro-Glu;MT=fixed;PP=Anywhere;AC=Unimod:27;TA=E
     - NT=Oxidation;MT=Variable;TA=M

Cleavage agents
--------------------------------------

The REQUIRED :guilabel:`comment[cleavage agent details]` property is used to capture the enzyme information. Similar to protein modification a key=value pair representation is used to encode the following properties for each enzyme:

.. list-table:: Example about how to annotated two modifications in SDRF-Proteomics
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - Property
     - Key
     - Example
     - Required
     - comment
   * - Name of the Enzyme
     - NT
     - NT=Trypsin
     - required
     - Name of the Term in this particular case Name of the Enzyme.
   * - Enzyme Accession
     - AC
     - AC=MS:1001251
     - required
     - Accession in an external PSI-MS Ontology definition under the following category `cleavage agent name <https://www.ebi.ac.uk/ols/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1001045>`_
   * - Cleavage site regular expression
     - CS
     - CS=(?<=[KR])(?!P)
     - optional
     - The cleavage site defined as a regular expression.

An example of an SDRF-Proteomics with annotated endopeptidase:

.. list-table:: Example about how to annotated enzymes in SDRF-Proteomics
   :widths: 20 20 60
   :header-rows: 1

   * - source name
     - ...
     - comment[cleavage agent details]
   * - Sample 1
     - ...
     - NT=Trypsin;AC=MS:1001251;CS=(?<=[KR])(?!P)

.. warning:: If no endopeptidase is used, for example in the case of Top-down/intact protein experiments, the value SHOULD be ‘not applicable’.

Precursor and Fragment mass tolerances
--------------------------------------

For proteomics experiments, it is important to encode different mass tolerances (for precursor and fragment ions).

Example:

.. list-table:: Example about how to annotated tolerances in SDRF-Proteomics
   :widths: 20 20 30 30
   :header-rows: 1

   * - source name
     - ...
     - comment[fragment mass tolerance]
     - comment[precursor mass tolerance]
   * - Sample 1
     - ...
     - 0.6 Da
     - 20 ppm

.. note:: Units for the mass tolerances (either Da or ppm) MUST be provided.

Factor values
=========================

The variable/property under study MUST be highlighted using the :guilabel:`factor value` category. For example, the :guilabel:`factor value[disease]` is used when the main purpose of a given experiment is to compare protein expression across different diseases or different states of a given disease. Multiple variables under study can be included by adding multiple factor values columns.

.. Important:: “factor value” columns SHOULD indicate which experimental factor/variable is used as the hypothesis to perform the data analysis. The “factor value” columns SHOULD occur after all characteristics and attributes of the samples.








