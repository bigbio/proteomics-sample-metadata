Additional conventions
########################

Specific use cases and conventions
*************************************

Conventions define how to encode some particular information in the file format by supporting specific use cases. Conventions define a set of new columns that are needed to represent a particular use case or experiment type (e.g., phosphorylation-enriched dataset). In addition, conventions define how some specific free-text columns (values that are not defined as ontology terms) should be written.

Conventions are documented and compiled from at https://github.com/bigbio/proteomics-sample-metadata/issues or by performing a pull-request. New conventions will be added to updated versions of this specification document in the future. It is planned that, unlike in other PSI formats, more regular updates will need to be done to be able to explain how new use cases for the format can be accommodated.

How to encode age and other elapsed times
==========================================

One of the characteristics of a sample can be the age of an individual. It is RECOMMENDED to provide the age in the following format: {X}Y{X}M{X}D. Some valid examples are:

- 40Y (forty years)
- 40Y5M (forty years and 5 months)
- 40Y5M2D (forty years, 5 months, and 2 days)

When needed, weeks can also be used: 8W (eight weeks)

Age interval:

Sometimes the sample does not have an exact age but contains a range of ages. To annotate an age range the following convention is RECOMMENDED:

40Y-85Y

This means that the subject (sample) is between 40 and 85 years old.
Other temporal information can be encoded similarly.

Phosphoproteomics and other post-translational modifications enriched studies
=============================================================================

In PTM-enriched experiments, the characteristics[enrichment process] SHOULD be provided. The different values already included in EFO are:

- enrichment of phosphorylated proteins
- enrichment of glycosylated proteins

This characteristic can be used as a factor value[enrichment process] to differentiate the expression between proteins in the phospho-enriched sample when compared with the control.

Synthetic peptide libraries
===========================

It is common to use synthetic peptide libraries for multiple use cases including:

- Benchmark of analytical and bioinformatics methods and algorithms.
- Improvement of peptide identification/quantification using spectral libraries.

When describing synthetic peptide libraries most of the sample metadata can be declared as “not applicable”. However, some authors can also annotate the organism, for example, because they know that the library has been designed from specific peptide species, see example the following experiment containing synthetic peptides (`Example PXD000759 <https://github.com/bigbio/proteomics-sample-metadata/blob/master/annotated-projects/PXD000759>`_).

In these cases, it is important to annotate that the sample is composed of a synthetic peptide library. This can be done by adding the **characteristics[synthetic peptide]**. The possible values are “synthetic”, “not synthetic” or “mixed”.

Normal and healthy samples
==========================

Samples from healthy patients or individuals normally appear in manuscripts and are often annotated as healthy or normal. We RECOMMEND using the word “normal” mapped to the CV term PATO_0000461, which is also included in EFO: `normal PATO term <https://www.ebi.ac.uk/ols/ontologies/efo/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPATO_0000461>`_.

Example:

.. list-table:: Minimum data metadata for any proteomics dataset
   :widths: 14 14 14 14 14 14
   :header-rows: 1

   * - source name
     - characteristics[organism]
     - characteristics[organism part]
     - characteristics[phenotype]
     - characteristics[compound]
     - factor value[phenotype]
   * - sample_treat
     - homo sapiens
     - liver
     - necrotic tissue
     - drug A
     - necrotic tissue
   * - sample_control
     - homo sapiens
     - liver
     - normal
     - none
     - normal

Multiple projects into one annotation file
==========================================

It may be needed to annotate multiple ProteomeXchange datasets into one large SDRF-Proteomics file e.g., reanalysis purposes. If that is the case, it is RECOMMENDED to use the column name comment[proteomexchange accession number] to differentiate between different datasets.
