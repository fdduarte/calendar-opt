import os
import json
from ...types import SSTPAParams


# pylint: disable=invalid-name
def parse_params(filepath: str, start_date: int) -> SSTPAParams:
  """Funcion que lee el archivo .json de los parametros"""
  filename = os.path.split(filepath)[1]
  filename_wo_extension = filename.split('.')[0]
  infile_path = f'./data/json/params_{filename_wo_extension}_{start_date}.json'
  with open(infile_path, 'r', encoding='UTF-8') as infile:
    params = json.load(infile)

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

  # RF
  for key in list(params['RF'].keys()):
    u, v, l, i = key.strip('(').strip(')').split(',')
    i = i.strip().strip('\'').strip('\'')
    params['RF'][(int(u), int(v), int(l), i)] = params['RF'][key]

  # Rub, Rlb
  for key in list(params['Rub'].keys()):
    params['Rub'][int(key)] = params['Rub'][key]
    params['Rlb'][int(key)] = params['Rlb'][key]

  return params
