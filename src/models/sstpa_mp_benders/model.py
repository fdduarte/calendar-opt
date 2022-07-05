from gurobipy import GRB
from .subproblem import subproblem as _subproblem
from .master import master as _master
from ..sstpa_mp import create_model as _sstpa
from .utils import (
  set_subproblem_values,
  generate_hamming_cut,
  parse_vars,
  set_sstpa_restrictions,
  set_cb_sol,
  create_sstpa_restrictions,
  generate_benders_cut,
  preprocess
)
from ...libs.argsparser import args
from ...libs.timer import timer
from .parse_params import parse_params


# pylint: disable=invalid-name
class Benders:
  """Clase del modelo de optimización SSTPA con descomposición de benders"""
  def __init__(self):
    self.params = parse_params()
    self.subproblem_indexes = [(i, l, s) for i in self.params['I']
                               for l in self.params['F'] for s in ["m", "p"]]
    # Models
    self._init_sstpa_model()
    self._init_master_model()
    self._init_subproblems()
    self.last_sol = None
    self.visited_sols = set()

  def _init_sstpa_model(self):
    """Instancia el modelo SSTPA"""
    self.sstpa_model = _sstpa()
    self.sstpa_model.Params.LogToConsole = 0
    create_sstpa_restrictions(self, self.sstpa_model, 'x')

  def _init_master_model(self):
    """Instancia modelo maestro"""
    m, variables = _master(self.params)
    self.master_model = m
    self.master_vars = variables

  def _init_subproblems(self, relaxed=True):
    """Instancia los subproblemas"""
    self.subproblem_model = {}
    self.subproblem_res = {}
    if relaxed:
      self.subproblem_relaxed_model = {}
      self.subproblem_relaxed_res = {}
    for i, l, s in self.subproblem_indexes:
      m, res = _subproblem(i, l, s, self.params)
      self.subproblem_model[i, l, s] = m
      self.subproblem_res[i, l, s] = res
      if relaxed:
        m, res = _subproblem(i, l, s, self.params, True)
        self.subproblem_relaxed_model[i, l, s] = m
        self.subproblem_relaxed_res[i, l, s] = res

  @timer.timeit('callback')
  def _lazy_cb(self, model, where):
    """Gurobi callback"""
    if where == GRB.Callback.MIPNODE:
      timer.timestamp('MIPNODE')
      if self.last_sol and not str(self.last_sol) in self.visited_sols:
        # Set SSTPA x values and optimize
        set_sstpa_restrictions(self.sstpa_model, 'x', self.last_sol)
        self.sstpa_model.optimize()

        # Pass solution to current model and get incumbent
        set_cb_sol(model, self.sstpa_model)
        model.cbUseSolution()

        # Add solution to visited
        self.visited_sols.add(str(self.last_sol))
      timer.timestamp('MIPNODE')

    if where == GRB.Callback.MIPSOL:
      timer.timestamp('MIPSOL')
      # Si estamos en un nodo de solución entera, seteamos last_sol a la
      # solucón del nodo.
      self.last_sol = parse_vars(self.master_model, 'x', callback=True)

      for i, l, s in self.subproblem_indexes:
        # Se setean las restricciones que fijan a x y alpha en el subproblema
        # y se resuelve.
        timer.timestamp('cortes de hamming')
        subproblem = self.subproblem_model[i, l, s]
        set_subproblem_values(self, model, (i, l, s))
        subproblem.optimize()

        # Si el modelo es infactible, se agregan cortes de factibilidad
        if subproblem.Status == GRB.INFEASIBLE:
          if args.IIS:
            timer.timeit_nd(subproblem.computeIIS, 'IIS')
          cut = generate_hamming_cut(self, (i, l, s), model, IIS=args.IIS)
          model.cbLazy(cut >= 1)
        timer.timestamp('cortes de hamming')

        if args.benders_cuts:
          # Se resuelve la relajación y agregan cortes de Benders
          timer.timestamp('cortes de benders')
          subproblem_relaxed = self.subproblem_relaxed_model[i, l, s]
          subproblem_relaxed_res = self.subproblem_relaxed_res[i, l, s]

          # set_subproblem_values(self, model, (i, l, s))
          subproblem_relaxed.optimize()

          if subproblem_relaxed.Status == GRB.INFEASIBLE:
            cut = generate_benders_cut(self, subproblem_relaxed_res, subproblem_relaxed)
            model.cbLazy(cut <= 0)
          timer.timestamp('cortes de benders')
      timer.timestamp('MIPSOL')

  def optimize(self):
    """
    Optimiza el maestro con callbacks.
    """
    # Currying
    def callback(x, y):
      self._lazy_cb(x, y)

    if args.preprocess:
      preprocess(self)

    self.master_model.write('logs/model/master.mps')
    self.master_model.optimize(callback)
    if self.master_model.Status == GRB.INFEASIBLE:
      print('Modelo Infactible')
      return
    x = parse_vars(self.master_model, 'x')
    # le pasamos el x a sstpa

    # creamos una instancia del sstpa con x fijo
    sstpa = _sstpa()
    sstpa.Params.LogToConsole = 0
    create_sstpa_restrictions(self, sstpa, 'x')
    set_sstpa_restrictions(sstpa, 'x', x)
    sstpa.optimize()

    # creamos una instancia de sstpa con x irrestricto
    irr = True
    if irr:
      sstpa_irr = _sstpa()
      sstpa_irr.Params.LogToConsole = 0
      sstpa_irr.optimize()
      print('SSTPA Irr ObjVal:', sstpa_irr.objVal)
    print('Benders objVal:  ', self.master_model.objVal)
    print('SSTPA objVal:    ', sstpa.objVal)

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
