from .data_classes import TeamData, MatchData


def _get_team_local_patterns(
  teams_data: dict[str, TeamData],
  results_data: list[MatchData],
  dates: list[int]
) -> dict[str, str]:
  """
  Funcion que retorna las localias y visitas de un equipo en un string.
  el patron incluye dos fechas antes que parta el torneo.
  """
  # Una fecha antes de la primera vuelta (para ver si arrastra break)
  mid_date = int(dates[-1] / 2)

  patterns = {team: "" for team in teams_data.keys()}

  for curr_date in range(mid_date - 1, dates[-1] + 1):
    for team in patterns.keys():
      filter_fun = lambda x: team in [x.home, x.away] and x.date == curr_date
      match = list(filter(filter_fun, results_data))[0]
      if match.home == team:
        patterns[team] += '1'
      else:
        patterns[team] += '0'

  return patterns


def _get_team_win_patterns(
  teams_data: dict[str, TeamData],
  results_data: list[MatchData],
  dates: list[int]
) -> dict[str, str]:
  """
  Funcion que retorna las victorias, empates o perdidas de un equipo en un string..
  """
  # Una fecha antes de la primera vuelta (para ver si arrastra break)
  mid_date = int(dates[-1] / 2)

  patterns = {team: "" for team in teams_data.keys()}

  for curr_date in range(mid_date + 1, dates[-1] + 1):
    for team in patterns.keys():
      filter_fun = lambda x: team in [x.home, x.away] and x.date == curr_date
      match = list(filter(filter_fun, results_data))[0]
      if match.home == team and match.winner == 'home':
        patterns[team] += 'W'
      elif match.away == team and match.winner == 'away':
        patterns[team] += 'W'
      elif match.winner == 'draw':
        patterns[team] += 'D'
      else:
        patterns[team] += 'L'

  return patterns


def _get_team_matches_points(
  teams_data: dict[str, TeamData],
  results_data: list[MatchData],
  dates: list[int]
) -> dict[str, dict[int, int]]:
  """
  Funcion que retorna los puntos que gana un equipo al jugar un partido n.
  """
  # Una fecha antes de la primera vuelta (para ver si arrastra break)
  mid_date = int(dates[-1] / 2)

  patterns: dict[str, dict[int, int]] = {team: {} for team in teams_data.keys()}

  for curr_date in range(mid_date + 1, dates[-1] + 1):
    for team in patterns.keys():
      filter_fun = lambda x: team in [x.home, x.away] and x.date == curr_date
      match = list(filter(filter_fun, results_data))[0]
      if match.home == team and match.winner == 'home':
        patterns[team][match.number] = 3
      elif match.away == team and match.winner == 'away':
        patterns[team][match.number] = 3
      elif match.winner == 'draw':
        patterns[team][match.number] = 1
      else:
        patterns[team][match.number] = 0

  return patterns


def _get_team_points(
  teams_data: dict[str, TeamData],
  results_data: list[MatchData],
  date: int,
  dates: list[int]
) -> dict[str, int]:
  """
  Funcion que retorna la cantidad de puntos que tiene un equipo al inicio
  en una fecha.
  """
  points = {team: team_data.points for team, team_data in teams_data.items()}
  second_round_start_date = int((dates[-1] / 2) + 1)

  for curr_date in range(second_round_start_date, date):
    for team in points.keys():
      filter_fun = lambda x: team in [x.home, x.away] and x.date == curr_date
      match = list(filter(filter_fun, results_data))[0]
      if match.winner == 'draw':
        points[team] += 1
      if match.winner == 'home' and match.home == team:
        points[team] += 3
      if match.winner == 'away' and match.away == team:
        points[team] += 3

  return points


def _get_team_localties(
  teams_data: dict[str, TeamData],
  results_data: list[MatchData],
  dates: list[int]
) -> dict[str, dict[int, str]]:
  """retorna si el equipo i es local o visita en el partido n"""
  localties: dict[str, dict[int, str]] = {team: {} for team in teams_data.keys()}
  second_round_start_date = int((dates[-1] / 2) + 1)

  for curr_date in range(second_round_start_date, dates[-1] + 1):
    for team in localties.keys():
      filter_fun = lambda x: team in [x.home, x.away] and x.date == curr_date
      match = list(filter(filter_fun, results_data))[0]
      if match.home == team:
        localties[team][match.number] = 'L'
      else:
        localties[team][match.number] = 'V'
  return localties

