from invoke import task
import time

# Task params

PATTERNS = False  # Si se usan patrones de localia/visita
PREPROCESS = True  # Si se usa preprocesamiento
BENDERS = True  # Si se usan cortes de benders
POSITION_CUTS = True  # Si se usan cortes de posiciones
IIS = True  # Si se usa IIS para cortes de Hamming
VERBOSE = True  # Si se imprime a consola


@task
def delete_cache(context, full=False):
  """Elimina el cache, si --full=true elimina logs"""
  context.run('rm data/json/params_*')
  context.run('rm data/json/patterns/*')
  context.run('rm data/patterns/*')

  if full:
    context.run('rm logs/*.txt')
    context.run('rm logs/model/*')


@task
def run_tiny(con, start=4):
  """Campeonato enano con descomposición"""
  com = f'python main.py --model 3 --start_date {start} --filepath "data/campeonato_4_1.xlsx"'
  if not PATTERNS:
    com += ' --no_local_patterns'
  if not PREPROCESS:
    com += ' --no_preprocess'
  if not BENDERS:
    com += ' --no_benders_cuts'
  if not IIS:
    com += ' --no_IIS'
  if not VERBOSE:
    com += ' --not_verbose'
  if not POSITION_CUTS:
    com += ' --no_position_cuts'
  con.run(com)


@task
def run_small(con, start=6):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_6_1.xlsx"'
  if not PATTERNS:
    com += ' --no_local_patterns'
  if not PREPROCESS:
    com += ' --no_preprocess'
  if not BENDERS:
    com += ' --no_benders_cuts'
  if not IIS:
    com += ' --no_IIS'
  if not VERBOSE:
    com += ' --not_verbose'
  con.run(com)


@task
def run_med(con, start=7):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_8_1.xlsx"'
  if not PATTERNS:
    com += ' --no_local_patterns'
  if not PREPROCESS:
    com += ' --no_preprocess'
  if not BENDERS:
    com += ' --no_benders_cuts'
  if not IIS:
    com += ' --no_IIS'
  if not VERBOSE:
    com += ' --not_verbose'
  con.run(com)


@task
def run_big(context, start=8, patterns=False, no_preprocess=False):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_10_1.xlsx"'
  if not patterns:
    com += ' --no_local_patterns'
  if no_preprocess:
    com += ' --no_preprocess'
  context.run(com)


@task
def run_huge(con, start=9):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_12_1.xlsx"'
  if not PATTERNS:
    com += ' --no_local_patterns'
  if not PREPROCESS:
    com += ' --no_preprocess'
  if not BENDERS:
    com += ' --no_benders_cuts'
  if not IIS:
    com += ' --no_IIS'
  if not VERBOSE:
    com += ' --not_verbose'
  con.run(com)


@task
def run_full(con, start=16):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/Datos.xlsx"'
  if not PATTERNS:
    com += ' --no_local_patterns'
  if not PREPROCESS:
    com += ' --no_preprocess'
  if not BENDERS:
    com += ' --no_benders_cuts'
  if not IIS:
    com += ' --no_IIS'
  if not VERBOSE:
    com += ' --not_verbose'
  con.run(com)


@task
def compare(con, reps=10):
  """Compara resultados de dos variaciones"""
  times1, times2 = [], []
  com = 'python main.py --model 5 --start_date 7 --filepath "data/campeonato_8_1.xlsx"'
  com1 = com + ' --not_verbose'
  com2 = com1 + ' --no_position_cuts'
  for _ in range(reps):
    start = time.time()
    con.run(com1)
    times1.append(time.time() - start)

    start = time.time()
    con.run(com2)
    times2.append(time.time() - start)
    avg1 = round(sum(times1) / len(times1), 5)
    avg2 = round(sum(times2) / len(times2), 5)

    print('Tiempo var 1:', avg1)
    print('Tiempo var 2:', avg2)

