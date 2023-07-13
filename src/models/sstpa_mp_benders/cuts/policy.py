from itertools import product
from ....libs.array_tools import closed_interval
from ....libs.argsparser import args


def generate_policy_cuts(self, model):
  """
  Dado un subproblema resuelto, crea cortes de hamming con o sin
  el calculo de IIS.
  """
  if not args.policy:
    return
  Rp = self.params['Rp']
  I = self.params['I']
  F = self.params['F']
  M = self.params['M']
  for i, l in enumerate(Rp):
    if i + 1 < len(Rp):
      lp1 = Rp[i + 1]
    elif l != F[-1]:
      lp1 = F[-1] + 1
    else:
      continue
    for _l in closed_interval(l, lp1):
      for i, j in product(I, I):
        if j != i:
          pm_j = self.subproblem_vars[i, l, 'm']['p'][j, i, l, F[-1]].X
          pm_i = self.subproblem_vars[i, l, 'm']['p'][i, i, l, F[-1]].X
          pp_j = self.subproblem_vars[i, l, 'p']['p'][j, i, l, F[-1]].X
          pp_i = self.subproblem_vars[i, l, 'p']['p'][i, i, l, F[-1]].X
          model.cbLazy(pm_j - pm_i <= M[j] * (1 - self.master_vars['alpha_m'][j, i, _l]))
          model.cbLazy(pp_i - pp_j <= M[i] * self.master_vars['alpha_p'][j, i, _l])
