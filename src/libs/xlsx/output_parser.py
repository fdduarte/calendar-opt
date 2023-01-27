import pandas as pd
from .sheet_parser import read_teams_file, read_results_file


def create_output(infile_name, outfile_name, solfile_name):
  """Genera un archivo xlsx de output similar al del input con datos del .sol"""
  teams_sheet = read_teams_file(infile_name)
  results_sheet = read_results_file(infile_name)
  # xvars = read_sol_file(solfile_name)

  # write sheet 1
  # write sheet 2
  print(teams_sheet)

# def write_sheet


if __name__ == '__main__':
  create_output('', 'outfile_name', 'solfile_name')
