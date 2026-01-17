# Development Guide

This guide explains how to build and maintain the SDRF-Proteomics documentation website.

## Repository Structure

```
proteomics-metadata-standard/
├── sdrf-proteomics/           # Main specification source
│   ├── README.adoc            # Main specification (AsciiDoc)
│   ├── metadata-guidelines/   # Detailed metadata guidelines
│   │   ├── sample-metadata.adoc
│   │   ├── human-sample-metadata.adoc
│   │   ├── data-file-metadata.adoc
│   │   └── sdrf-terms.tsv
│   ├── templates/             # Experiment-specific templates
│   │   ├── cell-lines/
│   │   ├── crosslinking/
│   │   ├── immunopeptidomics/
│   │   └── ...
│   └── core-templates/        # Core SDRF templates (TSV files)
├── site/                      # Website assets and build scripts
│   ├── css/style.css          # Main stylesheet
│   ├── js/search.js           # Search functionality
│   ├── index.html             # Homepage
│   ├── sdrf-explorer.html     # SDRF dataset explorer
│   ├── sdrf-terms.html        # Terms reference page
│   ├── build-sdrf-index.py    # Builds dataset index
│   └── build-search-index.py  # Builds search index
├── annotated-projects/        # Annotated SDRF files (~300 datasets)
├── demo_page/                 # Local preview output
├── .github/workflows/         # CI/CD configuration
│   └── build-docs.yml         # Website build workflow
└── README.md                  # Project overview
```

## Prerequisites

Install the required tools:

```bash
# Install Asciidoctor (Ruby)
gem install asciidoctor
gem install asciidoctor-diagram

# Python 3 is required for build scripts
python3 --version
```

## Building the Website Locally

### Quick Build (Specification Only)

```bash
# Build the main specification
asciidoctor \
  -D demo_page \
  -a stylesheet=css/style.css \
  -a linkcss \
  -a toc=left \
  -a toclevels=3 \
  -a sectanchors \
  -a sectlinks \
  -a source-highlighter=highlight.js \
  --backend=html5 \
  -o specification.html \
  sdrf-proteomics/README.adoc
```

### Full Build (All Pages)

```bash
# Set output directory
OUTPUT_DIR="demo_page"

# Create directories
mkdir -p $OUTPUT_DIR/metadata-guidelines $OUTPUT_DIR/templates $OUTPUT_DIR/images $OUTPUT_DIR/css $OUTPUT_DIR/js

# Build main specification
asciidoctor -D $OUTPUT_DIR -a stylesheet=css/style.css -a linkcss -a toc=left -a toclevels=3 -a sectanchors -a sectlinks -a source-highlighter=highlight.js --backend=html5 -o specification.html sdrf-proteomics/README.adoc

# Build metadata guidelines
asciidoctor -D $OUTPUT_DIR/metadata-guidelines -a stylesheet=../css/style.css -a linkcss -a toc=left -a toclevels=3 -a sectanchors -a sectlinks --backend=html5 -o sample-metadata.html sdrf-proteomics/metadata-guidelines/sample-metadata.adoc

asciidoctor -D $OUTPUT_DIR/metadata-guidelines -a stylesheet=../css/style.css -a linkcss -a toc=left -a toclevels=3 -a sectanchors -a sectlinks --backend=html5 -o human-metadata.html sdrf-proteomics/metadata-guidelines/human-sample-metadata.adoc

asciidoctor -D $OUTPUT_DIR/metadata-guidelines -a stylesheet=../css/style.css -a linkcss -a toc=left -a toclevels=3 -a sectanchors -a sectlinks --backend=html5 -o data-file-metadata.html sdrf-proteomics/metadata-guidelines/data-file-metadata.adoc

# Copy assets
cp -r images/* $OUTPUT_DIR/images/ 2>/dev/null || true
cp site/css/style.css $OUTPUT_DIR/css/
cp site/index.html $OUTPUT_DIR/
cp site/js/search.js $OUTPUT_DIR/js/
cp site/sdrf-terms.html $OUTPUT_DIR/
cp sdrf-proteomics/metadata-guidelines/sdrf-terms.tsv $OUTPUT_DIR/
cp site/sdrf-data.json $OUTPUT_DIR/
cp site/sdrf-explorer.html $OUTPUT_DIR/

echo "Build complete! Open demo_page/specification.html in your browser."
```

### View Locally

Simply open the HTML files directly in your browser:

```bash
open demo_page/specification.html
open demo_page/index.html
```

No web server is required - the pages are self-contained.

## Key Files to Modify

| File | Purpose |
|------|---------|
| `sdrf-proteomics/README.adoc` | Main specification document |
| `sdrf-proteomics/metadata-guidelines/*.adoc` | Detailed metadata guidelines |
| `site/css/style.css` | Website styling (including SDRF table colors) |
| `site/index.html` | Homepage |
| `site/sdrf-explorer.html` | Dataset explorer page |
| `site/sdrf-terms.html` | Terms reference page |
| `.github/workflows/build-docs.yml` | CI/CD build configuration |

## SDRF Example Table Styling

SDRF example tables use color-coded columns. Add these CSS classes:

| Class | Color | Use For |
|-------|-------|---------|
| `sample-col` | Blue | source name, characteristics[...] |
| `data-col` | Green | assay name, comment[...], technology type |
| `factor-col` | Orange | factor value[...] |

Example HTML in AsciiDoc:

```asciidoc
++++
<div class="sdrf-example-table">
<table>
<thead>
<tr>
<th class="sample-col">source name</th>
<th class="sample-col">characteristics [organism]</th>
<th class="data-col">assay name</th>
<th class="data-col">comment [data file]</th>
<th class="factor-col">factor value [disease]</th>
</tr>
</thead>
<tbody>
<tr>
<td class="sample-col">sample_1</td>
<td class="sample-col">homo sapiens</td>
<td class="data-col">run_1</td>
<td class="data-col">file.raw</td>
<td class="factor-col">normal</td>
</tr>
</tbody>
</table>
<div class="sdrf-legend">
<span class="legend-item"><span class="legend-color sample-bg"></span> Sample metadata</span>
<span class="legend-item"><span class="legend-color data-bg"></span> Data file metadata</span>
<span class="legend-item"><span class="legend-color factor-bg"></span> Factor values</span>
</div>
</div>
++++
```

## CI/CD Deployment

The website is automatically built and deployed when pushing to:
- `master` branch → Production site (https://sdrf.quantms.org/)
- `dev` branch → Development site (https://sdrf.quantms.org/dev/)

The build process is defined in `.github/workflows/build-docs.yml`.

## Adding New Annotated Projects

1. Create a folder in `annotated-projects/` with the PXD accession
2. Add the SDRF file as `{PXD}.sdrf.tsv`
3. Validate the file:
   ```bash
   pip install sdrf-pipelines
   parse_sdrf validate-sdrf --sdrf_file annotated-projects/PXD000000/PXD000000.sdrf.tsv
   ```
4. Rebuild the dataset index:
   ```bash
   python3 site/build-sdrf-index.py
   ```

## References in AsciiDoc

Use bibliography format for proper cross-references:

```asciidoc
# In text:
This is supported by research <<ref1>>.

# In References section:
[bibliography]
== References

- [[[ref1,1]]] Author et al. Title. Journal (Year). https://doi.org/xxx[doi:xxx]
```

## Useful Commands

```bash
# Validate all SDRF files in a folder
for f in annotated-projects/*/sdrf.tsv; do
  parse_sdrf validate-sdrf --sdrf_file "$f"
done

# Find all SDRF files with a specific column
grep -l "characteristics\[disease\]" annotated-projects/*/*.sdrf.tsv

# Count annotated projects
ls -d annotated-projects/PXD* | wc -l
```
