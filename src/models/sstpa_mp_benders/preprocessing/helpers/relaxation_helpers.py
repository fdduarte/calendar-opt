from itertools import product


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
      value = value_to_binary(x)
      subproblem_res['R3'][n, i, f, l].rhs = value

  # R4
  for j, f in product(I, F):
    value = 0
    for n in N:
      if EL[j][n] + EV[j][n] == 1:
        for theta in F:
          if theta <= l:
            x = master_vars['x'][n, theta].X
            x = value_to_binary(x)
            value += R[j][n] * x
      subproblem_res['R4'][j, i, f, l].rhs = PI[j] + value

  # R15
  if s == 'm':
    for j in I:
      if j != i:
        alpha = master_vars[f'alpha_{s}'][j, i, l].X
        alpha = value_to_binary(alpha)
        subproblem_res['R5M'][l, i, j].rhs = M[i] * (1 - alpha) - 1

  # R16
  if s == 'p':
    for j in I:
      if j != i:
        alpha = master_vars[f'alpha_{s}'][j, i, l].X
        alpha = value_to_binary(alpha)
        subproblem_res['R5P'][l, i, j].rhs = M[i] * alpha - 1

def generate_benders_cut(self, model, master_vars, subproblem_res, subproblem):
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
      r3 = subproblem_res['R3'][n, i, f, l]
      x = master_vars['x'][n, f].X
      value = value_to_binary(x)
      cut += r3.farkasDual * value

  # R14
  for j, f in product(I, F):
    r4 = subproblem_res['R4'][j, i, f, l]
    value = 0
    for n in N:
      if EL[j][n] + EV[j][n] == 1:
        for theta in F:
          if theta <= l:
            x = self.master_vars['x'][n, theta]
            x = model.cbGetSolution(x)
            x = value_to_binary(x)
            value += R[j][n] * x
    cut += r4.farkasDual * (PI[j] + value)

  # R15
  if s == 'm':
    for j in I:
      if j != i:
        r5m = subproblem_res['R5M'][l, i, j]
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        cut += r5m.farkasDual * (M[i] * (1 - alpha) - 1)

  # R16
  if s == 'p':
    for j in I:
      if j != i:
        r5p = subproblem_res['R5P'][l, i, j]
        alpha = self.master_vars[f'alpha_{s}'][j, i, l]
        alpha = model.cbGetSolution(alpha)
        alpha = value_to_binary(alpha)
        cut += r5p.farkasDual * (M[i] * alpha - 1)
  return cut


def value_to_binary(value: float):
  """Funcion que aproxima un float a el binario mas cercano"""
  if value > 0.5:
    return 1
  return 0
