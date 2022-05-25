import os
import json
from ...types import SSTPAParams
from ...libs.argsparser import args


# pylint: disable=invalid-name
def parse_params():
  """Funcion que lee el archivo .json de los parametros"""
  filepath = args.filepath
  start_date = args.start_date

  filename = os.path.split(filepath)[1]
  filename_wo_extension = filename.split('.')[0]
  infile_path = f'./data/json/params_{filename_wo_extension}_{start_date}.json'
  with open(infile_path, 'r', encoding='UTF-8') as infile:
    params: SSTPAParams = json.load(infile)

  # R
  for key in params['R'].keys():
    params['R'][key] = {int(k): v for k, v in params['R'][key].items()}

  # L
  for key in params['L'].keys():
    params['L'][key] = {int(k): v for k, v in params['L'][key].items()}

  # EL
  for key in params['EL'].keys():
    params['EL'][key] = {int(k): v for k, v in params['EL'][key].items()}

  # EV
  for key in params['EV'].keys():
    params['EV'][key] = {int(k): v for k, v in params['EV'][key].items()}

  return params
