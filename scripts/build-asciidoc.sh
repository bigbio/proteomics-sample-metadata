#!/bin/bash
# Build AsciiDoc documentation files
# Usage: ./build-asciidoc.sh <output_dir>

set -e

OUTPUT_DIR="${1:-docs}"

echo "Building AsciiDoc documentation to: $OUTPUT_DIR"

# Create output directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/metadata-guidelines"
mkdir -p "$OUTPUT_DIR/templates"

# Common asciidoctor options
ASCIIDOCTOR_OPTS="-a linkcss -a toc=left -a toclevels=3 -a sectanchors -a sectlinks -a source-highlighter=highlight.js --backend=html5"

# Build main specification
echo "Building main specification..."
asciidoctor \
    -D "$OUTPUT_DIR" \
    -a stylesheet=css/style.css \
    $ASCIIDOCTOR_OPTS \
    -o specification.html \
    sdrf-proteomics/README.adoc

# Build tool support page
echo "Building tool support page..."
asciidoctor \
    -D "$OUTPUT_DIR" \
    -a stylesheet=css/style.css \
    $ASCIIDOCTOR_OPTS \
    -o tool-support.html \
    sdrf-proteomics/TOOLS.adoc

# Build sample metadata guidelines
echo "Building sample metadata guidelines..."
asciidoctor \
    -D "$OUTPUT_DIR/metadata-guidelines" \
    -a stylesheet=../css/style.css \
    $ASCIIDOCTOR_OPTS \
    -o sample-metadata.html \
    sdrf-proteomics/metadata-guidelines/sample-metadata.adoc

# Build templates guide
if [ -f "sdrf-proteomics/TEMPLATES.adoc" ]; then
    echo "Building templates guide..."
    asciidoctor \
        -D "$OUTPUT_DIR" \
        -a stylesheet=css/style.css \
        $ASCIIDOCTOR_OPTS \
        -o TEMPLATES.html \
        sdrf-proteomics/TEMPLATES.adoc
fi

# Build data analysis metadata guide
if [ -f "sdrf-proteomics/metadata-guidelines/data-analysis-metadata.adoc" ]; then
    echo "Building data analysis metadata guide..."
    asciidoctor \
        -D "$OUTPUT_DIR/metadata-guidelines" \
        -a stylesheet=../css/style.css \
        $ASCIIDOCTOR_OPTS \
        -o data-analysis-metadata.html \
        sdrf-proteomics/metadata-guidelines/data-analysis-metadata.adoc
fi

# Build template pages from YAML definitions
echo "Building template pages from YAML..."
python3 scripts/build_template_pages.py \
    sdrf-proteomics/sdrf-templates "$OUTPUT_DIR/templates"

echo "AsciiDoc build complete!"
