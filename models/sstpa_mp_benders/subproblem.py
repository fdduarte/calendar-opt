from gurobipy import Model, GRB, quicksum
from .params import get_params


def subproblem(i, l, s, params):
    m = Model(f"SSTPA Benders subproblem: {i}-{l}-{s}")
    m.setParam('LogToConsole', 0)
    m.setParam('InfUnbdInfo', 1)
    m.setParam('LazyConstraints', 1)
    m.setParam('IISMethod', 0)

    # Parse params dict to values
    N = params['N']
    F = params['F']
    I = params['I']
    R = params['R']
    M = params['M']
    EL = params['EL']
    EV = params['EV']
    PI = params['PI']

    #################
    #*  VARIABLES  *#
    #################

    # x_nf: x[partido, fecha]
    # 1 si el partido n se programa finalmente
    # en la fecha f
    # 0 en otro caso.
    x = m.addVars(N, F, vtype=GRB.BINARY, name="x")

    # p_jilf: P[equipo, equipo, fecha, fecha]
    # discreta, cant de puntos del equipo j al finalizar la fecha f con
    # la info de los resultados hasta la fecha l inclusive en el
    # MEJOR/PEOR conjunto de resultados futuros para el equipo i
    p = m.addVars(I, F, vtype=GRB.INTEGER, name="p")

    # v_nilf : v[partido, equipo, fecha, fecha]
    # binaria,  1 si el equipo local gana el partido n de la
    # fecha f teniendo informacion finalizada la fecha l en el
    # MEJOR/PEOR conjunto de resultados futuros para el equipo i
    v = m.addVars(N, F, vtype=GRB.BINARY, name="v")

    # a_nilf: a[partido,equipo,fecha,fecha]
    # 1 si el equipo visitante gana el partido n de la fecha f
    # teniendo información finalizada la fecha l
    # en el MEJOR/PEOR conjunto de resultados para el equipo i
    a = m.addVars(N, F, vtype=GRB.BINARY, name="a")

    # e_nilf: e[partido,equipo,fecha,fecha]
    # binaria, toma el valor 1 si se empata el partido n de la fecha f,
    # con la info de los resultados hasta la fecha l inclusive en el
    # MEJOR/PEOR conjunto de resultados futuros para el euqipo i
    e = m.addVars(N, F, vtype=GRB.BINARY, name="e")

    # alfa_jil : alfa[equipo, equipo, fecha]
    # binaria, toma el valor 1 si el equipo j termina con menos
    # puntos que el equipo i en el MEJOR/PEOR conjunto de
    # resultados futuros para el equipo i considerando que
    # se está en la fecha l
    alfa = m.addVars(I, vtype=GRB.BINARY, name="alfa")

    #####################
    #*  RESTRICCIONES  *#
    #####################

    # R14
    m.addConstrs((x[n, f] == 0 for n in N for f in F), name='R14')

    # R15
    m.addConstrs((alfa[j] == 0 for j in I), name='R15')

    # R16
    m.addConstrs((x[n, f] == (v[n, f] + e[n, f] + a[n, f]) for n in N
                  for f in F if f > l),
                 name='R16')

    # R17
    m.addConstrs(((p[j, f] == PI[j] + quicksum(
        quicksum(R[j][n] * x[n, theta] for n in N if EL[j][n] + EV[j][n] == 1)
        for theta in F if theta > 5 and theta <= l) + quicksum(
            quicksum(3 * v[n, theta]
                     for theta in F if theta > l and theta <= f)
            for n in N if EL[j][n] == 1) + quicksum(
                quicksum(3 * a[n, theta]
                         for theta in F if theta > l and theta <= f)
                for n in N if EV[j][n] == 1) + quicksum(
                    quicksum(e[n, theta]
                             for theta in F if theta > l and theta <= f)
                    for n in N if EL[j][n] + EV[j][n] == 1)) for j in I
                  for f in F),
                 name="R17")

    # R18
    if s == 'p':
        m.addConstrs(
            (((M * (alfa[j]) >= p[i, F[-1]] - p[j, F[-1]])) for j in I),
            name="R12")
    # R19
    if s == 'm':
        m.addConstrs(
            (((M - M * alfa[j] >= p[j, F[-1]] - p[i, F[-1]])) for j in I),
            name="R13")

    m.update()

    return m
