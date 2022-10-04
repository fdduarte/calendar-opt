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
  m.write('logs/model/model.lp')
  m.write('logs/output/model.sol')

  if args.verbose:
    print('\n[time] logs:')
    print(timer.times_string())

    print('\n[stats] logs:')
    print(logger.stats_string())
