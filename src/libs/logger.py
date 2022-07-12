from .argsparser import args


def log(category: str, message: str):
  """Loggea en caso del el argumento verbose sea verdad"""
  if args.verbose:
    print(f"[{category}] {message}")
