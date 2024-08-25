# Configuration file for the Sphinx documentation builder.
#
# For a full list of options see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------

project = 'proteomics sample metadata'
author = 'Yasset Perez-Riverol'
release = '1.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
# These can be extensions coming with Sphinx or custom ones.
extensions = [
    'sphinx_asciidoc',  # AsciiDoc support
]

# The master toctree document.
master_doc = 'index'

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.adoc': 'asciidoc',  # Include .adoc files
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# -- Options for sphinx-asciidoc --------------------------------------------

# Additional arguments to pass to asciidoctor
asciidoc_args = ['-a', 'toc=left', '-a', 'sectnums']

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))
