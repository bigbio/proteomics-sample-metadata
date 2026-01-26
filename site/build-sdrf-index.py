#!/usr/bin/env python3
"""
Build SDRF Index and Statistics

This script scans all SDRF files in the repository and generates:
1. A JSON index of all datasets with metadata
2. Pre-computed statistics for the SDRF explorer dashboard

Run this script as part of the CI/CD build process.
"""

import os
import json
import glob
import re
from collections import Counter, defaultdict
from datetime import datetime

def parse_sdrf_file(filepath):
    """Parse an SDRF file and extract metadata and statistics."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    lines = content.strip().split('\n')

    # Parse header metadata
    metadata = {}
    data_start = 0

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('#'):
            match = re.match(r'^#(\w+)=(.+)$', line)
            if match:
                metadata[match.group(1)] = match.group(2)
            data_start = i + 1
        else:
            break

    # Parse column headers
    if data_start >= len(lines):
        return None

    headers = lines[data_start].split('\t')
    headers = [h.strip().lower() for h in headers]
    data_start += 1

    # Parse data rows
    rows = []
    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        if line:
            values = line.split('\t')
            row = {headers[j]: values[j].strip() if j < len(values) else ''
                   for j in range(len(headers))}
            rows.append(row)

    return {
        'metadata': metadata,
        'headers': headers,
        'rows': rows,
        'num_rows': len(rows)
    }

def extract_column_values(rows, column_patterns):
    """Extract values from columns matching patterns."""
    values = []
    for row in rows:
        for col, val in row.items():
            for pattern in column_patterns:
                if pattern in col and val and val.lower() not in ['not available', 'not applicable', 'na', 'n/a', '']:
                    values.append(val)
                    break
    return values

def get_unique_values(rows, column_patterns):
    """Get unique values from columns matching patterns."""
    return list(set(extract_column_values(rows, column_patterns)))

def parse_ontology_term(value):
    """Extract the name from an ontology term value like 'NT=Homo sapiens;AC=NCBITaxon:9606'."""
    if not value:
        return value

    # Check for NT= format
    nt_match = re.search(r'NT=([^;]+)', value)
    if nt_match:
        return nt_match.group(1)

    # Check for AC= format and return the value before it or the whole thing
    if ';AC=' in value:
        return value.split(';AC=')[0]

    return value

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    annotated_dir = os.path.join(base_dir, 'annotated-projects')
    templates_dir = os.path.join(base_dir, 'sdrf-proteomics')

    # Find all SDRF files
    sdrf_files = glob.glob(os.path.join(annotated_dir, '**', '*.sdrf.tsv'), recursive=True)

    # Statistics counters
    total_samples = 0
    organisms = Counter()
    organism_parts = Counter()
    diseases = Counter()
    cell_types = Counter()
    instruments = Counter()
    labels = Counter()
    acquisition_methods = Counter()
    modifications = Counter()
    cleavage_agents = Counter()

    # Dataset index
    datasets = []

    for filepath in sorted(sdrf_files):
        # Skip hidden files
        if '/.' in filepath:
            continue

        rel_path = os.path.relpath(filepath, base_dir)

        # Extract project ID from path
        parts = rel_path.split(os.sep)
        if len(parts) >= 2:
            project_id = parts[1]
        else:
            project_id = os.path.basename(filepath).replace('.sdrf.tsv', '')

        # Parse the file
        parsed = parse_sdrf_file(filepath)
        if not parsed or parsed['num_rows'] == 0:
            continue

        rows = parsed['rows']
        headers = parsed['headers']
        num_samples = parsed['num_rows']
        total_samples += num_samples

        # Extract organisms
        org_values = extract_column_values(rows, ['characteristics[organism]'])
        for org in org_values:
            org_name = parse_ontology_term(org)
            if org_name:
                organisms[org_name] += 1

        # Extract organism parts
        org_part_values = extract_column_values(rows, ['characteristics[organism part]'])
        for op in org_part_values:
            op_name = parse_ontology_term(op)
            if op_name and op_name.lower() not in ['not available', 'not applicable']:
                organism_parts[op_name] += 1

        # Extract diseases
        disease_values = extract_column_values(rows, ['characteristics[disease]'])
        for d in disease_values:
            d_name = parse_ontology_term(d)
            if d_name and d_name.lower() not in ['not available', 'not applicable', 'normal']:
                diseases[d_name] += 1

        # Extract cell types
        cell_type_values = extract_column_values(rows, ['characteristics[cell type]'])
        for ct in cell_type_values:
            ct_name = parse_ontology_term(ct)
            if ct_name and ct_name.lower() not in ['not available', 'not applicable']:
                cell_types[ct_name] += 1

        # Extract instruments
        instr_values = extract_column_values(rows, ['comment[instrument]'])
        for instr in instr_values:
            instr_name = parse_ontology_term(instr)
            if instr_name:
                instruments[instr_name] += 1

        # Extract labels
        label_values = extract_column_values(rows, ['comment[label]'])
        for lbl in label_values:
            lbl_name = parse_ontology_term(lbl)
            if lbl_name:
                labels[lbl_name] += 1

        # Extract acquisition methods
        acq_values = extract_column_values(rows, ['comment[proteomics data acquisition method]'])
        for acq in acq_values:
            acq_name = parse_ontology_term(acq)
            if acq_name:
                acquisition_methods[acq_name] += 1

        # Extract modifications
        mod_values = extract_column_values(rows, ['comment[modification parameters]', 'comment[modification identifier]'])
        for mod in mod_values:
            mod_name = parse_ontology_term(mod)
            if mod_name:
                modifications[mod_name] += 1

        # Extract cleavage agents
        cleav_values = extract_column_values(rows, ['comment[cleavage agent details]'])
        for cleav in cleav_values:
            cleav_name = parse_ontology_term(cleav)
            if cleav_name:
                cleavage_agents[cleav_name] += 1

        # Get unique values for this dataset
        dataset_organisms = list(set([parse_ontology_term(o) for o in get_unique_values(rows, ['characteristics[organism]'])]))
        dataset_diseases = list(set([parse_ontology_term(d) for d in get_unique_values(rows, ['characteristics[disease]'])
                                     if parse_ontology_term(d) and parse_ontology_term(d).lower() not in ['not available', 'not applicable', 'normal']]))
        dataset_instruments = list(set([parse_ontology_term(i) for i in get_unique_values(rows, ['comment[instrument]'])]))
        dataset_labels = list(set([parse_ontology_term(l) for l in get_unique_values(rows, ['comment[label]'])]))
        dataset_acq = list(set([parse_ontology_term(a) for a in get_unique_values(rows, ['comment[proteomics data acquisition method]'])]))

        # Determine experiment type (DDA/DIA/SRM)
        exp_type = 'Unknown'
        for acq in dataset_acq:
            if acq:
                acq_lower = acq.lower()
                if 'dia' in acq_lower or 'data-independent' in acq_lower or 'data independent' in acq_lower:
                    exp_type = 'DIA'
                    break
                elif 'dda' in acq_lower or 'data-dependent' in acq_lower or 'data dependent' in acq_lower:
                    exp_type = 'DDA'
                    break
                elif 'srm' in acq_lower or 'mrm' in acq_lower or 'prm' in acq_lower or 'selected reaction monitoring' in acq_lower or 'multiple reaction monitoring' in acq_lower or 'parallel reaction monitoring' in acq_lower:
                    exp_type = 'SRM/MRM'
                    break

        # Determine labeling type
        label_type = 'Label-free'
        for lbl in dataset_labels:
            if lbl:
                lbl_lower = lbl.lower()
                if 'tmt' in lbl_lower:
                    label_type = 'TMT'
                    break
                elif 'itraq' in lbl_lower:
                    label_type = 'iTRAQ'
                    break
                elif 'silac' in lbl_lower:
                    label_type = 'SILAC'
                    break
                elif 'label free' in lbl_lower or 'label-free' in lbl_lower:
                    label_type = 'Label-free'

        # Create dataset entry
        dataset_entry = {
            'id': project_id,
            'file': os.path.basename(filepath),  # Alias for filename (used by quickstart search)
            'filename': os.path.basename(filepath),
            'path': rel_path,
            'github_url': f'https://github.com/bigbio/proteomics-metadata-standard/blob/master/{rel_path}',
            'raw_url': f'https://raw.githubusercontent.com/bigbio/proteomics-metadata-standard/master/{rel_path}',
            'num_samples': num_samples,
            'num_columns': len(headers),
            'organisms': [o for o in dataset_organisms if o],
            'diseases': [d for d in dataset_diseases if d],
            'instruments': [i for i in dataset_instruments if i],
            'acquisition_methods': [a for a in dataset_acq if a],  # Used by quickstart search
            'experiment_type': exp_type,
            'label_type': label_type,
            'template': parsed['metadata'].get('template', 'unknown'),
            'version': parsed['metadata'].get('version', 'unknown')
        }

        datasets.append(dataset_entry)

    # Build statistics summary
    statistics = {
        'total_datasets': len(datasets),
        'total_samples': total_samples,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'organisms': dict(organisms.most_common(50)),
        'organism_parts': dict(organism_parts.most_common(50)),
        'diseases': dict(diseases.most_common(50)),
        'cell_types': dict(cell_types.most_common(50)),
        'instruments': dict(instruments.most_common(50)),
        'labels': dict(labels.most_common(20)),
        'acquisition_methods': dict(acquisition_methods.most_common(20)),
        'modifications': dict(modifications.most_common(30)),
        'cleavage_agents': dict(cleavage_agents.most_common(20)),
        'experiment_types': dict(Counter(d['experiment_type'] for d in datasets)),
        'label_types': dict(Counter(d['label_type'] for d in datasets)),
        'templates': dict(Counter(d['template'] for d in datasets))
    }

    # Build final output
    output = {
        'statistics': statistics,
        'datasets': datasets
    }

    # Write output
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sdrf-data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated SDRF index with {len(datasets)} datasets and {total_samples} total samples")
    print(f"Output written to: {output_path}")

    # Print summary
    print(f"\nTop 10 organisms:")
    for org, count in organisms.most_common(10):
        print(f"  {org}: {count}")

    print(f"\nExperiment types:")
    for exp_type, count in Counter(d['experiment_type'] for d in datasets).items():
        print(f"  {exp_type}: {count}")

    print(f"\nLabel types:")
    for label_type, count in Counter(d['label_type'] for d in datasets).items():
        print(f"  {label_type}: {count}")

if __name__ == '__main__':
    main()
