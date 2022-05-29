def parse_vars(model, var_name, callback=False, is_binary=True):
  """
  Parsea la variable "var_name" de un modelo, retornando un diccionario.
  """
  _vars = {}
  for var in model.getVars():
    name = var.VarName
    if var_name in name:
      name = name.strip(f"{var_name}[").strip("]").split(",")
      name = (int(i) if i.isdigit() else i for i in name)
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
