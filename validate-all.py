#!/usr/bin/env python

import os
import glob
import sys
import argparse
import logging
import itertools

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


def count_errors(errors):
    return sum(err._error_type == logging.ERROR for err in errors)


def count_warnings(errors):
    return sum(err._error_type == logging.WARN for err in errors)


def collapse_warnings(errors):
    warnings = [err for err in errors if err._error_type == logging.WARN]
    messages = []
    if warnings:
        key = lambda w: (w.column, w.message)
        for keyv, group in itertools.groupby(sorted(warnings, key=key), key=key):
            col, message = keyv
            gr = list(group)
            w = min(gr, key=lambda w: w.row)
            messages.append('{} validation warnings collapsed on column {} (first row {}, value {}): {}'.format(
                len(gr), col, w.row, w.value, message))
    return messages


def main(args):
    status = []
    for project in projects:
        sdrf_files = glob.glob(os.path.join(DIR, project, 'sdrf*'))
        error_types = set()
        error_files = set()
        errors = []
        if sdrf_files:
            result = 'OK'
            for sdrf_file in sdrf_files:
                df = sdrf.SdrfDataFrame.parse(sdrf_file)
                err = df.validate(sdrf_schema.DEFAULT_TEMPLATE)
                errors.extend(err)
                if count_errors(err):
                    error_types.add('basic')
                else:
                    templates = get_template(df)
                    if templates:
                        for t in templates:
                            err = df.validate(t)
                            errors.extend(err)
                            if count_errors(err):
                                error_types.add('{} template'.format(t))
                    err = df.validate(sdrf_schema.MASS_SPECTROMETRY)
                    errors.extend(err)
                    if count_errors(err):
                        error_types.add('mass spectrometry')
                if count_errors(errors):
                    error_files.add(os.path.basename(sdrf_file))
            if error_types:
                result = 'Failed ' + ', '.join(error_types) + ' validation ({})'.format(', '.join(error_files))
            elif count_warnings(errors):
                result = 'OK (with warnings)'
        else:
            result = 'SDRF file not found'
        status.append(result)
        if args.verbose == 2:
            for err in errors:
                print(err)
        elif args.verbose:
            for w in collapse_warnings(errors):
                print(w)
            for err in errors:
                if err._error_type == logging.ERROR:
                    print(err)
        print(project, result, sep='\t')
    errors = 0
    warnings = 0
    print('Final results:')
    for project, result in zip(projects, status):
        if result != 'OK' and result != 'SDRF file not found':
            if result[:2] == 'OK':
                warnings += 1
            else:
                errors += 1
    print('Total: {} projects checked, {} had validation errors, {} had validation warnings.'.format(
        len(projects), errors, warnings))
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', help='Print all errors. If specified twice, print all warnings.')
    args = parser.parse_args()
    out = main(args)
    sys.exit(out)
