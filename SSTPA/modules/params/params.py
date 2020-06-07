import sys, os
import pandas as pd
import time
from modules.params.pat_gen import homeaway_patterns, check_homeaway_pattern, results_patterns_gen, check_results_pattern, result_patterns_gen_v4, check_short_result_pattern


def open_excel(name, page):
    """
    :param name: nombre del archivo a abrir
    :param page: nombre de la pagina de interes
    :return: lista por filas de pagina de excel
    """
    file = pd.ExcelFile(name)
    file = file.parse(page)
    column = []
    for key in file.keys():
        buff = []
        for i in range(len(file[key])):
            buff.append(str(file[key][i]).rstrip().replace("\xa0", " "))
        column.append(buff)
    buff = list(zip(*column))
    return buff

def parse_match(filename, start_date, final_date):
  """
  :param filename: nombre del archivo excel
  :return: {match: [{event_date: , home: , away: , winner: }]},
  {team: {date: home -> 1 else 0}}
  Retorna todos los 240 partidos del campeonato
  """
  match_file = open_excel(filename, 1)
  matches = {i: [] for i in range(1, 241)}
  date = False
  match = 240
  home_match = dict()
  teams_stats = dict()
  teams_stats_to_date = dict()
  team_points = dict()
  for i in match_file:
    if i[0] != "nan":
      date = int(float(i[0]))
    else:
      _, home, away, score = i[1:5]
      score = [int(i.strip()) for i in score.split(":")]
      if score[0] > score[1]:
        winner = 'H'
      elif score[0] < score[1]:
        winner = "A"
      else:
        winner = "D"
      matches[match] = {"date": date, "home": home,
                        "away": away, "winner": winner}
      match -= 1
      if home not in team_points.keys():
        team_points[home] = 0
      if away not in team_points.keys():
        team_points[away] = 0
      if date < start_date:
        if winner == "H":
          team_points[home] += 3
        if winner == "A":
          team_points[away] += 3
        if winner == "D":
          team_points[home] += 1
          team_points[away] += 1
      if home not in home_match.keys():
        home_match[home] = dict()
      home_match[home][date] = 1
      if away not in home_match.keys():
        home_match[away] = dict()
      home_match[away][date] = 0
      if date >= start_date:
        if home not in teams_stats.keys():
          teams_stats[home] = {'wins': 0, 'loses': 0, 'draws': 0}
        if away not in teams_stats.keys():
          teams_stats[away] = {'wins': 0, 'loses': 0, 'draws': 0}
        if winner == "H":
          teams_stats[home]['wins'] += 1
          teams_stats[away]['loses'] += 1
        if winner == "A":
          teams_stats[away]['wins'] += 1
          teams_stats[home]['loses'] += 1
        if winner == "D":
          teams_stats[home]['draws'] += 1
          teams_stats[away]['draws'] += 1
      if date >= start_date and date <= final_date:
        if home not in teams_stats_to_date.keys():
          teams_stats_to_date[home] = {'wins': 0, 'loses': 0, 'draws': 0}
        if away not in teams_stats_to_date.keys():
          teams_stats_to_date[away] = {'wins': 0, 'loses': 0, 'draws': 0}
        if winner == "H":
          teams_stats_to_date[home]['wins'] += 1
          teams_stats_to_date[away]['loses'] += 1
        if winner == "A":
          teams_stats_to_date[away]['wins'] += 1
          teams_stats_to_date[home]['loses'] += 1
        if winner == "D":
          teams_stats_to_date[home]['draws'] += 1
          teams_stats_to_date[away]['draws'] += 1
  return matches, home_match, teams_stats, team_points, teams_stats_to_date

def parse_teams(filename):
  teams_file = open_excel(filename, 0)
  teams = {}
  for line in teams_file:
    _, _, alias, fr_points, home_left = line
    teams[alias] = {"fr_points": int(fr_points), "home_left": int(home_left)}
  return teams


##########################
#* GENERADOR PARAMETROS *#
#*   MODELOS V3 Y V4    *#
##########################


#############################
#* PARAMETROS DE INSTANCIA *#
#############################
START_TIME = time.time()
FECHAINI = 16
FECHAFIN = 30
TARGET = 30
FILENAME = "SSTPA/modules/params/Datos"
TIMELIMIT = (100) * 60 * 60
MODEL = "V4" # {V3, V4}


# Carga de Datos
matches, home_match, teams_stats, team_points, teams_stats_to_date = parse_match(f"{FILENAME}.xlsx", FECHAINI, FECHAFIN)
teams = parse_teams(f"{FILENAME}.xlsx")


#################
#*  CONJUNTOS  *#
#################

# I: Equipos
I = list(teams.keys())

# N: Partidos
N = list(range((FECHAINI - 1) * 8 + 1, FECHAFIN * 8 + 1))

# Si: S[equipo]
# Patrones de localias asociados al equipo i
full_homeaway_patterns = list(homeaway_patterns).copy()
patterns = list(set([pat[FECHAINI - 16:FECHAFIN - 15] for pat in full_homeaway_patterns]))
patterns = {i + 1: patterns[i] for i in range(len(patterns))}

S_full = dict()
for i in I:
  pat = check_homeaway_pattern(i, home_match, full_homeaway_patterns, teams, FECHAINI)
  pat = list(set([p[FECHAINI - 16:FECHAFIN - 15] for p in pat]))
  S_full[i] = {f"{i}-{j + 1}": pat[j] for j in range(len(pat))}
S = {i: list(S_full[i].keys()) for i in I}


# F: Fechas
F = list(range(FECHAINI, FECHAFIN + 1))

if MODEL == "V3":
  # Gi: G[equipo]
  # Patrones de resultados asociados al equipo i
  full_results_patterns = results_patterns_gen(FILENAME, teams_stats)
  team_patterns = check_results_pattern(teams_stats, full_results_patterns)
  G_full = dict()
  for i in I:
    pat = list(set([pat[FECHAINI - 16:FECHAFIN - 15] for pat in team_patterns[i]]))
    G_full[i] = {f"{i}-{j + 1}": pat[j] for j in range(len(pat))} # Contiene el valor asociado a la llave patron de Gi
  G = {i: list(G_full[i].keys()) for i in I}
if MODEL == "V4":
  # G1, G2: Patrones de resultados para la primera y segunda mitad
  dates = FECHAFIN - FECHAINI + 1
  FIRST_HALF = dates // 2
  FH = list(range(FECHAINI, FECHAINI + FIRST_HALF))
  SH = list(range(FECHAINI + FIRST_HALF, FECHAFIN + 1))
  SECOND_HALF = dates - FIRST_HALF
  G1_patterns_list = result_patterns_gen_v4(FIRST_HALF)
  G2_patterns_list = result_patterns_gen_v4(SECOND_HALF)
  G1_full = {i: G1_patterns_list[i] for i in range(len(G1_patterns_list))}
  G2_full = {i: G2_patterns_list[i] for i in range(len(G2_patterns_list))}
  G1 = list(G1_full.keys())
  G2 = list(G2_full.keys())


# T: Puntos
max_points = max([team_points[i] for i in I]) + 3 * (FECHAFIN + 1 - FECHAINI)
min_points = min([team_points[i] for i in I])
T = list(range(min_points, max_points + 1))


############################
#* PARAMETROS DEL MODELO *#
############################

# Ei: E[equipo]
# cantidad de puntos del equipo i la fecha anterior a la primera
# de las fechas que quedan por jugar
E = {i: team_points[i] for i in I}

# EBit: EB[equipo][puntos]
# 1 si equipo i tiene t puntos la fecha anterior a la primera
# de las fechas que quedan por jugar
# 0 en otro caso
EB = {i: {t: 1 if team_points[i] == t else 0 for t in T} for i in I}


# Rin: R[equipo][partido]:
# Puntos que gana el equipo i al jugar partido n
R = dict()
for i in I:
  R[i] = dict()
  for n in N:
    if i == matches[n]['home']:
      if matches[n]['winner'] == "H":
        R[i][n] = 3
      elif matches[n]['winner'] == "D":
        R[i][n] = 1
      else:
        R[i][n] = 0
    elif i == matches[n]['away']:
      if matches[n]['winner'] == "A":
        R[i][n] = 3
      elif matches[n]['winner'] == "D":
        R[i][n] = 1
      else:
        R[i][n] = 0
    else:
      R[i][n] = 0

# EL: EL[equipo][partido]
# 1 Si el equipo i es local en el partido n
# 0 En otro caso
EL = {i: {n: 1 if matches[n]['home'] == i else 0 for n in N} for i in I}

# EVin: EV[equipo][partido]
# 1 Si el equipo i es visita en el partido n
# 0 En otro caso
EV = {i: {n: 1 if matches[n]['away'] == i else 0 for n in N} for i in I}


# Lsf: L[patron][fecha]
# 1 Si el patron s indica que la fecha f
# es local
# 0 en otro caso
L = dict()
for i in I:
  for s in S[i]:
    L[s] = {f: 1 if S_full[i][s][FECHAINI - f] == "1" else 0 for f in F}


if MODEL == "V3":
  # RPgf: RP[patron][fecha]
  # Cantidad de puntos asociados al resultado
  # del patrón g en la fecha f
  char_to_int = {"W": 3, "L": 0, "D": 1}

  RP = dict()
  for i in I:
    for gi in G[i]:
      RP[gi] = {f: char_to_int[G_full[i][gi][f - FECHAINI]] for f in F}

if MODEL == "V4":
  # RP1gf, RP2gf: RPi[patron][fecha]
  # Cantidad de puntos asociados al resultado del patron g
  # del conjunto Gi en la fecha f
  char_to_int = {"W": 3, "L": 0, "D": 1}
  RP1 = {g: {f: char_to_int[G1_full[g][f - FH[0]]] for f in FH} for g in G1}
  RP2 = {g: {f: char_to_int[G2_full[g][f - SH[0]]] for f in SH} for g in G2}

  #VG1ig, VG2ig: VGi[equipo][patron]
  # 1 Si al equipo i se le puede asignar el patron g
  # 0 en otro caso.
  VG1 = {i: {g: check_short_result_pattern(G1_full[g], teams_stats, i) for g in G1} for i in I}
  VG2 = {i: {g: check_short_result_pattern(G2_full[g], teams_stats, i) for g in G2} for i in I}

  # NVi, NV[equipo]
  # Cantidad de victorias que obtendría el equipo
  # i en las fechas que restan por programar.
  NV = {i: teams_stats_to_date[i]['wins'] for i in I}

  # NEi: EV[equipo]
  # Cantidad de empates que obtendría el equipo
  # i en las fechas que restan por programar.
  NE = {i: teams_stats_to_date[i]['draws'] for i in I}

  # PV1gf: PV1[patron][fecha]
  # Cantidad de victorias que tiene el patron g
  # entre las fechas FECHAINI y f
  PV1 = {g: {f: G1_full[g][:f - FH[0] + 1].count("W") for f in FH} for g in G1}

  # PV2gf: PV2[patron][fecha]
  # Cantidad de victorioas que tiene el patron g
  # entre las fechas q y FECHAFIN
  PV2 = {g: {f: G2_full[g][:f - SH[0] + 1].count("W") for f in SH} for g in G2}

  # PE1gf: PE1[patron][fecha]
  # Cantidad de empates que tiene el patron g
  # entre las fechas FECHAINI y f
  PE1 = {g: {f: G1_full[g][:f - FH[0] + 1].count("D") for f in FH} for g in G1}

  # PE2gf: PE2[patron][fecha]
  # Cantidad de empates que tiene el patron g
  # entre las fechas q y FECHAFIN
  PE2 = {g: {f: G2_full[g][:f - SH[0] + 1].count("D") for f in SH} for g in G2}


# Vf: V[fecha]
# Ponderación de atractivo de fecha f
V = {f: f - 15  if f - 15 <= TARGET else 0 for f in F}


if MODEL == "V3":
  # GTift: G[equipo][fecha][puntos]
  # Patrones tales que el equipo i tiene
  # t puntos en la fecha f
  H = dict()
  puntos = lambda i, f, g: E[i] + sum([RP[g][l] for l in range(F[0], f + 1)])
  for i in I:
    H[i] = dict()
    for f in F:
      H[i][f] = dict()
      for t in T:
        H[i][f][t] = list()
      for g in G[i]:
        H[i][f][puntos(i, f, g)].append(g)

if MODEL == "V4":
  # H1ift, H2ift: Hi[equipo][fecha][puntos]
  # Patrones tales que el equipo i tiene
  # t puntos en la fecha f
  H1 = dict()
  H2 = dict()
  puntos1 = lambda i, f, g: E[i] + sum([RP1[g][l] for l in range(F[0], f + 1)])
  puntos2 = lambda i, f, g: sum([RP2[g][l] for l in range(SH[0], f + 1)])
  for i in I:
    H1[i] = dict()
    for f in FH:
      H1[i][f] = dict()
      for t in T:
        H1[i][f][t] = list()
      for g in G1:
        if VG1[i][g]:
          H1[i][f][puntos1(i, f, g)].append(g)
  for i in I:
    H2[i] = dict()
    for f in SH:
      H2[i][f] = dict()
      for t in range(0, T[-1]):
        H2[i][f][t] = list()
      for g in G1:
        if VG1[i][g]:
          H2[i][f][puntos2(i, f, g)].append(g)


print("FINISHED LOADING PARAMS")


      








