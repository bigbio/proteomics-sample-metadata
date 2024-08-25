# -- General configuration ---------------------------------------------------

extensions = [
    'sphinxcontrib.asciidoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master document is the index file
master_doc = 'index'

# The suffix of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.adoc': 'asciidoc',
}

# Explicitly set the AsciiDoc parser
asciidoc_parser = 'asciidoc'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# -- Options for sphinx-asciidoc --------------------------------------------

# Arguments to pass to asciidoctor (optional)
asciidoc_args = ['-a', 'toc=left', '-a', 'sectnums']