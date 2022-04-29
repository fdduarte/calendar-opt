from ...types import TeamData, MatchData


def get_team_points(
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