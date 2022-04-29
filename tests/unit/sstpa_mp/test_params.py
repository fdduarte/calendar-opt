import os
import sys
import unittest
from typing import Optional
# Se agrega path a param_generator
path_to_parser = os.path.join(os.getcwd())
sys.path.append(path_to_parser)

from libs.stats_parser import generate_params
from models.sstpa_mp.params import get_params


def get_pattern_key(team: str, pattern: str, patterns: dict[str, str]) -> Optional[str]:
  """
  Funcion que dado un diccionario de index, pattern,
  retorna el indice de un patrón
  """
  for idx, pat in patterns.items():
    if pat == pattern and team in idx:
      return idx
  return None


class TestStringMethods(unittest.TestCase):
  """Unit test para param generator"""
  def setUp(self):
    file_params_small_4 = generate_params('./data/campeonato_prueba.xlsx', 4, 6, 1)
    file_params_small_5 = generate_params('./data/campeonato_prueba.xlsx', 5, 6, 1)

    self.model_params_small_4 = get_params(4, 6, file_params_small_4)
    self.model_params_small_5 = get_params(5, 6, file_params_small_5)

  def test_teams(self):
    """Test para los equipos 'I' del modelo"""
    teams = self.model_params_small_4.teams
    expected_teams = ['A', 'B', 'C', 'D', 'E', 'F']

    self.assertEqual(teams, expected_teams)

  def test_dates(self):
    """Test para las fechas 'F'"""
    # Partiendo en fecha 4
    dates = self.model_params_small_4.dates
    expected_dates = [4, 5, 6]

    self.assertEqual(dates, expected_dates)

    # partiendo en fecha 5
    dates = self.model_params_small_5.dates
    expected_dates = [5, 6]

    self.assertEqual(dates, expected_dates)

  def test_matches(self):
    """Test para partidos 'N'"""
    # partiendo en fecha 4
    matches = self.model_params_small_4.matches
    expected_matches = list(range(1, 10))

    self.assertEqual(matches, expected_matches)

    # partiendo en fecha 5
    matches = self.model_params_small_5.matches
    expected_matches = list(range(1, 7))

    self.assertEqual(matches, expected_matches)

  def test_points(self):
    """Test de puntos 'T'"""
    points = self.model_params_small_4.points
    min_points = 3
    max_points = 21
    expected_points = list(range(min_points, max_points + 1))

    self.assertEqual(points, expected_points)

  def test_team_points(self):
    """Test de los puntos de cada equipo al inicio 'PTi'"""
    # Instancia que parte en la fecha 4
    expected_team_a = 12
    expected_team_b = 3
    team_a = self.model_params_small_4.team_points['A']
    team_b = self.model_params_small_4.team_points['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

    # Instancia que parte en la fecha 5
    expected_team_a = 13
    expected_team_b = 4
    team_a = self.model_params_small_5.team_points['A']
    team_b = self.model_params_small_5.team_points['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

  def test_team_points_discrete(self):
    """Test de los puntos de cada equipo discreto 'EBit'"""
    # Instancia que parte en la fecha 4
    expected_team_a = {i: 0 for i in range(3, 22)}
    expected_team_a[12] = 1

    expected_team_b = {i: 0 for i in range(3, 22)}
    expected_team_b[3] = 1

    team_a = self.model_params_small_4.team_points_discrete['A']
    team_b = self.model_params_small_4.team_points_discrete['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

    # Instancia que parte en la fecha 5
    expected_team_a = {i: 0 for i in range(4, 20)}
    expected_team_a[13] = 1

    expected_team_b = {i: 0 for i in range(4, 20)}
    expected_team_b[4] = 1

    team_a = self.model_params_small_5.team_points_discrete['A']
    team_b = self.model_params_small_5.team_points_discrete['B']

    self.assertEqual(expected_team_a, team_a)
    self.assertEqual(expected_team_b, team_b)

  def test_local_patterns(self):
    """Test de patrones de cada equipo 'Si'"""
    # Instancia que parte en la fecha 4
    expected_team_a = {'A-0', 'A-1'}
    expected_team_b = {'B-0', 'B-1'}

    team_a = self.model_params_small_4.local_patterns['indexes']['A']
    team_b = self.model_params_small_4.local_patterns['indexes']['B']

    self.assertEqual(set(team_a), expected_team_a)
    self.assertEqual(set(team_b), expected_team_b)

    # Instancia que parte en la fecha 5
    expected_team_a = {'A-0', 'A-1'}
    expected_team_b = {'B-0', 'B-1'}

    team_a = self.model_params_small_5.local_patterns['indexes']['A']
    team_b = self.model_params_small_5.local_patterns['indexes']['B']

    self.assertEqual(set(team_a), expected_team_a)
    self.assertEqual(set(team_b), expected_team_b)

  def test_result_patterns(self):
    """Test de patrones de resultado de cada equipo 'Gi'"""
    # Instancia que parte en la fecha 4
    expected_team_a = {f"A-{i}" for i in range(6)}
    team_a = self.model_params_small_4.result_patterns['indexes']['A']

    self.assertEqual(expected_team_a, set(team_a))

  def test_team_matches_points(self):
    """Test de los puntos de equipos 'Rin'"""
    # Instancia que parte en la fecha 4
    self.assertEqual(self.model_params_small_4.team_matches_points['A'][1], 3)
    self.assertEqual(self.model_params_small_4.team_matches_points['A'][4], 0)
    self.assertEqual(self.model_params_small_4.team_matches_points['A'][5], 0)

    self.assertEqual(self.model_params_small_4.team_matches_points['B'][7], 1)
    self.assertEqual(self.model_params_small_4.team_matches_points['B'][4], 0)
    self.assertEqual(self.model_params_small_4.team_matches_points['B'][5], 1)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.model_params_small_5.team_matches_points['A'][8])
    self.assertEqual(self.model_params_small_5.team_matches_points['A'][1], 3)
    self.assertEqual(self.model_params_small_5.team_matches_points['A'][4], 0)

    self.assertRaises(KeyError, lambda: self.model_params_small_5.team_matches_points['B'][7])
    self.assertEqual(self.model_params_small_5.team_matches_points['B'][4], 0)

  def test_team_localties(self):
    """Test de localias de equipos 'ELin'"""
    # Instancia que parte en la fecha 4
    self.assertEqual(self.model_params_small_4.team_localties['A'][1], 1)
    self.assertEqual(self.model_params_small_4.team_localties['A'][3], 0)
    self.assertEqual(self.model_params_small_4.team_localties['A'][7], 0)

    self.assertEqual(self.model_params_small_4.team_localties['C'][8], 0)
    self.assertEqual(self.model_params_small_4.team_localties['C'][3], 1)
    self.assertEqual(self.model_params_small_4.team_localties['C'][4], 1)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.model_params_small_5.team_localties['A'][8])
    self.assertEqual(self.model_params_small_5.team_localties['A'][1], 1)
    self.assertEqual(self.model_params_small_5.team_localties['A'][3], 0)

  def test_team_aways(self):
    """Test de localias de equipos 'EVin'"""
    # Instancia que parte en la fecha 4
    self.assertEqual(self.model_params_small_4.team_aways['A'][1], 0)
    self.assertEqual(self.model_params_small_4.team_aways['A'][3], 0)
    self.assertEqual(self.model_params_small_4.team_aways['A'][4], 1)

    self.assertEqual(self.model_params_small_4.team_aways['C'][8], 1)
    self.assertEqual(self.model_params_small_4.team_aways['C'][3], 0)
    self.assertEqual(self.model_params_small_4.team_aways['C'][1], 0)

    # Instancia que parte en la fecha 5
    self.assertRaises(KeyError, lambda: self.model_params_small_5.team_aways['A'][8])
    self.assertEqual(self.model_params_small_5.team_aways['A'][1], 0)
    self.assertEqual(self.model_params_small_5.team_aways['A'][4], 1)

  def test_local_pattern_localties(self):
    """Test de localias de patrones 'Lsf'"""
    pat_idx = get_pattern_key('A', '010', self.model_params_small_4.local_patterns['full_patterns'])

    self.assertEqual(self.model_params_small_4.local_pattern_localties[pat_idx][4], 0)
    self.assertEqual(self.model_params_small_4.local_pattern_localties[pat_idx][5], 1)
    self.assertEqual(self.model_params_small_4.local_pattern_localties[pat_idx][6], 0)

  def test_result_patterns_points(self):
    """Test de puntos de un patron en una fecha 'RPgf'"""
    pat_idx = get_pattern_key(
      'A', 'DLW', self.model_params_small_4.result_patterns['full_patterns']
    )

    self.assertEqual(self.model_params_small_4.result_patterns_points[pat_idx][4], 1)
    self.assertEqual(self.model_params_small_4.result_patterns_points[pat_idx][5], 0)
    self.assertEqual(self.model_params_small_4.result_patterns_points[pat_idx][6], 3)

  def test_patterns_team_points(self):
    """Test de patrones tal que el equipo tiene k puntos 'GTift'"""
    pat_team_points = self.model_params_small_4.pattern_team_points
    patterns = self.model_params_small_4.result_patterns['full_patterns']
    self.assertEqual(pat_team_points['A'][6][11], [])
    self.assertEqual(pat_team_points['A'][5][11], [])
    self.assertEqual(pat_team_points['A'][4][11], [])

    pats = ['LWD', 'LDW']
    pats_idx = [get_pattern_key('A', pat, patterns) for pat in pats]
    self.assertEqual(pat_team_points['A'][6][12], [])
    self.assertEqual(pat_team_points['A'][5][12], [])
    self.assertEqual(pat_team_points['A'][4][12], pats_idx)

  def test_attractivness(self):
    """Test de ponderadores de atractivo 'Vf'"""
    expected = {4: 1, 5: 2, 6: 3}

    self.assertEqual(self.model_params_small_4.attractiveness, expected)


if __name__ == '__main__':
  unittest.main()
