import os
import sys
import unittest
import json
from typing import Optional
# Se agrega path a param_generator
path_to_parser = os.path.join(os.getcwd())
sys.path.append(path_to_parser)

from src.libs.argsparser import args
from src.params.sstpa_normal import generate_params


def get_pattern_key(team: str, pattern: str, patterns: dict[str, str]) -> Optional[str]:
  """
  Funcion que dado un diccionario de index, pattern,
  retorna el indice de un patrón
  """
  for idx, pat in patterns.items():
    if pat == pattern and team in idx:
      return idx
  return None


class TestSSTPAMed(unittest.TestCase):
  """Unit test para param generator"""
  def setUp(self):
    filename = "campeonato_prueba_10eq"

    args.start_date = 6
    args.end_date = 10
    args.verbose = False
    args.filepath = f"data/{filename}.xlsx"
    generate_params()
    args.start_date = 7
    generate_params()

    with open(f'./data/json/params_{filename}_6.json', 'r', encoding='UTF-8') as infile:
      self.small_4_params = json.load(infile)

    path = f'./data/json/patterns/result_patterns_{filename}_6.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_4_result_patterns = json.load(infile)

    path = f'./data/json/patterns/local_patterns_{filename}_6.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_4_local_patterns = json.load(infile)

    with open(f'./data/json/params_{filename}_7.json', 'r', encoding='UTF-8') as infile:
      self.small_5_params = json.load(infile)

    path = f'./data/json/patterns/result_patterns_{filename}_7.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_5_result_patterns = json.load(infile)

    path = f'./data/json/patterns/local_patterns_{filename}_7.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_5_local_patterns = json.load(infile)

  def test_teams(self):
    """Test parametro I: equipos del torneo"""
    teams = self.small_4_params['I']
    expected_teams = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'}

    self.assertEqual(set(teams), expected_teams)

if __name__ == '__main__':
  unittest.main()
