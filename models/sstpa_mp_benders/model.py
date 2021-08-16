from .slave import slave as _slave
from .master import master as _master
import time
import random

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

    def master(self):
        return _master(self.start_date, self.end_date, self.pattern_generator,
                       self.champ_stats)

    def optimize(self):
        """
        Main Loop
        """

        while True:
          # Condición de termino por tiempo o GAP
          m = self.master()
          m.optimize()

          # Obtener los valores de x e alpha
          alpha_p = None
          alpha_m = None
          x = None

          alpha = [alpha_p, alpha_m]
          for i in range(2):
            s = self.slave(x, alpha[i]) 
            s.optimize()

            # Guardar cortes
          break

        self.final_model = m

    def getVars(self):
        pass


def create_model(start_date, end_date, time_limit, pattern_generator, champ_stats, mip_focus=1, mip_gap=0.3):
    m = Benders(start_date, end_date, time_limit, pattern_generator, champ_stats)
    return m
    