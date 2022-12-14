from platform import python_version

assert python_version() != '3.11.0', 'Invoke not working in python 3.11'

from invoke import task

# Task params

PATTERNS = True  # Si se usan patrones de localia/visita
BENDERS = True  # Si se usan cortes de benders
POSITION_CUTS = True  # Si se usan cortes de posiciones
IIS = True  # Si se usa IIS para cortes de Hamming
VERBOSE = True  # Si se imprime a consola
SHUFFLE = True  # Si se ordenan los patrones de forma aleatoria
MODEL = 5  # Modelo a utilizar. Opciones válidas 3 y 5.


@task
def clear_cache(context, full=False):
  """Elimina el cache, si --full=true elimina logs"""
  context.run('rm data/json/params_*')
  context.run('rm data/json/patterns/*')
  context.run('rm data/patterns/*')

  if full:
    context.run('rm logs/*.txt')
    context.run('rm logs/model/*')


@task
def run_tiny(con, start=4, gap='0', preprocess_gap='0'):
  """Campeonato enano con descomposición"""
  com = f'python main.py --model {MODEL} --start_date {start} --filepath "data/campeonato_4_1.xlsx"'
  if SHUFFLE:
    com += ' --shuffle_params'
  con.run(com)


@task
def run_small(con, start=6, gap='0', preprocess_gap='0'):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model {MODEL} --start_date {start} --filepath "data/campeonato_6_1.xlsx"'
  if SHUFFLE:
    com += ' --shuffle_params'
  con.run(com)
