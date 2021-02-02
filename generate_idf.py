#!/usr/bin/env python
# The following script generates the IDF for all the SDRF projects annotated.
# TODO:  One open problem in the script is that when the factor value in the sdrf is annotated with UpperCase its annotate the Factor value in the IDF in lowercase which throws an error in the validation script simple_validate_magetab.pl

import argparse
import glob
import os
import re
import sys

import requests
from sdrf_pipelines.sdrf import sdrf

DIR = 'annotated-projects'
PROJECTS = os.listdir(DIR)


class ProjectIDF:
  """
  Class for IDF project information
  """

  def __init__(self, title, description, submission_date, publication_date, data_protocol, sample_protocol, submitters,
               lab_heads, instruments_str, softwares_str):
    self.description = clean_whitespaces_return(description)
    self.title = clean_whitespaces_return(title)
    self.submission_date = submission_date
    self.publication_date = publication_date
    self.data_protocol = clean_whitespaces_return(data_protocol)
    self.sample_protocol = clean_whitespaces_return(sample_protocol)
    self.submitter = submitters
    self.lab_head = lab_heads
    self.instruments = instruments_str
    self.softwares = softwares_str

  def title(self):
    return self.title

  def description(self):
    return self.description

  def sample_protocol(self, sample_protocol):
    self.sample_protocol = sample_protocol

  def data_protocol(self, data_protocol):
    self.data_protocol = data_protocol

  def __str__(self) -> str:
    project_str = 'Title --- {title}'.format(title=self.title)
    return project_str


def clean_whitespaces_return(original_str: str):
  """
  Clean white spcaes and tabs, replace with whitespaces.
  :param original_str: original string
  :return: clean string
  """
  original_str = original_str.replace("\n", " ").replace("\t", " ").replace("\r", " ")
  return original_str


def parse_persons(person_list, role):
  """
  Parse person from PRIDE API into submitter or PI
  :param person_list:
  :return:
  """
  persons = []
  for person_pride in person_list:
    person = {}
    person['affiliation'] = clean_whitespaces_return(person_pride['affiliation'])
    person['email'] = person_pride['email']
    p = re.compile(r'^(\s+)?(Mr(\.)?|Mrs(\.)?)?(?P<FIRST_NAME>.+)(\s+)(?P<LAST_NAME>.+)$', re.IGNORECASE)
    m = p.match(person_pride['name'])
    if (m != None):
      person['firstname'] = m.group('FIRST_NAME')
      person['lastname'] = m.group('LAST_NAME')
    person['role'] = role
    persons.append(person)
  return persons


def read_from_pride(px_accession):
  """
  Read the PRIDE dataset from the API using the PX Accession
  :param px_accession:  PX Accession
  :return: ProjectIDF
  """
  url = 'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/' + px_accession
  print(px_accession)
  try:
    r = requests.get(url)
    project_json = r.json()

    submitters = parse_persons(project_json['submitters'], 'submitter')
    lab_heads = parse_persons(project_json['labPIs'], 'principal investigator')
    instruments = []
    for instrument in project_json['instruments']:
      instruments.append(instrument['name'])
    softwares = []
    for software in project_json['softwares']:
      softwares.append(software['name'])

    return ProjectIDF(project_json['title'], project_json['projectDescription'], project_json['submissionDate'],
                      project_json['publicationDate'], project_json['dataProcessingProtocol'],
                      project_json['sampleProcessingProtocol'], submitters, lab_heads, ';'.join(instruments),
                      ';'.join(softwares))
  except:
    raise RuntimeError('Project error when retrieving PX: ' + px_accession)


def print_idf(id_px, sdrf_file_path, sdrf):
  """
  Write in the folder of the project the IDF with the general project metadata.
  :param id_px: ProjectIDF project with the information to be written in IDF file
  :param sdrf_file_path: Path where the IDF will be written
  :param sdrf: sdrf to extract the experimental factors
  :return:
  """
  selected_columns = [e for e in sdrf.columns if 'factor value' in e]
  factor_values = []
  for column in selected_columns:
    m = re.search(r"\[.*?]", column)
    factor_values.append(m.group(0).replace("[", "").replace("]", ""))

  path_id = sdrf_file_path.split("/");
  folder = path_id[0]
  project = path_id[1]
  sdrf_name = path_id[2]
  idf_path = folder + "/" + project + "/" + project + ".idf.tsv"
  with open(idf_path, 'w') as writer:
    writer.write("MAGE-TAB Version\t1.1\n")
    writer.write("Investigation Title\t" + id_px.title + '\n')
    writer.write("Experiment Description\t" + id_px.description + '\n')
    writer.write('\n')

    writer.write('Date of Experiment\t' + id_px.submission_date + '\n')
    writer.write('Public Release Date\t' + id_px.publication_date + '\n')
    writer.write('\n')

    writer.write('Protocol Name\tP-MTAB-Sample-' + project + '\tP-MTAB-Data-' + project + '\n')
    writer.write('Protocol Type\tsample collection protocol\tdata analysis protocol\n')
    writer.write('Protocol Description\t' + id_px.sample_protocol + '\t' + id_px.data_protocol + '\n')
    writer.write('Protocol Parameters\n')
    if bool(id_px.instruments.strip()):
      writer.write('Protocol Hardware\t' + id_px.instruments + '\n')
    else:
      writer.write('Protocol Hardware\n')
    if bool(id_px.softwares.strip()):
      writer.write('Protocol Software\t\t' + id_px.softwares + '\n')
    else:
      writer.write('Protocol Software\n')
    writer.write('Protocol Contact\n')
    writer.write('\n')

    last_names = ''
    first_names = ''
    emails = ''
    affiliations = ''
    roles = ''
    persons = id_px.submitter + id_px.lab_head
    for a in persons:
      last_names = last_names + "\t" + a['lastname']
      first_names = first_names + "\t" + a['firstname']
      emails = emails + "\t" + a['email']
      affiliations = affiliations + '\t' + a['affiliation']
      roles = roles + '\t' + a['role']
    writer.write('Person Last Name' + last_names + '\n')
    writer.write('Person First Name' + first_names + '\n')
    writer.write('Person Mid Initials\n')
    writer.write('Person Email' + emails + '\n')
    writer.write('Person Phone\n')
    writer.write('Person Fax\n')
    writer.write('Person Affiliation' + affiliations + '\n')
    writer.write('Person Address\n')
    writer.write('Person Roles' + roles + '\n')
    writer.write('Person Roles Term Source REF\n')
    writer.write('Person Roles Term Accession Number\n')
    writer.write('\n')

    if len(factor_values) > 0:
      writer.write("Experimental Factor Name\t" + "\t".join(factor_values) + "\n")
    else:
      writer.write("Experimental Factor Name\n")
    writer.write('\n')

    writer.write('SDRF File\t' + sdrf_name + '\n')
    writer.write('Comment[SDRF-Proteomics version]\t1.1\n')
    writer.write('Comment[TemplateType]\t' + 'proteomics' + '\n')
    writer.write('\n')

    writer.write('Comment[ProteomeXchange accession number]\t' + project + '\n')

    writer.close()


def annotate_idf(sdrf, sdrf_file_path, px_accession):
  """
  This function takes a px accession and annotate the corresponding idf.
  :param sdrf_file_path:
  :param sdrf: SDRF representation to read the Experimental Factors
  :param px_accession: PX accession
  :return:
  """
  error_message = set()
  try:
    id_px = read_from_pride(px_accession)
    print(id_px)
    print_idf(id_px, sdrf_file_path, sdrf)
  except RuntimeError as e:
    error_message.add(e.args)
  return error_message


def main(args):
  statuses = []
  if args.project:
    projects = args.project
  else:
    projects = PROJECTS
  try:
    i = 0
    for project in projects:
      sdrf_files = glob.glob(os.path.join(DIR, project, '*.sdrf.tsv'))
      if sdrf_files:
        result = 'OK'
        status = 0
        for sdrf_file_path in sdrf_files:
          print(sdrf_file_path)
          df = sdrf.SdrfDataFrame.parse(sdrf_file_path)
          px_accession = sdrf_file_path.split('/')[1]
          error_types = annotate_idf(df, sdrf_file_path, px_accession)
          if len(error_types):
            statuses.append(2)
      i = i + 1
  except KeyboardInterrupt:
    pass
  finally:
    errors = sum(s == 2 for s in statuses)
    warnings = sum(s == 1 for s in statuses)
    print('Final results:')
    print(f'Total: {i} of {len(projects)} projects checked, '
          f'{errors} had validation errors, {warnings} had validation warnings.')
  return errors


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', '--verbose', action='count',
                      help='Print all errors. If specified twice, print all warnings.')
  parser.add_argument('project', nargs='*')
  args = parser.parse_args()
  out = main(args)
  sys.exit(out)
