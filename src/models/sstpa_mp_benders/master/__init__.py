from .master import master as master_normal
from .master_relaxed import master as master_relaxed


def master(params, relaxed=False):
  """Genera el modelo maestro de SSTPA, relajado o normal"""
  if not relaxed:
    return master_normal(params)
  return master_relaxed(params)
