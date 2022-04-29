"""
El siguiente módulo se encarga de, dado los datos de una instancia,
retornar un diccionario con los parametros generales de los datos,
para que luego se puedan adaptar fácilmente al modelo.
"""
from .sheet_parser import read_results_file, read_teams_file
from .data_classes import FileParams
from .pattern_generator import generate_patterns
from .helpers import (
  _get_team_local_patterns,
  _get_team_matches_points,
  _get_team_points,
  _get_team_win_patterns,
  _get_team_localties
)


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

  _max_points = max(team_points.values()) + dates_number * 3
  _min_points = min(team_points.values())
  available_points = list(range(_min_points, _max_points + 1))

  # Patrones de localia y visita de la segunda rueda del equipo mas la ultima fecha
  # de la primera.
  second_round_date = int((dates[-1] / 2) + 1)

  team_original_local_patterns = _get_team_local_patterns(teams_data, results_data, dates)
  team_original_win_patterns = _get_team_win_patterns(teams_data, results_data, dates)

  team_local_patterns, team_win_patterns = generate_patterns(
    team_original_local_patterns, team_original_win_patterns,
    second_round_date, start_date, end_date, breaks)

  # Puntos por partido
  matches_points = _get_team_matches_points(teams_data, results_data, dates)

  # Localias de equipos por partido
  team_localties = _get_team_localties(teams_data, results_data, dates)

  params = FileParams(
    dates,
    teams,
    matches,
    available_points,
    team_points,
    team_local_patterns,
    team_win_patterns,
    matches_points,
    team_localties
  )

  return params


if __name__ == '__main__':
  print(generate_params('./data/campeonato_prueba.xlsx', 6, 6, 1))
