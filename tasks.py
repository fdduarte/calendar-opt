from invoke import task
from src.tasks import default_values as default
from src.tasks.run_championships import championships
from src.tasks.pipes import pipelines


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
  con, champ='small', start=None, gap=default.GAP, preprocess_gap='0', model=default.MODEL,
  shuffle=default.SHUFFLE, fixed_x=default.FIXED_X, no_policy=(not default.POLICY),
  parser=default.PARSER, filepath=None
):
  """Corre el campeonato"""
  if fixed_x:
    model = 3
  command = championships[champ](start, model, gap, preprocess_gap, fixed_x, filepath)
  if shuffle:
    command += ' --shuffle_params'
  if no_policy:
    command += ' --no_policy'
  if parser != 'sheets':
    command += f' --parser {parser}'
  print(command)
  con.run(command)


@task
def pipeline(con, number='1'):
  """Corre pipelines"""
  pipelines[number](con)
