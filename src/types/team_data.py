from dataclasses import dataclass


@dataclass
class TeamData:
  """Guarda la informacion de equipos"""
  full_name: str
  points: int
  home_matches_left: int
