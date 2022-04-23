"""
El siguiente módulo se encarga de, dado los datos de una instancia,
retornar un diccionario con los parametros del modelo de optimización
"""
from typing import cast, Any
import sheet_parser

params: dict[str, Any] = {}

teams_data = sheet_parser.read_teams_file("./data/Datos.xlsx")
results_data = sheet_parser.read_results_file("./data/Datos.xlsx")

# Lista de equipos del torneo
params['teams'] = list(teams_data.keys())

# Lista de los partidos del torneo por número
params['matches'] = [match['number'] for match in cast(list[dict[str, int]], results_data)]

# To Do: Obtener de argv las fechas a programar
_max_points = max([team['points'] for team in teams_data.values()]) + 15 * 3
_min_points = min([team['points'] for team in teams_data.values()])
# Lista de los puntos disponibles en el torneo
params['available_points'] = list(range(_min_points, _max_points + 1))

# Diccionario de los puntos iniciales de un equipo en el torneo

# To Do: Si la fecha inicial es != a la 16
params['team_points'] = {team: team_data['points'] for team, team_data in teams_data.items()}

if __name__ == '__main__':
  print(params)

