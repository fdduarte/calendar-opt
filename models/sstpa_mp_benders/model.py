from .slave import slave as _slave
from .master import master as _master
import time
from gurobipy import GRB

class Benders():
    def __init__(self, start_date, end_date, time_limit, pattern_generator, champ_stats):
        self.start_date = start_date
        self.end_date = end_date
        self.time_limit = time_limit
        self.start_time = time.time()
        self.pattern_generator = pattern_generator
        self.champ_stats = champ_stats
        self.final_model = None

    def slave(self, x_opt, alpha_opt):
        return _slave(x_opt, alpha_opt, self.start_date, self.end_date,
                      self.pattern_generator, self.champ_stats)

    def master(self, time_limit):
        return _master(time_limit, self.start_date, self.end_date, self.pattern_generator,
                       self.champ_stats)

    def optimize(self):
        """
        Main Loop
        """
        while True:
          time_left = self.time_limit - (time.time() - self.start_time)

          m = self.master(time_left)
          m.optimize()

          x, alpha_m, alpha_p = self._parse_master_output(m)

          alpha = [alpha_p, alpha_m]

          is_optimal = True
          for i in range(2):
            s = self.slave(x, alpha[i]) 
            s.optimize()

            if s.status != GRB.OPTIMAL:
              is_optimal = False

            # Add Cuts

          # End Condition
          if time.time() - self.start_time > self.time_limit or is_optimal:
            break

        self.final_model = m

    def getVars(self):
        pass

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
      return x, alpha_m, alpha_p


def create_model(start_date, end_date, time_limit, pattern_generator, champ_stats, mip_focus=1, mip_gap=0.3):
    m = Benders(start_date, end_date, time_limit, pattern_generator, champ_stats)
    return m
    