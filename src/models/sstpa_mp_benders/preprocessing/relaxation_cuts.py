from gurobipy import GRB
from ..subproblem import subproblem
from ..master import master
from .helpers import set_subproblem_values


def relaxation_cuts(self):
  """
  Resuelve mediante descomposición de benders el problema maestro
  y subproblemas relajados, generando una colección de cortes que se aplicarán
  al problema maestro
  """
  m_model, m_variables = master(self.params, relaxed=True)
  s_model, s_res = {}, {}
  for i, l, s in self.subproblem_indexes:
    sub, r = subproblem(i, l, s, self.params, relaxed=True)
    s_model[i, l, s] = sub
    s_res[i, l, s] = r

  while True:
    m_model.optimize()

    for i, l, s in self.subproblem_indexes:
      sub = s_model[i, l, s]
      sub_res = s_res[i, l, s]
      set_subproblem_values(self, (i, l, s), sub_res, m_variables)
      sub.optimize()
      if sub.Status == GRB.INFEASIBLE:
        # generar cortes
        continue
    break
  exit()
  return
