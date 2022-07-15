from .position_cuts import upgraded_position_cuts, normal_position_cuts
from .relaxation_cuts import relaxation_cuts


def preprocess(self, model, variables, upgraded=True):
  """Función principal que agrega cortes al modelo"""
  position_cuts = False
  rel_cuts = False
  if position_cuts:
    if upgraded:
      upgraded_position_cuts(self, model, variables)
    else:
      normal_position_cuts(self)
  if rel_cuts:
    relaxation_cuts(self)
