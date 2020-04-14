import pandas as pd
from pat_gen import patterns, check_pattern


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

def parse_match(filename):
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
  return matches, home_match

def parse_teams(filename):
  teams_file = open_excel(filename, 0)
  teams = {}
  for line in teams_file:
    _, _, alias, fr_points, home_left = line
    teams[alias] = {"fr_points": int(fr_points), "home_left": int(home_left)}
  return teams

# Carga de Datos
matches, home_match = parse_match("Datos.xlsx")
teams = parse_teams("Datos.xlsx")


#############################
#* PARAMETROS DE INSTANCIA *#
#############################
FECHAINI = 16


#################
#*  CONJUNTOS  *#
#################

# N: Partidos
N = list(range((FECHAINI - 1) * 8 + 1, 241))

# S: Patrones
full_patterns = list(patterns).copy()
patterns = list(set([pat[FECHAINI - 16:] for pat in full_patterns]))
patterns = {i + 1: patterns[i] for i in range(len(patterns))}
S = patterns.keys()

# F: Fechas
F = list(range(FECHAINI, 31))


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

# ELin: ELin[equipo][partido]
# 1 Si el equipo i es local en el partido n
# 0 En otro caso
ELin = {team: {match: 1 if matches[match]['home'] == team else 0 for match in N} for team in teams.keys()}

# EVin: ELin[equipo][partido]
# 1 Si el equipo i es visita en el partido n
# 0 En otro caso
EVin = {team: {match: 1 if matches[match]['away'] == team else 0 for match in N} for team in teams.keys()}

# Wis: Wis[equipo][patron]
# 1 Si al equipo i se le puede asignar el
# patron de localias s
# 0 En otro caso
Wis = dict()
for team in teams.keys():
  Wis[team] = dict()
  possible_pat = check_pattern(team, home_match, full_patterns, teams, FECHAINI)
  possible_pat = list(set([pat[FECHAINI - 16:] for pat in possible_pat]))
  for pat_num in S:
    if patterns[pat_num] in possible_pat:
      Wis[team][pat_num] = 1
    else:
      Wis[team][pat_num] = 0

# Lsf: Lsf[patron][fecha]
# 1 Si el patron s indica que la fecha f
# es local
# 0 en otro caso
Lsf = {i: {f: 1 if patterns[i][16 - f] == "1" else 0 for f in F} for i in S}






      








