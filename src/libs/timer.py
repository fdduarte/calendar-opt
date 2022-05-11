from time import time

class Timer:
  """Clase que toma tiempos"""
  def __init__(self):
    self.times = {}

  def create_time(self, *times: list[str]):
    """Crea variables para tomar el tiempo"""
    for time in times:
      self.times[time] = 0

  def timeit(self, name: str, verbose: bool = False):
    """Decorador que toma el tiempo de una funcion y lo guarda"""
    if not name in self.times.keys():
      self.times[name] = 0
    def _inner(func):
      def wrapper(*args, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        self.times[name] += time() - start
        if verbose: print(time() - start)
      return wrapper
    return _inner

  def print_time(self, name: str):
    print(self.times[name])

  def times_string(self):
    string = ""
    for name, value in self.times.items():
      value = round(value, 5)
      string += f'{name: <20} | {value: <10}\n'
    string = string[0:-1]
    return string

timer = Timer()
