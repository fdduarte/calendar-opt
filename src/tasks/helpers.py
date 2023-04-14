def add_params(command, gap, preprocess_gap, fixed_x):
  """add params to a command"""
  command += f' --gap {gap} --lp_gap {preprocess_gap}'
  if fixed_x:
    command += ' --fixed_x'
  return command


def add_output_file(command, filename):
  return f"{command} --output {filename}"


def parse_command_file(filename):
  commands = []
  with open(f'./src/tasks/data/{filename}', 'r', encoding='utf-8') as infile:
    for line in infile:
      if line[0] == '#':
        continue
      if line[0:3] == 'py-':
        line = line.strip('py-')
        commands.append(('py', line))
        continue
      command = line.strip()
      commands.append(('shell', command))
  return commands
