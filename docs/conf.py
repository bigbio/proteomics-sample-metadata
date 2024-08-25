# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'proteomics metadata'
author = 'Yasset Perez-Riverol, Dai Chengxin'
release = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_asciidoc',  # Add the sphinx_asciidoc extension to handle .adoc files
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master document is the index file
master_doc = 'index'

# The suffix of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.adoc': 'asciidoc',  # Add support for .adoc files
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The theme to use for HTML and HTML Help pages.
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for sphinx-asciidoc --------------------------------------------

# Arguments to pass to asciidoctor (optional)
# For example, you might add asciidoc attributes or extensions here.
asciidoc_args = ['-a', 'toc=left', '-a', 'sectnums']

# -- Extension configuration -------------------------------------------------
# This is where you can configure settings for other extensions, if needed.
