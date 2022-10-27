from itertools import product
from .helpers import value_to_binary


# pylint: disable=invalid-name
def set_subproblem_values(self, model, subproblem, indexes, relaxed=False, cb=True, mn=False):
  """
  Dado el problema maestro, setea el lado derecho de las
  restricciones del subproblema (R15, R16 y  R17/R18)
  """
  if relaxed:
    _set_subproblem_values_relaxed(self, model, subproblem, indexes, cb, mn)
  else:
    _set_subproblem_values_normal(self, model, subproblem, indexes)


def _set_subproblem_values_relaxed(self, model, subproblem, indexes, cb, mn):
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  R = self.params['R']
  M = self.params['M']
  PI = self.params['PI']
  EV = self.params['EV']
  EL = self.params['EL']

  subproblem_model, subproblem_res = subproblem

  # R3
  for n, f in product(N, F):
    if f > l:
      x = self.master_vars['x'][n, f]
      if cb:
        x = model.cbGetSolution(x)
      elif mn:
        x = model.cbGetNodeRel(x)
      else:
        x = x.X
      value = value_to_binary(x)
      subproblem_res[i, l, s]['R3'][n, i, f, l].rhs = value

  # R4
  for j, f in product(I, F):
    if f > l:
      value = 0
      for n in N:
        if EL[j][n] + EV[j][n] == 1:
          for theta in F:
            if theta <= l:
              x = self.master_vars['x'][n, theta]
              if cb:
                x = model.cbGetSolution(x)
              elif mn:
                x = model.cbGetNodeRel(x)
              else:
                x = x.X
              x = value_to_binary(x)
              value += R[j][n] * x
      subproblem_res[i, l, s]['R4'][j, i, f, l].rhs = PI[j] + value

  # R5M
  if s == 'm':
    for j in I:
      if j != i:
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        if cb:
          alpha = model.cbGetSolution(alpha)
        elif mn:
          alpha = model.cbGetNodeRel(alpha)
        else:
          alpha = alpha.X
        alpha = value_to_binary(alpha)
        subproblem_res[i, l, s]['R5M'][l, i, j].rhs = (M[j] * alpha - M[j])

  # R5P
  if s == 'p':
    for j in I:
      if j != i:
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        if cb:
          alpha = model.cbGetSolution(alpha)
        elif mn:
          alpha = model.cbGetNodeRel(alpha)
        else:
          alpha = model.X
        alpha = value_to_binary(alpha)
        subproblem_res[i, l, s]['R5P'][l, i, j].rhs = (-M[i] * alpha)

  subproblem_model[i, l, s].update()


def _set_subproblem_values_normal(self, model, subproblem, indexes):
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']

  subproblem_model, subproblem_res = subproblem

  # R1
  for n, f in product(N, F):
    x = self.master_vars['x'][n, f]
    x = model.cbGetSolution(x)
    value = value_to_binary(x)
    subproblem_res[i, l, s]['R1'][n, f].rhs = value

  # R2
  for j in I:
    alpha = self.master_vars[f'alpha_{s}'][j, i, l]
    alpha = model.cbGetSolution(alpha)
    value = value_to_binary(alpha)
    subproblem_res[i, l, s]['R2'][j, i, l].rhs = value

  subproblem_model[i, l, s].update()
