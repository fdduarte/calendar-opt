def set_cb_sol(model, sstpa):
  """Dado el modelo maestro, y un modelo SSTPA resuelto, inyecta la
  solución heuristica del SSTPA al maestro."""
  for var in model.getVars():
    name = var.VarName
    if 'gamma' in name or 'tau' in name or 'epsilon' in name:
      continue
    value = sstpa.getVarByName(var.VarName).X
    model.cbSetSolution(var, value)
  model.cbUseSolution()
