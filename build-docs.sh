#!/bin/bash
#
# SDRF-Proteomics Documentation Build Script
# ===========================================
#
# This script builds the documentation site for SDRF-Proteomics.
# It can be used both locally for testing and in CI/CD pipelines.
#
# Usage:
#   ./build-docs.sh [OUTPUT_DIR] [OPTIONS]
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
#   ./build-docs.sh                    # Build to demo_page/
#   ./build-docs.sh docs               # Build to docs/
#   ./build-docs.sh docs/dev --dev     # Build dev version to docs/dev/
#   ./build-docs.sh --clean            # Clean build to demo_page/
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

# Get script directory (repository root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "SDRF-Proteomics Documentation Build"
echo "=========================================="
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

asciidoctor \
    -D "$OUTPUT_DIR/metadata-guidelines" \
    -a stylesheet=../css/style.css \
    -a linkcss \
    -a toc=left \
    -a toclevels=3 \
    -a sectanchors \
    -a sectlinks \
    --backend=html5 \
    -o data-file-metadata.html \
    sdrf-proteomics/metadata-guidelines/data-file-metadata.adoc

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

# Create header injection Python script
cat > /tmp/inject_header.py << 'PYEOF'
import sys
import re

filepath = sys.argv[1]
header_html = sys.argv[2]

with open(filepath, 'r') as f:
    content = f.read()

# Add has-doc-header class to body
content = re.sub(r'<body class="([^"]*)"', r'<body class="has-doc-header \1"', content)
content = re.sub(r'<body>', '<body class="has-doc-header">', content)

# Insert header after opening body tag
content = re.sub(r'(<body[^>]*>)', r'\1\n' + header_html, content)

with open(filepath, 'w') as f:
    f.write(content)
PYEOF

# Define navigation headers
echo "Adding navigation headers..."

# Version link differs for dev vs production
if [ "$IS_DEV" = true ]; then
    VERSION_LINK='<a href="/" class="version-link">Stable Version</a>'
else
    VERSION_LINK='<a href="/dev/" class="version-link">Dev Version</a>'
fi

# Header for root-level pages
ROOT_HEADER="<header class=\"doc-header\"><div class=\"doc-header-brand\"><a href=\"./index.html\">SDRF-Proteomics</a></div><nav class=\"doc-header-nav\"><a href=\"./index.html\">Home</a><a href=\"./specification.html\" class=\"nav-current\">Specification</a><a href=\"./index.html#metadata-guidelines\">Metadata Guidelines</a><a href=\"./index.html#templates\">Templates</a><a href=\"./index.html#tools\">Tools</a><a href=\"./sdrf-explorer.html\">Explorer</a><a href=\"./index.html#contributors\">Contributors</a>${VERSION_LINK}<a href=\"https://github.com/bigbio/proteomics-metadata-standard\" target=\"_blank\">GitHub</a></nav></header>"

# Header for tool support page
TOOLS_HEADER="<header class=\"doc-header\"><div class=\"doc-header-brand\"><a href=\"./index.html\">SDRF-Proteomics</a></div><nav class=\"doc-header-nav\"><a href=\"./index.html\">Home</a><a href=\"./specification.html\">Specification</a><a href=\"./index.html#metadata-guidelines\">Metadata Guidelines</a><a href=\"./index.html#templates\">Templates</a><a href=\"./index.html#tools\" class=\"nav-current\">Tools</a><a href=\"./sdrf-explorer.html\">Explorer</a><a href=\"./index.html#contributors\">Contributors</a>${VERSION_LINK}<a href=\"https://github.com/bigbio/proteomics-metadata-standard\" target=\"_blank\">GitHub</a></nav></header>"

# Header for metadata guidelines pages
GUIDELINES_HEADER="<header class=\"doc-header\"><div class=\"doc-header-brand\"><a href=\"../index.html\">SDRF-Proteomics</a></div><nav class=\"doc-header-nav\"><a href=\"../index.html\">Home</a><a href=\"../specification.html\">Specification</a><a href=\"../index.html#metadata-guidelines\" class=\"nav-current\">Metadata Guidelines</a><a href=\"../index.html#templates\">Templates</a><a href=\"../index.html#tools\">Tools</a><a href=\"../sdrf-explorer.html\">Explorer</a><a href=\"../index.html#contributors\">Contributors</a>${VERSION_LINK}<a href=\"https://github.com/bigbio/proteomics-metadata-standard\" target=\"_blank\">GitHub</a></nav></header>"

# Header for template pages
TMPL_HEADER="<header class=\"doc-header\"><div class=\"doc-header-brand\"><a href=\"../index.html\">SDRF-Proteomics</a></div><nav class=\"doc-header-nav\"><a href=\"../index.html\">Home</a><a href=\"../specification.html\">Specification</a><a href=\"../index.html#metadata-guidelines\">Metadata Guidelines</a><a href=\"../index.html#templates\" class=\"nav-current\">Templates</a><a href=\"../index.html#tools\">Tools</a><a href=\"../sdrf-explorer.html\">Explorer</a><a href=\"../index.html#contributors\">Contributors</a>${VERSION_LINK}<a href=\"https://github.com/bigbio/proteomics-metadata-standard\" target=\"_blank\">GitHub</a></nav></header>"

# Add header to specification.html
if [ -f "$OUTPUT_DIR/specification.html" ]; then
    python3 /tmp/inject_header.py "$OUTPUT_DIR/specification.html" "$ROOT_HEADER"
fi

# Add header to tool-support.html
if [ -f "$OUTPUT_DIR/tool-support.html" ]; then
    python3 /tmp/inject_header.py "$OUTPUT_DIR/tool-support.html" "$TOOLS_HEADER"
fi

# Add header to metadata guidelines pages
for file in "$OUTPUT_DIR"/metadata-guidelines/*.html; do
    if [ -f "$file" ]; then
        python3 /tmp/inject_header.py "$file" "$GUIDELINES_HEADER"
    fi
done

# Add header to template pages
for file in "$OUTPUT_DIR"/templates/*.html; do
    if [ -f "$file" ]; then
        python3 /tmp/inject_header.py "$file" "$TMPL_HEADER"
    fi
done

# Transform SDRF links to use viewer
echo "Transforming SDRF links..."
python3 << EOF
import re

filepath = "$OUTPUT_DIR/specification.html"
with open(filepath, 'r') as f:
    content = f.read()

# Replace GitHub annotated-projects links with SDRF Explorer viewer links
pattern = r'href="https://github\.com/bigbio/proteomics-metadata-standard/tree/master/annotated-projects/(PXD\d+)"'
replacement = r'href="./sdrf-explorer.html?view=\1"'
content = re.sub(pattern, replacement, content)

with open(filepath, 'w') as f:
    f.write(content)

print("  Transformed SDRF links in specification.html")
EOF

# Build search index
echo "Building search index..."
python3 site/build-search-index.py . "$OUTPUT_DIR/search-index.json"

# Add dev banner if building dev version
if [ "$IS_DEV" = true ]; then
    echo "Adding dev version banner..."

    # Add banner to index.html
    sed -i.bak 's/<body>/<body><div class="dev-banner">⚠️ Development Version - This documentation is from the dev branch and may contain unreleased changes. <a href="\/">View stable version<\/a><\/div>/' "$OUTPUT_DIR/index.html"
    rm -f "$OUTPUT_DIR/index.html.bak"

    # Add dev banner styles to CSS
    cat >> "$OUTPUT_DIR/css/style.css" << 'CSSEOF'

/* Dev banner */
.dev-banner {
  background: #fef3c7;
  color: #92400e;
  padding: 0.75rem 1rem;
  text-align: center;
  font-size: 0.9rem;
  border-bottom: 1px solid #fcd34d;
}
.dev-banner a {
  color: #92400e;
  font-weight: 600;
}
CSSEOF
fi

# Clean up
rm -f /tmp/inject_header.py

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo "Output: $OUTPUT_DIR/"
echo ""
echo "To view locally, open $OUTPUT_DIR/index.html in your browser"
echo ""
