#!/usr/bin/env python

import os
import glob
import sys
import argparse
from sdrf_pipelines.sdrf import sdrf, sdrf_schema
DIR = 'annotated-projects'
projects = os.listdir(DIR)


def get_template(df):
    """Extract organism information and pick a template for validation"""
    organisms = df['characteristics[organism]'].unique()
    templates = []
    if 'homo sapiens' in organisms:
        templates.append(sdrf_schema.HUMAN_TEMPLATE)
    return templates


def main(args):
    status = []
    for project in projects:
        sdrf_files = glob.glob(os.path.join(DIR, project, '*.tsv'))
        errors = []
        if sdrf_files:
            result = 'OK'
            for sdrf_file in sdrf_files:
                df = sdrf.SdrfDataFrame.parse(sdrf_file)
                errors = df.validate(sdrf_schema.DEFAULT_TEMPLATE)
                if errors:
                    result = 'Failed basic validation'
                    break
                else:
                    templates = get_template(df)
                    if templates:
                        for t in templates:
                            errors = df.validate(t)
                            if errors:
                                result = 'Failed validation for {}'.format(t)
                                break
                    if errors:
                        break
                    errors = df.validate(sdrf_schema.MASS_SPECTROMETRY)
                    if errors:
                        result = 'Failed mass spectrometry validation'
                        break
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
