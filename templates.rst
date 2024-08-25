SDRF-Proteomics Templates
########################################

The sample metadata **Templates** are a set of guidelines to annotate the different types of proteomics experiments (use cases) to ensure that Minimum Metadata and characteristics are provided to understand the dataset. These templates respond to the distribution and frequency of experiment types in public databases like PRIDE and ProteomeXchange. The Python/Java validators will check the columns checklists depending on the template.

NOTE: It is planned that, unlike in other PSI formats, regular updates will need to be done to be able to explain how new use cases for the format can be accommodated.

- **Default proteomics experiment**: Minimum information for any proteomics experiment - `Default template <https://github.com/bigbio/proteomics-metadata-standard/blob/master/templates/sdrf-default.tsv>`_
- **Human experiment**: All experiments that use `Human samples <https://github.com/bigbio/proteomics-metadata-standard/blob/master/templates/sdrf-human.tsv>`_
- **Vertebrates experiment**: Vertebrate experiment - `Vertebrate template <https://github.com/bigbio/proteomics-metadata-standard/blob/master/templates/sdrf-vertebrates.tsv>`_
- **Non-vertebrates experiment**: Non-vertebrate experiment - `Non-vertebrate template <https://github.com/bigbio/proteomics-metadata-standard/blob/master/templates/sdrf-nonvertebrates.tsv>`_
- **Plants experiment**: Plant experiment - `Plant template <https://github.com/bigbio/proteomics-metadata-standard/blob/master/templates/sdrf-plants.tsv>`_
- **Cell lines experiment**: Experiments using cell-lines - `Cell lines template <https://github.com/bigbio/proteomics-metadata-standard/blob/master/templates/sdrf-cell-line.tsv>`_

.. note:: Each of the template is a tsv file with the minimum columns to describe the experiment. The community can create they are own templates for example for meta-proteomics experiments, imaging proteomics or top-down. If the community would like to add a new template, the following table should be modified and the corresponding tsv should be created in this folder.

**Sample attributes**: Minimum sample attributes for primary cells from different species and cell lines

.. list-table:: SDRF-Proteomics templates sample attributes
   :widths: 14 14 14 14 14 14 14
   :header-rows: 1

   * -
     - Default
     - Human
     - Vertebrates
     - Non-vertebrates
     - Plants
     - Cell lines
   * - source name
     - required
     - required
     - required
     - required
     - required
     - required
   * - characteristics[organism]
     - required
     - required
     - required
     - required
     - required
     - required
   * - characteristics[strain/breed]
     -
     -
     -
     - required
     -
     -
   * - characteristics[ecotype/cultivar]
     -
     -
     -
     -
     - required
     -
   * - characteristics[ancestry category]
     -
     - required
     -
     -
     -
     -
   * - characteristics[age]
     -
     - required
     - required
     -
     - required
     -
   * - characteristics[developmental stage]
     -
     - required
     - required
     -
     - required
     -
   * - characteristics[sex]
     -
     - required
     - required
     -
     - required
     -
   * - characteristics[organism part]
     - required
     - required
     - required
     - required
     - required
     - required
   * - characteristics[cell type]
     - required
     - required
     - required
     - required
     - required
     - required
   * - technology type
     - required
     - required
     - required
     - required
     - required
     - required
   * - characteristics[disease]
     - required
     - required
     - required
     - required
     - required
     - required
   * - characteristics[individual]
     -
     - required
     -
     -
     -
     -
   * - characteristics[biological replicate]
     - required
     - required
     - required
     - required
     - required
     - required
   * - characteristics[cell line]
     -
     -
     -
     -
     -
     - required
   * -
     -
     -
     -
     -
     -
     -
   * - assay name
     - required
     - required
     - required
     - required
     - required
     - required
   * - comment[data file]
     - required
     - required
     - required
     - required
     - required
     - required
   * - comment[technical replicate]
     - required
     - required
     - required
     - required
     - required
     - required
   * - comment[fraction identifier]
     - required
     - required
     - required
     - required
     - required
     - required
   * - comment[label]
     - required
     - required
     - required
     - required
     - required
     - required
   * - comment[instrument]
     - required
     - required
     - required
     - required
     - required
     - required

