import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import os
from gurobipy import GRB

"""
Módulo de Visualización.

Interpeta stdout de model.py (V3 y V4), para
generar visualizaciónes del rendimiento.

To Do:

- Separate plotter from output logger
- Refactors
"""
class ModelStats:
  @staticmethod
  def get_vars_normal(model_vars, matches):
    prog_file_lines = dict()
    best_case_lines = list()
    points_lines = list()
    for var in model_vars:
      # Refactor: read values correctly (var is gurobipy.Var but acts like string)
      if "x" in str(var):
        _, var, _, value = str(var).split()
        match, date = var.split(",")
        value = int(float(value.strip(")>")))
        match = int(match.strip("x["))
        date = int(date.strip("]"))
        if date not in prog_file_lines.keys():
          prog_file_lines[date] = list()
        if value:
          prog_file_lines[date].append(f",{matches[match]['home']},{matches[match]['away']}\n")
      if "p_m" in str(var):
        _, var, _, value = str(var).split()
        team1, team2, obs_date, date = var.strip('p_m[').strip(']').split(',')
        value = float(value.strip(')>'))
        if team1 == team2:
          points_lines.append((team2, obs_date, date, str(value)))

      if "beta_m" in str(var):
        _, var, _, value = str(var).split()
        team, date = var.split(",")
        team = team.strip("beta_m[")
        date = int(date.strip("]"))
        value = int(float(value.strip(")>")))
        best_case_lines.append([team, str(date), str(value)])
    return prog_file_lines, best_case_lines, points_lines

  @staticmethod
  def get_vars_benders(model, matches):
    prog_file_lines = dict()
    best_case_lines = list()
    points_lines = list()
    for var in model.getVars():
      # Refactor: read values correctly (var is gurobipy.Var but acts like string)
      if "x" in str(var):
        _, var, _, value = str(var).split()
        match, date = var.split(",")
        value = int(float(value.strip(")>")))
        match = int(match.strip("x["))
        date = int(date.strip("]"))
        if date not in prog_file_lines.keys():
          prog_file_lines[date] = list()
        if value:
          prog_file_lines[date].append(f",{matches[match]['home']},{matches[match]['away']}\n")
      if "beta_m" in str(var):
        _, var, _, value = str(var).split()
        team, date = var.split(",")
        team = team.strip("beta_m[")
        date = int(date.strip("]"))
        value = int(float(value.strip(")>")))
        best_case_lines.append([team, str(date), str(value)])

    for (i, l, s), subproblem in model.subproblem_model.items():
      if s == 'm':
        if subproblem.Status == 3:
          print(GRB.INFEASIBLE, subproblem.status)
          print('model', i, l, s, 'is infeasible')
        for var in subproblem.getVars():
          if "p" in str(var):
            try:
              _, var, _, value = str(var).split()
              team1, team2, obs_date, date = var.strip('p[').strip(']').split(',')
              value = float(value.strip(')>'))
              if team1 == i and team1 == team2 and int(l) == int(obs_date):
                points_lines.append((team2, obs_date, date, str(value)))
            except Exception:
              pass
    return prog_file_lines, best_case_lines, points_lines

  @staticmethod
  def parse_gurobi_output(model_vars, matches, name='programacion', benders=False):
    BASE_DIR = f'output/{name}'
    os.mkdir(BASE_DIR)
    try:
      if benders:
        prog_file_lines, best_case_lines, points_lines = ModelStats.get_vars_benders(model_vars, matches)
      else:
        prog_file_lines, best_case_lines, points_lines = ModelStats.get_vars_normal(model_vars, matches)
      with open(f"{BASE_DIR}/programacion.csv", "w", encoding="UTF-8") as infile:
        infile.write("jornada, local, visita\n")
        for date in prog_file_lines.keys():
          infile.write(f"{date},,\n")
          for line in prog_file_lines[date]:
            infile.write(line)
      with open(f"{BASE_DIR}/mejor_posicion.csv", "w", encoding="UTF-8") as infile:
        infile.write("equipo,fecha,posicion\n")
        for line in best_case_lines:
          infile.write(",".join(line))
          infile.write("\n")
      with open(f"{BASE_DIR}/puntos_equipo.csv", "w", encoding="UTF-8") as infile:
        infile.write("equipo,fecha_obs,fecha,puntos\n")
        for line in points_lines:
          infile.write(",".join(line))
          infile.write("\n")
    except ValueError:
      with open("{BASE_DIR}/programacion.csv", "w", encoding="UTF-8") as infile:
        infile.write("Modelo Infactible")

  @staticmethod
  def check_valid_output():
    patterns = dict()
    with open("output/programacion.csv", "r", encoding="UTF-8") as infile:
      for line in infile:
        if line[0] == ",":
          _, home, away = line.strip().split(",")
          if not home in patterns.keys():
            patterns[home] = "1"
          else:
            patterns[home] += "1"
          if not away in patterns.keys():
            patterns[away] = "0"
          else:
            patterns[away] += "0"
    for pattern in patterns.values():
      if "000" in pattern or "111" in pattern:
        raise Exception(f"Modelo arrojó un resultado no valido de local visita: {pattern}.")

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
