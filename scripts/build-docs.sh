#!/bin/bash
#
# SDRF-Proteomics Documentation Build Script
# ===========================================
#
# This script builds the documentation site for SDRF-Proteomics.
# It can be used both locally for testing and in CI/CD pipelines.
#
# Usage:
#   ./scripts/build-docs.sh [OUTPUT_DIR] [OPTIONS]
#
# Arguments:
#   OUTPUT_DIR    Output directory (default: demo_page)
#
# Options:
#   --dev         Build as dev version (adds dev banner)
#   --clean       Remove output directory before building
#   --help        Show this help message
#
# Examples:
#   ./scripts/build-docs.sh                    # Build to demo_page/
#   ./scripts/build-docs.sh docs               # Build to docs/
#   ./scripts/build-docs.sh docs/dev --dev     # Build dev version to docs/dev/
#   ./scripts/build-docs.sh --clean            # Clean build to demo_page/
#

set -e  # Exit on error

# Default values
OUTPUT_DIR="demo_page"
IS_DEV=false
CLEAN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            IS_DEV=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --help)
            head -30 "$0" | tail -28
            exit 0
            ;;
        *)
            OUTPUT_DIR="$1"
            shift
            ;;
    esac
done

# Get repository root directory (parent of scripts folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "=========================================="
echo "SDRF-Proteomics Documentation Build"
echo "=========================================="
echo "Repository root: $REPO_ROOT"
echo "Output directory: $OUTPUT_DIR"
echo "Dev version: $IS_DEV"
echo ""

# Check dependencies
if ! command -v asciidoctor &> /dev/null; then
    echo "Error: asciidoctor is not installed."
    echo "Install with: gem install asciidoctor"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Clean if requested
if [ "$CLEAN" = true ] && [ -d "$OUTPUT_DIR" ]; then
    echo "Cleaning output directory..."
    rm -rf "$OUTPUT_DIR"
fi

# Create output directories
echo "Creating output directories..."
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/css"
mkdir -p "$OUTPUT_DIR/js"
mkdir -p "$OUTPUT_DIR/images"
mkdir -p "$OUTPUT_DIR/templates"
mkdir -p "$OUTPUT_DIR/metadata-guidelines"

# Common Asciidoctor options
ASCIIDOCTOR_OPTS="-a stylesheet=css/style.css -a linkcss -a toc=left -a toclevels=3 -a sectanchors -a sectlinks -a source-highlighter=highlight.js --backend=html5"

# Build main specification
echo "Building main specification..."
asciidoctor \
    -D "$OUTPUT_DIR" \
    $ASCIIDOCTOR_OPTS \
    -o specification.html \
    sdrf-proteomics/README.adoc

# Build tool support page
echo "Building tool support page..."
asciidoctor \
    -D "$OUTPUT_DIR" \
    $ASCIIDOCTOR_OPTS \
    -o tool-support.html \
    sdrf-proteomics/tool-support.adoc

# Build metadata guidelines
echo "Building metadata guidelines..."
asciidoctor \
    -D "$OUTPUT_DIR/metadata-guidelines" \
    -a stylesheet=../css/style.css \
    -a linkcss \
    -a toc=left \
    -a toclevels=3 \
    -a sectanchors \
    -a sectlinks \
    --backend=html5 \
    -o sample-metadata.html \
    sdrf-proteomics/metadata-guidelines/sample-metadata.adoc

# Check if human-sample-metadata.adoc exists and build it
if [ -f "sdrf-proteomics/metadata-guidelines/human-sample-metadata.adoc" ]; then
    echo "Building human sample metadata guidelines..."
    asciidoctor \
        -D "$OUTPUT_DIR/metadata-guidelines" \
        -a stylesheet=../css/style.css \
        -a linkcss \
        -a toc=left \
        -a toclevels=3 \
        -a sectanchors \
        -a sectlinks \
        --backend=html5 \
        -o human-sample-metadata.html \
        sdrf-proteomics/metadata-guidelines/human-sample-metadata.adoc
fi

# Build template documentation
echo "Building templates..."
for dir in sdrf-proteomics/templates/*/; do
    if [ -f "${dir}README.adoc" ]; then
        template_name=$(basename "$dir")
        echo "  Building template: $template_name"
        asciidoctor \
            -D "$OUTPUT_DIR/templates" \
            -a stylesheet=../css/style.css \
            -a linkcss \
            -a toc=left \
            -a toclevels=3 \
            -a sectanchors \
            -a sectlinks \
            --backend=html5 \
            -o "${template_name}.html" \
            "${dir}README.adoc"
    fi
done

# Copy assets
echo "Copying assets..."

# Copy CSS
cp site/css/style.css "$OUTPUT_DIR/css/"

# Copy JavaScript
cp site/js/search.js "$OUTPUT_DIR/js/"

# Copy images
cp -r sdrf-proteomics/images/* "$OUTPUT_DIR/images/" 2>/dev/null || true
cp -r images/* "$OUTPUT_DIR/images/" 2>/dev/null || true

# Copy static HTML pages
echo "Copying static pages..."
cp site/index.html "$OUTPUT_DIR/"
cp site/sdrf-terms.html "$OUTPUT_DIR/"
cp site/quickstart.html "$OUTPUT_DIR/"
cp site/sdrf-explorer.html "$OUTPUT_DIR/"

# Copy SDRF terms TSV
cp sdrf-proteomics/metadata-guidelines/sdrf-terms.tsv "$OUTPUT_DIR/"

# Build SDRF Explorer index
echo "Building SDRF Explorer index..."
python3 site/build-sdrf-index.py
cp site/sdrf-data.json "$OUTPUT_DIR/"

# Inject navigation headers
echo "Adding navigation headers..."
python3 scripts/inject-headers.py "$OUTPUT_DIR"

# Transform SDRF links to use viewer
echo "Transforming SDRF links..."
python3 scripts/transform-links.py "$OUTPUT_DIR/specification.html"

# Build search index
echo "Building search index..."
python3 site/build-search-index.py . "$OUTPUT_DIR/search-index.json"

# Add dev banner if building dev version
if [ "$IS_DEV" = true ]; then
    echo "Adding dev version banner..."
    ./scripts/add-dev-banner.sh "$OUTPUT_DIR"
fi

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo "Output: $OUTPUT_DIR/"
echo ""
echo "To view locally, open $OUTPUT_DIR/index.html in your browser"
echo ""
