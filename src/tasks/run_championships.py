from .helpers import add_params


def run_tiny(start, model, gap, preprocess_gap, fixed_x, filepath):
  """Campeonato 4"""
  if not start:
    start = 4
  if not filepath:
    filepath = '"data/campeonato_4_1.xlsx"'
  com = f'python main.py --model {model} --start_date {start} --filepath {filepath}'
  com = add_params(com, gap, preprocess_gap, fixed_x)
  return com


def run_small(start, model, gap, preprocess_gap, fixed_x, filepath):
  """Campeonato 6"""
  if not start:
    start = 6
  if not filepath:
    filepath = '"data/campeonato_6_1.xlsx"'
  com = f'python main.py --model {model} --start_date {start} --filepath {filepath}'
  com = add_params(com, gap, preprocess_gap, fixed_x)
  return com


def run_azerb(start, model, gap, preprocess_gap, fixed_x, filepath):
  """Campeonato azerbaijan"""
  if not start:
    start = 8
  if not filepath:
    filepath = '"data/azerbaijan_8.xlsx"'
  com = f'python main.py --model {model} --start_date {start} --filepath {filepath}'
  com = add_params(com, gap, preprocess_gap, fixed_x)
  return com


championships = {
  'tiny': run_tiny,
  'small': run_small,
  'azerbaijan': run_azerb,
}
