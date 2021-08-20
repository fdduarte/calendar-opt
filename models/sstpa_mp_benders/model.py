from .subproblem import subproblem as _subproblem
from .master import master as _master
import time
from gurobipy import GRB, LinExpr

class Benders():
    def __init__(self, start_date, end_date, time_limit, breaks, pattern_generator, champ_stats):
        self.start_date = start_date
        self.end_date = end_date
        self.time_limit = time_limit
        self.breaks = breaks
        self.start_time = time.time()
        self.pattern_generator = pattern_generator
        self.champ_stats = champ_stats
        self.final_model = None
        self.master_vars = {'x': None, 'a': None}
        self.subproblem_restrictions = {'m': {'x': None, 'a': None}, 'p': {'x': None, 'a': None}}
        self.cuts = []

    def subproblem(self, x_opt, alpha_opt, model_type):
        s, x_r, a_r = _subproblem(x_opt, alpha_opt, self.start_date, self.end_date,
                      self.pattern_generator, self.champ_stats)
        self.subproblem_restrictions[model_type]['x'] = x_r
        self.subproblem_restrictions[model_type]['a'] = a_r
        return s

    def master(self, time_limit):
        m, x, a = _master(time_limit, self.start_date, self.end_date, self.pattern_generator,
                       self.champ_stats)
        self.master_vars['x'] = x
        self.master_vars['a'] = a
        return m

    def optimize(self):
        """
        Main Loop
        """
        m = self.master(self.time_limit)

        m.optimize() # Optimizamos solamente para obtener vectores x y alfa

        x, a = self._parse_master_output(m)

        s = {'m': self.subproblem(x, a['m'], 'm'), 'p': self.subproblem(x, a['p'], 'p')}

        niter = 1

        print("{:<10}   {:<13}   {:<5}".format("Iteration", "Objective", "Time"))

        while True:

          m.optimize()

          self._print(niter, m.objVal)

          niter += 1

          x, a = self._parse_master_output(m)

          self._set_restriction_values(s, x, a)
          # Setear valores de afa y x en subproblema

          is_optimal = True
          for s_type in ['m', 'p']:
            s[s_type].optimize()

            if s[s_type].status != GRB.OPTIMAL:
              s[s_type]
              is_optimal = False
              cut = self._generate_cut(x, a[s_type], s_type)
              m.addConstr(cut >= 1)


          # End Condition
          if time.time() - self.start_time > self.time_limit or is_optimal:
            break

        self.final_model = m

    def getVars(self):
        pass

    def _set_restriction_values(self, s, x, a):
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

    def _generate_cut(self, x, a, s_type):
      """
      Dado un subproblema infactible, genera un corte para
      el problema maestro usando los valores de x y alfa.
      """
      cut = LinExpr()
      for i, value in x.items():
        if value > 0.5: cut = cut + (1 - self.master_vars['x'][i])
        else: cut = cut + self.master_vars['x'][i]

      for i, value in a.items():
        if value > 0.5: cut = cut + (1 - self.master_vars['a'][s_type][i])
        else: cut = cut + self.master_vars['a'][s_type][i]

      return cut

    def _parse_master_output(self, model):
      """
      Función que dada una instancia optimizada del maestro, retorna
      3 diccionarios con los valores obtenidos para alfa y x.
      """
      x, alpha_m, alpha_p = {}, {}, {}
      for var in model.getVars():
        name, value = var.VarName, var.X
        if 'x' in name:
          name = name.strip('x[').strip(']')
          name = tuple(int(i) for i in name.split(','))
          x[name] = int(value)
        if 'alfa_m' in name:
          name = name.strip('alfa_m[').strip(']')
          name = name.split(',')
          name[2] = int(name[2])
          alpha_m[tuple(name)] = int(value)
        if 'alfa_p' in name:
          name = name.strip('alfa_p[').strip(']')
          name = name.split(',')
          name[2] = int(name[2])
          alpha_p[tuple(name)] = int(value)
      alpha = {'m': alpha_m, 'p': alpha_p}
      return x, alpha

    def _print(self, niter, objval):
      elapsed_time = str(int(time.time() - self.start_time)) + 's'
      print("{:<10}   {:<13}   {:<5}".format(niter, objval, elapsed_time))


def create_model(start_date, end_date, time_limit, breaks, pattern_generator, champ_stats,  mip_focus=1, mip_gap=0.3):
    m = Benders(start_date, end_date, time_limit, breaks, pattern_generator, champ_stats)
    return m
    