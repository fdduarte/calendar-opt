from itertools import product
from gurobipy import GRB
from .subproblem import subproblem as _subproblem
from .master import master as _master
from ..sstpa_mp import create_model as _sstpa
from .utils import (
  set_subproblem_values,
  parse_vars,
  set_sstpa_restrictions,
  set_cb_sol,
  create_sstpa_restrictions
)
from .cuts import (
  generate_benders_cut,
  generate_hamming_cut,
  generate_policy_cuts,
)
from .preprocessing import preprocess
from ...libs.argsparser import args
from ...libs.logger import log, logger
from ...libs.timer import timer
from ...libs.output import write_sol_file_from_dict
from ...libs.output_namer import name_output
from .parse_params import parse_params


# pylint: disable=invalid-name
class Benders:
  """Clase del modelo de optimización SSTPA con descomposición de benders"""
  def __init__(self):
    self.params = parse_params()
    self.subproblem_indexes = list(product(self.params['I'], self.params['F'], ["m", "p"]))
    # Models
    self._init_sstpa_model()
    self._init_master_model()
    self._init_subproblems()
    self.last_sol = None
    self.visited_sols = set()

  def _init_sstpa_model(self):
    """Instancia el modelo SSTPA"""
    m, variables = _sstpa(log=False)
    self.sstpa_model = m
    self.sstpa_variables = variables
    create_sstpa_restrictions(self, self.sstpa_model)

  def _init_master_model(self):
    """Instancia modelo maestro"""
    m, variables = _master(self.params)
    self.master_model = m
    self.master_vars = variables

  def _init_subproblems(self, relaxed=True):
    """Instancia los subproblemas"""
    self.subproblem_model = {}
    self.subproblem_res = {}
    self.subproblem_vars = {}
    if relaxed:
      self.subproblem_relaxed_model = {}
      self.subproblem_relaxed_res = {}
    for i, l, s in self.subproblem_indexes:
      m, res, variables = _subproblem(i, l, s, self.params)
      self.subproblem_model[i, l, s] = m
      self.subproblem_res[i, l, s] = res
      self.subproblem_vars[i, l, s] = variables
      if relaxed:
        m, res = _subproblem(i, l, s, self.params, True)
        self.subproblem_relaxed_model[i, l, s] = m
        self.subproblem_relaxed_res[i, l, s] = res

  @timer.timeit('callback')
  def _lazy_cb(self, model, where):
    """Gurobi callback"""
    mipnode = True
    mipsol = True
    try:
      if where == GRB.Callback.MIPNODE and mipnode:
        timer.timestamp('MIPNODE')
        if self.last_sol and not str(self.last_sol) in self.visited_sols:
          # Set SSTPA x values and optimize
          self.sstpa_model.optimize()

          assert self.sstpa_model.Status == GRB.OPTIMAL, 'Modelo no es factible'
          # Pass solution to current model and get incumbent
          set_cb_sol(model, self.sstpa_model)

          # Add solution to visited
          self.visited_sols.add(str(self.last_sol))
        timer.timestamp('MIPNODE')

        node_count = model.cbGet(GRB.Callback.MIPNODE_NODCNT)
        if int(node_count) == 0 and args.mipnode_cuts:  # nodo raíz
          for i, l, s in self.subproblem_indexes:
            timer.timestamp('cortes de benders')
            subproblem_relaxed = self.subproblem_relaxed_model[i, l, s]
            subproblem_relaxed_res = self.subproblem_relaxed_res[i, l, s]

            sub = (self.subproblem_relaxed_model, self.subproblem_relaxed_res)
            set_subproblem_values(self, model, sub, (i, l, s), relaxed=True, cb=False, mn=True)

            timer.timestamp('opt benders sub')
            subproblem_relaxed.optimize()
            logger.increment_stats('sub(r) solved')
            timer.timestamp('opt benders sub')

            if subproblem_relaxed.Status == GRB.INFEASIBLE:
              cut = generate_benders_cut(self, model, subproblem_relaxed_res, subproblem_relaxed)
              model.cbLazy(cut <= 0)
              logger.increment_stats('benders cut')
            timer.timestamp('cortes de benders')

      if where == GRB.Callback.MIPSOL and mipsol:
        timer.timestamp('MIPSOL')
        # Si estamos en un nodo de solución entera, seteamos last_sol a la
        # solucón del nodo.
        self.last_sol = parse_vars(self.master_vars, self.master_model, callback=True)
        outfile_name = name_output()
        write_sol_file_from_dict(self.last_sol, f'logs/output/{outfile_name}.temp.sol', model.ModelName)
        set_sstpa_restrictions(self.sstpa_model, self.last_sol)

        all_feasible = True
        for i, l, s in self.subproblem_indexes:
          if l not in self.params['Rp']:
            continue
          # Se setean las restricciones que fijan a x y alpha en el subproblema
          # y se resuelve.
          timer.timestamp('cortes de hamming')
          subproblem = self.subproblem_model[i, l, s]
          sub = (self.subproblem_model, self.subproblem_res)
          set_subproblem_values(self, model, sub, (i, l, s))
          timer.timestamp('opt hamming sub')
          subproblem.optimize()
          logger.increment_stats('subsolved')
          timer.timestamp('opt hamming sub')

          # Si el modelo es infactible, se agregan cortes de factibilidad
          if subproblem.Status == GRB.INFEASIBLE:
            all_feasible = False
            if args.IIS:
              timer.timeit_nd(subproblem.computeIIS, 'IIS')
            cut = generate_hamming_cut(self, (i, l, s), model, IIS=args.IIS)
            logger.increment_stats('hamming cut', verbose=True)
            model.cbLazy(cut >= 1)

          timer.timestamp('cortes de hamming')

          if args.benders_cuts:
            # Se resuelve la relajación y agregan cortes de Benders
            timer.timestamp('cortes de benders')
            subproblem_relaxed = self.subproblem_relaxed_model[i, l, s]
            subproblem_relaxed_res = self.subproblem_relaxed_res[i, l, s]

            sub = (self.subproblem_relaxed_model, self.subproblem_relaxed_res)
            set_subproblem_values(self, model, sub, (i, l, s), relaxed=True)

            timer.timestamp('opt benders sub')
            subproblem_relaxed.optimize()
            logger.increment_stats('sub(r) solved')
            timer.timestamp('opt benders sub')

            if subproblem_relaxed.Status == GRB.INFEASIBLE:
              cut = generate_benders_cut(self, model, subproblem_relaxed_res, subproblem_relaxed)
              model.cbLazy(cut <= 0)
              logger.increment_stats('benders cut')
            timer.timestamp('cortes de benders')
        if all_feasible:
          generate_policy_cuts(self, model)
          logger.increment_stats('policy cuts')
        timer.timestamp('MIPSOL')

    except Exception as err:
      log('error', 'callback')
      log('error', err)
      model.terminate()
      raise Exception from err

  def optimize(self):
    """
    Optimiza el maestro con callbacks.
    """
    # Currying
    def callback(x, y):
      self._lazy_cb(x, y)

    if args.preprocess:
      timer.timestamp('preprocess')
      preprocess(self, self.master_model, self.master_vars)
      timer.timestamp('preprocess')

    self.master_model.optimize(callback)
    if self.master_model.Status == GRB.INFEASIBLE:
      log('result', 'Modelo Infactible')

  def getVars(self):
    """Retorna las variables del modelo maestro"""
    return self.master_model.getVars()

  def objVal(self):
    """Retorna el valor objetivo"""
    return self.master_model.objVal

  def write(self, *m_args):
    """Escribe el modelo maestro"""
    return self.master_model.write(*m_args)


def create_model():
  """Crea modelo SSTPA MP Benders"""
  return Benders()
