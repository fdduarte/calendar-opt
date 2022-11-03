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
def run(con, model=5, no_pats=False):
  """Campeonato azerbeijan"""
  com = f'python main.py --model {model} --start_date 8 --filepath "data/azerbaijan_8.xlsx"'
  if no_pats:
    com += ' --no_local_patterns'
  con.run(com)
