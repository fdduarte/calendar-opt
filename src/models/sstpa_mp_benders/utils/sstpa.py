from gurobipy import quicksum

def create_sstpa_restrictions(self, model, var):
    """
    Dada una familia de variables del modelo sstpa, crea restricciones del tipo
    for var in fam_var: var = 0. Esta restricción permite posteriormente fijar
    el lado derecho para así fijar la variable.
    """
    for n in self.params['N']:
        for f in self.params['F']:
            var = model.getVarByName(f'x[{n},{f}]')
            model.addConstr(var == 0, name=f'R-x[{n},{f}]')

    model.update()


def set_sstpa_restrictions(model, var_name, var):
    """
    Setea el lado derecho (rhs) de la restriccion de la variable var para
    el modelo SSTPA.
    """
    assert var_name in ['x'], 'Variable no soportada'
    for index, value in var.items():
        if value > 0.5:
            value = 1
        else:
            value = 0
        if var_name == 'x':
            n, f = index
            model.getConstrByName(f'R-x[{n},{f}]').rhs = value
    
    model.update()

def create_position_cut(model, self, i, l, d=2):
    """
    Given the model, a solved instance of the SSTPA model,
    a team i and a date l, generates a position cut.
    """
    # Get best possible position k
    k = int(self.sstpa_model.getVarByName(f'beta_m[{i},{l}]').X)
    S_indexes, S = [], []

    # Get x^* support S
    for (n, f), value in self.last_sol.items():
        if value > 0.5:
            S_indexes.append(f'x[{n},{f}]')

    # Get the model vars in S
    for index in S_indexes:
        S.append(model.getVarByName(index))

    # Get the model beta
    beta = model.getVarByName(f'beta_m[{i},{l}]')
    
    # Generate cut
    cut1 = beta >= (1 - k) * (1 / d) * quicksum((1 - x) for x in S) + k
    cut2 = beta <= (1 - k) * (len(self.params['N']) / d) * quicksum((1 - x) for x in S) + k
    return cut1, cut2

def _to_int(value):
    if value > 0.5:
        return 1
    else:
        return 0
