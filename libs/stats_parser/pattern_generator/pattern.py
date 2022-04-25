import itertools
from typing import Tuple


def _generate_home_away_pattern_string(start_date: int, end_date: int, breaks: int) -> list[str]:
  """
  Función que retorna una lista con todos los patrones posibles
  de 1 y 0 para el largo del campeonato
  """
  length = end_date - start_date + 1
  patterns = ["".join(seq) for seq in itertools.product("01", repeat=length)]

  # Se eliminan patrones que rompan maximo dos (0 o 1) seguidos
  patterns_filtered = list(filter(lambda x: x.count('000') == 0 and x.count('111') == 0, patterns))

  # Patrones con máximo un partido de diferencia
  same_matches_fil = lambda x: x.count('1') == x.count('0') + 1 or x.count('1') == x.count('0') - 1
  patterns_filtered = list(filter(same_matches_fil, patterns_filtered))

  # Patrones deben tener maximo n breaks
  patterns_filtered = list(filter(lambda x: x.count('11') <= breaks, patterns_filtered))
  patterns_filtered = list(filter(lambda x: x.count('00') <= breaks, patterns_filtered))

  return patterns_filtered


def _check_home_away_paterns(
  patterns: list[str],
  team_pattern: str,
  breaks: int,
  start_date: int,
  second_round_date: int
) -> list[str]:
  """
  Dado un patrón de localias de un equipo, filtra los patrones que
  sean validos.
  """
  # Se hace copia de los patrones
  patterns = patterns.copy()

  # Se revisa que tenga cantidad localias y visitas congruentes con la data
  home_left = team_pattern[2:].count('1')
  away_left = team_pattern[2:].count('0')
  patterns = list(filter(lambda x: x.count('1') == home_left, patterns))
  patterns = list(filter(lambda x: x.count('0') == away_left, patterns))

  # Se revisa si arrastra un break o tiene 3 localias/visitas seguidas
  patterns = [f"{team_pattern[0:2]}{p}" for p in patterns]
  patterns = list(filter(lambda x: x.count('000') == 0 and x.count('111') == 0, patterns))
  patterns = [p[1:] for p in patterns]
  patterns = list(filter(lambda x: x.count('11') <= breaks, patterns))
  patterns = list(filter(lambda x: x.count('00') <= breaks, patterns))
  patterns = [p[1:] for p in patterns]

  # Por ultimo, se dejan achican los patrones para respresentar solo las fechas a
  # programar
  patterns = [p[(start_date - second_round_date):] for p in patterns]
  patterns = list(set(patterns))  # eliminar duplicados

  return patterns


def _generate_result_patterns(start_date: int, end_date: int) -> list[str]:
  """
  Funcion que retorna una lista con todos los patrones posibles
  de W, D y L para el largo del campeonato
  """
  length = end_date - start_date + 1
  return ["".join(seq) for seq in itertools.product("WDL", repeat=length)]


def _check_win_patterns(patterns: list[str]) -> list[str]:
  """
  Chequea si se le puede asignar un patrón de resultados 
  a un equipo
  """
  # stub
  return patterns


def generate_patterns(
  team_patterns: dict[str, str],
  second_round_date: int,
  start_date: int,
  end_date: int,
  breaks: int
) -> Tuple[dict[str, list[str]], dict[str, list[str]]]:
  """Funcion que retorna los posibles patrones de localia-visita para un equipo."""
  # Se generan patrones para toda la segunda vuelta.
  pats = _generate_home_away_pattern_string(second_round_date, end_date, breaks)
  win_pats = _generate_result_patterns(start_date, end_date)
  team_pats, team_win_pats = {}, {}
  for team in team_patterns.keys():
    team_pats[team] = _check_home_away_paterns(
      pats, team_patterns[team], 1, start_date, second_round_date)
    team_win_pats[team] = _check_win_patterns(win_pats)
  return team_pats, team_win_pats
