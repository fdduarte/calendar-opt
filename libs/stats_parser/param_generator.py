"""
El siguiente módulo se encarga de, dado los datos de una instancia,
retornar un diccionario con los parametros generales de los datos,
para que luego se puedan adaptar fácilmente al modelo.
"""
from .sheet_parser import read_results_file, read_teams_file
from .data_classes import FileParams, TeamData, MatchData
from .pattern_generator import generate_patterns


def generate_params(filepath: str, start_date: int, end_date: int, breaks: int) -> FileParams:
  """
  Dado un path al archivo xlsx, una fecha de inicio y fecha de término,
  retorna un diccionario con los parametros de la instancia.
  """
  teams_data = read_teams_file(filepath)
  results_data = read_results_file(filepath)

  # Lista de equipos del torneo
  teams = list(teams_data.keys())

  # Lista de los partidos del torneo por número
  matches = [match.number for match in results_data]

  # Lista de fechas del campeonatp
  dates = list(set([match.date for match in results_data]))
  dates.sort()

  # Diccionario de los puntos iniciales de un equipo en el torneo
  team_points = _get_team_points(teams_data, results_data, start_date, dates)

  # Lista de los puntos disponibles en el torneo
  dates_number = end_date - start_date + 1

  _max_points = max([p for p in team_points.values()]) + dates_number * 3
  _min_points = min([p for p in team_points.values()])
  available_points = list(range(_min_points, _max_points + 1))

  # Patrones de localia y visita de la segunda rueda del equipo mas la ultima fecha
  # de la primera
  second_round_date = int((dates[-1] / 2) + 1)
  team_original_patterns = _get_team_patterns(teams_data, results_data, dates)
  team_local_patterns, team_win_patterns = generate_patterns(
    team_original_patterns, second_round_date, start_date, end_date, breaks)

  params = FileParams(
    dates,
    teams,
    matches,
    available_points,
    team_points,
    team_local_patterns,
    team_win_patterns
  )

  return params


def _get_team_patterns(
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


if __name__ == '__main__':
  print(generate_params('./data/campeonato_prueba.xlsx', 6, 6, 1))
