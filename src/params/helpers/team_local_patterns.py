from ...types import TeamData, MatchData
from ...libs.argsparser import args


def get_team_local_patterns(
  teams_data: dict[str, TeamData],
  results_data: list[MatchData],
  dates: list[int]
) -> dict[str, str]:
  """
  Funcion que retorna las localias y visitas de un equipo en un string.
  el patron incluye dos fechas antes que parta el torneo.
  """
  # Una fecha antes de la primera vuelta (para ver si arrastra break)
  if args.second_round_date == -1:
    mid_date = int(dates[-1] / 2)
  else:
    mid_date = args.second_round_date - 1

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
