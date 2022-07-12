from itertools import product
from .helpers import value_to_binary


# pylint: disable=invalid-name
def set_subproblem_values(self, model, indexes):
  """
  Dado el problema maestro, setea el lado derecho de las
  restricciones del subproblema (R15, R16 y  R17/R18)
  """
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  R = self.params['R']
  M = self.params['M']
  PI = self.params['PI']
  EV = self.params['EV']
  EL = self.params['EL']

  # R13
  for n, f in product(N, F):
    if f > l:
      x = self.master_vars['x'][n, f]
      x = model.cbGetSolution(x)
      value = value_to_binary(x)
      self.subproblem_res[i, l, s]['R13'][n, i, f, l].rhs = value

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
      self.subproblem_res[i, l, s]['R14'][j, i, f, l].rhs = PI[j] + value

  # R15
  if s == 'm':
    for j in I:
      if j != i:
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        self.subproblem_res[i, l, s]['R15'][l, i, j].rhs = M[i] * (1 - alpha) - 1

  # R16
  if s == 'p':
    for j in I:
      if j != i:
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        self.subproblem_res[i, l, s]['R16'][l, i, j].rhs = M[i] * alpha - 1

  self.subproblem_model[i, l, s].update()
