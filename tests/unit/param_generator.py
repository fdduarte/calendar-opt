import os
import sys
import unittest
# Se agrega path a param_generator
path_to_parser = os.path.join(os.getcwd())
sys.path.append(path_to_parser)

from libs.stats_parser import generate_params


class TestStringMethods(unittest.TestCase):
  """Unit test para param generator"""
  def setUp(self):
    self.file_params_small_4 = generate_params('./data/campeonato_prueba.xlsx', 4, 6, 1)
    self.file_params_small_5 = generate_params('./data/campeonato_prueba.xlsx', 5, 6, 1)

  def test_dates(self):
    """Test de fechas"""
    self.assertEqual(self.file_params_small_4.dates, [1, 2, 3, 4, 5, 6])

  def test_teams(self):
    """test de equipos"""
    self.assertEqual(self.file_params_small_4.teams, ['A', 'B', 'C', 'D', 'E', 'F'])

  def test_matches(self):
    """Test de partidos"""
    matches = list(range(1, 19))
    self.assertEqual(self.file_params_small_4.matches, matches)

  def test_available_points(self):
    """Test de puntos disponibles en el campeonato"""
    # Instancia que parte en la fecha 4
    min_points = 3
    max_points = 21
    points = list(range(min_points, max_points + 1))
    self.assertEqual(self.file_params_small_4.available_points, points)

    # Instancia que parte en la fecha 5
    min_points = 4
    max_points = 19
    points = list(range(min_points, max_points + 1))
    self.assertEqual(self.file_params_small_5.available_points, points)

  def test_team_points(self):
    """Test de puntos por equipo al comienzo"""
    # Instancia que parte en la fecha 4
    team_a = 12
    team_b = 3
    team_c = 4
    team_d = 4
    self.assertEqual(self.file_params_small_4.team_points['A'], team_a)
    self.assertEqual(self.file_params_small_4.team_points['B'], team_b)
    self.assertEqual(self.file_params_small_4.team_points['C'], team_c)
    self.assertEqual(self.file_params_small_4.team_points['D'], team_d)

    # Instancia que parte en la fecha 5
    team_a = 13
    team_b = 4
    team_c = 4
    team_d = 7
    self.assertEqual(self.file_params_small_5.team_points['A'], team_a)
    self.assertEqual(self.file_params_small_5.team_points['B'], team_b)
    self.assertEqual(self.file_params_small_5.team_points['C'], team_c)
    self.assertEqual(self.file_params_small_5.team_points['D'], team_d)

  def test_local_patterns(self):
    """Test de parton de localias"""
    # Instancia que parte en la fecha 4
    team_a = set(['010', '100'])
    team_b = set(['101', '011'])
    self.assertEqual(set(self.file_params_small_4.team_local_patterns['A']), team_a)
    self.assertEqual(set(self.file_params_small_4.team_local_patterns['B']), team_b)

    # Instancia que parte en la fecha 5
    team_a = set(['10', '00'])
    team_b = set(['01', '11'])
    self.assertEqual(set(self.file_params_small_5.team_local_patterns['A']), team_a)
    self.assertEqual(set(self.file_params_small_5.team_local_patterns['B']), team_b)


if __name__ == '__main__':
  unittest.main()
