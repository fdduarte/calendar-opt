from src.libs.argsparser import args
from src.models import sstpa_mp_create_model, sstpa_mp_benders_create_model
from src.params import sstpa_mp_generate_params, sstpa_mp_benders_generate_params
from src.libs.timer import timer
from src.libs.logger import logger


if __name__ == "__main__":
  assert args.model in range(1, 6)

  if args.model == 3:
    sstpa_mp_generate_params()
    m, _ = sstpa_mp_create_model()

  if args.model == 5:
    sstpa_mp_benders_generate_params()
    m = sstpa_mp_benders_create_model()

  m.optimize()
  outfile_name = 'model-'
  if args.fixed_x:
    outfile_name += 'init-0'
  else:
    outfile_name += f'opt-{int(args.gap * 100)}'
  if args.output != '':
    outfile_name += f'-{args.output}'
  m.write(f'logs/model/{outfile_name}.lp')
  m.write(f'logs/output/{outfile_name}.sol')

  if args.verbose:
    print('\n[time] logs:')
    print(timer.times_string())

    print('\n[stats] logs:')
    print(logger.stats_string())
