from itertools import product
from .helpers import value_to_binary


# pylint: disable=invalid-name
def set_subproblem_values(self, model, indexes, relaxed=False):
  """
  Dado el problema maestro, setea el lado derecho de las
  restricciones del subproblema (R15, R16 y  R17/R18)
  """
  if relaxed:
    _set_subproblem_values_relaxed(self, model, indexes)
  else:
    _set_subproblem_values_normal(self, model, indexes)


def _set_subproblem_values_relaxed(self, model, indexes):
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  R = self.params['R']
  M = self.params['M']
  PI = self.params['PI']
  EV = self.params['EV']
  EL = self.params['EL']

  subproblem_model = self.subproblem_relaxed_model
  subproblem_res = self.subproblem_relaxed_res

  # R13
  for n, f in product(N, F):
    if f > l:
      x = self.master_vars['x'][n, f]
      x = model.cbGetSolution(x)
      value = value_to_binary(x)
      subproblem_res[i, l, s]['R3'][n, i, f, l].rhs = value

  # R14
  for j, f in product(I, F):
    value = 0
    for n in N:
      if EL[j][n] + EV[j][n] == 1:
        for theta in F:
          if theta <= l:
            x = self.master_vars['x'][n, theta]
            x = model.cbGetSolution(x)
            x = value_to_binary(x)
            value += R[j][n] * x
      subproblem_res[i, l, s]['R4'][j, i, f, l].rhs = PI[j] + value

  # R15
  if s == 'm':
    for j in I:
      if j != i:
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        subproblem_res[i, l, s]['R5M'][l, i, j].rhs = M[i] * (1 - alpha) - 1

  # R16
  if s == 'p':
    for j in I:
      if j != i:
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        subproblem_res[i, l, s]['R5P'][l, i, j].rhs = M[i] * alpha - 1

  subproblem_model[i, l, s].update()


def _set_subproblem_values_normal(self, model, indexes):
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']

  subproblem_model = self.subproblem_model
  subproblem_res = self.subproblem_res

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
