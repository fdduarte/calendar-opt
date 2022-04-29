from ...types import TeamData, MatchData


def get_team_localties(
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
