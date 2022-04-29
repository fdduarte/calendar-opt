from libs.stats_parser import FileParams
from .params_data import ParamsData


def get_params(start_date: int, end_date: int, file_params: FileParams) -> ParamsData:
  """Generador de parámetros para SSTPA V3."""

  #################
  # * CONJUNTOS * #
  #################

  # I: Equipos
  teams = file_params.teams

  # F: Fechas
  dates = list(filter(lambda x: x >= start_date, file_params.dates))

  # N: Partidos
  # partidos por fecha
  matches_per_date = int(len(teams) / 2)
  dates_to_plan = dates[-1] - start_date + 1

  matches = list(range(1, dates_to_plan * matches_per_date + 1))

  # Si: S[equipo]
  # Patrones de localias asociados al equipo i. Si es un conjunto de
  # indices que corresponden a cada patron. Para acceder al detalle
  # de un patron, local_patterns[patron] lo retorna.

  # A cada patron se le asigna un indice.
  local_patterns_full = {}
  local_patterns_indexes: dict[str, list[str]] = {}
  for team in teams:
    local_patterns_indexes[team] = []
    team_local_patterns = file_params.team_local_patterns[team]
    for idx, pattern in enumerate(team_local_patterns):
      local_patterns_full[f"{team}-{idx}"] = pattern
      local_patterns_indexes[team].append(f"{team}-{idx}")

  local_patterns = {
    'indexes': local_patterns_indexes,
    'full_patterns': local_patterns_full
  }

  # Gi: G[equipo]
  # Patrones de resultados asociados al equipo i
  result_patterns_full = {}
  result_patterns_indexes: dict[str, list[str]] = {}
  for team in teams:
    result_patterns_indexes[team] = []
    team_result_patterns = file_params.team_win_patterns[team]
    for idx, pattern in enumerate(team_result_patterns):
      result_patterns_full[f"{team}-{idx}"] = pattern
      result_patterns_indexes[team].append(f"{team}-{idx}")

  result_patterns = {
    'indexes': result_patterns_indexes,
    'full_patterns': result_patterns_full
  }

  # T: Puntos
  points = file_params.available_points

  #############################
  # * PARAMETROS DEL MODELO * #
  #############################

  #  M
  big_m = 10**10

  # PIi: PI[equipo]
  # cantidad de puntos del equipo i la fecha anterior a la primera
  # de las fechas que quedan por jugar
  team_points = file_params.team_points

  # EBit: EB[equipo][puntos]
  # 1 si equipo i tiene t puntos la fecha anterior a la primera
  # de las fechas que quedan por jugar
  # 0 en otro caso
  team_points_discrete = {team: {point: 1 if file_params.team_points[team] == point else 0
                                 for point in points} for team in teams}

  # Rin: R[equipo][partido]:
  # Puntos que gana el equipo i al jugar partido n
  team_matches_points: dict[str, dict[int, int]] = {}
  for team in teams:
    team_matches_points[team] = {}
    for match in matches:
      if match in file_params.matches_points[team].keys():
        team_matches_points[team][match] = file_params.matches_points[team][match]
      else:
        team_matches_points[team][match] = 0

  # ELin: EL[equipo][partido]
  # 1 Si el equipo i es local en el partido n
  # 0 En otro caso
  team_localties: dict[str, dict[int, int]] = {}
  for team in teams:
    team_localties[team] = {}
    for match in matches:
      if match in file_params.team_localties[team].keys() and (
         file_params.team_localties[team][match] == 'L'):
        team_localties[team][match] = 1
      else:
        team_localties[team][match] = 0

  # EVin: EV[equipo][partido]
  # 1 Si el equipo i es visita en el partido n
  # 0 En otro caso
  team_aways: dict[str, dict[int, int]] = {}
  for team in teams:
    team_aways[team] = {}
    for match in matches:
      if match in file_params.team_localties[team].keys() and (
         file_params.team_localties[team][match] == 'V'):
        team_aways[team][match] = 1
      else:
        team_aways[team][match] = 0

  # Lsf: L[patron][fecha]
  # 1 Si el patron s indica que la fecha f
  # es local
  # 0 en otro caso
  local_pattern_localties: dict[str, dict[int, int]] = {}
  for index, pattern in local_patterns_full.items():
    local_pattern_localties[index] = {}
    for date in dates:
      if pattern[date - dates[0]] == '1':
        local_pattern_localties[index][date] = 1
      else:
        local_pattern_localties[index][date] = 0

  # RPgf: RP[patron][fecha]
  # Cantidad de puntos asociados al resultado
  # del patrón g en la fecha f
  char_to_int = {"W": 3, "L": 0, "D": 1}
  result_patterns_points: dict[str, dict[int, int]] = {}
  for index, pattern in result_patterns_full.items():
    result_patterns_points[index] = {}
    for date in dates:
      value = char_to_int[pattern[date - dates[0]]]
      result_patterns_points[index][date] = value

  # GTift: G[equipo][fecha][puntos]
  # Patrones tales que el equipo i tiene
  # t puntos en la fecha f
  def get_team_points_with_pattern(team, pattern, date):
    points = team_points[team]
    for curr_date in range(0, date - dates[0] + 1):
      if pattern[curr_date] == 'W':
        points += 3
      if pattern[curr_date] == 'D':
        points += 1
    return points

  pattern_team_points: dict[str, dict[int, dict[int, list[str]]]] = {}
  for team in teams:
    pattern_team_points[team] = {}
    for date in dates:
      pattern_team_points[team][date] = {}
      for point in points:
        pattern_team_points[team][date][point] = []
      for pattern_idx in result_patterns_indexes[team]:
        pattern = result_patterns_full[pattern_idx]
        point = get_team_points_with_pattern(team, pattern, date)
        pattern_team_points[team][date][point].append(pattern_idx)

  # Vf: V[fecha]
  # Ponderación de atractivo de fecha f
  attractiveness = {date: date - dates[0] + 1 for date in dates}

  subproblem_indexes = [(team, date, s) for team in teams for date in dates for s in ["m", "p"]]

  params = ParamsData(
    teams=teams,
    dates=dates,
    matches=matches,
    points=points,
    local_patterns=local_patterns,
    result_patterns=result_patterns,
    big_m=big_m,
    team_points=team_points,
    team_points_discrete=team_points_discrete,
    team_matches_points=team_matches_points,
    team_localties=team_localties,
    team_aways=team_aways,
    local_pattern_localties=local_pattern_localties,
    result_patterns_points=result_patterns_points,
    pattern_team_points=pattern_team_points,
    attractiveness=attractiveness,
    subproblem_indexes=subproblem_indexes
  )

  return params
