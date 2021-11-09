from gurobipy import LinExpr, quicksum

def set_sstpa_restrictions(model, x):
    """
    Set SSTPA model rhs for R1
    """
    for (i, j), value in x.items():
        if value > 0.5:
            value = 1
        else:
            value = 0
        model.getConstrByName(f'R1[{i},{j}]').rhs = value

def create_best_position_cut(model, i, l):
    """
    Given a solved instance of the SSTPA model, a team i and
    a date l, generates a cut.
    """
    # Get best possible position k
    beta = model.getVarByName(f'beta_m[{i},{l}]')
    k = int(beta.X)
    S = []

    # Get x^* support S
    for var in model.getVars():
        if 'x' in var.VarName:
            if _to_int(var.X) == 1:
                S.append(var)
    
    # Generate cut
    cut = beta >= (1 - k) * quicksum((1 - x) for x in S) + k
    return cut

def _to_int(value):
    if value > 0.5:
        return 1
    else:
        return 0
