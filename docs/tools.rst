Tools
##########

srdf-pipelines
*****************

The `SDRF pipelines <https://github.com/bigbio/sdrf-pipelines>`_ provide a set of tools to validate and convert SDRF-Proteomics files to different workflow configuration files such as MSstats,OpenMS and MaxQuant.

Installation:

.. code-block:: bash

   $> pip install sdrf-pipelines


Validate the SDRF:

Then, you can use the tool by executing the following command:

.. code-block:: bash

    $> parse_sdrf validate-sdrf --sdrf_file {here_the_path_to_sdrf_file}

jsdrf
******************

The `jsdrf <https://github.com/bigbio/jsdrf>`_ is a Java library to validate SDRF file formats. The SDRF file format represent the sample to data information in proteomics experiments.

Validation of sdrf files with proteomics rules. How to use it:

.. code-block:: bash

    $> java -jar jdsrf-{X.X.X}.jar --sdrf query_file.tsv --template HUMAN

Using the Java library with maven:

.. code-block:: xml

   <dependency>
       <groupId>uk.ac.ebi.pride.sdrf</groupId>
       <artifactId>jsdrf</artifactId>
       <version>{version}</version>
   </dependency>


