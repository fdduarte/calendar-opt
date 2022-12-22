import argparse
from datetime import datetime

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
    default=1,
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
    "--fixed_x",
    action='store_true',
    default=False,
    help="Se dejan los partidos como vienen",
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
    default=0.01,
    type=float,
    help="Gap del modelo."
)

parser.add_argument(
    "--lp_gap",
    default=0.0,
    type=float,
    help="Gap del preprocesamiento (relajación)."
)

parser.add_argument(
    "--w1",
    default=1.0,
    type=float,
    help="Peso w1 en la función objetivo."
)

parser.add_argument(
    "--w2",
    default=1.0,
    type=float,
    help="Peso w2 en la función objetivo."
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

parser.add_argument(
    "--no_position_cuts",
    action="store_true",
    default=False,
    help="Si se usan cortes de posiciones."
)

parser.add_argument(
    "--print_every_n_cuts",
    default=100,
    type=int,
    help="Valor que dice cada cuantos cortes agregados se hace una impresión a consola."
)

parser.add_argument(
    "--initial_sol",
    action="store_true",
    default=False,
    help="Si se usa el torneo como solución inicial."
)

parser.add_argument(
    "--shuffle_params",
    action="store_true",
    default=False,
    help="Si se ordenan de forma aleatoria los patrones de resultado."
)

parser.add_argument(
    "--mipnode_cuts",
    action="store_true",
    default=False,
    help="Si se agregan cortes en mipnode."
)

args = parser.parse_args()
args.IIS = not args.no_IIS
args.local_patterns = not args.no_local_patterns
args.preprocess = not args.no_preprocess
args.position_cuts = not args.no_position_cuts
args.benders_cuts = not args.no_benders_cuts
args.verbose = not args.not_verbose
args.mip_gap = args.gap
args.lp_gap = args.lp_gap

model_to_name = {
    3: 'Integrado',
    5: 'Descompuesto'
}

if args.fixed_x and args.model == 5:
  raise Exception("Solamente se pueden dejar las x's fijas en el modelo integrado")

if args.verbose:
  print('Optimización calendario deportivo')
  dt_s = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  print(dt_s, '\n')

  print('[args] Modelo:', model_to_name[args.model])
  print('[args] Fecha de inicio:', args.start_date)
  print('[args] Breaks:', args.breaks)
  print('[args] Path del archivo:', args.filepath)
  print('[args] MIP gap:', args.gap)
  print('[args] MIP focus:', args.mip_focus)
  print('[args] Tiempo máximo:', args.time_limit)
  print('[args] Patrones:', args.local_patterns)
  print('[args] Solución Inicial:', args.initial_sol)
  print('[args] Orden de parámetros aleatorio:', args.shuffle_params)
  print('[args] MIPNODE benders cuts', args.mipnode_cuts)
  print(f'[args] Pesos función objetivo: w1={args.w1}, w2={args.w2}')
  if args.model == 5:
    print('[args] IIS:', args.IIS)
    print('[args] Preprocesamiento', args.preprocess)
    print('[args] LP gap preprocesamiento', args.lp_gap)
    print('[args] Cortes de Benders', args.benders_cuts)
    print('[args] Cortes de posición', args.position_cuts)
    print('[args] Print cada n cortes', args.print_every_n_cuts)
  print("")
