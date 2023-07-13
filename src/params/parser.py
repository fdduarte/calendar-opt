from ..libs.argsparser import args
from ..libs.xlsx import sheet_parser
from ..libs import gurobi_sol_parser


parsers = {
  'sheets': sheet_parser,
  'gurobi_sol': gurobi_sol_parser,
}


def instanciate_parser():
  """instanciate the parser given args specs"""
  if args.parser not in parsers:
    raise Exception('Parser not defined')
  return parsers[args.parser]
