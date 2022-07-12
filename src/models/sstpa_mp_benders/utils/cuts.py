from itertools import product
from gurobipy import LinExpr
from .helpers import get_subproblem_indexes, value_to_binary


def generate_hamming_cut(self, indexes, master, IIS=False):
  """
  Dado un subproblema resuelto, crea cortes de hamming con o sin
  el calculo de IIS.
  """
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  cut = LinExpr()
  # x
  for n in N:
    for f in F:
      x = self.master_vars['x'][n, f]
      if master.cbGetSolution(x) > 0.5:
        x = LinExpr(1 - x)
      if IIS:
        # const = self.subproblem_res[i, l, s]['R13'][n, f]
        # if const.getAttr('IISConstr'):
        cut += x
      else:
        cut += x
  # alpha
  for j in I:
    alpha = self.master_vars[f'alpha_{s}'][j, i, l]
    if master.cbGetSolution(alpha) > 0.5:
      alpha = LinExpr(1 - alpha)
    if IIS:
      # const = self.subproblem_res[i, l, s]['R14'][j, i, l]
      # if const.getAttr('IISConstr'):
      cut += alpha
    else:
      cut += alpha
  return cut


def generate_benders_cut(self, model, subproblem_res, subproblem):
  """
  Dado un subproblema relajado, crea cortes de benders.
  """
  i, l, s = get_subproblem_indexes(subproblem)
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  PI = self.params['PI']
  R = self.params['R']
  M = self.params['M']
  PI = self.params['PI']
  EV = self.params['EV']
  EL = self.params['EL']

  # R13
  cut = LinExpr()
  for n, f in product(N, F):
    if f > l:
      r13 = subproblem_res['R13'][n, i, f, l]
      x = self.master_vars['x'][n, f]
      x = model.cbGetSolution(x)
      value = value_to_binary(x)
      cut += r13.farkasDual * value

  # R14
  for j, f in product(I, F):
    r14 = subproblem_res['R14'][j, i, f, l]
    value = 0
    for n in N:
      if EL[j][n] + EV[j][n] == 1:
        for theta in F:
          if theta <= l:
            x = self.master_vars['x'][n, theta]
            x = model.cbGetSolution(x)
            x = value_to_binary(x)
            value += R[j][n] * x
    cut += r14.farkasDual * (PI[j] + value)

  # R15
  if s == 'm':
    for j in I:
      if j != i:
        r15 = subproblem_res[i, l, s]['R15'][l, i, j]
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        cut += r15.farkasDual * (M[i] * (1 - alpha) - 1)

  # R16
  if s == 'p':
    for j in I:
      if j != i:
        r16 = subproblem_res[i, l, s]['R16'][l, i, j]
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        cut += r16.farkasDual * (M[i] * alpha - 1)
  return cut
