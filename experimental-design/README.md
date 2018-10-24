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

**Required sample attributes**: Minimum sample attributes for primary cells from different species and cell lines


|                      |Human          	  | Vertebrates               | Plants  | Cell lines | Comment |
|----------------------|------------------|---------------------------|---------|------------|---------|
|Organism              |X                 |	  X                       |	 X	    |   X        |         |
|                      |strain or breed	  |cultivar or ecotype	   	  |         |            |         |
|Age	               |X 	              |   X                       |    X    |            |         |
|Developmental stage   |X		          |	  X	                      |    X    |   X        |         |
|Sex	               |X                 |   X                       |         |   X        | 		   |
|Disease	           |X                 |   X		                  |         |            |         |
|Genotype	           |                  |   X                       |    X    |   X        |   genetic modification      |
|Organism part	       |X                 |   X                       |         |   X        |         |
|Cell type*	           |X                 |   X                       |         |            | * if known, see comment below        |
|Individual	individual |X                 |	  X		                  |         |            | donor or animal ID
|Cell line	           |                  |                           |         |            | name of commercial cell line |





Other annotations:
------------------

Spike-in Samples:



Single Cell Experiments (This is still exploratory):


|Example     |	single cell identifier (experimental variable) | inferred cell type | single cell well quality | post-analysis single cell quality |
|------------|-------------------------------------------------|--------------------|--------------------------|-----------------------------------|
|Sample 1	 |cell 1                                           | cell type A        |	OK                     |	pass                           |
|Sample 2    |cell 2	                                       | cell type B	    |   OK	                   |    pass                           |
|Sample 3	 |cell 3	                                       | not applicable	    |   OK	                   |    fail                           |


