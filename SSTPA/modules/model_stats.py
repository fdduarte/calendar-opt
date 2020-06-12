import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import os


class ModelStats:
  def __init__(self, logs_path, name):
    self.logs_path = logs_path
    self.name = name
    self.variable_loading_time = []
    self.restriction_loading_time = []
    self.presolve_time = []
    self.total_time = []

  def parse_logs(self, logs):
    # TO-DO: Auto search log files
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
          if not presolve:
            self.presolve_time.append((model_length, 0))
      except FileNotFoundError:
        print(f"{self.logs_path}/log_{log}.txt Not Found")

  def gen_linear_reg_scatter(self):
    path = f"{self.name}-Plots"
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
    # Scatter de carga variables vs fechas
    x = np.array([data[0] for data in self.variable_loading_time])
    y = np.array([data[1] for data in self.variable_loading_time])
    plt.plot(x, y, 'o')
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b)
    plt.title(f"Function: {m} + x{b}")
    plt.savefig(f"{path}/variable_loading_reg.png")
    plt.xlabel("Fechas")
    plt.ylabel("Tiempo (minutos)")
    plt.close()
    # Scatter de tiempo total vs fechas
    x = np.array([data[0] for data in self.total_time])
    y = np.array([data[1] for data in self.total_time])
    plt.plot(x, y, 'o')
    plt.title(f"Function: {m} + x{b}")
    plt.xlabel("Fechas")
    plt.ylabel("Tiempo (minutos)")
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b)
    plt.savefig(f"{path}/total_time_reg.png")
    plt.close()

  def gen_poli_funct_plot(self):
    path = f"{self.name}-Plots"
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
    def test_funct(x, a, b):
      return a + x**b
    x = np.array([data[0] for data in self.total_time])
    y = np.array([data[1] for data in self.total_time])
    params, _ = optimize.curve_fit(test_funct, x, y)
    plt.plot(x, y, 'o')
    plt.plot(x, test_funct(x, params[0], params[1]))
    plt.title(f"Function: {params[0]} + x^{params[1]}")
    plt.xlabel("Fechas")
    plt.ylabel("Tiempo (minutos)")
    plt.savefig(f"{path}/total_time_polin_fit.png")
    plt.close()

  def gen_exp_funct_plot(self):
    path = f"{self.name}-Plots"
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
    def test_funct(x, a, b):
      return a + b**x
    x = np.array([data[0] for data in self.total_time])
    y = np.array([data[1] for data in self.total_time])
    params, _ = optimize.curve_fit(test_funct, x, y)
    plt.plot(x, y, 'o')
    plt.plot(x, test_funct(x, params[0], params[1]))
    plt.title(f"Function: {params[0]} + {params[1]}^x")
    plt.xlabel("Fechas")
    plt.ylabel("Tiempo (minutos)")
    plt.savefig(f"{path}/total_time_exp_fit.png")
    plt.close()


