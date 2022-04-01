import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import os

"""
Módulo de Visualización.

Interpeta stdout de model.py (V3 y V4), para
generar visualizaciónes del rendimiento.

To Do:

- Separate plotter from output logger
- Refactors
"""
class ModelStats:
  def __init__(self, logs_path, name):
    self.logs_path = logs_path
    self.name = name
    self.variable_loading_time = []
    self.restriction_loading_time = []
    self.presolve_time = []
    self.total_time = []
    self.optimal_value = []
    self.bound_value = []
    self.create_dir(name)
    self.output_path = "output/visualization"
  
  @staticmethod
  def create_dir(name):
    try:
      os.mkdir(f"output")
    except FileExistsError:
      pass
    try:
      os.mkdir(f"output/visualization")
    except FileExistsError:
      pass
    try:
      os.mkdir(f"output/visualization/{name}-vis")
    except FileExistsError:
      pass

  @staticmethod
  def gen_plot(x, y, title):
    plt.plot(x, y, 'o')
    plt.title(title)
    plt.xlabel("Fechas")
    plt.ylabel("Tiempos (minutos)")

  @staticmethod
  def get_var_cords(variable):
    x = np.array([data[0] for data in variable])
    y = np.array([data[1] for data in variable])
    return x, y

  def parse_logs(self, logs):
    self.logs = logs
    for log in logs:
      presolve = False
      try:
        with open(f"{self.logs_path}/log_{log}.txt", "r", encoding="UTF-8") as infile:
          start, end = log.split("-")
          model_length = int(end) - int(start) + 1
          for line in infile:
            if "** VARIABLES TIME:" in line:
              _, _, _,  time = line.split()
              self.variable_loading_time.append((model_length, float(time)/60))
            if "** RESTRICTIONS TIME:" in line:
              _, _, _, time = line.split()
              self.restriction_loading_time.append((model_length, float(time)/60))
            if "** TOTAL TIME:" in line:
              _, _, _, time = line.split()
              self.total_time.append((model_length, float(time)/60))
            if "Presolve time:" in line:
              _, _, time = line.split()
              presolve = True
              self.presolve_time.append((model_length, float(time.strip("s"))/60))
            if "Best objective" in line:
              splitted_line = line.split()
              obj = float(splitted_line[2].strip(','))
              bound = float(splitted_line[5].strip(','))
              self.optimal_value.append((model_length, bound))
              self.bound_value.append((model_length, obj))
          if not presolve:
            self.presolve_time.append((model_length, 0))
      except FileNotFoundError:
        print(f"{self.logs_path}/log_{log}.txt Not Found")

  def gen_linear_reg_scatter(self):
    path = f"{self.output_path}/{self.name}-vis/Reg"
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
    # Scatter de carga variables vs fechas
    x, y = self.get_var_cords(self.variable_loading_time)
    m, b = np.polyfit(x, y, 1)
    self.gen_plot(x, y, f"Function: {b} + {m}x")
    plt.plot(x, m*x + b)
    plt.savefig(f"{path}/variable_loading_reg.png")
    plt.close()
    # Scatter Restricciones vs fechas
    x, y = self.get_var_cords(self.restriction_loading_time)
    m, b = np.polyfit(x, y, 1)
    self.gen_plot(x, y, f"Function: {b} + {m}x")
    plt.plot(x, m*x + b)
    plt.savefig(f"{path}/restriction_loading_reg.png")
    plt.close()
    # Scatter presolve vs fechas
    x, y = self.get_var_cords(self.restriction_loading_time)
    m, b = np.polyfit(x, y, 1)
    self.gen_plot(x, y, f"Function: {b} + {m}x")
    plt.plot(x, m*x + b)
    plt.savefig(f"{path}/presovle_reg.png")
    plt.close()
    # Scatter de tiempo total vs fechas
    x, y = self.get_var_cords(self.total_time)
    m, b = np.polyfit(x, y, 1)
    self.gen_plot(x, y, f"Function: {b} + {m}x")
    plt.plot(x, m*x + b)
    plt.savefig(f"{path}/total_time_reg.png")
    plt.close()

  def gen_poli_funct_plot(self):
    path = f"{self.output_path}/{self.name}-vis/PoliFit"
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
    def test_funct(x, a, b):
      return a + x**b
    x, y = self.get_var_cords(self.total_time)
    params, _ = optimize.curve_fit(test_funct, x, y)
    self.gen_plot(x, y, f"Function: {params[0]} + x^{params[1]}")
    plt.plot(x, test_funct(x, params[0], params[1]))
    plt.savefig(f"{path}/total_time_polifit.png")
    plt.close()

  def gen_exp_funct_plot(self):
    path = f"{self.output_path}/{self.name}-vis/ExpFit"
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
    def test_funct(x, a, b):
      return a + b**x
    x, y = self.get_var_cords(self.total_time)
    params, _ = optimize.curve_fit(test_funct, x, y)
    self.gen_plot(x, y, f"Function: {params[0]} + {params[1]}^x")
    plt.plot(x, test_funct(x, params[0], params[1]))
    plt.savefig(f"{path}/total_time_expfit.png")
    plt.close()

  def gen_csv(self):
    csv_lines = []
    for logs in self.logs:
      line = []
      start, end = logs.split("-")
      curr_dates = int(end) - int(start) + 1
      line.append(str(curr_dates))
      found = False
      for dates, val in self.variable_loading_time:
        if dates == curr_dates:
          found = True
          line.append(str(val))
      if not found:
        line.append("-")
      found = False
      for dates, val in self.restriction_loading_time:
        if dates == curr_dates:
          found = True
          line.append(str(val))
      if not found:
        line.append("-")
      found = False
      for dates, val in self.presolve_time:
        if dates == curr_dates:
          found = True
          line.append(str(val))
      if not found:
        line.append("-")
      found = False
      for dates, val in self.total_time:
        if dates == curr_dates:
          found = True
          line.append(str(val))
      if not found:
        line.append("-")
      for dates, val in self.optimal_value:
        if dates == curr_dates:
          found = True
          line.append(str(val))
      if not found:
        line.append("-")
      for dates, val in self.bound_value:
        if dates == curr_dates:
          found = True
          line.append(str(val))
      if not found:
        line.append("-")
      csv_lines.append(line)
    with open(f"{self.output_path}/{self.name}-vis/data.csv", "w", encoding="UTF-8") as infile:
      infile.write("dates,var_loading,res_loading,presolve,total,opt_val,bound_val\n")
      for line in csv_lines:
        infile.write(",".join(line))
        infile.write("\n")
      

if __name__ == '__main__':
  LOGS = [f"{i}-30" for i in range(18, 24)]
  PATH = "SSTPA/logs/13-6"
  NAME = "V3-t"

  plotter = ModelStats(PATH, NAME)
  plotter.parse_logs(LOGS)
  plotter.gen_linear_reg_scatter()
  plotter.gen_poli_funct_plot()
  plotter.gen_exp_funct_plot()
  plotter.gen_csv()