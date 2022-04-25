from dataclasses import dataclass
from typing import List


@dataclass
class TeamData:
  """Guarda la informacion de equipos"""
  full_name: str
  points: int
  home_matches_left: int


@dataclass
class MatchData:
  """Informacion de los partidos"""
  date: int
  number: int
  calendar_date: str
  home: str
  away: str
  result: str
  winner: str


@dataclass
class FileParams:
  """Clase para guardar los parametros de una instancia"""
  dates: List[int]
  teams: List[str]
  matches: List[int]
  available_points: List[int]
  team_points: dict[str, int]
  team_local_patterns: dict[str, list[str]]
  team_win_patterns: dict[str, list[str]]
