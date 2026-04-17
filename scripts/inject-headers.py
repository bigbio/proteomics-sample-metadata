#!/usr/bin/env python3
"""
Inject navigation headers into HTML documentation pages.

Usage: python3 inject-headers.py <output_dir>

This script adds a consistent navigation header to all generated HTML pages,
with appropriate styling and links based on the page location (root, templates, guidelines).
"""

import sys
import re
from pathlib import Path


# Version link placeholder — replaced at build time based on --dev flag
VERSION_LINK_PLACEHOLDER = '{{VERSION_LINK}}'

# Navigation header templates (use placeholder for version link)
HEADERS = {
    'root': f'''<header class="doc-header"><div class="doc-header-brand"><a href="./index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="./index.html">Home</a><a href="./specification.html" class="nav-current">Specification</a><a href="./index.html#metadata-guidelines">Metadata Guidelines</a><a href="./index.html#templates">Templates</a><a href="./sdrf-builder.html">Template Builder</a><a href="./index.html#tools">Tools</a><a href="./sdrf-explorer.html">Explorer</a><a href="./sdrf-editor.html">Editor</a><a href="./index.html#contributors">Contributors</a>{VERSION_LINK_PLACEHOLDER}<a href="https://github.com/bigbio/proteomics-sample-metadata" target="_blank">GitHub</a></nav></header>''',

    'tools': f'''<header class="doc-header"><div class="doc-header-brand"><a href="./index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="./index.html">Home</a><a href="./specification.html">Specification</a><a href="./index.html#metadata-guidelines">Metadata Guidelines</a><a href="./index.html#templates">Templates</a><a href="./sdrf-builder.html">Template Builder</a><a href="./index.html#tools" class="nav-current">Tools</a><a href="./sdrf-explorer.html">Explorer</a><a href="./sdrf-editor.html">Editor</a><a href="./index.html#contributors">Contributors</a>{VERSION_LINK_PLACEHOLDER}<a href="https://github.com/bigbio/proteomics-sample-metadata" target="_blank">GitHub</a></nav></header>''',

    'guidelines': f'''<header class="doc-header"><div class="doc-header-brand"><a href="../index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="../index.html">Home</a><a href="../specification.html">Specification</a><a href="../index.html#metadata-guidelines" class="nav-current">Metadata Guidelines</a><a href="../index.html#templates">Templates</a><a href="../sdrf-builder.html">Template Builder</a><a href="../index.html#tools">Tools</a><a href="../sdrf-explorer.html">Explorer</a><a href="../sdrf-editor.html">Editor</a><a href="../index.html#contributors">Contributors</a>{VERSION_LINK_PLACEHOLDER}<a href="https://github.com/bigbio/proteomics-sample-metadata" target="_blank">GitHub</a></nav></header>''',

    'templates': f'''<header class="doc-header"><div class="doc-header-brand"><a href="../index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="../index.html">Home</a><a href="../specification.html">Specification</a><a href="../index.html#metadata-guidelines">Metadata Guidelines</a><a href="../index.html#templates" class="nav-current">Templates</a><a href="../sdrf-builder.html">Template Builder</a><a href="../index.html#tools">Tools</a><a href="../sdrf-explorer.html">Explorer</a><a href="../sdrf-editor.html">Editor</a><a href="../index.html#contributors">Contributors</a>{VERSION_LINK_PLACEHOLDER}<a href="https://github.com/bigbio/proteomics-sample-metadata" target="_blank">GitHub</a></nav></header>''',

    'sample_guidelines': f'''<header class="doc-header"><div class="doc-header-brand"><a href="./index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="./index.html">Home</a><a href="./specification.html">Specification</a><a href="./index.html#metadata-guidelines" class="nav-current">Metadata Guidelines</a><a href="./index.html#templates">Templates</a><a href="./sdrf-builder.html">Template Builder</a><a href="./index.html#tools">Tools</a><a href="./sdrf-explorer.html">Explorer</a><a href="./sdrf-editor.html">Editor</a><a href="./index.html#contributors">Contributors</a>{VERSION_LINK_PLACEHOLDER}<a href="https://github.com/bigbio/proteomics-sample-metadata" target="_blank">GitHub</a></nav></header>''',

    'templates_guide': f'''<header class="doc-header"><div class="doc-header-brand"><a href="./index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="./index.html">Home</a><a href="./specification.html">Specification</a><a href="./index.html#metadata-guidelines">Metadata Guidelines</a><a href="./index.html#templates" class="nav-current">Templates</a><a href="./sdrf-builder.html">Template Builder</a><a href="./index.html#tools">Tools</a><a href="./sdrf-explorer.html">Explorer</a><a href="./sdrf-editor.html">Editor</a><a href="./index.html#contributors">Contributors</a>{VERSION_LINK_PLACEHOLDER}<a href="https://github.com/bigbio/proteomics-sample-metadata" target="_blank">GitHub</a></nav></header>'''
}


def inject_header(filepath: str, header_html: str, is_dev: bool = False) -> None:
    """Inject navigation header into an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Resolve version link: only show in dev builds (link back to stable)
    if is_dev:
        version_link = '<a href="/" class="version-link">Stable Version</a>'
    else:
        version_link = ''
    resolved_header = header_html.replace(VERSION_LINK_PLACEHOLDER, version_link)

    # Add has-doc-header class to body
    content = re.sub(r'<body class="([^"]*)"', r'<body class="has-doc-header \1"', content)
    content = re.sub(r'<body>', '<body class="has-doc-header">', content)

    # Insert header after opening body tag
    content = re.sub(r'(<body[^>]*>)', r'\1\n' + resolved_header, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def inject_version_link_into_static(filepath: str, is_dev: bool) -> None:
    """Inject a 'Stable Version' link into static HTML pages for dev builds."""
    if not is_dev:
        return  # Stable builds don't show a version link

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Already has a version link — skip
    if 'class="version-link"' in content:
        return

    # Insert "Stable Version" link before the GitHub link
    stable_link = '<a href="/" class="version-link">Stable Version</a>'
    content = content.replace(
        '<a href="https://github.com/bigbio/proteomics-sample-metadata"',
        stable_link + '<a href="https://github.com/bigbio/proteomics-sample-metadata"'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 inject-headers.py <output_dir> [--dev]")
        sys.exit(1)

    is_dev = '--dev' in sys.argv
    output_dir = Path(sys.argv[1])

    print(f"Dev mode: {is_dev}")

    # Inject header into specification.html
    spec_file = output_dir / "specification.html"
    if spec_file.exists():
        print(f"Injecting header into: {spec_file}")
        inject_header(str(spec_file), HEADERS['root'], is_dev)

    # Inject header into tools.html
    tools_file = output_dir / "tools.html"
    if tools_file.exists():
        print(f"Injecting header into: {tools_file}")
        inject_header(str(tools_file), HEADERS['tools'], is_dev)

    # Inject header into sample-guidelines.html
    sg_file = output_dir / "sample-guidelines.html"
    if sg_file.exists():
        print(f"Injecting header into: {sg_file}")
        inject_header(str(sg_file), HEADERS['sample_guidelines'], is_dev)

    # Inject header into templates.html (templates guide)
    tpl_guide = output_dir / "templates.html"
    if tpl_guide.exists():
        print(f"Injecting header into: {tpl_guide}")
        inject_header(str(tpl_guide), HEADERS['templates_guide'], is_dev)

    # Inject headers into metadata-guidelines pages
    guidelines_dir = output_dir / "metadata-guidelines"
    if guidelines_dir.exists():
        for html_file in guidelines_dir.glob("*.html"):
            print(f"Injecting header into: {html_file}")
            inject_header(str(html_file), HEADERS['guidelines'], is_dev)

    # Inject headers into template pages
    templates_dir = output_dir / "templates"
    if templates_dir.exists():
        for html_file in templates_dir.glob("*.html"):
            print(f"Injecting header into: {html_file}")
            inject_header(str(html_file), HEADERS['templates'], is_dev)

    # Inject version link into static HTML pages for dev builds
    for static_page in ["index.html", "quickstart.html", "sdrf-terms.html",
                         "sdrf-explorer.html", "sdrf-editor.html", "sdrf-builder.html"]:
        static_file = output_dir / static_page
        if static_file.exists():
            print(f"Processing version link in: {static_file}")
            inject_version_link_into_static(str(static_file), is_dev)

    print("Header injection complete!")


if __name__ == "__main__":
    main()
