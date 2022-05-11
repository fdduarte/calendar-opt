from .argsparser import args

def log(category: str, message: str):
  if args.verbose:
    print(f"[{category}] {message}")