from .helpers import value_to_binary


# pylint: disable=invalid-name
def set_subproblem_values(self, model, indexes):
  """Dado el problema maestro, setea el lado derecho de las
  restricciones del subproblema (R15 y R16) que fijan a x y alpha"""
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']

  for n in N:
    for f in F:
      x = self.master_vars['x'][n, f]
      x = model.cbGetSolution(x)
      value = value_to_binary(x)
      self.subproblem_res[i, l, s]['R13'][n, f].rhs = value
  for j in I:
    alpha = self.master_vars[f'alpha_{s}'][j, i, l]
    alpha = model.cbGetSolution(alpha)
    value = value_to_binary(alpha)
    self.subproblem_res[i, l, s]['R14'][j, i, l].rhs = value
  self.subproblem_model[i, l, s].update()


def _get_index(name):
  name = name.strip(']')
  _, name = name.split('[')
  index = [int(i) if i.isdigit() else i for i in name.split(',')]
  return tuple(index)


def _to_int(value):
  if value > 0.5:
    return 1
  return 0
