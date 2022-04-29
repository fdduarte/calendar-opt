from ...types import TeamData, MatchData


def get_team_matches_points(
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