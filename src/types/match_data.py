from dataclasses import dataclass


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
