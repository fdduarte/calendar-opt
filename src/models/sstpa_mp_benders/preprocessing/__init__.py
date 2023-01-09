from .position_cuts import upgraded_position_cuts, normal_position_cuts
from .relaxation_cuts import relaxation_cuts
from ....libs.argsparser import args
from ....libs.logger import log


def preprocess(self, model, variables, upgraded=False):
  """Función principal que agrega cortes al modelo"""
  position_cuts = False
  rel_cuts = True
  if rel_cuts:
    relaxation_cuts(self)
    for i in range(args.preprocess_iters - 1):
      log('preprocess', f'Iteration {i + 2}')
      relaxation_cuts(self, random=True)
  if position_cuts:
    if upgraded:
      upgraded_position_cuts(self, model, variables)
    else:
      normal_position_cuts(self)
