import sys
import os
from libs.stats_parser import FileParams


def get_params(start_date: int, end_date: int, file_params):
  """
  Generador de parámetros para SSTPA V3.

  Args:
  -- pattern_generator: Instancia de generador de patrones
  -- champ_stats: Instancia de ChampStats

  Return:
  -- stats: (dict) diccionario con parametros del modelo
  """

  # PARAMETROS DE INSTANCIA

  FECHAINI = start_date
  FECHAFIN = end_date
  TARGET = 10
  BREAKS = 2
  # print(f"\nPARAMS:\nFechas: {FECHAINI}-{FECHAFIN}\nTARGET:
  # {TARGET}\nFILTER: {FILTER} (thrs {THRESHOLD})\nBREAKS: {BREAKS}")

  #################
  # * CONJUNTOS * #
  #################

  # I: Equipos
  I = list(champ_stats.teams.keys())

  # N: Partidos
  N = list(range((FECHAINI - 1) * int(len(I) / 2) + 1, FECHAFIN  * (int(len(I) / 2)) + 1))


  # Si: S[equipo]
  # Patrones de localias asociados al equipo i
  home_away_patterns, S = pattern_generator.home_away_patterns()

  # F: Fechas
  F = list(range(FECHAINI, FECHAFIN + 1))

  # Gi: G[equipo]
  # Patrones de resultados asociados al equipo i
  results_patterns, G = pattern_generator.results_patterns()

  # T: Puntos
  max_points = max([champ_stats.team_points[i] for i in I]) + 3 * (FECHAFIN + 1 - FECHAINI)
  min_points = min([champ_stats.team_points[i] for i in I])
  T = list(range(min_points, max_points + 1))


  ############################
  #* PARAMETROS DEL MODELO *#
  ############################

  # M
  M = 10**10

  # PIi: PI[equipo]
  # cantidad de puntos del equipo i la fecha anterior a la primera
  # de las fechas que quedan por jugar
  PI = {i: champ_stats.team_points[i] for i in I}

  # EBit: EB[equipo][puntos]
  # 1 si equipo i tiene t puntos la fecha anterior a la primera
  # de las fechas que quedan por jugar
  # 0 en otro caso
  EB = {i: {t: 1 if champ_stats.team_points[i] == t else 0 for t in T} for i in I}


  # Rin: R[equipo][partido]:
  # Puntos que gana el equipo i al jugar partido n
  R = dict()
  for i in I:
    R[i] = dict()
    for n in N:
      if i == champ_stats.matches[n]['home']:
        if champ_stats.matches[n]['winner'] == "H":
          R[i][n] = 3
        elif champ_stats.matches[n]['winner'] == "D":
          R[i][n] = 1
        else:
          R[i][n] = 0
      elif i == champ_stats.matches[n]['away']:
        if champ_stats.matches[n]['winner'] == "A":
          R[i][n] = 3
        elif champ_stats.matches[n]['winner'] == "D":
          R[i][n] = 1
        else:
          R[i][n] = 0
      else:
        R[i][n] = 0

  # EL: EL[equipo][partido]
  # 1 Si el equipo i es local en el partido n
  # 0 En otro caso
  EL = {i: {n: 1 if champ_stats.matches[n]['home'] == i else 0 for n in N} for i in I}


  # EVin: EV[equipo][partido]
  # 1 Si el equipo i es visita en el partido n
  # 0 En otro caso
  EV = {i: {n: 1 if champ_stats.matches[n]['away'] == i else 0 for n in N} for i in I}


  # Lsf: L[patron][fecha]
  # 1 Si el patron s indica que la fecha f
  # es local
  # 0 en otro caso
  L = dict()
  for i in I:
    for s in S[i]:
      L[s] = {f: 1 if home_away_patterns[i][s][f - FECHAINI] == "1" else 0 for f in F}

  # RPgf: RP[patron][fecha]
  # Cantidad de puntos asociados al resultado
  # del patrón g en la fecha f
  char_to_int = {"W": 3, "L": 0, "D": 1}
  RP = dict()
  for i in I:
    for gi in G[i]:
      RP[gi] = {f: char_to_int[results_patterns[i][gi][f - FECHAINI]] for f in F}

  # GTift: G[equipo][fecha][puntos]
  # Patrones tales que el equipo i tiene
  # t puntos en la fecha f
  H = dict()
  puntos = lambda i, f, g: PI[i] + sum([RP[g][l] for l in range(F[0], f + 1)])
  for i in I:
    H[i] = dict()
    for f in F:
      H[i][f] = dict()
      for t in T:
        H[i][f][t] = list()
      for g in G[i]:
        H[i][f][puntos(i, f, g)].append(g)

  # Vf: V[fecha]
  # Ponderación de atractivo de fecha f
  V = {f: 0  if f - 15 <= TARGET else f - 15 for f in F}

  print("FINISHED LOADING PARAMS")

  params = {
    'N': N,
    'F': F,
    'S': S,
    'I': I,
    'R': R,
    'L': L,
    'M': M,
    'EL': EL,
    'EV': EV,
    'PI': PI,
    'S_F': home_away_patterns
  }

  return params