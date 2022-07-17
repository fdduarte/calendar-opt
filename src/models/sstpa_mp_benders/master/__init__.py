from .master import master as master_normal
from .master_relaxed import master as master_relaxed


def master(params, relaxed=False, log=True):
  """Genera el modelo maestro de SSTPA, relajado o normal"""
  if not relaxed:
    return master_normal(params, log)
  return master_relaxed(params, log)
