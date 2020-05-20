#!/usr/bin/env python

import os
import glob
import sys
import argparse
from sdrf_pipelines.sdrf import sdrf, sdrf_schema
from sdrf_pipelines.zooma import ols
DIR = 'annotated-projects'
projects = os.listdir(DIR)
client = ols.OlsClient()


def retry(func):
    def wrapper(*args, **kwargs):
        for i in range(5):
            try:
                return func(*args, **kwargs)
            except KeyError:
                pass
    return wrapper


@retry
def get_ancestors(iri):
    return client.get_ancestors('ncbitaxon', iri)


def get_template(df):
    """Extract organism information and pick a template for validation"""
    organisms = df['characteristics[organism]'].unique()
    templates = []

    for org in organisms:
        org = org.lower()
        if org == 'homo sapiens':
            templates.append(sdrf_schema.HUMAN_TEMPLATE)
        else:
            hit = client.besthit(org, ontology='ncbitaxon')
            if hit is not None:
                iri = hit['iri']
                ancestors = get_ancestors(iri)
                if ancestors is None:
                    print('Could not get ancestors for {}!'.format(org))
                    ancestors = []
                labels = {a['label'] for a in ancestors}
                if 'Gnathostomata <vertebrates>' in labels:
                    templates.append(sdrf_schema.VERTEBRATES_TEMPLATE)
                elif 'Metazoa' in labels:
                    templates.append(sdrf_schema.NON_VERTEBRATES_TEMPLATE)
                elif 'Viridiplantae' in labels:
                    templates.append(sdrf_schema.PLANTS_TEMPLATE)
    return templates


def main(args):
    status = []
    for project in projects:
        sdrf_files = glob.glob(os.path.join(DIR, project, 'sdrf*'))
        error_types = set()
        errors = []
        if sdrf_files:
            result = 'OK'
            for sdrf_file in sdrf_files:
                df = sdrf.SdrfDataFrame.parse(sdrf_file)
                errors = df.validate(sdrf_schema.DEFAULT_TEMPLATE)
                if errors:
                    error_types.add('basic')
                else:
                    templates = get_template(df)
                    if templates:
                        for t in templates:
                            errors.extend(df.validate(t))
                            if errors:
                                error_types.add('{} template'.format(t))
                    errors.extend(df.validate(sdrf_schema.MASS_SPECTROMETRY))
                    if errors:
                        error_types.add('mass spectrometry')
            if error_types:
                result = 'Failed ' + ', '.join(error_types) + ' validation'
        else:
            result = 'SDRF file not found'
        status.append(result)
        if args.verbose:
            for err in errors:
                print(err)
        print(project, result, sep='\t')
    errors = 0
    print('Final results:')
    for project, result in zip(projects, status):
        if result != 'OK':
            errors += 1
    print('Total: {} projects checked, {} had validation errors.'.format(len(projects), errors))
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Print all errors.')
    args = parser.parse_args()
    out = main(args)
    sys.exit(out)
