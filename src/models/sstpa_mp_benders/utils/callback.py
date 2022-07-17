def set_cb_sol(model, sstpa):
  """Dado el modelo maestro, y un modelo SSTPA resuelto, inyecta la
  solución heuristica del SSTPA al maestro."""
  for var in model.getVars():
    value = sstpa.getVarByName(var.VarName).X
    model.cbSetSolution(var, value)
  model.cbUseSolution()
