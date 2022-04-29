from dataclasses import dataclass


@dataclass
class ParamsData:
  """Guarda la informacion de los parámetros del modelo"""
  teams: list[str]
  dates: list[int]
  matches: list[int]
  points: list[int]
  local_patterns: dict[str, dict[str, list[str]]]
  result_patterns: dict[str, dict[str, list[str]]]
  big_m: int
  team_points: dict[str, int]
  team_points_discrete: dict[str, dict[int, int]]
  team_matches_points: dict[str, dict[int, int]]
  team_localties: dict[str, dict[int, int]]
  team_aways: dict[str, dict[int, int]]
  local_pattern_localties: dict[str, dict[int, int]]
  result_patterns_points: dict[str, dict[int, int]]
  pattern_team_points: dict[str, dict[int, dict[int, list[str]]]]
  attractiveness: dict[int, int]
