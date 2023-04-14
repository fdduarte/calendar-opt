from src.libs.argsparser import args
from src.models import sstpa_mp_create_model, sstpa_mp_benders_create_model
from src.params import generate_params, append_data
from src.libs.timer import timer
from src.libs.logger import logger
from src.libs.output_namer import name_output


if __name__ == "__main__":
  assert args.model in range(1, 6)
  generate_params()

  if args.model == 3:
    m, _ = sstpa_mp_create_model()
  if args.model == 5:
    m = sstpa_mp_benders_create_model()

  m.optimize()
  outfile_name = name_output()
  logger.log('output', outfile_name)
  m.write(f'logs/model/{outfile_name}.lp')
  m.write(f'logs/output/{outfile_name}.sol')
  append_data(f'logs/output/{outfile_name}.sol')

  if args.verbose:
    print('\n[time] logs:')
    print(timer.times_string())

    print('\n[stats] logs:')
    print(logger.stats_string())
