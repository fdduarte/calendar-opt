from gurobipy import LinExpr


def generate_position_cut(self, indexes, sum_alpha, ham_x):
  """
  Dado un subproblema resuelto, crea cortes de hamming con o sin
  el calculo de IIS.
  """
  i, l, s = indexes
  I = self.params['I']

  cut = LinExpr()

  # alpha
  for j in I:
    alpha = self.master_vars[f'alpha_{s}'][j, i, l]
    cut -= alpha
  cut += ham_x
  cut += sum_alpha
  return cut


def calculate_sum_alpha(self, indexes, master):
  """Calcula la suma de lo alpha del problema maestro"""
  i, l, s = indexes
  I = self.params['I']

  val = 0
  for j in I:
    alpha = self.master_vars[f'alpha_{s}'][j, i, l]
    alpha_val = master.cbGetSolution(alpha)
    val += alpha_val

  return val


def hamming_x(self, indexes, master):
  """Calcula distancia de hamming de vector x"""
  i, l, s = indexes
  N = self.params['N']
  F = self.params['F']

  expr = LinExpr()
  # distancia de hammin para x
  for n in N:
    for f in F:
      x = self.master_vars['x'][n, f]
      if master.cbGetSolution(x) > 0.5:
        expr += LinExpr(1 - x)
      else:
        expr += x

  return expr
