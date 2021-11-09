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

def create_best_position_cut(model, sstpa, i, l, d=2):
    """
    Given the model, a solved instance of the SSTPA model,
    a team i and a date l, generates a cut.
    """
    # Get best possible position k
    k = int(sstpa.getVarByName(f'beta_m[{i},{l}]').X)
    S_indexes, S = [], []

    # Get x^* support S
    for var in sstpa.getVars():
        if 'x' in var.VarName:
            if _to_int(var.X) == 1:
                S_indexes.append(var.VarName)

    # Get the model vars in S
    for index in S_indexes:
        S.append(model.getVarByName(index))

    # Get the model beta
    beta = model.getVarByName(f'beta_m[{i},{l}]')
    
    # Generate cut
    cut = beta >= (1 - k) * (1 / d) * quicksum((1 - x) for x in S) + k
    return cut

def create_worst_position_cut(model, sstpa, i, l, N, d=2):
    """
    Given the model, a solved instance of the SSTPA model,
    a team i and a date l, generates a cut.
    """
    # Get best possible position k
    k = int(sstpa.getVarByName(f'beta_m[{i},{l}]').X)
    S_indexes, S = [], []

    # Get x^* support S
    for var in sstpa.getVars():
        if 'x' in var.VarName:
            if _to_int(var.X) == 1:
                S_indexes.append(var.VarName)

    # Get the model vars in S
    for index in S_indexes:
        S.append(model.getVarByName(index))

    # Get the model beta
    beta = model.getVarByName(f'beta_m[{i},{l}]')
    
    # Generate cut
    cut = beta <= (1 - k) * (len(N) / d) * quicksum((1 - x) for x in S) + k
    return cut

def _to_int(value):
    if value > 0.5:
        return 1
    else:
        return 0
