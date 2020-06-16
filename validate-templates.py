#!/usr/bin/env python

import os
import sys
import re
from sdrf_pipelines.sdrf import sdrf, sdrf_schema
DIR = 'templates'
MAP = {
    'cell-line': sdrf_schema.cell_lines_schema,
    'default': sdrf_schema.default_schema,
    'human': sdrf_schema.human_schema,
    'nonvertebrates': sdrf_schema.nonvertebrates_chema,
    'plants': sdrf_schema.plants_chema,
    'vertebrates': sdrf_schema.vertebrates_chema,
}


def main():
    allerrors = 0
    for template_file in os.listdir(DIR):
        errors = 0
        try:
            temp_name = re.match(r'^sdrf-([\w-]+)\.tsv', template_file).group(1)
        except AttributeError:
            print('Could not parse template file name: ', template_file)
            allerrors += 1
            continue
        try:
            schema = MAP[temp_name]
        except KeyError:
            print('What is this template for? ', temp_name)
            continue
        with open(os.path.join(DIR, template_file)) as f:
            fields = set(next(f).strip().split('\t'))
        seen = set()
        for column in schema.columns + sdrf_schema.default_schema.columns + sdrf_schema.mass_spectrometry_schema.columns:
            if column._optional and column.name in fields:
                print('Optional column {} present in {}!'.format(column.name, template_file))
                # errors += 1
            if not column._optional:
                if column.name not in fields:
                    print('Mandatory column {} absent in {}!'.format(column.name, template_file))
                    errors += 1
                else:
                    seen.add(column.name)
        if seen != fields:
            print('Extra columns in {}: {}'.format(template_file, ', '.join(fields - seen)))
            errors += 1
        allerrors += errors
        if not errors:
            print('All good with', template_file)
        print()
    return errors


if __name__ == '__main__':
    sys.exit(main())
