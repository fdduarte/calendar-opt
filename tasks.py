from invoke import task


@task
def run_small(context, start=6, no_patterns=True):
  """Campeonato pequeño con descomposición"""
  com = f'python main.py --model 5 --start_date {start} --filepath "data/campeonato_6_1.xlsx"'
  if no_patterns:
    com += ' --no_local_patterns'
  context.run(com)
