#!/usr/bin/env python3
"""
Build search index for SDRF-Proteomics documentation site.
Extracts content from AsciiDoc files and creates a JSON index for Lunr.js
"""

import json
import os
import re
from pathlib import Path

def extract_text_from_adoc(filepath):
    """Extract plain text content from AsciiDoc file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'^= (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else Path(filepath).stem

    # Remove AsciiDoc formatting
    text = content

    # Remove document attributes
    text = re.sub(r'^:[\w-]+:.*$', '', text, flags=re.MULTILINE)

    # Remove ifdef/endif blocks markers
    text = re.sub(r'^ifdef::.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^endif::.*$', '', text, flags=re.MULTILINE)

    # Remove image references but keep alt text
    text = re.sub(r'image::?\S+\[([^\]]*)\]', r'\1', text)

    # Remove links but keep text
    text = re.sub(r'link:\S+\[([^\]]+)\]', r'\1', text)
    text = re.sub(r'https?://\S+\[([^\]]+)\]', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)

    # Remove anchors
    text = re.sub(r'\[\[[^\]]+\]\]', '', text)
    text = re.sub(r'<<[^>]+>>', '', text)

    # Remove formatting markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'__([^_]+)__', r'\1', text)  # italic
    text = re.sub(r'_([^_]+)_', r'\1', text)  # italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # code
    text = re.sub(r'\+\+\+([^+]+)\+\+\+', r'\1', text)  # passthrough

    # Remove table delimiters
    text = re.sub(r'^\|===.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|', '', text, flags=re.MULTILINE)

    # Remove source blocks markers
    text = re.sub(r'^\[source[^\]]*\]', '', text, flags=re.MULTILINE)
    text = re.sub(r'^----$', '', text, flags=re.MULTILINE)

    # Remove section markers but keep text
    text = re.sub(r'^=+ (.+)$', r'\1', text, flags=re.MULTILINE)

    # Remove admonition markers
    text = re.sub(r'^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):', '', text, flags=re.MULTILINE)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return title, text


def extract_sections(content):
    """Extract section titles from content."""
    sections = re.findall(r'^=+ (.+)$', content, re.MULTILINE)
    return ' '.join(sections)


def extract_keywords(content):
    """Extract potential keywords from content."""
    keywords = set()

    # Extract ontology terms (e.g., EFO, MONDO, NCIT)
    ontology_terms = re.findall(r'\b([A-Z]{2,}(?::[A-Z0-9]+)?)\b', content)
    keywords.update(ontology_terms)

    # Extract characteristics and comments
    characteristics = re.findall(r'characteristics\[([^\]]+)\]', content)
    keywords.update(characteristics)

    comments = re.findall(r'comment\[([^\]]+)\]', content)
    keywords.update(comments)

    # Extract column names
    columns = re.findall(r'_([a-z][a-z_ ]+)_', content)
    keywords.update(columns)

    return ' '.join(keywords)


def build_index(docs_dir, output_file):
    """Build search index from documentation files."""
    index = []

    # Define documents to index (use relative paths for file:// compatibility)
    documents = [
        {
            'file': 'sdrf-proteomics/README.adoc',
            'url': './specification.html',
            'section': 'Core Specification'
        },
        {
            'file': 'sdrf-proteomics/metadata-guidelines/sample-metadata.adoc',
            'url': './metadata-guidelines/sample-metadata.html',
            'section': 'Sample Metadata Guidelines'
        },
        {
            'file': 'sdrf-proteomics/metadata-guidelines/data-file-metadata.adoc',
            'url': './metadata-guidelines/data-file-metadata.html',
            'section': 'Data File Metadata Guidelines'
        },
    ]

    # Add template documents
    templates_dir = Path(docs_dir) / 'templates'
    if templates_dir.exists():
        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir():
                readme = template_dir / 'README.adoc'
                if readme.exists():
                    template_name = template_dir.name
                    documents.append({
                        'file': str(readme.relative_to(docs_dir)),
                        'url': f'./templates/{template_name}.html',
                        'section': f'{template_name.replace("-", " ").title()} Template'
                    })

    # Process each document
    for doc in documents:
        filepath = Path(docs_dir) / doc['file']
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            continue

        print(f"Indexing: {doc['file']}")

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        title, content = extract_text_from_adoc(filepath)
        keywords = extract_keywords(raw_content)

        # Split large documents into chunks for better search results
        chunks = split_into_chunks(content, title, doc['url'], doc['section'], keywords)
        index.extend(chunks)

    # Write JSON index (for server-based fetch)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

    # Write JS index (for direct file:// access without server)
    js_output = output_file.replace('.json', '.js')
    with open(js_output, 'w', encoding='utf-8') as f:
        f.write('// Auto-generated search index - do not edit\n')
        f.write('const SEARCH_INDEX = ')
        json.dump(index, f, indent=2)
        f.write(';\n')

    print(f"Search index built with {len(index)} entries: {output_file}")
    print(f"JavaScript index also created: {js_output}")


def split_into_chunks(content, title, url, section, keywords, max_chunk_size=2000):
    """Split content into smaller chunks for better search results."""
    chunks = []

    # First, add the full document as an entry
    chunks.append({
        'title': title,
        'content': content[:max_chunk_size],
        'url': url,
        'section': section,
        'keywords': keywords
    })

    # Split by sections (== headers)
    section_pattern = r'^(==+)\s+(.+)$'
    lines = content.split('\n')
    current_section_title = title
    current_section_content = []
    current_section_level = 0

    for line in lines:
        match = re.match(section_pattern, line)
        if match:
            # Save previous section if it has content
            if current_section_content and len('\n'.join(current_section_content)) > 100:
                section_text = '\n'.join(current_section_content)
                chunks.append({
                    'title': current_section_title,
                    'content': section_text[:max_chunk_size],
                    'url': url + '#' + slugify(current_section_title),
                    'section': section,
                    'keywords': extract_keywords(section_text)
                })

            current_section_level = len(match.group(1))
            current_section_title = match.group(2)
            current_section_content = []
        else:
            current_section_content.append(line)

    # Save last section
    if current_section_content and len('\n'.join(current_section_content)) > 100:
        section_text = '\n'.join(current_section_content)
        chunks.append({
            'title': current_section_title,
            'content': section_text[:max_chunk_size],
            'url': url + '#' + slugify(current_section_title),
            'section': section,
            'keywords': extract_keywords(section_text)
        })

    return chunks


def slugify(text):
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


if __name__ == '__main__':
    import sys

    docs_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'docs/search-index.json'

    build_index(docs_dir, output_file)
