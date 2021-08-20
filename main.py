from models import sstpa3_create_model, sstpa_mp_create_model, sstpa_mp_benders_create_model
from modules import ModelStats, PatternGenerator, ChampStats
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '--model',
        default=1, type=int,
        help='Tipo de modelo a ejecutar')

    parser.add_argument(
        '--start_date',
        default=23, type=int,
        help='Fecha de inicio del campeonato')

    parser.add_argument(
        '--end_date',
        default=30, type=int,
        help='Fecha de fin del campeonato')

    parser.add_argument(
        '--breaks',
        default=2, type=int,
        help='Cantidad de breaks localia-visita permitidos'
    )

    parser.add_argument(
        '--filepath',
        default='data/Datos.xlsx', type=str,
        help='Path del archivo de datos')

    parser.add_argument(
        '--timelimit',
        default=10000*60*60, type=int,
        help='Tiempo limite de ejecucion (en segundos)')

    args = parser.parse_args()

    assert args.model in range(1, 6)

    champ_stats = ChampStats(args.filepath, args.start_date, args.end_date)
    pattern_generator = PatternGenerator(args.start_date, args.end_date, args.breaks, champ_stats)

    if args.model == 1:
        m, S_F = sstpa3_create_model(args.start_date, args.end_date, args.timelimit, args.breaks, pattern_generator, champ_stats)

    if args.model == 3:
        m, S_F = sstpa_mp_create_model(args.start_date, args.end_date, args.timelimit, args.breaks, pattern_generator, champ_stats)

    if args.model == 5:
        m  = sstpa_mp_benders_create_model(args.start_date, args.end_date, args.timelimit, args.breaks, pattern_generator, champ_stats)

    m.optimize()

    if args.model != 5:
        ModelStats.parse_gurobi_output(m.getVars(), champ_stats.matches, S_F)
        ModelStats.check_valid_output()