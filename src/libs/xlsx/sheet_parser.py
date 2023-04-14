"""
El siguiente módulo se encarga de leer el archivo en formato
.xlsx y retornar una estructura de datos.
"""
import math
import pandas as pd
from ...types import TeamData, MatchData


def read_teams_file(filename: str) -> dict[str, TeamData]:
  """
  Función que lee la primera hoja del archivo .xlsx que contiene los datos.
  Retorna un diccionario cuya llave es el alias del equipo, y el valor es un
  diccionario con los datos del equipo.
  """
  parsed_data = {}
  data = pd.read_excel(filename, sheet_name="Equipos", index_col=0)
  for _, row in data.iterrows():
    team_data = TeamData(
        full_name=str(row["EQUIPO"]).strip(),
        points=int(row["Puntos al finalizar la primera rueda"]),
        home_matches_left=int(row["Localías faltantes"])
    )
    parsed_data[str(row["ALIAS"])] = team_data
  return parsed_data


def read_results_file(filename: str) -> list[MatchData]:
  """
  Función que lee la segunda oja del archivo .xlsx que contiene los datos.
  """
  parsed_data = []
  match_number = 1
  data = pd.read_excel(filename, sheet_name="Resultados")
  for _, row in data.iterrows():
    if not math.isnan(row["Jornada"]):
      date = row["Jornada"]
    else:
      parsed_result = _parse_result(row["Resultado"])
      match = MatchData(
          date=int(date),
          number=match_number,
          calendar_date=row["Fecha"],
          home=row["Local"].strip(),
          away=row["Visita"].strip(),
          result="-".join([str(i) for i in parsed_result.values()]),
          winner=_get_winner(parsed_result),
      )
      match_number += 1
      parsed_data.append(match)
  return parsed_data


def parse_filename(filename: str):
  """not implemented"""
  raise Exception('Method not implemented')


def _parse_result(result: str) -> dict[str, int]:
  """
  Función que parea el strings de resultados, retornando
  una diccionario con el resultado
  """
  home, away = [i.strip() for i in result.split(":")]
  return {"home": int(home), "away": int(away)}


def _get_winner(result: dict[str, int]) -> str:
  """
  Función que, dado un diccionario de resultados returna
  que equipo gano (local o visita o empate).
  """
  if result["home"] > result["away"]:
    return "home"
  if result["home"] < result["away"]:
    return "away"
  return "draw"


if __name__ == "__main__":
  file_1 = read_teams_file("./data/Datos.xlsx")
  file_2 = read_results_file("./data/Datos.xlsx")
