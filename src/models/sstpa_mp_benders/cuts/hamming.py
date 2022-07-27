from gurobipy import LinExpr


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
        const = self.subproblem_res[i, l, s]['R1'][n, f]
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
      const = self.subproblem_res[i, l, s]['R2'][j, i, l]
      if const.getAttr('IISConstr'):
        cut += alpha
    else:
      cut += alpha
  return cut
