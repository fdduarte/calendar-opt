import itertools
import random
import math


class PatternGenerator():
  # Types
  ValidPatterns = dict[str, dict[str, str]]

  def __init__(self, start_date: int, end_date: int, breaks: int, champ_stats: any):
    self.start_date = start_date
    self.end_date = end_date
    self.champ_stats = champ_stats
    self.breaks = breaks

  def _generate_home_away_pattern_string(self):
    """
    Función que retorna una lista con todos los patrones posibles
    de 1 y 0 para el largo del campeonato
    """
    length = self.end_date - self.start_date + 1
    return ["".join(seq) for seq in itertools.product("01", repeat=length)]

  def _check_home_away_paterns(self, patterns: list[str], original_pattern: str) -> list[str]:
    """
    Dado un el patrón de localias de un equipo, filtra los patrones que
    sean validos.
    """
    # Patrones completos
    p = [original_pattern[:self.start_date - 1] + pattern for pattern in patterns]

    # Se eliminan 3 localias o visitas seguidas
    p = list(filter(lambda x: x.count('000') == 0 and x.count('111') == 0, p))
    p = list(filter(lambda x: x.count('1') == x.count('0'), p))

    # Se revisa segunda vuelta
    p = [pat[self.start_date - 2:] for pat in p]

    # Se eliminan patrones que sobrepasen los breaks
    p = list(filter(lambda x: x.count('11') <= self.breaks, p))
    p = list(filter(lambda x: x.count('00') <= self.breaks, p))
    
    # Se rescata patron
    return [pat[1:] for pat in p]

  def home_away_patterns(self) -> tuple[ValidPatterns, dict[str, str]]:
    """
    Retorna un diccionario con los patrones de localias de los equipos
    """
    valid_patterns = {}
    S = {}
    all_patterns = self._generate_home_away_pattern_string()

    for team in self.champ_stats.teams.keys():
      patterns = all_patterns.copy()
      original_pattern = ''
      for i in range(1, self.end_date + 1):
        original_pattern += str(self.champ_stats.team_home_away[team][i])
      patterns = self._check_home_away_paterns(patterns, original_pattern)
      valid_patterns[team] = {f'{team}-{i}': pat for i, pat in enumerate(patterns, start=1)}
      S[team] = [f'{team}-{i + 1}' for i in range(len(patterns))]

    return valid_patterns, S

  def _generate_result_patterns(self) -> list[str]:
    """
    Función que retorna una lista con todos los patrones posibles
    de W, D y L para el largo del campeonato
    """
    length = self.end_date - self.start_date + 1
    return ["".join(seq) for seq in itertools.product("WDL", repeat=length)]

  def _check_results_patterns(self, stats: dict[str, int], patterns: list[str]) -> list[str]:
    p = list(filter(lambda x: x.count('W') == stats['wins'], patterns))
    p = list(filter(lambda x: x.count('D') == stats['draws'], p))
    p = list(filter(lambda x: x.count('L') == stats['loses'], p))
    return p

  def results_patterns(self):
    patterns = {}
    for team, stats in self.champ_stats.teams_results.items():
      pats = self._generate_result_patterns()
      pats = self._check_results_patterns(stats, pats)
      patterns[team] = pats
    return patterns
