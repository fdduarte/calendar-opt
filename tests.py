import unittest
import json
from modules import ModelStats, PatternGenerator, ChampStats

path_patterns = 'tests/data/patterns.json'
path_data = 'data/Datos.xlsx'

class PatternsTestCase(unittest.TestCase):
  def setUp(self):
    with open(path_patterns, 'r') as infile:
      data = json.load(infile)
    
    self.start_date = 23
    self.end_date = 30
    self.champ_stats = ChampStats(path_data, self.start_date, self.end_date)
    self.pattern_generator = PatternGenerator(self.start_date, self.end_date, 2, self.champ_stats)
    self.patterns = data['patterns']
    self.ids = data['S']

  def test_home_away(self):
    """
    Test para patrones de localia-visita.
    """
    for team in self.champ_stats.teams:
      pat_true = set(self.patterns[team].values())
      patterns, ids = self.pattern_generator.home_away_patterns()
      pat = set(patterns[team].values())
      self.assertEqual(pat_true, pat, msg=team)


if __name__ == '__main__':
  unittest.main()
