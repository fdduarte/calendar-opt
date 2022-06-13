from gurobipy import LinExpr, quicksum
# pylint: disable=invalid-name


def set_subproblem_values(master, subproblem):
  """Dado el problema maestro, setea el lado derecho de las
  restricciones del subproblema (R15 y R16) que fijan a x y alpha"""
  i, l, s = _get_subproblem_indexes(subproblem)
  for cons in subproblem.getConstrs():
    name = cons.getAttr('ConstrName')
    # Set same x vars (R13)
    if 'R14' in name:
      n, f = _get_index(name)
      var = master.getVarByName(f'x[{n},{f}]')
      value = _to_int(master.cbGetSolution(var))
      cons.rhs = value
    # Set same alpha vars (R14)
    if 'R15' in name:
      j = _get_index(name)[0]
      var = master.getVarByName(f'alfa_{s}[{j},{i},{l}]')
      value = _to_int(master.cbGetSolution(var))
      cons.rhs = value


def generate_cut(subproblem, master, IIS=False):
  """
  Dado un subproblema resuelto, crea cortes de hamming con o sin
  el calculo de IIS.
  """
  i, l, s = _get_subproblem_indexes(subproblem)
  cut = LinExpr()
  for var in subproblem.getVars():
    name = var.VarName
    if 'x' in name:
      n, f = _get_index(name)
      master_var = master.getVarByName(name)
      if master.cbGetSolution(master_var) > 0.5:
        master_var = LinExpr(1 - master_var)
      if IIS:
        const = subproblem.getConstrByName(f'R14[{n},{f}]')
        if const.getAttr('IISConstr'):
          cut += master_var
      else:
        cut += master_var
    if 'alfa' in name:
      j = _get_index(name)[0]
      master_var = master.getVarByName(f'alfa_{s}[{j},{i},{l}]')
      if master.cbGetSolution(master_var) > 0.5:
        master_var = LinExpr(1 - master_var)
      if IIS:
        const = subproblem.getConstrByName(f'R15[{j}]')
        if const.getAttr('IISConstr'):
          cut += master_var
      else:
        cut += master_var
  return cut


def generate_benders_cut(self, subproblem_res, subproblem):
  """
  Dado un subproblema relajado, crea cortes de benders.
  """
  i, l, s = _get_subproblem_indexes(subproblem)
  N = self.params['N']
  F = self.params['F']
  I = self.params['I']
  EL = self.params['EL']
  EV = self.params['EV']
  M = 61
  cut = LinExpr()
  for n in N:
    for f in F:
      if f > l:
        r16 = subproblem_res['R16'][n, i, f, l]
        x = self.master_vars['x'][n, f]
        cut += r16.farkasDual * x
  for j in I:
    for f in F:
      if f > l:
        x_sum = LinExpr()
        for theta in F:
          if l >= theta:
            for n in N:
              if EL[j][n] + EV[j][n] == 1:
                x = self.master_vars['x'][n, theta]
                x_sum += x
        r17 = subproblem_res['R17'][j, i, f, l]
        cut += r17.farkasDual * self.params['PI'][j] * (x_sum)
  if s == 'm':
    for j in I:
      if j != i:
        r18 = subproblem_res['R18'][l, i, j]
        alpha = self.master_vars['alpha_m'][j, i, l]
        cut += r18.farkasDual * (M - 1 - M * alpha)
  if s == 'p':
    for j in I:
      if j != i:
        r18 = subproblem_res['R18'][l, i, j]
        alpha = self.master_vars['alpha_p'][j, i, l]
        cut += r18.farkasDual * (M * alpha - 1)

  return cut


def _get_subproblem_indexes(subproblem):
  name = subproblem.getAttr('ModelName')
  _, name = name.split(': ')
  i, l, s = name.split('-')
  return i, int(l), s


def _get_index(name):
  name = name.strip(']')
  _, name = name.split('[')
  index = [int(i) if i.isdigit() else i for i in name.split(',')]
  return tuple(index)


def _to_int(value):
  if value > 0.5:
    return 1
  return 0
