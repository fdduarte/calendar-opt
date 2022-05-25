from typing import TypedDict


class SSTPAParams(TypedDict):
  """SSTPA params dict type"""
  I: list[str]
  F: list[int]
  N: list[int]
  S: dict[str, list[str]]
  T: list[int]
  PI: dict[str, int]
  EB: dict[str, dict[int, int]]
  R: dict[str, dict[int, int]]
  EL: dict[str, dict[int, int]]
  EV: dict[str, dict[int, int]]
  V: dict[int, int]
  L: dict[str, dict[int, int]]
