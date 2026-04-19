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
    -o tools.html \
    sdrf-proteomics/TOOLS.adoc

# Build sample guidelines page
echo "Building sample guidelines page..."
asciidoctor \
    -D "$OUTPUT_DIR" \
    $ASCIIDOCTOR_OPTS \
    -o sample-guidelines.html \
    sdrf-proteomics/SAMPLE-GUIDELINES.adoc

# Build templates guide
if [ -f "sdrf-proteomics/TEMPLATES.adoc" ]; then
    echo "Building templates guide..."
    asciidoctor \
        -D "$OUTPUT_DIR" \
        $ASCIIDOCTOR_OPTS \
        -o templates.html \
        sdrf-proteomics/TEMPLATES.adoc
fi

# Build data analysis metadata guide
if [ -f "sdrf-proteomics/metadata-guidelines/data-analysis-metadata.adoc" ]; then
    echo "Building data analysis metadata guide..."
    asciidoctor \
        -D "$OUTPUT_DIR/metadata-guidelines" \
        -a stylesheet=../css/style.css \
        -a linkcss \
        -a toc=left \
        -a toclevels=3 \
        -a sectanchors \
        -a sectlinks \
        -a source-highlighter=highlight.js \
        --backend=html5 \
        -o data-analysis-metadata.html \
        sdrf-proteomics/metadata-guidelines/data-analysis-metadata.adoc
fi

# Build template pages from YAML definitions
echo "Building template pages from YAML..."
python3 scripts/build_template_pages.py \
    sdrf-proteomics/sdrf-templates "$OUTPUT_DIR/templates"

# Copy assets
echo "Copying assets..."

# Copy CSS
cp site/css/style.css "$OUTPUT_DIR/css/"

# Copy JavaScript
cp site/js/search.js "$OUTPUT_DIR/js/"
cp site/js/sdrf-builder.js "$OUTPUT_DIR/js/"

# Copy images
cp -r sdrf-proteomics/images/* "$OUTPUT_DIR/images/" 2>/dev/null || true
cp -r images/* "$OUTPUT_DIR/images/" 2>/dev/null || true

# Copy static HTML pages
echo "Copying static pages..."
cp site/index.html "$OUTPUT_DIR/"
cp site/sdrf-terms.html "$OUTPUT_DIR/"
cp site/quickstart.html "$OUTPUT_DIR/"
cp site/sdrf-explorer.html "$OUTPUT_DIR/"
cp site/sdrf-editor.html "$OUTPUT_DIR/"
cp site/sdrf-builder.html "$OUTPUT_DIR/"

# Copy SDRF terms TSV (if present) — also create TERMS.tsv alias for AsciiDoc links
cp sdrf-proteomics/metadata-guidelines/sdrf-terms.tsv "$OUTPUT_DIR/" 2>/dev/null || true
cp sdrf-proteomics/TERMS.tsv "$OUTPUT_DIR/TERMS.tsv" 2>/dev/null || true

# Auto-generate index.html template section from YAML
echo "Updating index template section..."
python3 scripts/build_index_templates.py \
    sdrf-proteomics/sdrf-templates "$OUTPUT_DIR/index.html"

# Provision the external sdrf-annotated-datasets repository so the index
# script can read the SDRF files. Honour SDRF_DATASETS_DIR if the caller
# already provided one (local dev with an existing checkout); otherwise
# shallow-clone the default branch into vendor/.
SDRF_DATASETS_REPO="${SDRF_DATASETS_REPO:-bigbio/sdrf-annotated-datasets}"
SDRF_DATASETS_BRANCH="${SDRF_DATASETS_BRANCH:-main}"
if [ -z "${SDRF_DATASETS_DIR:-}" ]; then
    VENDOR_DIR="$REPO_ROOT/vendor/sdrf-annotated-datasets"
    if [ ! -d "$VENDOR_DIR/.git" ]; then
        echo "Cloning $SDRF_DATASETS_REPO@$SDRF_DATASETS_BRANCH into $VENDOR_DIR ..."
        mkdir -p "$(dirname "$VENDOR_DIR")"
        git clone --depth 1 --branch "$SDRF_DATASETS_BRANCH" \
            "https://github.com/$SDRF_DATASETS_REPO.git" "$VENDOR_DIR"
    else
        echo "Updating existing clone at $VENDOR_DIR ..."
        git -C "$VENDOR_DIR" fetch --depth 1 origin "$SDRF_DATASETS_BRANCH"
        git -C "$VENDOR_DIR" reset --hard "origin/$SDRF_DATASETS_BRANCH"
    fi
    SDRF_DATASETS_DIR="$VENDOR_DIR/datasets"
fi
export SDRF_DATASETS_DIR SDRF_DATASETS_REPO SDRF_DATASETS_BRANCH
echo "Using SDRF datasets from: $SDRF_DATASETS_DIR"

# Build SDRF Explorer index
echo "Building SDRF Explorer index..."
python3 site/build-sdrf-index.py
cp site/sdrf-data.json "$OUTPUT_DIR/"

# Inject navigation headers
echo "Adding navigation headers..."
if [ "$IS_DEV" = true ]; then
    python3 scripts/inject-headers.py "$OUTPUT_DIR" --dev
else
    python3 scripts/inject-headers.py "$OUTPUT_DIR"
fi

# Transform links (SDRF Explorer links and .adoc to .html)
echo "Transforming links..."
python3 scripts/transform-links.py "$OUTPUT_DIR"

# Transform SDRF example tables (add column styling)
echo "Transforming SDRF example tables..."
python3 scripts/transform-sdrf-tables.py "$OUTPUT_DIR"

# Build SDRF builder data
echo "Building SDRF builder data..."
python3 scripts/build_sdrf_builder_data.py \
    sdrf-proteomics/sdrf-templates "$OUTPUT_DIR/sdrf-builder-data.json"

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
