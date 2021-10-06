def parse_vars(model, val, callback=False, is_integer=True):
    """
    Parse the {val} var from a model to dict
    """
    vars = dict()
    for var in model.getVars():
        name = var.VarName
        if val in name:
            name = name.strip(f"{val}[").strip("]").split(",")
            name = tuple([int(i) if i.isdigit() else i for i in name])
            if callback:
                value = model.cbGetSolution(var)
            else:
                value = var.X
            if is_integer:
                if value > 0.5:
                    vars[name] = 1
                else:
                    vars[name] = 0
            else:
                vars[name] = value
    return vars