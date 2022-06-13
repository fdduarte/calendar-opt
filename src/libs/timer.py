from time import time


class Timer:
  """Clase que toma tiempos"""
  def __init__(self):
    self.start = time()
    self.times = {}
    self.timestamps = {}

  def create_time(self, *times: list[str]):
    """Crea variables para tomar el tiempo"""
    for tm in times:
      self.times[tm] = 0

  def timeit(self, name: str, verbose: bool = False):
    """Decorador que toma el tiempo de una funcion y lo guarda"""
    if name not in self.times:
      self.times[name] = 0

    def _inner(func):
      def wrapper(*args, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        self.times[name] += time() - start
        if verbose:
          print(time() - start)
        return ret
      return wrapper
    return _inner

  def timeit_nd(self, func, name, *args):
    """Función que le toma el tiempo a otra función y lo guarda,
    nd es por no decorator."""
    if name not in self.times:
      self.times[name] = 0
    start = time()
    ret = func(*args)
    self.times[name] += time() - start
    return ret

  def timestamp(self, name):
    """Crea un timestamp. en caso de ya existir, guarda el tiempo que se demoró y
    elimina el timestamp"""
    if name in self.timestamps:
      f_time = time() - self.timestamps[name]
      if name not in self.times:
        self.times[name] = f_time
      else:
        self.times[name] += f_time
      self.timestamps.pop(name)
    else:
      self.timestamps[name] = time()

  def print_time(self, name: str):
    """Imprime el tiempo de una variable particular"""
    print(self.times[name])

  def times_string(self):
    """"Retorna un string con el detalle de los tiempos"""
    string = f'{"nombre": <20} | {"tiempo": <10} | {"% del total": <10}%\n'
    total_time = round(time() - self.start, 5)
    for name, value in self.times.items():
      value = round(value, 5)
      perc = round(value / total_time * 100, 1)
      perc = f"{perc}%"
      string += f'{name: <20} | {value: <10} | {perc: <10}\n'
    string += f'{"Total": <20} | {total_time: <10} | 100%'
    return string


timer = Timer()
