# Development Guide

This guide explains how to build and maintain the SDRF-Proteomics documentation website.

## Repository Structure

```
proteomics-metadata-standard/
├── build-docs.sh              # Unified build script (local & CI/CD)
├── sdrf-proteomics/           # Main specification source
│   ├── README.adoc            # Main specification (AsciiDoc)
│   ├── tool-support.adoc      # Tool support page
│   ├── metadata-guidelines/   # General metadata guidelines
│   │   ├── sample-metadata.adoc
│   │   └── sdrf-terms.tsv
│   ├── templates/             # All templates (core + specialized)
│   │   ├── human/             # Human template (includes clinical metadata)
│   │   ├── vertebrates/       # Non-human vertebrates
│   │   ├── invertebrates/     # Invertebrates (Drosophila, C. elegans)
│   │   ├── plants/            # Plant organisms
│   │   ├── ms-proteomics/     # MS proteomics template (base for MS experiments)
│   │   ├── cell-lines/        # Cell line experiments
│   │   ├── crosslinking/      # XL-MS experiments
│   │   ├── immunopeptidomics/ # Immunopeptidomics
│   │   └── ...
│   └── images/                # Specification images
├── site/                      # Website assets and build scripts
│   ├── css/style.css          # Main stylesheet
│   ├── js/search.js           # Search functionality
│   ├── index.html             # Homepage
│   ├── quickstart.html        # Quick start guide
│   ├── sdrf-explorer.html     # SDRF dataset explorer
│   ├── sdrf-terms.html        # Terms reference page
│   ├── build-sdrf-index.py    # Builds dataset index
│   └── build-search-index.py  # Builds search index
├── annotated-projects/        # Annotated SDRF files (~300 datasets)
├── demo_page/                 # Local preview output (git-ignored)
├── .github/workflows/         # CI/CD configuration
│   └── build-docs.yml         # Website build workflow
├── DEVELOPMENT.md             # This file
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

### Using the Build Script (Recommended)

The easiest way to build the documentation is using the provided build script. This script replicates the exact CI/CD build process, ensuring consistency between local and deployed builds.

```bash
# Build to default directory (demo_page/)
./build-docs.sh

# Build with a clean start (removes existing output)
./build-docs.sh --clean

# Build to a specific directory
./build-docs.sh docs

# Build dev version (adds development banner)
./build-docs.sh docs/dev --dev

# Show help
./build-docs.sh --help
```

#### What the Build Script Does

1. **Converts AsciiDoc to HTML** using Asciidoctor with proper styling options
2. **Copies static assets** (CSS, JavaScript, images)
3. **Copies static HTML pages** (index.html, quickstart.html, sdrf-explorer.html, sdrf-terms.html)
4. **Builds SDRF Explorer index** from annotated-projects
5. **Injects navigation headers** into all generated HTML pages
6. **Transforms SDRF links** to use the SDRF Explorer viewer
7. **Builds search index** for site-wide search functionality
8. **Adds dev banner** (when using `--dev` flag)

### Manual Build (Advanced)

If you need to build individual files for quick iteration:

```bash
# Build the main specification only
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

**Note:** Manual builds will be missing navigation headers, search functionality, and other features. Use the build script for testing the complete site.

### View Locally

After building, open the site directly in your browser:

```bash
open demo_page/index.html
```

The site is self-contained and doesn't require a web server.

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

The CI/CD workflow (`.github/workflows/build-docs.yml`) performs the same steps as the local build script, ensuring consistency.

### Local vs CI/CD Comparison

| Feature | Local (build-docs.sh) | CI/CD |
|---------|----------------------|-------|
| AsciiDoc conversion | ✓ | ✓ |
| Navigation headers | ✓ | ✓ |
| SDRF link transformation | ✓ | ✓ |
| Search index | ✓ | ✓ |
| Dev banner | `--dev` flag | Auto for dev branch |
| Output directory | Configurable | docs/ or docs/dev/ |

### Ensuring Consistency

To verify your local build matches the deployed version:

```bash
# Build same as production
./build-docs.sh --clean

# Build same as dev deployment
./build-docs.sh --clean --dev
```

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

## Troubleshooting

### Stylesheet Warnings

When building, you may see warnings like:
```
asciidoctor: WARNING: stylesheet does not exist or cannot be read
```

These are expected and can be ignored. We use `-a linkcss` which links the stylesheet at runtime rather than embedding it during build.

### Missing Dependencies

If you see errors about missing commands:
- **asciidoctor**: `gem install asciidoctor`
- **python3**: Install Python 3 from https://python.org

### Build Output Differences

If the local build looks different from the deployed version:
1. Ensure you're using the build script (`./build-docs.sh`), not manual asciidoctor commands
2. Clear the output directory with `--clean`
3. Check that you have the latest site assets (`git pull`)

### Common Issues

| Issue | Solution |
|-------|----------|
| No navigation header | Use the build script instead of manual asciidoctor |
| CSS not loading | Ensure `site/css/style.css` was copied to output |
| Dev banner missing | Use `--dev` flag when building |
| Search not working | Ensure `search-index.json` was generated |

## Contributing

1. Make changes to the appropriate AsciiDoc or HTML files
2. Build locally and test: `./build-docs.sh --clean`
3. View locally: `open demo_page/index.html`
4. Create a pull request to the `dev` branch for review
5. After approval and merge to dev, changes deploy to https://sdrf.quantms.org/dev/
6. After merge to master, changes deploy to https://sdrf.quantms.org/
