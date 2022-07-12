import argparse

parser = argparse.ArgumentParser(description="")

parser.add_argument(
  "--model",
  default=3,
  type=int,
  help="Tipo de modelo a ejecutar"
)

parser.add_argument(
  "--start_date",
  default=23,
  type=int,
  help="Fecha de inicio del campeonato"
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
  "--not_verbose",
  action='store_true',
  default=False,
  help="Output en consola",
)

parser.add_argument(
  "--no_local_patterns",
  action='store_true',
  default=False,
  help="Booleano que representa si se usan patrones de localia",
)

parser.add_argument(
  "--gap",
  default=0.0,
  type=float,
  help="Gap del modelo."
)

parser.add_argument(
  "--no_IIS",
  action="store_true",
  default=False,
  help="Si se usa IIS para el subproblema."
)

parser.add_argument(
  "--no_preprocess",
  action="store_true",
  default=False,
  help="Si se usa IIS para el subproblema."
)

parser.add_argument(
  "--save_model",
  action="store_true",
  default=False,
  help="Si se usa IIS para el subproblema."
)

parser.add_argument(
  "--no_benders_cuts",
  action="store_true",
  default=False,
  help="Si se usan cortes de benders."
)

args = parser.parse_args()
args.IIS = not args.no_IIS
args.local_patterns = not args.no_local_patterns
args.preprocess = not args.no_preprocess
args.benders_cuts = not args.no_benders_cuts
args.verbose = not args.not_verbose

model_to_name = {
  3: 'Integrado',
  5: 'Descompuesto'
}

if args.verbose:
  print('Optimización calendario deportivo\n')
  print('[args] Modelo:', model_to_name[args.model])
  print('[args] Fecha de inicio:', args.start_date)
  print('[args] Breaks:', args.breaks)
  print('[args] Path del archivo:', args.filepath)
  print('[args] MIP gap:', args.mip_gap)
  print('[args] MIP focus:', args.mip_focus)
  print('[args] Tiempo máximo:', args.time_limit)
  print('[args] Patrones:', args.local_patterns)
  if args.model == 5:
    print('[args] IIS:', args.IIS)
    print('[args] Preprocesamiento', args.preprocess)
    print('[args] Cortes de Benders', args.benders_cuts)
  print("")
