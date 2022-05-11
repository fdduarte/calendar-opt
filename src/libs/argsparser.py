import argparse

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
  "--mip_gap",
  default=0,
  type=int,
  help="Gap de optimalidad"
)

parser.add_argument(
  "--mip_focus",
  default=1,
  type=int,
  help="Gurobi solver focus."
)

parser.add_argument(
  "--time_limit",
  default=10000 * 60 * 60,
  type=int,
  help="Tiempo limite de ejecucion (en segundos)",
)

parser.add_argument(
  "--verbose",
  default=True,
  type=bool,
  help="Output en consola",
)

parser.add_argument("--gap", default=0.0, type=float, help="Gap del modelo.")

args = parser.parse_args()