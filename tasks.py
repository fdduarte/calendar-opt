from invoke import task

# default values
PATTERNS = True  # Si se usan patrones de localia/visita
BENDERS = True  # Si se usan cortes de benders
POSITION_CUTS = True  # Si se usan cortes de posiciones
IIS = True  # Si se usa IIS para cortes de Hamming
VERBOSE = True  # Si se imprime a consola
SHUFFLE = True  # Si se ordenan los patrones de forma aleatoria
MODEL = 5  # Modelo a utilizar. Opciones válidas 3 y 5.
GAP = '0.01'
FIXED_X = False
POLICY = True


def add_params(command, gap, preprocess_gap, fixed_x):
  """add params to a command"""
  command += f' --gap {gap} --lp_gap {preprocess_gap}'
  if fixed_x:
    command += ' --fixed_x'
  return command


def run_tiny(start, model, gap, preprocess_gap, fixed_x):
  """Campeonato enano con descomposición"""
  if not start:
    start = 4
  com = f'python main.py --model {model} --start_date {start} --filepath "data/campeonato_4_1.xlsx"'
  com = add_params(com, gap, preprocess_gap, fixed_x)
  return com


def run_small(start, model, gap, preprocess_gap, fixed_x):
  """Campeonato pequeño con descomposición"""
  if not start:
    start = 6
  com = f'python main.py --model {model} --start_date {start} --filepath "data/campeonato_6_1.xlsx"'
  com = add_params(com, gap, preprocess_gap, fixed_x)
  return com


def run_azerb(start, model, gap, preprocess_gap, fixed_x):
  if not start:
    start = 8
  com = f'python main.py --model {model} --start_date {start} --filepath "data/azerbaijan_8.xlsx"'
  com = add_params(com, gap, preprocess_gap, fixed_x)
  return com


championships = {
  'tiny': run_tiny,
  'small': run_small,
  'azerbaijan': run_azerb,
}


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
def run(
  con, champ='small', start=None, gap=GAP, preprocess_gap='0', model=MODEL, shuffle=SHUFFLE,
  fixed_x=FIXED_X, no_policy=(not POLICY)
):
  """Corre el campeonato"""
  if fixed_x:
    model = 3
    
  command = championships[champ](start, model, gap, preprocess_gap, fixed_x)
  if shuffle:
    command += ' --shuffle_params'
  if no_policy:
    command += ' --no_policy'
  con.run(command)
