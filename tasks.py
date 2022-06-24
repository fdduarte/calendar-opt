from invoke import task


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
def run_small(context, start=6, patterns=False, no_preprocess=False):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_6_1.xlsx"'
  if not patterns:
    com += ' --no_local_patterns'
  if no_preprocess:
    com += ' --no_preprocess'
  context.run(com)


@task
def run_med(context, start=7, patterns=False, no_preprocess=False):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_8_1.xlsx"'
  if not patterns:
    com += ' --no_local_patterns'
  if no_preprocess:
    com += ' --no_preprocess'
  context.run(com)


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
def run_huge(context, start=9, patterns=False, no_preprocess=False):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_12_1.xlsx"'
  if not patterns:
    com += ' --no_local_patterns'
  if no_preprocess:
    com += ' --no_preprocess'
  context.run(com)
