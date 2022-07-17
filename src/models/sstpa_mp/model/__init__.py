from .model import create_model as create_model_normal
from .model_relaxed import create_model as create_model_relaxed


def create_model(log=True, relaxed=False):
  """Crea modelo de optimizacion de multiples posiciones sin descomposicion"""
  if not relaxed:
    return create_model_normal(log)
  return create_model_relaxed(log)
