#!/bin/bash
# Copy static assets to the output directory
# Usage: ./copy-assets.sh <output_dir>

set -e

OUTPUT_DIR="${1:-docs}"

echo "Copying assets to: $OUTPUT_DIR"

# Copy images
mkdir -p "$OUTPUT_DIR/images"
cp -r sdrf-proteomics/images/* "$OUTPUT_DIR/images/" 2>/dev/null || true
cp -r images/* "$OUTPUT_DIR/images/" 2>/dev/null || true

# Copy CSS
mkdir -p "$OUTPUT_DIR/css"
cp site/css/style.css "$OUTPUT_DIR/css/"

# Copy JavaScript
mkdir -p "$OUTPUT_DIR/js"
cp site/js/search.js "$OUTPUT_DIR/js/"

# Copy static HTML pages
cp site/index.html "$OUTPUT_DIR/"
cp site/sdrf-terms.html "$OUTPUT_DIR/"
cp site/quickstart.html "$OUTPUT_DIR/"

# Copy SDRF terms data
cp sdrf-proteomics/metadata-guidelines/sdrf-terms.tsv "$OUTPUT_DIR/"

# Copy SDRF Explorer
cp site/sdrf-explorer.html "$OUTPUT_DIR/"

echo "Assets copied successfully!"
