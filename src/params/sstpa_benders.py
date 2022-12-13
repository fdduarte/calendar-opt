import json
import os
from itertools import product
from ..libs import sheet_parser
from ..libs.argsparser import args
from ..libs import pattern_generator
from ..libs.timer import timer
from ..types import SSTPAParams
from ..libs.logger import log
from .helpers import (
    get_team_local_patterns,
    get_team_matches_points,
    get_team_points,
    get_team_localties
)


# pylint: disable=invalid-name
@timer.timeit('gen params benders')
def generate_params():
  """
  Funcion encargada de crear un archivo .json con los parametros de
  la instancia
  """
  log('params', 'comenzando generación de parámetros')
  filepath = args.filepath
  start_date = args.start_date
  w1, w2 = args.w1, args.w2

  teams_data = sheet_parser.read_teams_file(filepath)
  results_data = sheet_parser.read_results_file(filepath)

  # I: equipos del campeonato
  I = list(teams_data.keys())

  # P: posiciones que pueden alcanzar los equipos
  P = list(range(1, len(I) + 1))

  # F: fechas del campeonato
  F = list({match.date for match in results_data})
  F = list(filter(lambda x: x >= start_date, F))

  # N: Partidos
  # partidos por fecha
  matches_per_date = int(len(I) / 2)
  dates_to_program = F[-1] - start_date + 1

  N = list(range(1, dates_to_program * matches_per_date + 1))

  # se generan los patrones originales de los equipos
  team_original_patterns = get_team_local_patterns(teams_data, results_data, F)

  log("params", "comenzando la generación de patrones")
  # se genera diccionario con equipos y sus respectivos patrones.
  teams_local_patterns = pattern_generator.create_local_patterns(team_original_patterns, F[-1])

  # Si: S[equipo]
  # Patrones de localias asociados al equipo i. 'Si' es un conjunto de
  # indices que corresponden a cada patron. Para acceder al detalle
  # de un patron, revisar archivo correspondiente con detalle.
  log("params", "generación de patrones terminada\n")

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

  # PIi: PI[equipo]
  # cantidad de puntos del equipo i la fecha anterior a la primera
  # de las fechas que quedan por jugar
  PI = get_team_points(teams_data, results_data, start_date, F)

  # Lista de los puntos disponibles en el torneo
  dates_number = F[-1] - start_date + 1

  # XInf: XI[partido, fecha]
  # Si el partido n se juega en la fecha f inicialmente
  XI = {n: {f: 0 for f in F} for n in N}
  for match in results_data:
    if match.number in N and match.date in F:
      XI[match.number][match.date] = 1

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

  # Lsf: L[patron][fecha]
  # 1 Si el patron s indica que la fecha f
  # es local
  # 0 en otro caso
  L = {}
  for i in I:
    for s in S[i]:
      L[s] = {f: 1 if local_patterns_full[s][f - start_date] == "1" else 0 for f in F}

  # Vf: V[fecha]
  # Ponderación de atractivo de fecha f
  V = {f: f - F[0] + 1 for f in F}

  # Mi: M[equipo]
  # Cantidád máxima de puntos que puede alcanzar el equipo i + 1.
  M = {i: PI[i] + dates_number * 3 + 1 for i in I}
  # M = {i: 10**10 for i in I}

  # Ruvfi: R[posición, posición, fecha, equipo]
  # peso en la función objetivo
  RF = {}
  for u, v, f, i in product(P, P, F, I):
    ud = abs(u - ((len(I) - 1) / 2 + 1.5))
    ld = abs(v - ((len(I) - 1) / 2 + 1.5))
    date_pond = (f - min(F) + 1) ** 2
    m_pond = 1
    if u == 1:
      m_pond += 0.3
    if v == len(I):
      m_pond += 0.2
    pen_pond = 1
    if u == v:
      pen_pond = 0
    final_pond = date_pond * pen_pond * m_pond
    RF[str((u, v, f, i))] = final_pond * (w1 * (max(ud, ld))**2 + w2 * (v - u)**2 + 1)

  params: SSTPAParams = {
      'I': I,
      'F': F,
      'N': N,
      'S': S,
      'T': T,
      'PI': PI,
      'EB': EB,
      'R': R,
      'EL': EL,
      'EV': EV,
      'L': L,
      'V': V,
      'M': M,
      'XI': XI,
      'P': P,
      'RF': RF,
  }

  filename = os.path.split(filepath)[1]
  filename_wo_extension = filename.split('.')[0]
  outfile_path = f'./data/json/params_{filename_wo_extension}_{start_date}.json'
  with open(outfile_path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(params, indent=4))

  outfile_path = f'./data/json/patterns/local_patterns_{filename_wo_extension}_{start_date}.json'
  with open(outfile_path, 'w', encoding='UTF-8') as outfile:
    outfile.write(json.dumps(local_patterns_full, indent=4))
