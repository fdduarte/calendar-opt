import itertools
import os
import json
from typing import Tuple
from .logger import log
from .argsparser import args


def _generate_home_away_pattern_string(start_date: int, end_date: int, breaks: int) -> list[str]:
  """
  Función que retorna una lista con todos los patrones posibles
  de 1 y 0 para el largo del campeonato
  """
  log('params', 'generando patrones de localia')

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

  log('params', 'patrones de localia generados')

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

  # Por ultimo, se achican los patrones para respresentar solo las fechas a
  # programar
  patterns = [p[(start_date - second_round_date):] for p in patterns]
  patterns = list(set(patterns))  # eliminar duplicados

  return patterns


def _generate_result_patterns(start_date: int, end_date: int) -> list[str]:
  """
  Funcion que retorna una lista con todos los patrones posibles
  de W, D y L para el largo del campeonato
  """
  log('params', 'generando patrones de resultados')

  length = end_date - start_date + 1
  patterns = ["".join(seq) for seq in itertools.product("WDL", repeat=length)]

  log('params', 'patrones de resultados generados')
  return patterns


def _check_win_patterns(
  patterns: list[str],
  team_pattern: str,
  start_date: int,
  second_round_date: int
) -> list[str]:
  """
  Chequea si se le puede asignar un patrón de resultados
  a un equipo
  """
  team_pattern = team_pattern[(start_date - second_round_date):]
  patterns = [p[(start_date - second_round_date):] for p in patterns]
  patterns = list(set(patterns))

  wins = team_pattern.count('W')
  losses = team_pattern.count('L')
  draws = team_pattern.count('D')

  patterns = list(filter(lambda x: x.count('W') == wins, patterns))
  patterns = list(filter(lambda x: x.count('D') == draws, patterns))
  patterns = list(filter(lambda x: x.count('L') == losses, patterns))

  return patterns


def load_patterns(path: str) -> list[str]:
  """Funcion que carga patrones de un path"""
  with open(path, 'r', encoding='UTF-8') as infile:
    pats = json.load(infile)
  return pats

def save_patterns(path: str, patterns: list[str]):
  """Funcion que guarda patrones de un path"""
  with open(path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(patterns, indent=4))


# To Do: refactor a dos clases -> colapsada de argumentos.
def generate_patterns(
  team_local_patterns: dict[str, str],
  team_win_patterns: dict[str, str],
  second_round_date: int,
  start_date: int,
  end_date: int,
  breaks: int
) -> Tuple[dict[str, list[str]], dict[str, list[str]]]:
  """Funcion que retorna los posibles patrones de localia-visita para un equipo."""
  # Se generan patrones de localía

  # Primero se revisa si estan cacheados
  filename = args.filepath.split(os.path.sep)[1]
  filename = filename.split('.')[0]
  pattern_file_path = os.path.join('data', 'patterns', f"l-{filename}-{start_date}-{breaks}.json")
  
  if os.path.exists(pattern_file_path):
    team_pats = load_patterns(pattern_file_path)
    log('params', 'patrones de localia cargados de cache.')
  else:
    team_pats = {}
    pats = _generate_home_away_pattern_string(second_round_date, end_date, breaks)
    log('params', 'filtrando patrones de localia por equipos.')
    for team in team_local_patterns.keys():
      team_pats[team] = _check_home_away_paterns(
        pats, team_local_patterns[team], 1, start_date, second_round_date)
    log('params', 'patrones de localia por equipos filtrados.')
    save_patterns(pattern_file_path, team_pats)
 
  # Se generan patrones de resultados

  # Primero se revisa si estan cacheados
  pattern_file_path = os.path.join('data', 'patterns', f"r-{filename}-{start_date}-{breaks}.json")

  if os.path.exists(pattern_file_path):
    team_win_pats = load_patterns(pattern_file_path)
    log('params', 'patrones de resultados cargados de cache.')
  else:
    team_win_pats = {}
    win_pats = _generate_result_patterns(second_round_date, end_date)
    log('params', 'filtrando patrones de resultado por equipos.')
    for team in team_local_patterns.keys():
      team_win_pats[team] = _check_win_patterns(
        win_pats, team_win_patterns[team], start_date, second_round_date)
    log('params', 'patrones de resultados por equipos filtrados.')
    save_patterns(pattern_file_path, team_win_pats)
  return team_pats, team_win_pats
