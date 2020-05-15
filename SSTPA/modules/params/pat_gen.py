import itertools


def valid_homeaway_pattern(string):
  """
  :param string: string con patron de 1s y 0s
  :return: (bool) Indica si el patron es valido o no
  """
  local = string.count("0")
  visit = string.count("1")
  if local < 7 or visit < 7:
    return False
  if "111" in string or "000" in string:
    return False
  if string.count("00") > 1 or string.count("11") > 1:
    return False
  return True

def check_homeaway_pattern(team, home_match, full_patterns, teams, start_date):
  """
  :param team: string alias equipo
  :home_match: Diccionario home_match[equipo][fecha]
  :full_patterns: Conjunto de patrones para 15 fechas
  :return: Conjunto de patrones que son posibles para
  el equipo
  """
  if start_date == 16 or start_date == 17:
    correct_pat = list()
    for pattern in full_patterns:
      cond1 = pattern.count("1") == teams[team]['home_left'] # Localías faltantes
      if home_match[team][14] and home_match[team][15]: # Ultimas dos fechas local,
        cond2 = pattern[0] == "0" # Primera fecha de la rueda visita.
      elif not home_match[team][14] and not home_match[team][15]: # Ultimas dos fechas visita,
        cond2 = pattern[0] == "1" # Primera fecha de la rueda local.
      elif home_match[team][15] and pattern[0] == 1: # Break de local
        cond2 = pattern.count("11") == 0 # Ningún otro break
      elif not home_match[team][15] and pattern[0] == 0: # Break de visita
        cond2 = pattern.count("00") == 0 # Ningún otro break
      else:
        cond2 = True
      if start_date == 17:
        if home_match[team][16]:
          cond3 = pattern[0] == "1"
        else:
          cond3 = pattern[0] == "0"
      else:
        cond3 = True
      if cond1 and cond2 and cond3:
        correct_pat.append(pattern)
    return correct_pat
  tent_correct_pat = list()
  pattern_start = ""
  for date in range(16, start_date): # Hacer calzar fechas jugadas
    pattern_start += str(home_match[team][date]) # con patron
  for pattern in full_patterns:
    if pattern[:start_date - 16] == pattern_start:
      tent_correct_pat.append(pattern)
  correct_pat = list()
  for pattern in tent_correct_pat: # Revisar si se llevo un break de rueda pasada
    if home_match[team][15] and pattern[0] == "1" and pattern.count("11") == 0:
      correct_pat.append(pattern)
    elif not home_match[team][15] and pattern[0] == "0" and pattern.count("00") == 0:
      correct_pat.append(pattern)
  return correct_pat

def check_results_pattern(teams_stats, patterns):
  """
  :param teams_stats: (dict) diccionario con equipos y cantidad de partidos W,D,L
  :param patterns: (dict) conunto de patrones {int numero: str patron}
  :return: Diccionario {equipo: [patrones_utiles]}
  """
  team_patterns = dict()
  for team in teams_stats.keys():
    team_patterns[team] = list()
  for pattern in patterns:
    for team in teams_stats.keys():
      if pattern.count("D") == teams_stats[team]['draws'] and pattern.count("W") == teams_stats[team]['wins'] and pattern.count("L") == teams_stats[team]['loses']:
        team_patterns[team].append(pattern)
  return team_patterns

def results_patterns_gen(filename, teams_stats):
  """
  :param dates: (int) cantidad de fechas a programar
  :param teams_stats: (dict) diccionario con equipos y cantidad de partidos W,D,L
  :return: (list) patrones de resultados.
  """
  try:
    with open(f"{filename}_results_pattern.txt", "r", encoding="UTF-8") as infile:
      permutations = list()
      for line in infile:
        permutations.append(line.strip())
      return permutations
  except FileNotFoundError:
    print("Creating Patterns File")
    permutations = ["".join(seq) for seq in itertools.product("WDL", repeat=15)]
    patterns = set()
    for team in teams_stats.keys():
      stats = ["W" for _ in range(teams_stats[team]['wins'])]
      stats.extend(["L" for _ in range(teams_stats[team]['loses'])])
      stats.extend(["D" for _ in range(teams_stats[team]['draws'])])
      stats = "".join(stats)
      patterns.add(stats)
    permutations_filtered = set()
    for perm in permutations:
      for pat in patterns:
        if pat.count("D") == perm.count("D") and pat.count("W") == perm.count("W") and pat.count("L") == perm.count("L"):
          permutations_filtered.add(perm)
    with open(f"{filename}_results_pattern.txt", "w", encoding="UTF-8") as infile:
      for perm in list(permutations_filtered):
        infile.write(f"{perm}\n")
    return list(permutations_filtered)



homeaway_patterns = filter(valid_homeaway_pattern, ["".join(seq) for seq in itertools.product("01", repeat=15)])







