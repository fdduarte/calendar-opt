from typing import Tuple
from gurobipy import Model


def parse_vars(model_var, model, callback=False, is_binary=True):
  """
  Parsea la variable "var_name" de un modelo, retornando un diccionario.
  """

  _vars = {}
  for var in model_var['x'].values():
    name = var.VarName
    if callback:
      value = model.cbGetSolution(var)
    else:
      value = var.X
    if is_binary:
      value = value_to_binary(value)
    _vars[name] = value
  return _vars


def value_to_binary(value: float):
  """Funcion que aproxima un float a el binario mas cercano"""
  if value > 0.5:
    return 1
  return 0


def get_subproblem_indexes(subproblem: Model) -> Tuple[int, int, int]:
  """Dado un modelo de un subproblema de gurobi, retorna los indices del modelo"""
  name = subproblem.getAttr('ModelName')
  _, name = name.split(': ')
  i, l, s = name.split('-')
  return i, int(l), s
