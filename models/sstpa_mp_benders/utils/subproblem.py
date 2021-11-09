from gurobipy import LinExpr


def set_subproblem_values(master, subproblem):
    i, l, s = _get_subproblem_indexes(subproblem)
    for cons in subproblem.getConstrs():
        name = cons.getAttr('ConstrName')
        # Set same x vars (R14)
        if 'R14' in name:
            n, f = _get_index(name)
            var = master.getVarByName(f'x[{n},{f}]')
            value = _to_int(master.cbGetSolution(var))
            cons.rhs = value
        # Set same alpha vars (R15)
        if 'R15' in name:
            j = _get_index(name)[0]
            var = master.getVarByName(f'alfa_{s}[{j},{i},{l}]')
            value = _to_int(master.cbGetSolution(var))
            cons.rhs = value


def generate_cut(subproblem, master):
    """
    Given a solved suproblem with calculated IIS, returns
    a valid cut for the master problem
    """
    i, l, s = _get_subproblem_indexes(subproblem)
    cut = LinExpr()
    for var in subproblem.getVars():
        name = var.VarName
        if 'x' in name:
            n, f = _get_index(name)
            const = subproblem.getConstrByName(f'R14[{n},{f}]')
            if const.getAttr('IISConstr'):
                master_var = master.getVarByName(name)
                cut += master_var
        if 'alfa' in name:
            j = _get_index(name)[0]
            const = subproblem.getConstrByName(f'R15[{j}]')
            if const.getAttr('IISConstr'):
                master_var = master.getVarByName(f'alfa_{s}[{j},{i},{l}]')
                if master.cbGetSolution(master_var) > 0.5:
                    cut += 1 - master_var
                else:
                    cut += master_var
    return cut


def _get_subproblem_indexes(subproblem):
    name = subproblem.getAttr('ModelName')
    _, name = name.split(': ')
    i, l, s = name.split('-')
    return i, int(l), s


def _get_index(name):
    name = name.strip(']')
    _, name = name.split('[')
    index = [int(i) if i.isdigit() else i for i in name.split(',')]
    return tuple(index)


def _to_int(value):
    if value > 0.5:
        return 1
    else:
        return 0
