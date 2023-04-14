from colorama import Back, Style
from .helpers import add_params, add_output_file, parse_command_file
from .console import print_color


def first_pipe(con):
  """Experimento reoptimizar con calendario prueba_6"""
  command1 = 'python main.py --start_date 6 --filepath "data/campeonato_6_1.xlsx"'
  command1 = add_output_file(add_params(command1, 0, 0, fixed_x=False), 'pipe1')
  print_color('Starting optimization from date 6', 'green')
  con.run(command1)

  command2 = 'python main.py --model 3 --start_date 6 --filepath logs/output/model-opt-0-pipe1.sol --no_policy --parser gurobi_sol'
  command2 = add_params(command2, 0, 0, fixed_x=True)
  print_color('--- Getting champ obj value', 'blue')
  con.run(command2)

  command3 = 'python main.py --model 3 --start_date 8 --filepath logs/output/model-opt-0-pipe1.sol --parser gurobi_sol --no_policy'
  command3 = add_output_file(add_params(command3, 0, 0, fixed_x=False), 'pipe2')
  print_color('Starting optimization from date 8', 'green')
  con.run(command3)

  command4 = 'python main.py --model 3 --start_date 6 --filepath logs/output/model-opt-0-pipe2.sol --no_policy --parser gurobi_sol'
  command4 = add_params(command4, 0, 0, fixed_x=True)
  print_color('--- Getting champ obj value', 'blue')
  con.run(command4)


def second_pipe(con):
  """Diferencia de GAP"""
  print(Back.GREEN, 'Starting optimization from date 6', Style.RESET_ALL)
  con.run('python main.py --start_date 6 --filepath "data/campeonato_6_1.xlsx" --gap 0 --lp_gap 0 --output pipe1 --no_policy')
  print(Back.BLUE, '--- Getting champ objective value', Style.RESET_ALL)
  con.run('python main.py --model 3 --start_date 6 --filepath logs/output/model-opt-0-pipe1.sol --gap 0 --lp_gap 0 --no_policy --parser gurobi_sol --fixed_x')
  print(Back.GREEN, 'Starting optimization from date 8', Style.RESET_ALL)
  con.run('python main.py --start_date 8 --filepath "data/campeonato_6_1.xlsx" --gap 0 --lp_gap 0 --output pipe2 --no_policy')
  print(Back.BLUE, '--- Getting champ objective value', Style.RESET_ALL)
  con.run('python main.py --model 3 --start_date 6 --filepath logs/output/model-opt-0-pipe2.sol --gap 0 --lp_gap 0 --no_policy --parser gurobi_sol --fixed_x')


def third_pipe(con):
  """Experimento reoptimizar con calendario suiza"""
  command1 = 'python main.py --model 5 --start_date 10 --filepath "data/suiza_10.xlsx" --no_policy'
  command1 = add_output_file(add_params(command1, 0, 0, fixed_x=False), 'pipe1')
  print_color('Starting optimization from date 10', 'green')
  con.run(command1)

  command2 = 'python main.py --model 3 --start_date 10 --filepath logs/output/model-opt-0-pipe1.sol --no_policy --parser gurobi_sol'
  command2 = add_output_file(add_params(command2, 0, 0, fixed_x=True), 'output1')
  print_color('--- Getting champ obj value', 'blue')
  con.run(command2)

  command3 = 'python main.py --model 5 --start_date 13 --filepath logs/output/model-opt-0-pipe1.sol --parser gurobi_sol --no_policy'
  command3 = add_output_file(add_params(command3, 0, 0, fixed_x=False), 'pipe2')
  print_color('Starting optimization from date 13', 'green')
  con.run(command3)

  command4 = 'python main.py --model 3 --start_date 10 --filepath logs/output/model-opt-0-pipe2.sol --no_policy --parser gurobi_sol'
  command4 = add_output_file(add_params(command4, 0, 0, fixed_x=True), 'output2')
  print_color('--- Getting champ obj value', 'blue')
  con.run(command4)


def fourth_pipe(con):
  commands = parse_command_file('pipeline4.txt')
  for ex, command in commands:
    if ex == 'shell':
      con.run(command)
    if ex == 'py':
      exec(commands)


pipelines = {
  '1': first_pipe,
  '2': second_pipe,
  '3': third_pipe,
  '4': fourth_pipe,
}
