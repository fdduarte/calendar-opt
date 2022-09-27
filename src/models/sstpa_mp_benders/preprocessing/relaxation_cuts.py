from time import time
from gurobipy import GRB
from ....libs.argsparser import args
from ..subproblem import subproblem
from ..master import master
from ...sstpa_mp import create_model as sstpa
from .helpers import set_subproblem_values, generate_benders_cut
from ..utils import parse_vars, set_sstpa_restrictions, create_sstpa_restrictions


def relaxation_cuts(self):
  """
  Resuelve mediante descomposición de benders el problema maestro
  y subproblemas relajados, generando una colección de cortes que se aplicarán
  al problema maestro.
  """
  start_time = time()
  sstpa_model, sstpa_variables = sstpa(log=False, relaxed=True)
  create_sstpa_restrictions(self, sstpa_model)
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
    print(f'{"iteration": <10} | {"objVal": <8} | {"BestBd": <8} | {"Gap": <4} | {"Time": <4}')

  last_obj_val = 10000000
  while True:
    niter += 1

    m_model.optimize()

    # solución heurística
    sol = parse_vars(m_variables, m_model, is_binary=False)
    set_sstpa_restrictions(sstpa_model, sol, is_binary=False)
    sstpa_model.optimize()

    obj_val = round(m_model.objVal, 4)
    best_bound = round(m_model.ObjBound, 4)
    gap = None
    if sstpa_model.Status == GRB.OPTIMAL:
      heuristic_sol = round(sstpa_model.objVal, 5)
      gap = round((1 - (heuristic_sol / best_bound)) * 100, 1)
    else:
      gap = '-'

    if obj_val < last_obj_val and args.verbose:
      last_obj_val = obj_val
      fgap = f'{gap}%'
      spent_time = int(time() - start_time)
      spent_time = f"{spent_time}s"
      print(f"{niter: <10} | {obj_val: <8} | {best_bound: <8} | {fgap: <4} | {spent_time: <4}")

    if gap != '-' and gap / 100 < args.lp_gap:
      break

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
    print('\nRelaxation objective', m_model.objVal)
    print('Relaxation added', ncuts, 'cuts')
    print('Total time', round(time() - start_time, 2), 'seconds\n')

  return
