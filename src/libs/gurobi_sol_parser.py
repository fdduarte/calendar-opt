import json
from ..types import TeamData, MatchData
from typing import Any


def read_teams_file(filename: str) -> dict[str, TeamData]:
  """
  Función que lee un archivo .sol
  Retorna un diccionario cuya llave es el alias del equipo, y el valor es un
  diccionario con los datos del equipo.
  """
  teams = {}
  with open(filename, 'r', encoding='utf-8') as infile:
    for line in infile:
      if '**********' in line:
        _, jsons = line.strip().split('|')
        teams_dict = json.loads(jsons)
      if '++++++++++' in line:
        _, jsons = line.strip().split('|')

  for key, value in teams_dict.items():
    teams[key] = TeamData(value['full_name'], value['points'], value['home_matches_left'])
  return teams


def read_results_file(filename: str) -> list[MatchData]:
  """Función que lee un archivo .sol y retorna los resultados"""
  number_to_date: dict[int, int] = {}
  dates: list[int] = []
  with open(filename, 'r', encoding='utf-8') as infile:
    for line in infile:
      if '++++++++++' in line:
        _, jsons = line.strip().split('|')
        results_dict = json.loads(jsons)
      if 'x[' in line:
        name, value = line.strip().split()
        if float(value) < 0.5:
          int_value = 0
        else:
          int_value = 1
        n, f = name.strip('x[').strip(']').split(',')
        if int_value == 1:
          number_to_date[int(n)] = int(f)
        dates.append(int(f))
  dates = list(set(dates))
  results_by_date: dict[int, list[Any]] = {date: [] for date in dates}
  for result in results_dict['data']:
    if result['number'] in number_to_date:
      date = number_to_date[result['number']]
      results_by_date[date].append(result)
  current_number = 1
  results = []
  dates.sort(reverse=True)
  for date in dates:
    for result in results_by_date[date]:
      results.append(MatchData(
        date, current_number, result['calendar_date'], result['home'], result['away'],
        result['result'], result['winner']
      ))
      current_number += 1
  for result in results_dict['data']:
    if result['number'] not in number_to_date:
      results.append(MatchData(
        result['date'], result['number'], result['calendar_date'], result['home'],
        result['away'], result['result'], result['winner']
      ))
  return results


def parse_filename(filename: str) -> str:
  """parse filename"""
  with open(filename, 'r', encoding='utf-8') as infile:
    for line in infile:
      if 'ssssssssss' in line:
        _, og_filename = line.strip().split('|')
        break
  return og_filename
