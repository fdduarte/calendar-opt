from itertools import product
from gurobipy import LinExpr


def set_subproblem_values(self, indexes, subproblem_res, master_vars):
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  R = self.params['R']
  M = self.params['M']
  PI = self.params['PI']
  EV = self.params['EV']
  EL = self.params['EL']

  # R3
  for n, f in product(N, F):
    if f > l:
      x = master_vars['x'][n, f].X
      subproblem_res['R3'][n, i, f, l].rhs = x

  # R4
  for j, f in product(I, F):
    if f > l:
      value = 0
      for n in N:
        if EL[j][n] + EV[j][n] == 1:
          for theta in F:
            if theta <= l:
              x = master_vars['x'][n, theta].X
              value += R[j][n] * x
      subproblem_res['R4'][j, i, f, l].rhs = PI[j] + value

  # R5M
  if s == 'm':
    for j in I:
      if j != i:
        alpha = master_vars[f'alpha_{s}'][j, i, l].X
        subproblem_res['R5M'][l, i, j].rhs = (1 - M[i] + M[i] * alpha)

  # R5P
  if s == 'p':
    for j in I:
      if j != i:
        alpha = master_vars[f'alpha_{s}'][j, i, l].X
        subproblem_res['R5P'][l, i, j].rhs = (1 - M[i] * alpha)


def generate_benders_cut(self, indexes, master_vars, subproblem_res):
  """
  Dado un subproblema relajado, crea cortes de benders.
  """
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  PI = self.params['PI']
  R = self.params['R']
  M = self.params['M']
  PI = self.params['PI']
  EV = self.params['EV']
  EL = self.params['EL']

  # R3
  cut = LinExpr()
  for n, f in product(N, F):
    if f > l:
      r3 = subproblem_res['R3'][n, i, f, l]
      x = master_vars['x'][n, f]
      cut += -r3.farkasDual * x

  # R4
  for j, f in product(I, F):
    if f > l:
      r4 = subproblem_res['R4'][j, i, f, l]
      value = 0
      for n in N:
        if EL[j][n] + EV[j][n] == 1:
          for theta in F:
            if theta <= l:
              x = master_vars['x'][n, theta]
              value += R[j][n] * x
      cut += -r4.farkasDual * (PI[j] + value)

  # R5M
  if s == 'm':
    for j in I:
      if j != i:
        r5m = subproblem_res['R5M'][l, i, j]
        alpha = master_vars[f'alpha_{s}'][j, i, l]
        cut += -r5m.farkasDual * (M[i] - M[i] * alpha)

  # R5P
  if s == 'p':
    for j in I:
      if j != i:
        r5p = subproblem_res['R5P'][l, i, j]
        alpha = master_vars[f'alpha_{s}'][j, i, l]
        cut += -r5p.farkasDual * (1 * M[i] * alpha)

  return cut
