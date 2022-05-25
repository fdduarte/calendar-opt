from gurobipy import Model, GRB, quicksum, LinExpr
from ...libs.argsparser import args


# pylint: disable=invalid-name
def master(params, time_limit=3600, mip_gap=1):
  """Genera el modelo maestro de SSTPA"""

  local_patterns = not args.no_local_patterns

  m = Model("SSTPA Benders Master")
  m.setParam("TimeLimit", time_limit)
  m.setParam("LogToConsole", 1)
  m.setParam("LazyConstraints", 1)
  m.setParam("MIPGap", mip_gap)

  # Parse params dict to values
  N = params['N']
  F = params['F']
  S = params['S']
  I = params['I']
  L = params['L']
  EL = params['EL']
  EV = params['EV']

  #################
  # *  VARIABLES  *#
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

  # beta_il: beta[equipo,fecha]
  # discreta, indica la mejor posicion
  # que puede alcanzar el equipo i al final del
  # torneo, mirando desde la fecha l en el MEJOR
  # conjunto de resultados futuros para el equipo i
  beta_m = m.addVars(I, F, vtype=GRB.INTEGER, name="beta_m")

  # beta_il: beta[equipo, fecha]
  # discreta, indica la mejor posicion
  # que puede alcanzar el equipo i al final del
  # torneo, mirando desde la fecha l en el PEOR
  # conjunto de resultados futuros para el equipo i
  beta_p = m.addVars(I, F, vtype=GRB.INTEGER, name="beta_p")

  #####################
  # *  RESTRICCIONES  *#
  #####################

  # R2
  for n in N:
    m.addConstr((quicksum(x[n, f] for f in F) == 1), name=f"R2-{n}")

  # R3
  for i in I:
    for f in F:
      m.addConstr((quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1) == 1), name="R3")

  # R4
  if local_patterns:
    m.addConstrs((quicksum(y[i][s] for s in S[i]) == 1 for i in I), name="R4")

  # R6
  if local_patterns:
    for f in F:
      for i in I:
        _exp1 = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] == 1))
        _exp2 = LinExpr(quicksum(y[i][s] for s in S[i] if L[s][f] == 1))
        m.addConstr(_exp1 == _exp2, name=f"R6-{f}-{i}")

  # R7
  if local_patterns:
    for f in F:
      for i in I:
        _exp1 = LinExpr(quicksum(x[n, f] for n in N if EV[i][n] == 1))
        _exp2 = LinExpr(quicksum(y[i][s] for s in S[i] if L[s][f] == 0))
        m.addConstr(_exp1 == _exp2, name=f"R7-{f}-{i}")

  # R8
  for i in I:
    for l in F:
      _exp = LinExpr(quicksum(alfa_m[j, i, l] for j in I if i != j))
      m.addConstr(beta_m[i, l] == len(I) - _exp, name=f"R8-{i}-{l}")

  # R9
  for i in I:
    for l in F:
      _exp = LinExpr(quicksum(alfa_p[j, i, l] for j in I if i != j))
      m.addConstr(beta_p[i, l] == len(I) - _exp, name=f"R9-{i}-{l}")

  #########################
  # *  FUNCION OBJETIVO  *#
  #########################

  _obj = quicksum(quicksum(beta_p[i, l] - beta_m[i, l] for i in I) for l in F)
  m.setObjective(_obj, GRB.MAXIMIZE)

  return m
