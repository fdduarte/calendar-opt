from .position_cuts import upgraded_position_cuts, normal_position_cuts
from .relaxation_cuts import relaxation_cuts


def preprocess(self, model, variables, upgraded=False):
  """Función principal que agrega cortes al modelo"""
  position_cuts = True
  rel_cuts = True
  if rel_cuts:
    relaxation_cuts(self)
  if position_cuts:
    if upgraded:
      upgraded_position_cuts(self, model, variables)
    else:
      normal_position_cuts(self)
