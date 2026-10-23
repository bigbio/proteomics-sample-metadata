#!/usr/bin/env python3
"""Build the SDRF Explorer catalog.

Scans every ``*.sdrf.tsv`` under ``SDRF_DATASETS_DIR`` and writes a compact
``site/sdrf-data.json``. The explorer page fetches that file at runtime.

The weekly "Refresh SDRF explorer catalog" workflow rebuilds this file from
``bigbio/sdrf-annotated-datasets``. Documentation builds reuse the published
snapshot instead of cloning the dataset repository on every push.
"""

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

HEADER_RE = re.compile(r'^#(\w+)=(.+)$')
SKIP_VALUES = frozenset({'', 'not available', 'not applicable', 'na', 'n/a'})
DISEASE_SKIP = frozenset({'normal'})

COLUMN_BUCKETS = (
    ('organism', ('characteristics[organism]',)),
    ('organism_part', ('characteristics[organism part]',)),
    ('disease', ('characteristics[disease]',)),
    ('cell_type', ('characteristics[cell type]',)),
    ('instrument', ('comment[instrument]',)),
    ('label', ('comment[label]',)),
    ('acquisition', ('comment[proteomics data acquisition method]',)),
    ('modification', ('comment[modification parameters]', 'comment[modification identifier]')),
    ('cleavage', ('comment[cleavage agent details]',)),
)


def column_matches(header, pattern):
    """Match an SDRF column without treating a longer name as the shorter one.

    ``characteristics[organism]`` is a prefix of ``characteristics[organism part]``.
    A substring test would count tissues as organisms.
    """
    return header == pattern or header.startswith(pattern + '.')


def parse_ontology_term(value):
    """Return the label from ``NT=Homo sapiens;AC=NCBITaxon:9606`` style values."""
    if not value:
        return ''
    nt_match = re.search(r'NT=([^;]+)', value)
    if nt_match:
        return nt_match.group(1).strip()
    if ';AC=' in value:
        return value.split(';AC=', 1)[0].strip()
    return value.strip()


def usable_term(value, extra_skip=()):
    name = parse_ontology_term(value)
    if not name:
        return None
    lowered = name.lower()
    if lowered in SKIP_VALUES or lowered in extra_skip:
        return None
    return name


def classify_columns(headers):
    classified = []
    for index, header in enumerate(headers):
        for bucket, patterns in COLUMN_BUCKETS:
            if any(column_matches(header, pattern) for pattern in patterns):
                classified.append((index, bucket))
                break
    return classified


def classify_experiment(methods):
    lowered = [method.lower() for method in methods if method]

    def has(*needles):
        return any(any(needle in item for needle in needles) for item in lowered)

    if has('dia', 'data-independent', 'data independent', 'swath', 'diapasef', 'dia-pasef'):
        return 'DIA'
    if has('dda', 'data-dependent', 'data dependent'):
        return 'DDA'
    if has(
        'srm',
        'mrm',
        'prm',
        'selected reaction monitoring',
        'multiple reaction monitoring',
        'parallel reaction monitoring',
    ):
        return 'SRM/MRM'
    return 'Unknown'


def classify_label(labels):
    lowered = [label.lower() for label in labels if label]
    if any('tmt' in label for label in lowered):
        return 'TMT'
    if any('itraq' in label for label in lowered):
        return 'iTRAQ'
    if any('silac' in label for label in lowered):
        return 'SILAC'
    return 'Label-free'


def iter_sdrf_paths(datasets_dir):
    root = os.path.abspath(datasets_dir)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not name.startswith('.')]
        for name in sorted(filenames):
            if name.startswith('.') or not name.endswith('.sdrf.tsv'):
                continue
            yield os.path.join(dirpath, name)


def project_id_for(filepath, datasets_dir):
    relative = os.path.relpath(filepath, datasets_dir)
    parts = relative.split(os.sep)
    if len(parts) >= 2:
        return parts[0]
    return os.path.basename(filepath).replace('.sdrf.tsv', '')


def scan_sdrf_file(filepath):
    """Stream one SDRF file. Returns metadata, row count, and per-bucket terms."""
    metadata = {}
    headers = None
    classified = []
    num_rows = 0
    collected = {bucket: [] for bucket, _patterns in COLUMN_BUCKETS}

    with open(filepath, 'r', encoding='utf-8-sig', errors='replace') as handle:
        for raw_line in handle:
            line = raw_line.rstrip('\r\n')
            if headers is None:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith('#'):
                    match = HEADER_RE.match(stripped)
                    if match:
                        metadata[match.group(1)] = match.group(2).strip()
                    continue
                headers = [cell.strip().lower() for cell in line.split('\t')]
                classified = classify_columns(headers)
                continue
            if not line.strip():
                continue
            num_rows += 1
            values = line.split('\t')
            for index, bucket in classified:
                if index >= len(values):
                    continue
                collected[bucket].append(values[index].strip())

    return {
        'metadata': metadata,
        'headers': headers or [],
        'num_rows': num_rows,
        'collected': collected,
    }


def _unique_terms(values, extra_skip=()):
    terms = []
    seen = set()
    for value in values:
        term = usable_term(value, extra_skip)
        if term and term not in seen:
            seen.add(term)
            terms.append(term)
    return terms


def casefold_total(counter):
    return len({name.lower() for name in counter})


def _count_terms(counter, values, extra_skip=()):
    for value in values:
        term = usable_term(value, extra_skip)
        if term:
            counter[term] += 1


def dataset_entry(project_id, filename, parsed, file_count):
    collected = parsed['collected']
    organisms = _unique_terms(collected['organism'])
    diseases = _unique_terms(collected['disease'], DISEASE_SKIP)
    instruments = _unique_terms(collected['instrument'])
    acquisitions = _unique_terms(collected['acquisition'])
    template = parsed['metadata'].get('template') or 'unknown'
    version = parsed['metadata'].get('version') or 'unknown'

    entry = {
        'id': project_id,
        'file': filename,
        'samples': parsed['num_rows'],
        'columns': len(parsed['headers']),
        'experiment_type': classify_experiment(acquisitions),
        'label_type': classify_label(_unique_terms(collected['label'])),
        'files': file_count,
    }
    if organisms:
        entry['organisms'] = organisms
    if diseases:
        entry['diseases'] = diseases
    if instruments:
        entry['instruments'] = instruments
    if acquisitions:
        entry['acquisition_methods'] = acquisitions
    if template != 'unknown':
        entry['template'] = template
    if version != 'unknown':
        entry['version'] = version
    return entry


def build_catalog(datasets_dir, datasets_repo, datasets_branch):
    if not os.path.isdir(datasets_dir):
        raise SystemExit(f'SDRF_DATASETS_DIR={datasets_dir!r} does not exist or is not a directory.')

    paths = list(iter_sdrf_paths(datasets_dir))
    organisms = Counter()
    organism_parts = Counter()
    diseases = Counter()
    cell_types = Counter()
    instruments = Counter()
    labels = Counter()
    acquisition_methods = Counter()
    modifications = Counter()
    cleavage_agents = Counter()
    pending = []
    total_samples = 0

    counters = {
        'organism': organisms,
        'organism_part': organism_parts,
        'disease': diseases,
        'cell_type': cell_types,
        'instrument': instruments,
        'label': labels,
        'acquisition': acquisition_methods,
        'modification': modifications,
        'cleavage': cleavage_agents,
    }
    extra_skips = {'disease': DISEASE_SKIP}

    for index, filepath in enumerate(paths, start=1):
        parsed = scan_sdrf_file(filepath)
        if parsed['num_rows'] == 0:
            continue
        project_id = project_id_for(filepath, datasets_dir)
        filename = os.path.basename(filepath)
        for bucket, counter in counters.items():
            _count_terms(counter, parsed['collected'][bucket], extra_skips.get(bucket, ()))
        pending.append((project_id, dataset_entry(project_id, filename, parsed, 1)))
        total_samples += parsed['num_rows']
        if index % 500 == 0:
            print(f'Indexed {index} of {len(paths)} SDRF files...', flush=True)

    file_counts = Counter(project_id for project_id, _entry in pending)
    datasets = []
    for project_id, entry in pending:
        entry['files'] = file_counts[project_id]
        datasets.append(entry)
    datasets.sort(key=lambda item: (item['id'], item['file']))
    statistics = {
        'total_datasets': len(datasets),
        'total_accessions': len(file_counts),
        'total_sdrf_files': len(datasets),
        'split_accessions': sum(1 for count in file_counts.values() if count > 1),
        'total_samples': total_samples,
        'organism_count': casefold_total(organisms),
        'instrument_count': casefold_total(instruments),
        'disease_count': casefold_total(diseases),
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source_repository': datasets_repo,
        'source_branch': datasets_branch,
        'source_repository_url': f'https://github.com/{datasets_repo}',
        'organisms': dict(organisms.most_common(50)),
        'organism_parts': dict(organism_parts.most_common(50)),
        'diseases': dict(diseases.most_common(50)),
        'cell_types': dict(cell_types.most_common(50)),
        'instruments': dict(instruments.most_common(50)),
        'labels': dict(labels.most_common(20)),
        'acquisition_methods': dict(acquisition_methods.most_common(20)),
        'modifications': dict(modifications.most_common(30)),
        'cleavage_agents': dict(cleavage_agents.most_common(20)),
        'experiment_types': dict(Counter(item['experiment_type'] for item in datasets)),
        'label_types': dict(Counter(item['label_type'] for item in datasets)),
        'templates': dict(Counter(item.get('template', 'unknown') for item in datasets)),
    }
    return {'statistics': statistics, 'datasets': datasets}


def write_catalog(catalog, output_path):
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(catalog, handle, ensure_ascii=False, separators=(',', ':'))
        handle.write('\n')


def main():
    datasets_repo = os.environ.get('SDRF_DATASETS_REPO', 'bigbio/sdrf-annotated-datasets')
    datasets_branch = os.environ.get('SDRF_DATASETS_BRANCH', 'main')
    datasets_dir = os.environ.get('SDRF_DATASETS_DIR')
    if not datasets_dir:
        raise SystemExit(
            'SDRF_DATASETS_DIR is not set. Point it at a checkout of '
            f'https://github.com/{datasets_repo} (the datasets/ folder). '
            'scripts/refresh-explorer-catalog.sh provisions this.'
        )

    catalog = build_catalog(datasets_dir, datasets_repo, datasets_branch)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sdrf-data.json')
    write_catalog(catalog, output_path)

    stats = catalog['statistics']
    print(
        f"Generated SDRF catalog with {stats['total_accessions']} accessions, "
        f"{stats['total_sdrf_files']} SDRF files, and {stats['total_samples']} samples"
    )
    print(f'Output written to: {output_path} ({os.path.getsize(output_path)} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
