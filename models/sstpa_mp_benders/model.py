from slave import slave as _slave
from master import master as _master
import time

class Benders():
    def __init__(self, start_date, end_date, time_limit, pattern_generator, champ_stats):
        self.start_date = start_date
        self.end_date = end_date
        self.time_limit = time_limit
        self.start_time = time.time()
        self.pattern_generator = pattern_generator
        self.champ_stats = champ_stats

    def slave(self, x_opt, alpha_opt):
        return _slave(x_opt, alpha_opt, self.start_date, self.end_date,
                      self.pattern_generator, self.champ_stats)

    def master(self, *args):
        return _master(*args)

    def optimize(self):
        """
        Main Loop
        """
        m = self.slave()
        m.optimize()

    def getVars(self):
        pass


def create_model(start_date, end_date, time_limit, pattern_generator, champ_stats, mip_focus=1, mip_gap=0.3):
    m = Benders(start_date, end_date, time_limit, pattern_generator, champ_stats)
    return m
    