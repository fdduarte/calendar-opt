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