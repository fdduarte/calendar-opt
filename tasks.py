from invoke import task

# Task params

PATTERNS = False  # Si se usan patrones de localia/visita
PREPROCESS = False  # Si se usa preprocesamiento
BENDERS = True  # Si se usan cortes de benders
IIS = False  # Si se usa IIS para cortes de Hamming
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
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_4_1.xlsx"'
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
