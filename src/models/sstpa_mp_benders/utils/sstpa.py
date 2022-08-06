from gurobipy import quicksum
from .helpers import value_to_binary
# pylint: disable=invalid-name


def create_sstpa_restrictions(self, model):
  """
  Dada una familia de variables del modelo sstpa, crea restricciones del tipo
  for var in fam_var: var = 0. Esta restricción permite posteriormente fijar
  el lado derecho para así fijar la variable.
  """
  for n in self.params['N']:
    for f in self.params['F']:
      var = model.getVarByName(f'x[{n},{f}]')
      model.addConstr(var == 0, name=f'R-x[{n},{f}]')

  model.update()


def set_sstpa_restrictions(model, last_sol, is_binary=True):
  """
  Setea el lado derecho (rhs) de la restriccion de la variable {var} para
  el modelo SSTPA.
  """
  for name, value in last_sol.items():
    if is_binary:
      value = value_to_binary(value)
    _, index = name.strip(']').split('[')
    index = index.split(',')
    n, f = index
    model.getConstrByName(f'R-x[{n},{f}]').rhs = value

  model.update()


def create_position_cut(model, self, i, l, d=2):
  """
  Dado el modelo maestro, una instancia del modelo SSTPA óptima, un equipo
  i, y una fecha l, genera un corte de posición.
  """
  # Se obtiene la mejor posicion
  k = int(self.sstpa_model.getVarByName(f'beta_m[{i},{l}]').X)
  S_indexes, S = [], []

  # Se obtiene el soporte de X.
  for (n, f), value in self.last_sol.items():
    if value > 0.5:
      S_indexes.append(f'x[{n},{f}]')

  # Se obtiene la variable x del soporte
  for index in S_indexes:
    S.append(model.getVarByName(index))

  # Se obtiene el beta del modelo.
  beta = model.getVarByName(f'beta_m[{i},{l}]')

  # Se generan ambos cortes.
  cut1 = beta >= (1 - k) * (1 / d) * quicksum((1 - x) for x in S) + k
  cut2 = beta <= (1 - k) * (len(self.params['N']) / d) * quicksum((1 - x) for x in S) + k
  return cut1, cut2
