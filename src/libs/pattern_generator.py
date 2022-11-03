import itertools
import os
import json
import random
from .logger import log
from .argsparser import args
from .array_tools import remove_duplicates


def _generate_home_away_pattern_string(second_round_date: int, end_date: int) -> list[str]:
  """
  Función que retorna una lista con todos los patrones posibles
  de 1 y 0 para el largo del campeonato
  """
  log('params', 'generando patrones de localia')

  breaks = args.breaks

  length = end_date - second_round_date + 1
  patterns = ["".join(seq) for seq in itertools.product("01", repeat=length)]

  # Se eliminan patrones que rompan maximo dos (0 o 1) seguidos
  patterns_filtered = list(filter(lambda x: x.count('000') == 0 and x.count('111') == 0, patterns))

  # Patrones con 2, 3 o 4 localías
  same_matches_fil = lambda x: x.count('1') in [4, 5, 6]
  patterns_filtered = list(filter(same_matches_fil, patterns_filtered))

  # Patrones deben tener maximo n breaks
  patterns_filtered = list(filter(lambda x: x.count('11') <= breaks, patterns_filtered))
  patterns_filtered = list(filter(lambda x: x.count('00') <= breaks, patterns_filtered))

  log('params', 'patrones de localia generados')

  return patterns_filtered


def filter_local_patterns(
  patterns: list[str],
  team_pattern: str,
  second_round_date: int,
) -> list[str]:
  """
  Dado un patrón de localias de un equipo, filtra los patrones que
  sean validos.
  """
  start_date = args.start_date
  breaks = args.breaks

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
  patterns = remove_duplicates(patterns)

  if args.shuffle_params:
    random.shuffle(patterns)

  return patterns


def load_patterns(path: str) -> dict[str, list[str]]:
  """Funcion que carga patrones de un path"""
  with open(path, 'r', encoding='UTF-8') as infile:
    pats = json.load(infile)
  return pats


def save_patterns(path: str, patterns: dict[str, list[str]]):
  """Funcion que guarda patrones de un path"""
  with open(path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(patterns, indent=4))


def create_local_patterns(team_patterns: dict[str, str], end_date: int) -> dict[str, list[str]]:
  """Función que crea los patrones de localía de un equipo."""
  start_date = args.start_date
  breaks = args.breaks

  second_round_date = int((end_date / 2) + 1)

  filename = args.filepath.split(os.path.sep)[1]
  filename = filename.split('.')[0]
  pattern_file_path = os.path.join('data', 'patterns', f"l-{filename}-{start_date}-{breaks}.json")

  patterns: dict[str, list] = {}

  # Se revisa si patrones estan en el cache
  if os.path.exists(pattern_file_path) and False:
    patterns = load_patterns(pattern_file_path)
    log('params', 'patrones de localia cargados de cache.')
  # Si no estan se crean
  else:
    pats = _generate_home_away_pattern_string(second_round_date, end_date)
    log('params', 'filtrando patrones de localia por equipos.')
    for team in team_patterns.keys():
      patterns[team] = filter_local_patterns(pats, team_patterns[team], second_round_date)
    log('params', 'patrones de localia por equipos filtrados.')
    save_patterns(pattern_file_path, patterns)
  return patterns
