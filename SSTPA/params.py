import pandas as pd
from pat_gen import homeaway_patterns, check_homeaway_pattern, results_patterns_gen, check_results_pattern


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

def parse_match(filename, start_date):
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
  return matches, home_match, teams_stats

def parse_teams(filename):
  teams_file = open_excel(filename, 0)
  teams = {}
  for line in teams_file:
    _, _, alias, fr_points, home_left = line
    teams[alias] = {"fr_points": int(fr_points), "home_left": int(home_left)}
  return teams


#############################
#* PARAMETROS DE INSTANCIA *#
#############################
FECHAINI = 20


# Carga de Datos
matches, home_match, teams_stats = parse_match("Datos.xlsx", FECHAINI)
teams = parse_teams("Datos.xlsx")



#################
#*  CONJUNTOS  *#
#################

# I: Equipos
I = teams.keys()

# N: Partidos
N = list(range((FECHAINI - 1) * 8 + 1, 241))

# S: Patrones
full_homeaway_patterns = list(homeaway_patterns).copy()
patterns = list(set([pat[FECHAINI - 16:] for pat in full_homeaway_patterns]))
patterns = {i + 1: patterns[i] for i in range(len(patterns))}
S = list(patterns.keys())

# F: Fechas
F = list(range(FECHAINI, 31))

# G: Patrones de resultados
results_patterns = results_patterns_gen(len(F), teams_stats)
G = {i + 1: results_patterns[i] for i in range(len(results_patterns))}


############################
#* PARAMETROS DEL MODELO *#
############################

# Eit: Eit[equipo][puntos]
# 1 Si el equipo i tiene t puntos la fecha anterior a N
# 0 En otro caso
#**** ARREGLAR PARA CAMBIAR FECHA INI
max_points = max([teams[team]['fr_points'] for team in teams.keys()]) + 45
min_points = min([teams[team]['fr_points'] for team in teams.keys()])
points_range = [min_points, max_points]

Eit = {team: {i: 1 if teams[team]['fr_points'] == i else 0 for i in range(*points_range)} for team in teams.keys()}

# Rin: Rin[equipo][partido]:
# Puntos que gana el equipo i al jugar partido n
Rin = dict()
for team in teams.keys():
  Rin[team] = dict()
  for match in N:
    if team == matches[match]['home']:
      if matches[match]['winner'] == "H":
        Rin[team][match] = 3
      elif matches[match]['winner'] == "D":
        Rin[team][match] = 1
      else:
        Rin[team][match] = 0
    elif team == matches[match]['away']:
      if matches[match]['winner'] == "A":
        Rin[team][match] = 3
      elif matches[match]['winner'] == "D":
        Rin[team][match] = 1
      else:
        Rin[team][match] = 0
    else:
      Rin[team][match] = 0

# EL: EL[equipo][partido]
# 1 Si el equipo i es local en el partido n
# 0 En otro caso
EL = {team: {match: 1 if matches[match]['home'] == team else 0 for match in N} for team in teams.keys()}

# EVin: EV[equipo][partido]
# 1 Si el equipo i es visita en el partido n
# 0 En otro caso
EV = {team: {match: 1 if matches[match]['away'] == team else 0 for match in N} for team in teams.keys()}

# Wis: W[equipo][patron]
# 1 Si al equipo i se le puede asignar el
# patron de localias s
# 0 En otro caso
W = dict()
for team in teams.keys():
  W[team] = dict()
  possible_pat = check_homeaway_pattern(team, home_match, full_homeaway_patterns, teams, FECHAINI)
  possible_pat = list(set([pat[FECHAINI - 16:] for pat in possible_pat]))
  for pat_num in S:
    if patterns[pat_num] in possible_pat:
      W[team][pat_num] = 1
    else:
      W[team][pat_num] = 0

# Lsf: L[patron][fecha]
# 1 Si el patron s indica que la fecha f
# es local
# 0 en otro caso
L = {i: {f: 1 if patterns[i][FECHAINI - f] == "1" else 0 for f in F} for i in S}

# VGig: VG[equipo][patron]
# 1 Si al equipo i se le puede asignar
# el patron de resultados g.
# 0 en otro caso.
VGig = check_results_pattern(teams_stats, G)

# RPgf: RPgf[patron][fecha]
# Cantidad de puntos asociados al resultado
# del patrón g en la fecha f
char_to_int = {"W": 3, "L": 0, "D": 1}
RPgh = {g: {f: char_to_int[G[g][f - FECHAINI]] for f in F} for g in G.keys()}




      








