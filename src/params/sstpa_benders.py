import json
import os
from ..libs import sheet_parser
from ..libs.argsparser import args
from ..libs import pattern_generator
from ..libs.timer import timer
from ..types import SSTPAParams
from .helpers import (
  get_team_local_patterns,
  get_team_matches_points,
  get_team_points,
  get_team_result_patterns,
  get_team_localties
)


# pylint: disable=invalid-name
@timer.timeit('gen params benders')
def generate_params():
  """
  Funcion encargada de crear un archivo .json con los parametros de
  la instancia
  """
  print('comenzando generación de parámetros')
  filepath = args.filepath
  start_date = args.start_date
  breaks = args.breaks

  teams_data = sheet_parser.read_teams_file(filepath)
  results_data = sheet_parser.read_results_file(filepath)

  # I: equipos del campeonato
  I = list(teams_data.keys())

  # F: fechas del campeonato
  F = list({match.date for match in results_data})
  F = list(filter(lambda x: x >= start_date, F))

  # N: Partidos
  # partidos por fecha
  matches_per_date = int(len(I) / 2)
  dates_to_program = F[-1] - start_date + 1

  N = list(range(1, dates_to_program * matches_per_date + 1))

  # se generan los patrones originales de los equipos
  second_round_date = int((F[-1] / 2) + 1)

  team_original_local_patterns = get_team_local_patterns(teams_data, results_data, F)
  team_original_result_patterns = get_team_result_patterns(teams_data, results_data, F)

  # se genera diccionario con equipos y sus respectivos patrones.
  teams_local_patterns, teams_result_patterns = pattern_generator.generate_patterns(
    team_original_local_patterns, team_original_result_patterns,
    second_round_date, start_date, F[-1], breaks)

  # Si: S[equipo]
  # Patrones de localias asociados al equipo i. 'Si' es un conjunto de
  # indices que corresponden a cada patron. Para acceder al detalle
  # de un patron, revisar archivo correspondiente con detalle.

  # A cada patron se le asigna un indice.
  local_patterns_full = {}
  S: dict[str, list[str]] = {}
  for i in I:
    S[i] = []
    team_local_patterns = teams_local_patterns[i]
    for idx, pattern in enumerate(team_local_patterns):
      local_patterns_full[f"{i}-{idx}"] = pattern
      S[i].append(f"{i}-{idx}")

  # Gi: G[equipo]
  # Patrones de resultados asociados al equipo i
  result_patterns_full = {}
  G: dict[str, list[str]] = {}
  for i in I:
    G[i] = []
    team_result_patterns = teams_result_patterns[i]
    for idx, pattern in enumerate(team_result_patterns):
      result_patterns_full[f"{i}-{idx}"] = pattern
      G[i].append(f"{i}-{idx}")

  # PIi: PI[equipo]
  # cantidad de puntos del equipo i la fecha anterior a la primera
  # de las fechas que quedan por jugar
  PI = get_team_points(teams_data, results_data, start_date, F)

  # Lista de los puntos disponibles en el torneo
  dates_number = F[-1] - start_date + 1

  # T: Puntos
  _max_points = max(PI.values()) + dates_number * 3
  _min_points = min(PI.values())
  T = list(range(_min_points, _max_points + 1))

  # EBit: EB[equipo][puntos]
  # 1 si equipo i tiene t puntos la fecha anterior a la primera
  # de las fechas que quedan por jugar
  # 0 en otro caso
  EB = {i: {t: 1 if PI[i] == t else 0 for t in T} for i in I}

  # Rin: R[equipo][partido]:
  # Puntos que gana el equipo i al jugar partido n
  matches_points = get_team_matches_points(teams_data, results_data, F)
  R: dict[str, dict[int, int]] = {}
  for i in I:
    R[i] = {}
    for n in N:
      if n in matches_points[i].keys():
        R[i][n] = matches_points[i][n]
      else:
        R[i][n] = 0

  team_localties = get_team_localties(teams_data, results_data, F)

  # ELin: EL[equipo][partido]
  # 1 Si el equipo i es local en el partido n
  # 0 En otro caso
  EL: dict[str, dict[int, int]] = {}
  for i in I:
    EL[i] = {}
    for n in N:
      if n in team_localties[i].keys() and team_localties[i][n] == 'L':
        EL[i][n] = 1
      else:
        EL[i][n] = 0

  # EVin: EV[equipo][partido]
  # 1 Si el equipo i es visita en el partido n
  # 0 En otro caso
  EV: dict[str, dict[int, int]] = {}
  for i in I:
    EV[i] = {}
    for n in N:
      if n in team_localties[i].keys() and team_localties[i][n] == 'V':
        EV[i][n] = 1
      else:
        EV[i][n] = 0

  # RPgf: RP[patron][fecha]
  # Cantidad de puntos asociados al resultado
  # del patrón g en la fecha f
  char_to_int = {"W": 3, "L": 0, "D": 1}
  RP: dict[str, dict[int, int]] = {}
  for g, pattern in result_patterns_full.items():
    RP[g] = {}
    for f in F:
      value = char_to_int[pattern[f - F[0]]]
      RP[g][f] = value

  # Lsf: L[patron][fecha]
  # 1 Si el patron s indica que la fecha f
  # es local
  # 0 en otro caso
  L = {}
  for i in I:
    for s in S[i]:
      L[s] = {f: 1 if local_patterns_full[s][f - start_date] == "1" else 0 for f in F}

  # GTift: G[equipo][fecha][puntos]
  # Patrones tales que el equipo i tiene
  # t puntos en la fecha f
  def get_team_points_with_pattern(team, pattern, date):
    points = PI[team]
    for curr_date in range(0, date - F[0] + 1):
      if pattern[curr_date] == 'W':
        points += 3
      if pattern[curr_date] == 'D':
        points += 1
    return points

  GT: dict[str, dict[int, dict[int, list[str]]]] = {}
  for i in I:
    GT[i] = {}
    for f in F:
      GT[i][f] = {}
      for t in T:
        GT[i][f][t] = []
      for pattern_idx in G[i]:
        pattern = result_patterns_full[pattern_idx]
        t = get_team_points_with_pattern(i, pattern, f)
        GT[i][f][t].append(pattern_idx)

  # Vf: V[fecha]
  # Ponderación de atractivo de fecha f
  V = {f: f - F[0] + 1 for f in F}

  params: SSTPAParams = {
    'I': I,
    'F': F,
    'N': N,
    'S': S,
    'G': G,
    'T': T,
    'PI': PI,
    'EB': EB,
    'R': R,
    'EL': EL,
    'EV': EV,
    'RP': RP,
    'GT': GT,
    'L': L,
    'V': V
  }

  filename = os.path.split(filepath)[1]
  filename_wo_extension = filename.split('.')[0]
  outfile_path = f'./data/json/params_{filename_wo_extension}_{start_date}.json'
  with open(outfile_path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(params, indent=4))

  outfile_path = f'./data/json/patterns/result_patterns_{filename_wo_extension}_{start_date}.json'
  with open(outfile_path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(result_patterns_full, indent=4))

  outfile_path = f'./data/json/patterns/local_patterns_{filename_wo_extension}_{start_date}.json'
  with open(outfile_path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(local_patterns_full, indent=4))