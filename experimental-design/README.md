Experimental Design:
====================

The PRIDE Experimental Design project will handle and represent each PRIDE project with the corresponding experiment design, including the annotation of:

- Sample Metadata.
- MSRun Metadata.
- The relation between the Sample and the MSRun
- The Fraction and Fraction Group

The following design is based on other efforts from [OpenMS](external-examples/openms-experimental/OpenMS.md), [MaxQuant](external-examples/maxquant/mqpar-jarnuczak-phospho.xml), [ArrayExpress](external-examples/arrayexpress/ArrayExpress.md)

Ontologies Supported:
---------------------

The PRIDE metadata annotation system will be supported by four main ontologies:

- PRIDE Ontology: Ontology to handle PRIDE metadata terms. https://www.ebi.ac.uk/ols/search?q=&groupField=iri&start=0&ontology=pride
- EFO: Experimental Factor Ontology. https://www.ebi.ac.uk/ols/search?q=&groupField=iri&start=0&ontology=efo
- PSI-MS: The HUPO-PSI standard initiative ontology https://www.ebi.ac.uk/ols/search?q=&groupField=iri&start=0&ontology=ms



Minimum information about Sample:
---------------------------------

**Sample attributes**: Minimum sample attributes for primary cells from different species and cell lines


|                      |Human                | Vertebrates               | Non-vertebrates | Plants  | Cell lines | Comment |
|----------------------|------------------|---------------------------|-----------------|---------|------------|---------|
|Organism              |X                 |	  X                       |	 X	            |   X     |     X      |         |
|Strain/breed          |O	              |   O	                   	  |  O              |   O     |     O      |         |
|Ethnicity             |X                 |	  O                       |	 O	            |   O     |     X      |         |
|Age	               |O 	              |   O                       |                 |         |            |         |
|Developmental stage   |X		          |	  O	                      |                 |         |            |         |
|Sex	               |X                 |   O                       |                 |         |            |         |
|Disease	           |X                 |   X		                  |  X              |  X      |     X      |         |
|Organism part	       |X                 |   X                       |  X              |  X      |     X      |         |
|Cell type*	           |X                 |   X                       |  X              |  X      |     X      | * if known, see comment below |
|Individual	           |O                 |	  O		                  |  O              |  O      |            |donor or animal ID |
|Cell line	Code           |                  |                           |                 |         |     X      |name of commercial cell line |

- X : Required Attributes for each sample Type (e.g. Human, Vertebrates).
- O : Optional Attributes.


X: Required
O: Not Required

Annotation MSRun:
-----------------

MSRun: From each MSRun we need to capture:
   - **unique identifier** : A unique identifier provided by PRIDE during the submission process.
   - **filename**: The filename provided by the user during the submissions process.

Relation between Sample, Fraction and MSRun:
--------------------------------------------

The relation between the Sample and MSRun will be given by two other Properties:

- Label: Label represents the information of a Multiplex or label free experiments. It can be used to spot the type of the experiment. For each Label two major characteristics are mandatory:
    - Label Identifier: An identifier of the labelling in the Experimental Design Table.
    - Label Name: A CvTerm with the type of Labeling apply:  **\["PRIDE", "PRIDE:0000312", "Label free", ]**

- Fraction Id
    - Fraction Identifier: A unique fraction identifier to classified the sample.

**Additional**:

Some search engines as MaxQuant use two more levels of grouping to perform better statistical analysis:

- Fraction Group
    - Fraction Group Identifier: The fraction group identifier is used to classified multiple fractions.
- Condition Group
    - Condition Group Identifier: The 'treatment' group to which the sample/file does belong to (where treatment can be anything that changes the sample preparation protocol, e.g. the application of a treatment)

**Examples Label Free Experiment**:

Sample |Sample \[Sample Name] | Sample \[Organism] | Sample \[Organism Part] | Fraction_Group | Fraction    | Condition    | Spectra_Filepath                            | Label                        | Technical replicate                 | Note:                |
|------|----------------------|--------------------|-------------------------|----------------|-------------|-------------|---------------------------------------------|------------------------------|-------------------------------------|----------------------|
| 1    | sample_dog           | [?NCBI:txid9615?]                | Whole Organism          |1               |1           |1           | SPECTRAFILE_DOG_F1_TR1.mzML                 | 1                            | 1                                   |                      |
| 1    | sample_dog           | [?NCBI:txid9615?]                | Whole Organism          |1               |2           |1           | SPECTRAFILE_DOG_F2_TR1.mzML                 | 1                            | 1                                   |                      |
| 1    | sample_dog           | [?NCBI:txid9615?]                | Whole Organism          |1               |3           |1           | SPECTRAFILE_DOG_F3_TR1.mzML                 | 1                            | 1                                   |                      |
| 2    | sample_dog           | [?NCBI:txid9615?]                | Whole Organism          |2               |1           |2           | SPECTRAFILE_DOG_F1_TR2.mzML                 | 1                            | 1                                   |                      |
| 2    | sample_dog           | [?NCBI:txid9615?]                | Whole Organism          |2               |2           |2           | SPECTRAFILE_DOG_F2_TR2.mzML                 | 1                            | 1                                   |                      |
| 2    | sample_dog           | [?NCBI:txid9615?]                | Whole Organism          |2               |3           |2           | SPECTRAFILE_DOG_F3_TR2.mzML                 | 1                            | 1                                   |                      |
| 3    | sample_cat           | [?NCBI:txid9685?]                | Whole Organism          |3               |1           |1           | SPECTRAFILE_CAT_F1_TR1.mzML                 | 1                            | 1                                   |                      |
| 3    | sample_cat           | [?NCBI:txid9685?]                | Whole Organism          |3               |2           |1           | SPECTRAFILE_CAT_F2_TR1.mzML                 | 1                            | 1                                   |                      |
| 3    | sample_cat           | [?NCBI:txid9685?]                | Whole Organism          |3               |3           |1           | SPECTRAFILE_CAT_F3_TR1.mzML                 | 1                            | 1                                   |                      |
| 4    | sample_cat           | [?NCBI:txid9685?]                | Whole Organism          |4               |1           |2           | SPECTRAFILE_CAT_F1_TR2.mzML                 | 1                            | 1                                   |                      |
| 4    | sample_cat           | [?NCBI:txid9685?]                | Whole Organism          |4               |2           |2           | SPECTRAFILE_CAT_F2_TR2.mzML                 | 1                            | 1                                   |                      |
| 4    | sample_cat           | [?NCBI:txid9685?]                | Whole Organism          |4               |3           |2           | SPECTRAFILE_CAT_F3_TR2.mzML                 | 1                            | 1                                   |                      |
