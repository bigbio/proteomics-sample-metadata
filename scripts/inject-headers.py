#!/usr/bin/env python3
"""
Inject navigation headers into HTML documentation pages.

Usage: python3 inject-headers.py <output_dir>

This script adds a consistent navigation header to all generated HTML pages,
with appropriate styling and links based on the page location (root, templates, guidelines).
"""

import sys
import re
import os
from pathlib import Path


# Navigation header templates
HEADERS = {
    'root': '''<header class="doc-header"><div class="doc-header-brand"><a href="./index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="./index.html">Home</a><a href="./specification.html" class="nav-current">Specification</a><a href="./index.html#metadata-guidelines">Metadata Guidelines</a><a href="./index.html#templates">Templates</a><a href="./index.html#tools">Tools</a><a href="./sdrf-explorer.html">Explorer</a><a href="./index.html#contributors">Contributors</a><a href="/dev/" class="version-link">Dev Version</a><a href="https://github.com/bigbio/proteomics-metadata-standard" target="_blank">GitHub</a></nav></header>''',

    'tools': '''<header class="doc-header"><div class="doc-header-brand"><a href="./index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="./index.html">Home</a><a href="./specification.html">Specification</a><a href="./index.html#metadata-guidelines">Metadata Guidelines</a><a href="./index.html#templates">Templates</a><a href="./index.html#tools" class="nav-current">Tools</a><a href="./sdrf-explorer.html">Explorer</a><a href="./index.html#contributors">Contributors</a><a href="/dev/" class="version-link">Dev Version</a><a href="https://github.com/bigbio/proteomics-metadata-standard" target="_blank">GitHub</a></nav></header>''',

    'guidelines': '''<header class="doc-header"><div class="doc-header-brand"><a href="../index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="../index.html">Home</a><a href="../specification.html">Specification</a><a href="../index.html#metadata-guidelines" class="nav-current">Metadata Guidelines</a><a href="../index.html#templates">Templates</a><a href="../index.html#tools">Tools</a><a href="../sdrf-explorer.html">Explorer</a><a href="../index.html#contributors">Contributors</a><a href="/dev/" class="version-link">Dev Version</a><a href="https://github.com/bigbio/proteomics-metadata-standard" target="_blank">GitHub</a></nav></header>''',

    'templates': '''<header class="doc-header"><div class="doc-header-brand"><a href="../index.html">SDRF-Proteomics</a></div><nav class="doc-header-nav"><a href="../index.html">Home</a><a href="../specification.html">Specification</a><a href="../index.html#metadata-guidelines">Metadata Guidelines</a><a href="../index.html#templates" class="nav-current">Templates</a><a href="../index.html#tools">Tools</a><a href="../sdrf-explorer.html">Explorer</a><a href="../index.html#contributors">Contributors</a><a href="/dev/" class="version-link">Dev Version</a><a href="https://github.com/bigbio/proteomics-metadata-standard" target="_blank">GitHub</a></nav></header>'''
}


def inject_header(filepath: str, header_html: str) -> None:
    """Inject navigation header into an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add has-doc-header class to body
    content = re.sub(r'<body class="([^"]*)"', r'<body class="has-doc-header \1"', content)
    content = re.sub(r'<body>', '<body class="has-doc-header">', content)

    # Insert header after opening body tag
    content = re.sub(r'(<body[^>]*>)', r'\1\n' + header_html, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 inject-headers.py <output_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])

    # Inject header into specification.html
    spec_file = output_dir / "specification.html"
    if spec_file.exists():
        print(f"Injecting header into: {spec_file}")
        inject_header(str(spec_file), HEADERS['root'])

    # Inject header into tool-support.html
    tools_file = output_dir / "tool-support.html"
    if tools_file.exists():
        print(f"Injecting header into: {tools_file}")
        inject_header(str(tools_file), HEADERS['tools'])

    # Inject headers into metadata-guidelines pages
    guidelines_dir = output_dir / "metadata-guidelines"
    if guidelines_dir.exists():
        for html_file in guidelines_dir.glob("*.html"):
            print(f"Injecting header into: {html_file}")
            inject_header(str(html_file), HEADERS['guidelines'])

    # Inject headers into template pages
    templates_dir = output_dir / "templates"
    if templates_dir.exists():
        for html_file in templates_dir.glob("*.html"):
            print(f"Injecting header into: {html_file}")
            inject_header(str(html_file), HEADERS['templates'])

    print("Header injection complete!")


if __name__ == "__main__":
    main()
