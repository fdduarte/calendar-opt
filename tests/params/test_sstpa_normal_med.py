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

    args.start_date = 10
    args.end_date = 18
    args.verbose = False
    args.filepath = f"data/{filename}.xlsx"
    generate_params()
    args.start_date = 11
    generate_params()

    with open(f'./data/json/params_{filename}_10.json', 'r', encoding='UTF-8') as infile:
      self.small_10_params = json.load(infile)

    path = f'./data/json/patterns/result_patterns_{filename}_10.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_10_result_patterns = json.load(infile)

    path = f'./data/json/patterns/local_patterns_{filename}_10.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_10_local_patterns = json.load(infile)

    with open(f'./data/json/params_{filename}_11.json', 'r', encoding='UTF-8') as infile:
      self.small_11_params = json.load(infile)

    path = f'./data/json/patterns/result_patterns_{filename}_11.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_11_result_patterns = json.load(infile)

    path = f'./data/json/patterns/local_patterns_{filename}_11.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_11_local_patterns = json.load(infile)

  def test_teams(self):
    """Test parametro I: equipos del torneo"""
    teams = self.small_10_params['I']
    expected_teams = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'}

    self.assertEqual(set(teams), expected_teams)

  def test_points(self):
    """Test parametro T: Puntos disponibles"""
    # Instancia que parte en la fecha 10
    points = self.small_10_params['T']
    min_points = 5
    max_points = 48
    expected_points = set(range(min_points, max_points + 1))

    self.assertEqual(set(points), expected_points)
    # Instancia que parte en la fecha 7
    points = self.small_11_params['T']
    min_points = 5
    max_points = 48
    expected_points = set(range(min_points, max_points + 1))

    self.assertEqual(set(points), expected_points)

  def test_team_points(self):
    """Test parametro PTi: puntos del equipo i al inicio de la programacion"""
    # Instancia que parte en la fecha 10
    expected_team_a = 21
    expected_team_b = 10
    team_a = self.small_10_params['PI']['A']
    team_b = self.small_10_params['PI']['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

    # Instancia que parte en la fecha 11
    expected_team_a = 24
    expected_team_b = 13
    team_a = self.small_11_params['PI']['A']
    team_b = self.small_11_params['PI']['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

  def test_team_localties(self):
    """Test de parametro ELin: 1 ssi el equipo i es local en el partido n"""
    # Instancia que parte en la fecha 6
    self.assertEqual(self.small_10_params['EL']['A']['1'], 0)
    self.assertEqual(self.small_10_params['EL']['J']['4'], 1)
    self.assertEqual(self.small_10_params['EL']['C']['42'], 1)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.small_11_params['EL']['C']['42'])
    self.assertEqual(self.small_11_params['EL']['A']['1'], 0)
    self.assertEqual(self.small_11_params['EL']['J']['4'], 1)

  def test_local_patterns(self):
    """Test de parametro Si: Patrones del localias equipo i"""
    # Instancia que parte en la fecha 6
    expected_team_a = 21

    team_a = self.small_10_params['S']['A']

    self.assertEqual(len(team_a), expected_team_a)

    # equipos tienen mas de 1 patron
    for i in self.small_10_params['I']:
      print(i, len(self.small_10_params['S'][i]))
      self.assertGreater(len(self.small_10_params['S'][i]), 1)


if __name__ == '__main__':
  unittest.main()
