# hardcodeado por mientars

curr_points = {
  'A': 4,
  'B': 3,
  'C': 3,
  'D': 7,
  'E': 4,
  'F': 4
}

matches = {
  4: ['C-B', 'E-D', 'A-F'],
  5: ['D-F', 'B-E', 'C-A'],
  6: ['F-E', 'D-C', 'B-A']
}

results = {
  'C-B': {'C': 0, 'B': 3},
  'E-D': {'E': 3, 'D': 0},
  'A-F': {'A': 3, 'F': 0},
  'D-F': {'D': 3, 'F': 0},
  'B-E': {'B': 1, 'E': 1},
  'C-A': {'C': 3, 'A': 0},
  'F-E': {'F': 0, 'E': 3},
  'D-C': {'D': 3, 'C': 0},
  'B-A': {'B': 1, 'A': 1}
}

# Naive
# Al parecer no funciona, no necesariamente con
# el máximo de puntos se alcanza el mejor lugar,
# ya que puede pasar que puede que un equipo no
# gane 0 puntos (por ej empate doble en primer lugar y
# ambos estan para jugar última fecha)

max_positions = {
  4: {}, 5: {}, 6: {}
}

for date in range(4, 7):
  for match in matches[date]:
    team_a, team_b = match.split('-')
    curr_points[team_a] += results[match][team_a]
    curr_points[team_b] += results[match][team_b]
  positions = list(curr_points.values())
  positions.sort(reverse=True)
  available_points = (6 - date) * 3
  for team, points in curr_points.items():
    for i, p in enumerate(positions, start=1):
      if points + available_points > p:
        break
    max_positions[date][team] = i

for team in curr_points.keys():
  for date in range(4, 7):
    print(team,date,max_positions[date][team])