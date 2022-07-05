from gurobipy import LinExpr
from .helpers import get_subproblem_indexes


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
        const = self.subproblem_res[i, l, s]['R13'][n, f]
        if const.getAttr('IISConstr'):
          cut += x
      else:
        cut += x
  # alpha
  for j in I:
    alpha = self.master_vars[f'alpha_{s}'][j, i, l]
    if master.cbGetSolution(alpha) > 0.5:
      alpha = LinExpr(1 - alpha)
    if IIS:
      const = self.subproblem_res[i, l, s]['R14'][j, i, l]
      if const.getAttr('IISConstr'):
        cut += alpha
    else:
      cut += alpha
  return cut


def generate_hamming_cut_depr(self, indexes, master, IIS=False):
  """
  Dado un subproblema resuelto, crea cortes de hamming con o sin
  el calculo de IIS.
  """
  i, l, s = indexes
  subproblem = self.subproblem_model[i, l, s]
  cut = LinExpr()
  for var in subproblem.getVars():
    name = var.VarName
    if 'x' in name:
      n, f = _get_index(name)
      master_var = master.getVarByName(name)
      print(master_var, master.cbGetSolution(master_var))
      if master.cbGetSolution(master_var) > 0.5:
        master_var = LinExpr(1 - master_var)
      if IIS:
        const = subproblem.getConstrByName(f'R13[{n},{f}]')
        if const.getAttr('IISConstr'):
          cut += master_var
      else:
        cut += master_var
    if 'alpha' in name:
      j = _get_index(name)[0]
      master_var = master.getVarByName(f'alpha_{s}[{j},{i},{l}]')
      if master.cbGetSolution(master_var) > 0.5:
        master_var = LinExpr(1 - master_var)
      if IIS:
        const = subproblem.getConstrByName(f'R14[{j},{i},{l}]')
        if const.getAttr('IISConstr'):
          cut += master_var
      else:
        cut += master_var
  # print(cut)
  return cut


def generate_benders_cut(self, subproblem_res, subproblem):
  """
  Dado un subproblema relajado, crea cortes de benders.
  """
  i, l, s = get_subproblem_indexes(subproblem)
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  PI = self.params['PI']

  # R13
  cut = LinExpr()
  for n in N:
    for f in F:
      if f > l:
        r13 = subproblem_res['R13'][n, f]
        x = self.master_vars['x'][n, f]
        cut += r13.farkasDual * x

  # R14
  for j in I:
    if j != i:
      r14 = subproblem_res['R14'][j, i, l]
      alpha = self.master_vars[f'alpha_{s}'][j, i, l]
      cut += r14.farkasDual * alpha

  # R16
  for j in I:
    for f in F:
      if f > l:
        r16 = subproblem_res['R16'][j, i, f, l]
        cut += r16.farkasDual * PI[j]

  # R17
  if s == 'm':
    for j in I:
      if j != i:
        r17 = subproblem_res['R17'][l, i, j]
        cut += r17.farkasDual * alpha
  if s == 'p':
    for j in I:
      if j != i:
        r17 = subproblem_res['R18'][l, i, j]
        cut += r17.farkasDual * alpha
  return cut


def _get_index(name):
  name = name.strip(']')
  _, name = name.split('[')
  index = [int(i) if i.isdigit() else i for i in name.split(',')]
  return tuple(index)