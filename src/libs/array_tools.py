def remove_duplicates(iterable):
  """Elimina los elementos duplicados de una lista"""
  new_iter = []
  for i in iterable:
    if i not in new_iter:
      new_iter.append(i)
  return new_iter
