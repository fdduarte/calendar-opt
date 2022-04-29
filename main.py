import argparse
from src.models import sstpa_mp_create_model
from src.params import sstpa_mp_generate_params


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="")

  parser.add_argument(
    "--model", default=1, type=int, help="Tipo de modelo a ejecutar"
  )

  parser.add_argument(
    "--start_date", default=23, type=int, help="Fecha de inicio del campeonato"
  )

  parser.add_argument(
    "--end_date", default=30, type=int, help="Fecha de fin del campeonato"
  )

  parser.add_argument(
    "--breaks",
    default=2,
    type=int,
    help="Cantidad de breaks localia-visita permitidos",
  )

  parser.add_argument(
    "--filepath",
    default="data/Datos.xlsx",
    type=str,
    help="Path del archivo de datos",
  )

  parser.add_argument(
    "--timelimit",
    default=10000 * 60 * 60,
    type=int,
    help="Tiempo limite de ejecucion (en segundos)",
  )

  parser.add_argument("--gap", default=0.0, type=float, help="Gap del modelo.")

  args = parser.parse_args()

  assert args.model in range(1, 6)

  """
  if args.model == 1:
    m, S_F = sstpa3_create_model(
      args.start_date,
      args.end_date,
      args.timelimit,
      args.breaks,
      champ_stats,
    )
  """

  if args.model == 3:
    sstpa_mp_generate_params(args.filepath, args.start_date)
    m = sstpa_mp_create_model(
      args.start_date,
      args.filepath,
      args.timelimit,
      args.breaks,
      mip_gap=args.gap,
    )

  """
  if args.model == 5:
    m = sstpa_mp_benders_create_model(
      args.start_date,
      args.end_date,
      args.timelimit,
      args.breaks,
      instance_params,
      mip_gap=args.gap,
    )"""

  m.optimize()

  if args.model == 5:
    m._print()

  # if args.model == 5:
  #  ModelStats.parse_gurobi_output(m, champ_stats.matches, f'model-{args.model}-{time.time()}', benders=True)
  # else:
  #  ModelStats.parse_gurobi_output(m.getVars(), champ_stats.matches, f'model-{args.model}-{time.time()}')
  # ModelStats.check_valid_output()
