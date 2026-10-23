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

# The explorer fetches sdrf-data.json. Weekly refresh-explorer-catalog.yml
# rebuilds that file from bigbio/sdrf-annotated-datasets and publishes it on
# the explorer-catalog branch. Ordinary builds download the snapshot.
# Set SDRF_REBUILD_CATALOG=1 to scan the dataset repository in this build.
CATALOG_FILE="$REPO_ROOT/site/sdrf-data.json"
ensure_explorer_catalog() {
    if [ "${SDRF_REBUILD_CATALOG:-}" = "1" ]; then
        echo "Rebuilding SDRF explorer catalog from annotated datasets..."
        bash "$REPO_ROOT/scripts/refresh-explorer-catalog.sh"
        return
    fi

    if [ -n "${GITHUB_ACTIONS:-}" ] || [ ! -s "$CATALOG_FILE" ]; then
        CATALOG_REPO="${GITHUB_REPOSITORY:-bigbio/proteomics-sample-metadata}"
        CATALOG_URL="${SDRF_CATALOG_URL:-https://raw.githubusercontent.com/${CATALOG_REPO}/explorer-catalog/sdrf-data.json}"
        CATALOG_TMP="$(mktemp)"
        echo "Downloading SDRF explorer catalog from ${CATALOG_URL}"
        if curl -fsSL "$CATALOG_URL" -o "$CATALOG_TMP" \
            && python3 -c 'import json,sys; data=json.load(open(sys.argv[1], encoding="utf-8")); assert "datasets" in data and "statistics" in data' "$CATALOG_TMP"; then
            mv "$CATALOG_TMP" "$CATALOG_FILE"
            echo "Using published explorer catalog."
            return
        fi
        rm -f "$CATALOG_TMP"
        if [ -s "$CATALOG_FILE" ]; then
            echo "Published catalog is unavailable. Using the catalog already on disk."
            return
        fi
        echo "Published catalog is unavailable. Building it from annotated datasets."
        bash "$REPO_ROOT/scripts/refresh-explorer-catalog.sh"
        return
    fi

    echo "Using existing SDRF explorer catalog: $CATALOG_FILE"
}

ensure_explorer_catalog
cp "$CATALOG_FILE" "$OUTPUT_DIR/sdrf-data.json"

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
