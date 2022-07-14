from .subproblem_relaxed import subproblem as subproblem_relaxed
from .subproblem import subproblem as subproblem_normal


# pylint: disable=invalid-name
def subproblem(i, l, s, params, relaxed=False):
  """Genera el subproblema de SSTPA"""
  if relaxed:
    return subproblem_relaxed(i, l, s, params)
  return subproblem_normal(i, l, s, params)
