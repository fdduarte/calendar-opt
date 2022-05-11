import time
from gurobipy import GRB
from .subproblem import subproblem as _subproblem
from .master import master as _master
from .sstpa_model import create_model as _sstpa
from .utils import (
  set_subproblem_values,
  generate_cut,
  parse_vars,
  set_sstpa_restrictions,
  set_cb_sol,
)
from .parse_params import parse_params


# pylint: disable=invalid-name
class Benders:
  """Clase del modelo de optimización SSTPA con descomposición de benders"""
  def __init__(self):
    self.params = parse_params()
    self.subproblem_indexes = [(i, l, s) for i in self.params['I']
                               for l in self.params['F'] for s in ["m", "p"]]
    # Models
    self.sstpa_model = _sstpa(self.params)
    self.master_model = _master(self.params)
    self.subproblem_model = {}
    for i, l, s in self.subproblem_indexes:
      self.subproblem_model[i, l, s] = _subproblem(i, l, s, self.params)
    self.times = {
      'IIS': 0,
      'subproblem': 0,
      'sstpa': 0,
      'relax': 0,
      'MIPNode': 0,
      'MIPSOL': 0,
      'generate cut': 0,
      'total': 0
    }
    self.stats = {
      'betaneq': 0,
      'cuts': 0,
    }
    self.last_sol = None
    self.visited_sols = set()

  def _timeit(self, func, name, *args):
    start = time.time()
    ret = func(*args)
    self.times[name] += time.time() - start
    return ret

  def _lazy_cb(self, model, where):
    start = time.time()
    if where == GRB.Callback.MIPNODE:
      if not str(self.last_sol) in self.visited_sols:
        # Set SSTPA x values and optimize
        set_sstpa_restrictions(self.sstpa_model, self.last_sol)
        self._timeit(self.sstpa_model.optimize, 'sstpa')

        # Pass solution to current model and get incumbent
        set_cb_sol(model, self.sstpa_model)
        obj_val = model.cbUseSolution()
        print(' ' * 34, obj_val)

        # Add solution to visited
        self.visited_sols.add(str(self.last_sol))

    self.times['MIPNode'] += time.time() - start
    start = time.time()
    if where == GRB.Callback.MIPSOL:
      self.last_sol = parse_vars(model, 'x', callback=True)

      # Set SSTPA x values and optimize
      set_sstpa_restrictions(self.sstpa_model, self.last_sol)
      self._timeit(self.sstpa_model.optimize, 'sstpa')

      for i, l, s in self.subproblem_indexes:
        # Generate best/worst position cut
        """
        if s == 'm':
            cut1, cut2 = self._timeit(create_position_cut, 'generate cut', model, self, i, l) 
            model.cbLazy(cut1)
            model.cbLazy(cut2)
            self.stats['cuts'] += 2
        """

        # set subproblem values and optimize
        subproblem = self.subproblem_model[i, l, s]
        set_subproblem_values(model, subproblem)
        self._timeit(subproblem.optimize, 'subproblem')

        # ver != de betas
        beta1 = self.sstpa_model.getVarByName(f'beta_m[{i},{l}]').X
        var = model.getVarByName(f'beta_m[{i},{l}]')
        beta2 = model.cbGetSolution(var)
        if beta1 != beta2:
          self.stats['betaneq'] += 1

        # If infeasible, add cuts

        if subproblem.Status == GRB.INFEASIBLE:
          # self._timeit(subproblem.computeIIS, 'IIS')
          cut = generate_cut(subproblem, model)
          model.cbLazy(cut >= 1)

    self.times['MIPSOL'] += time.time() - start

  def optimize(self):
    """
    Main Loop
    """
    start_time = time.time()
    self.master_model.optimize(lambda x, y: self._lazy_cb(x, y))
    self.times['total'] = time.time() - start_time

  def getVars(self):
    """Retorna las variables del modelo maestro"""
    return self.master_model.getVars()

  def write(self, *args):
    """Escribe el modelo maestro"""
    return self.master_model.write(*args)

  def print_stats(self):
    """Imprime estadisticas de tiempo del modelo"""
    print("\n" + "=" * 20 + "\n")
    print('TIME:')
    print('Total time:', self.times['total'])
    print('Time computing subproblems:', self.times['subproblem'])
    print('Time computing IIS:', self.times['IIS'])
    print('Time computing heuristic SSTPA:', self.times['sstpa'])
    print('Time computing subproblem relaxation:', self.times['relax'])
    print('Time in generating best/worst position cuts', self.times['generate cut'])
    print('Time in MIPNODE callback', self.times['MIPNode'])
    print('Time in MIPSOL callback', self.times['MIPSOL'])
    print('STATS:')
    print('Cuts:', self.stats['cuts'])
    print('Betas not equal:', self.stats['betaneq'])


def create_model():
  """Crea modelo SSTPA MP Benders"""
  return Benders()
