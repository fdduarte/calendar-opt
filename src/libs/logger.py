from .argsparser import args


class Logger():
  """Clase para loggeae"""
  def __init__(self):
    self.data = {}

  @staticmethod
  def log(category: str, message: str):
    """Loggea en caso del el argumento verbose sea verdad"""
    if args.verbose:
      print(f"[{category}] {message}")

  def increment_stats(self, name: str, verbose=False):
    """Incrementa en uno la estadistica {name}"""
    if name in self.data:
      self.data[name] += 1
      if args.print_every_n_cuts != 0:
        if args.verbose and verbose and self.data[name] % args.print_every_n_cuts == 0:
          print('[stats]', name, self.data[name])
    else:
      self.data[name] = 1

  def stats_string(self):
    """Retorna un string con todas las estadisticas"""
    string = f'{"nombre": <20} | {"numero": <5}\n'
    for name, value in self.data.items():
      string += f'{name: <20} | {value: <5}\n'
    return string


log = Logger.log
logger = Logger()
