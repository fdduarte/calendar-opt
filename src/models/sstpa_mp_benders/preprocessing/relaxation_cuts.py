from gurobipy import GRB
from ....libs.argsparser import args
from ..subproblem import subproblem
from ..master import master
from .helpers import set_subproblem_values, generate_benders_cut


def relaxation_cuts(self):
  """
  Resuelve mediante descomposición de benders el problema maestro
  y subproblemas relajados, generando una colección de cortes que se aplicarán
  al problema maestro.
  """
  m_model, m_variables = master(self.params, relaxed=True, log=False)
  s_model, s_res = {}, {}
  for i, l, s in self.subproblem_indexes:
    sub, r = subproblem(i, l, s, self.params, relaxed=True)
    s_model[i, l, s] = sub
    s_res[i, l, s] = r

  niter = 0
  ncuts = 0

  if args.verbose:
    print('\nSolving problem relaxation')
    print(f'{"iteration": <10} | {"objVal": <8}')

  last_obj_val = 10000000
  while True:
    niter += 1

    m_model.optimize()
    obj_val = round(m_model.objVal, 5)
    if obj_val < last_obj_val and args.verbose:
      last_obj_val = obj_val
      print(f"{niter: <10} | {obj_val: <8}")

    all_factible = True
    for i, l, s in self.subproblem_indexes:
      sub = s_model[i, l, s]
      sub_res = s_res[i, l, s]
      set_subproblem_values(self, (i, l, s), sub_res, m_variables)
      sub.optimize()
      if sub.Status == GRB.INFEASIBLE:
        cut = generate_benders_cut(self, (i, l, s), m_variables, sub_res)
        ncuts += 1
        m_model.addConstr(cut <= 0)

        # agregamoso corte al problema normal
        cut = generate_benders_cut(self, (i, l, s), self.master_vars, sub_res)
        self.master_model.addConstr(cut <= 0)
        all_factible = False
    if all_factible:
      break

  if args.verbose:
    print('\nRelaxation objectibe', m_model.objVal)
    print('Relaxation added', ncuts, 'cuts\n')
  return
