from .argsparser import args


def name_output():
  """Names the output file"""
  filepath, _ = args.filepath.split('.')
  filename = filepath.split('/')[-1]
  outfile_name = f'model-{filename}-'
  if args.fixed_x:
    outfile_name += 'init-0'
  else:
    outfile_name += f'opt-{int(args.gap * 100)}'
  if args.output != '':
    outfile_name += f'-{args.output}'
  return outfile_name
