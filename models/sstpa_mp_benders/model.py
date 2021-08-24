from .subproblem import subproblem as _subproblem
from .master import master as _master
import time
from gurobipy import GRB, LinExpr

class Benders():
  def __init__(self, start_date, end_date, time_limit, breaks, pattern_generator, champ_stats, ModelStats):
    self.start_date = start_date
    self.end_date = end_date
    self.time_limit = time_limit
    self.breaks = breaks
    self.start_time = time.time()
    self.pattern_generator = pattern_generator
    self.champ_stats = champ_stats
    self.ModelStats = ModelStats
    self.master_model = None
    self.subproblem_model = {'m': None, 'p': None}
    self.master_vars = {'x': None, 'a': None}
    self.subproblem_restrictions = {'m': {'x': None, 'a': None}, 'p': {'x': None, 'a': None}}
    self.cuts = []

  def subproblem(self, x_opt, alpha_opt, model_type):
    s, x_r, a_r = _subproblem(x_opt, alpha_opt, model_type, self.start_date,
                              self.end_date, self.pattern_generator, self.champ_stats)
    self.subproblem_restrictions[model_type]['x'] = x_r
    self.subproblem_restrictions[model_type]['a'] = a_r
    self.subproblem_model[model_type] = s
    return s

  def master(self, time_limit):
    m = _master(time_limit, self.start_date, self.end_date, self.pattern_generator,
                    self.champ_stats)
    return m

  def _lazy_cb(self, model, where):
    if where == GRB.Callback.MIPSOL:
      x, a = self._parse_master_output(model)
      self._set_restriction_values(x, a)
      for s_type in ['m', 'p']:
        self.subproblem_model[s_type].optimize()
        if self.subproblem_model[s_type].Status == GRB.INFEASIBLE:
          self.subproblem_model[s_type].computeIIS()
          cut = self._generate_cut(s_type, model)
          model.cbLazy(cut >= 1)


  def optimize(self):
      """
      Main Loop
      """
      _m = self.master(self.time_limit)
      _m.optimize() # Optimizamos solamente para obtener vectores x y alfa

      x, a = self._parse_master_output(_m, cb=False)

      for s_type in ['m', 'p']: self.subproblem(x, a[s_type], s_type)

      m = self.master(self.time_limit)
      self.master_model = m

      m.optimize(lambda x, y: self._lazy_cb(x, y))

  def getVars(self):
      return self.master_model.getVars()

  def _set_restriction_values(self, x, a):
    """
    Dados valores de x y alfa del maestro, setea estos
    valores en las restricciones de los subproblemas.
    """
    for index, value in x.items():
      if value > 0.5: value = 1
      else: value = 0
      self.subproblem_restrictions['m']['x'][index].rhs = value
      self.subproblem_restrictions['p']['x'][index].rhs = value

    for index, value in a['m'].items():
      if value > 0.5: value = 1
      else: value = 0
      self.subproblem_restrictions['m']['a'][index].rhs = value

    for index, value in a['p'].items():
      if value > 0.5: value = 1
      else: value = 0
      self.subproblem_restrictions['p']['a'][index].rhs = value

  def _generate_cut(self, s_type, model):
    """
    Dado un subproblema infactible, genera un corte para
    el problema maestro usando los valores de x y alfa.
    """
    cut = LinExpr()
    for var in model.getVars():
      name = var.VarName
      if 'x' in name or f'alfa_{s_type}' in name:
        if 'x' in name: r = 'x'
        else: r = 'a'

        value = model.cbGetSolution(var)

        name = name.strip('x[').strip(f'alfa_{s_type}[').strip(']')
        name = tuple(int(i) if not i.isalpha() else i for i in name.split(','))

        if self.subproblem_restrictions[s_type][r][name].IISConstr:
          if value > 0.5: cut += (1 - var)
          else: cut += var
    return cut

  def _parse_master_output(self, model, cb=True):
    """
    Función que dada una instancia optimizada del maestro, retorna
    3 diccionarios con los valores obtenidos para alfa y x.
    """
    x, alpha_m, alpha_p = {}, {}, {}
    for var in model.getVars():
      name = var.VarName
      if 'x' in name:
        name = name.strip('x[').strip(']')
        name = tuple(int(i) for i in name.split(','))
        if cb: x[name] = int(model.cbGetSolution(var))
        else: x[name] = int(var.X)
      if 'alfa_m' in name:
        name = name.strip('alfa_m[').strip(']')
        name = name.split(',')
        name[2] = int(name[2])
        if cb: alpha_m[tuple(name)] = int(model.cbGetSolution(var))
        else: alpha_m[tuple(name)] = int(var.X)
      if 'alfa_p' in name:
        name = name.strip('alfa_p[').strip(']')
        name = name.split(',')
        name[2] = int(name[2])
        if cb: alpha_p[tuple(name)] = int(model.cbGetSolution(var))
        else: alpha_p[tuple(name)] = int(var.X)
    alpha = {'m': alpha_m, 'p': alpha_p}
    return x, alpha

  def _print(self, niter, objval):
    elapsed_time = str(int(time.time() - self.start_time)) + 's'
    print("{:<10}   {:<13}   {:<5}".format(niter, objval, elapsed_time))


def create_model(start_date, end_date, time_limit, breaks, pattern_generator, champ_stats,  ModelStats, mip_focus=1, mip_gap=0.3):
    m = Benders(start_date, end_date, time_limit, breaks, pattern_generator, champ_stats, ModelStats)
    return m
    