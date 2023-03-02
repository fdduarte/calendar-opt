def remove_duplicates(iterable):
  """Elimina los elementos duplicados de una lista"""
  new_iter = []
  for i in iterable:
    if i not in new_iter:
      new_iter.append(i)
  return new_iter


def closed_interval(lb, ub):
  """Obtiene el intervalo entre dos márgenes. de ser iguales retorna una lista vacía"""
  if lb == ub:
    return []
  else:
    return list(range(lb + 1, ub))
