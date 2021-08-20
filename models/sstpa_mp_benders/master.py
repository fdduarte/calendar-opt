from gurobipy import Model, GRB, quicksum
from .params import get_params


def master(time_limit, start_date, end_date, pattern_generator, champ_stats):
  m = Model("SSTPA Benders Master")
  m.setParam('TimeLimit', time_limit)
  m.setParam('LogToConsole', 1)

  params = get_params(start_date, end_date, pattern_generator, champ_stats)

  # Parse params dict to values
  N = params['N']
  F = params['F']
  S = params['S']
  I = params['I']
  L = params['L']
  EL = params['EL']
  EV = params['EV']

  #################
  #*  VARIABLES  *#
  #################


  # x_nf: x[partido, fecha]
  # 1 si el partido n se programa finalmente
  # en la fecha f
  # 0 en otro caso.
  x = m.addVars(N, F, vtype=GRB.BINARY, name="x")

  # y_is: y[equipo][patron_localias]
  # 1 si al equipo i se le asigna el patron
  # de localias s
  # 0 en otro caso
  y = {i: m.addVars(S[i], vtype=GRB.BINARY, name="y") for i in I}

  # alfa_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j termina con menos puntos
  # que el equipo i en el
  # MEJOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alfa_m = m.addVars(I, I, F, vtype=GRB.BINARY, name="alfa_m")

  # alfa_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j tiene termina
  # con menos puntos que el equipo i, en el PEOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alfa_p = m.addVars(I, I, F, vtype=GRB.BINARY, name="alfa_p")

  #beta_il: beta[equipo,fecha]
  #discreta, indica la mejor posicion
  #que puede alcanzar el equipo i al final del 
  #torneo, mirando desde la fecha l en el MEJOR
  #conjunto de resultados futuros para el equipo i
  beta_m = m.addVars(I, F, vtype=GRB.INTEGER, name="beta_m")

  #beta_il: beta[equipo, fecha]
  #discreta, indica la mejor posicion
  #que puede alcanzar el equipo i al final del 
  #torneo, mirando desde la fecha l en el PEOR
  #conjunto de resultados futuros para el equipo i
  beta_p = m.addVars(I, F, vtype=GRB.INTEGER, name="beta_p")

  #####################
  #*  RESTRICCIONES  *#
  #####################

  # R2
  m.addConstrs((quicksum(x[n, f] for f in F) == 1 for n in N), name="R2")

  # R3
  m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1) == 1 for i in I
                                                                            for f in F), name="R3")

  # R4
  for i in I:
      m.addConstr((quicksum(y[i][s] for s in S[i]) == 1), name="R4")


  # R6
  for i in I:
      m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] == 1) == quicksum(y[i][s] for s in S[i] if L[s][f] == 1) for f in F), name="R6")

  # R7
  for i in I:
      m.addConstrs((quicksum(x[n, f] for n in N if EV[i][n] == 1) == quicksum(y[i][s] for s in S[i] if L[s][f] == 0) for f in F), name="R7")

  # R8
  for i in I:
      m.addConstrs(((beta_m[i, l] == len(I) - (quicksum(alfa_m[j, i, l] for j in I if i != j))) for l in F), name="R8")


  # R9
  for i in I:
      m.addConstrs(((beta_p[i, l] == 1 + (quicksum((1 - alfa_p[j, i, l]) for j in I if i != j))) for l in F), name="R9")

  ########################
  #*  FUNCION OBJETIVO  *#
  ########################

  m.setObjective(quicksum(quicksum(beta_p[i,l]-beta_m[i,l] for i in I) for l in F), GRB.MAXIMIZE)

  alpha = {'m': alfa_m, 'p': alfa_p}

  return m, x, alpha