Experimental Design:
====================

The PRIDE Experimental Design project will handle and represent each PRIDE project with the corresponding experiment design, including the annotation of:

- Sample Metadata.
- MSRun Metadata.
- The relation beetween the Sample and the MSRun
- The Fraction and Fraction Group

The following design is based on other efforts from [OpenMS](external-examples/openms-experimental/OpenMS.md), [MaxQuant](external-examples/maxquant/mqpar-jarnuczak-phospho.xml), [ArrayExpress](external-examples/arrayexpress/ArrayExpress.md)

Minimum information about Sample:
---------------------------------

**Sample attributes**: Minimum sample attributes for primary cells from different species and cell lines


|                      |Human          	  | Vertebrates               | Non-vertebrates | Plants  | Cell lines | Comment |
|----------------------|------------------|---------------------------|-----------------|---------|------------|---------|
|Organism              |X                 |	  X                       |	 X	            |   X     |     X      |         |
|Strain/breed          |O	              |   O	                   	  |  O              |   O     |     O      |         |
|Age	               |O 	              |   O                       |                 |         |            |         |
|Developmental stage   |X		          |	  O	                      |                 |         |            |         |
|Sex	               |X                 |   O                       |                 |         |            |         |
|Disease	           |X                 |   X		                  |  X              |  X      |     X      |         |
|Organism part	       |X                 |   X                       |  X              |  X      |     X      |         |
|Cell type*	           |X                 |   X                       |  X              |  X      |     X      | * if known, see comment below |
|Individual	           |O                 |	  O		                  |  O              |  O      |            |donor or animal ID |
|Cell line	           |                  |                           |                 |         |     X      |name of commercial cell line |

- X : Required Attributes for each sample Type (e.g. Human, Vertebrates).
- O : Optional Attributes.


Annotation MSRun:
-----------------

MSRun: From each MSRun we need to capture:
   - **unique identifier** : A unique identifier provided by PRIDE during the submission process.
   - **filename**: The filename provided by the user during the submissions process.

Relation between Sample, Fraction and MSRun:
--------------------------------------------

The relation between the Sample and MSRun will be given by two other Properties:

- Label: Label represent the information of a Multiplex or label free experiments. It can be used to spot the type of the experiment. For each Label two major caracterities are mandatory:
    - Label Identifier: An identifier of the lalbeling in the Experimental Design Table.
    - Label Name: A CvTerm with the type of Laling apply:  **\["PRIDE", "PRIDE:0000312", "Label free", ]**

- Fraction Id
    - Fraction Idnetifier: A unique fraction identifier to classified the sample.

**Additional**:

Some search engines as MaxQuant use the Fraction Group to perform better statistical analysis:

- Fraction Group
    - Fraction Group Identifier: The fraction group identifier is use to classified multiple fractions.


**Examples Label Free Experiment**:

Sample |Sample \[Sample Name] | Sample \[Organism] | Sample \[Organism Part] | Fraction_Group | Fraction    | Spectra_Filepath                            | Label                        | Sample                              | Note:                |
|------|----------------------|--------------------|-------------------------|----------------|-------------|---------------------------------------------|------------------------------|-------------------------------------|----------------------|
| 1    | sample_dog           | DOG                | Whole Organism          |1               |1            | SPECTRAFILE_DOG_F1_TR1.mzML                 | 1                            | 1                                   |                      |
| 1    | sample_dog           | DOG                | Whole Organism          |1               |2            | SPECTRAFILE_DOG_F2_TR1.mzML                 | 1                            | 1                                   |                      |
| 1    | sample_dog           | DOG                | Whole Organism          |1               |3            | SPECTRAFILE_DOG_F3_TR1.mzML                 | 1                            | 1                                   |                      |
| 2    | sample_dog           | DOG                | Whole Organism          |2               |1            | SPECTRAFILE_DOG_F1_TR2.mzML                 | 1                            | 2                                   |                      |
| 2    | sample_dog           | DOG                | Whole Organism          |2               |2            | SPECTRAFILE_DOG_F2_TR2.mzML                 | 1                            | 2                                   |                      |
| 2    | sample_dog           | DOG                | Whole Organism          |2               |3            | SPECTRAFILE_DOG_F3_TR2.mzML                 | 1                            | 2                                   |                      |
| 3    | sample_cat           | CAT                | Whole Organism          |3               |1            | SPECTRAFILE_CAT_F1_TR1.mzML                 | 1                            | 3                                   |                      |
| 3    | sample_cat           | CAT                | Whole Organism          |3               |2            | SPECTRAFILE_CAT_F2_TR1.mzML                 | 1                            | 3                                   |                      |
| 3    | sample_cat           | CAT                | Whole Organism          |3               |3            | SPECTRAFILE_CAT_F3_TR1.mzML                 | 1                            | 3                                   |                      |
| 4    | sample_cat           | CAT                | Whole Organism          |4               |1            | SPECTRAFILE_CAT_F1_TR2.mzML                 | 1                            | 4                                   |                      |
| 4    | sample_cat           | CAT                | Whole Organism          |4               |2            | SPECTRAFILE_CAT_F2_TR2.mzML                 | 1                            | 4                                   |                      |
| 4    | sample_cat           | CAT                | Whole Organism          |4               |3            | SPECTRAFILE_CAT_F3_TR2.mzML                 | 1                            | 4                                   |                      |



Other annotations:
------------------

Spike-in Samples:


Single Cell Experiments (This is still exploratory):


|Example     |	single cell identifier (experimental variable) | inferred cell type | single cell well quality | post-analysis single cell quality |
|------------|-------------------------------------------------|--------------------|--------------------------|-----------------------------------|
|Sample 1	 |cell 1                                           | cell type A        |	OK                     |	pass                           |
|Sample 2    |cell 2	                                       | cell type B	    |   OK	                   |    pass                           |
|Sample 3	 |cell 3	                                       | not applicable	    |   OK	                   |    fail                           |


