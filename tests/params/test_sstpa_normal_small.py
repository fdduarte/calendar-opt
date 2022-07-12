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


class TestSSTPASmall(unittest.TestCase):
  """Unit test para param generator"""
  def setUp(self):
    args.start_date = 4
    # args.verbose = False
    args.filepath = "data/campeonato_prueba.xlsx"
    generate_params()
    args.start_date = 5
    generate_params()

    with open('./data/json/params_campeonato_prueba_4.json', 'r', encoding='UTF-8') as infile:
      self.small_4_params = json.load(infile)

    path = './data/json/patterns/result_patterns_campeonato_prueba_4.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_4_result_patterns = json.load(infile)

    path = './data/json/patterns/local_patterns_campeonato_prueba_4.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_4_local_patterns = json.load(infile)

    with open('./data/json/params_campeonato_prueba_5.json', 'r', encoding='UTF-8') as infile:
      self.small_5_params = json.load(infile)

    path = './data/json/patterns/result_patterns_campeonato_prueba_5.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_5_result_patterns = json.load(infile)

    path = './data/json/patterns/local_patterns_campeonato_prueba_5.json'
    with open(path, 'r', encoding='UTF-8') as infile:
      self.small_5_local_patterns = json.load(infile)

  def test_teams(self):
    """Test parametro I: equipos del torneo"""
    teams = self.small_4_params['I']
    expected_teams = ['A', 'B', 'C', 'D', 'E', 'F']

    self.assertEqual(teams, expected_teams)

  def test_dates(self):
    """Test parametro F: fechas del torneo"""
    # Partiendo en fecha 4
    dates = self.small_4_params['F']
    expected_dates = [4, 5, 6]

    self.assertEqual(dates, expected_dates)

    # partiendo en fecha 5
    dates = self.small_5_params['F']
    expected_dates = [5, 6]

    self.assertEqual(dates, expected_dates)

  def test_matches(self):
    """Test parametro N: partidos del torneo"""
    # partiendo en fecha 4
    matches = self.small_4_params['N']
    expected_matches = list(range(1, 10))

    self.assertEqual(matches, expected_matches)

    # partiendo en fecha 5
    matches = self.small_5_params['N']
    expected_matches = list(range(1, 7))

    self.assertEqual(matches, expected_matches)

  def test_local_patterns(self):
    """Test de parametro Si: Patrones del localias equipo i"""
    # Instancia que parte en la fecha 4
    expected_team_a = {'A-0', 'A-1'}
    expected_team_b = {'B-0', 'B-1'}

    team_a = self.small_4_params['S']['A']
    team_b = self.small_4_params['S']['B']

    self.assertEqual(set(team_a), expected_team_a)
    self.assertEqual(set(team_b), expected_team_b)

    # Instancia que parte en la fecha 5
    expected_team_a = {'A-0', 'A-1'}
    expected_team_b = {'B-0', 'B-1'}

    team_a = self.small_5_params['S']['A']
    team_b = self.small_5_params['S']['B']

    self.assertEqual(set(team_a), expected_team_a)
    self.assertEqual(set(team_b), expected_team_b)

  def test_result_patterns(self):
    """Test de parametro Gi: Patrones del resultados equipo i"""
    # Instancia que parte en la fecha 4
    expected_team_a = {f"A-{i}" for i in range(6)}
    team_a = self.small_4_params['G']['A']

    self.assertEqual(expected_team_a, set(team_a))

    # Instancia que parte en la fecha 5
    expected_team_a = {f"A-{i}" for i in range(2)}
    team_a = self.small_5_params['G']['A']

    self.assertEqual(expected_team_a, set(team_a))

  def test_points(self):
    """Test parametro T: Puntos disponibles"""
    points = self.small_4_params['T']
    min_points = 3
    max_points = 21
    expected_points = list(range(min_points, max_points + 1))

    self.assertEqual(points, expected_points)

  def test_team_points(self):
    """Test parametro PTi: puntos del equipo i al inicio de la programacion"""
    # Instancia que parte en la fecha 4
    expected_team_a = 12
    expected_team_b = 3
    team_a = self.small_4_params['PI']['A']
    team_b = self.small_4_params['PI']['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

    # Instancia que parte en la fecha 5
    expected_team_a = 13
    expected_team_b = 4
    team_a = self.small_5_params['PI']['A']
    team_b = self.small_5_params['PI']['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

  def test_team_points_discrete(self):
    """Test parametro EBit: 1 ssi el equipo i tiene t puntos"""
    # Instancia que parte en la fecha 4
    expected_team_a = {i: 0 for i in range(3, 22)}
    expected_team_a[12] = 1

    expected_team_b = {i: 0 for i in range(3, 22)}
    expected_team_b[3] = 1

    team_a = self.small_4_params['EB']['A']
    team_a = {int(key): value for key, value in team_a.items()}
    team_b = self.small_4_params['EB']['B']
    team_b = {int(key): value for key, value in team_b.items()}

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

    # Instancia que parte en la fecha 5
    expected_team_a = {i: 0 for i in range(4, 20)}
    expected_team_a[13] = 1

    expected_team_b = {i: 0 for i in range(4, 20)}
    expected_team_b[4] = 1

    team_a = self.small_5_params['EB']['A']
    team_a = {int(key): value for key, value in team_a.items()}
    team_b = self.small_5_params['EB']['B']
    team_b = {int(key): value for key, value in team_b.items()}

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

  def test_team_matches_points(self):
    """Test de parametro Rin: Puntos que gana el equipo i al jugar la fecha n"""
    # Instancia que parte en la fecha 4
    self.assertEqual(self.small_4_params['R']['A']['1'], 3)
    self.assertEqual(self.small_4_params['R']['A']['4'], 0)
    self.assertEqual(self.small_4_params['R']['A']['5'], 0)

    self.assertEqual(self.small_4_params['R']['B']['7'], 1)
    self.assertEqual(self.small_4_params['R']['B']['4'], 0)
    self.assertEqual(self.small_4_params['R']['B']['5'], 1)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.small_5_params['R']['A'][8])
    self.assertEqual(self.small_5_params['R']['A']['1'], 3)
    self.assertEqual(self.small_5_params['R']['A']['4'], 0)

    self.assertRaises(KeyError, lambda: self.small_5_params['R']['B'][7])
    self.assertEqual(self.small_5_params['R']['B']['4'], 0)

  def test_team_localties(self):
    """Test de parametro ELin: 1 ssi el equipo i es local en la fecha n"""
    # Instancia que parte en la fecha 4
    self.assertEqual(self.small_4_params['EL']['A']['1'], 1)
    self.assertEqual(self.small_4_params['EL']['A']['3'], 0)
    self.assertEqual(self.small_4_params['EL']['A']['7'], 0)

    self.assertEqual(self.small_4_params['EL']['C']['8'], 0)
    self.assertEqual(self.small_4_params['EL']['C']['3'], 1)
    self.assertEqual(self.small_4_params['EL']['C']['4'], 1)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.small_5_params['EL']['A']['8'])
    self.assertEqual(self.small_5_params['EL']['A']['1'], 1)
    self.assertEqual(self.small_5_params['EL']['A']['3'], 0)

  def test_team_aways(self):
    """Test de parametro EVin: 1 ssi el equipo i es visita en la fecha n"""
    # Instancia que parte en la fecha 4
    self.assertEqual(self.small_4_params['EV']['A']['1'], 0)
    self.assertEqual(self.small_4_params['EV']['A']['3'], 0)
    self.assertEqual(self.small_4_params['EV']['A']['4'], 1)

    self.assertEqual(self.small_4_params['EV']['C']['8'], 1)
    self.assertEqual(self.small_4_params['EV']['C']['3'], 0)
    self.assertEqual(self.small_4_params['EV']['C']['1'], 0)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.small_5_params['EV']['A']['8'])
    self.assertEqual(self.small_5_params['EV']['A']['1'], 0)
    self.assertEqual(self.small_5_params['EV']['A']['4'], 1)

  def test_result_patterns_points(self):
    """Test de parametro RPgf: cantidad de puntos del patron g en la fecha f"""
    pat_idx = get_pattern_key('A', 'DLW', self.small_4_result_patterns)

    self.assertEqual(self.small_4_params['RP'][pat_idx]['4'], 1)
    self.assertEqual(self.small_4_params['RP'][pat_idx]['5'], 0)
    self.assertEqual(self.small_4_params['RP'][pat_idx]['6'], 3)

  def test_patterns_team_points(self):
    """Test de patrones tal que el equipo tiene k puntos 'GTift'"""
    self.assertEqual(self.small_4_params['GT']['A']['6']['11'], [])
    self.assertEqual(self.small_4_params['GT']['A']['5']['11'], [])
    self.assertEqual(self.small_4_params['GT']['A']['4']['11'], [])

    pats = ['LWD', 'LDW']
    pats_idx = [get_pattern_key('A', pat, self.small_4_result_patterns) for pat in pats]
    self.assertEqual(self.small_4_params['GT']['A']['6']['12'], [])
    self.assertEqual(self.small_4_params['GT']['A']['5']['12'], [])
    self.assertEqual(set(self.small_4_params['GT']['A']['4']['12']), set(pats_idx))

  def test_attractivness(self):
    """Test de ponderadores de atractivo 'Vf'"""
    expected = {'4': 1, '5': 2, '6': 3}

    self.assertEqual(self.small_4_params['V'], expected)


if __name__ == '__main__':
  unittest.main()
