from itertools import product
from gurobipy import Model, GRB, quicksum, LinExpr
from ....libs.argsparser import args


# pylint: disable=invalid-name
def master(params, log=True):
  """Genera el modelo maestro de SSTPA"""
  mip_gap = args.mip_gap
  time_limit = args.time_limit
  local_patterns = args.local_patterns

  m = Model("SSTPA Benders Master")
  if not args.verbose or not log:
    m.Params.LogToConsole = 0
  m.Params.TimeLimit = time_limit
  m.Params.LazyConstraints = 1
  m.Params.InfUnbdInfo = 1
  m.Params.MIPGap = mip_gap

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

  variables = {}

  # x_nf: x[partido, fecha]
  # 1 si el partido n se programa finalmente
  # en la fecha f
  # 0 en otro caso.
  x = m.addVars(N, F, vtype=GRB.CONTINUOUS, name="x")
  variables['x'] = x

  # y_is: y[equipo][patron_localias]
  # 1 si al equipo i se le asigna el patron
  # de localias s
  # 0 en otro caso
  y = {i: m.addVars(S[i], vtype=GRB.CONTINUOUS, name="y") for i in I}

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j termina con menos puntos
  # que el equipo i en el
  # MEJOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha_m = m.addVars(I, I, F, vtype=GRB.CONTINUOUS, name="alpha_m")
  variables['alpha_m'] = alpha_m

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j tiene termina
  # con menos puntos que el equipo i, en el PEOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha_p = m.addVars(I, I, F, vtype=GRB.CONTINUOUS, name="alpha_p")
  variables['alpha_p'] = alpha_p

  # beta_il: beta[equipo,fecha]
  # discreta, indica la mejor posicion
  # que puede alcanzar el equipo i al final del
  # torneo, mirando desde la fecha l en el MEJOR
  # conjunto de resultados futuros para el equipo i
  beta_m = m.addVars(I, F, vtype=GRB.CONTINUOUS, name="beta_m")
  variables['beta_m'] = beta_m

  # beta_il: beta[equipo, fecha]
  # discreta, indica la mejor posicion
  # que puede alcanzar el equipo i al final del
  # torneo, mirando desde la fecha l en el PEOR
  # conjunto de resultados futuros para el equipo i
  beta_p = m.addVars(I, F, vtype=GRB.CONTINUOUS, name="beta_p")
  variables['beta_p'] = beta_m

  #####################
  # *  RESTRICCIONES  *#
  #####################

  # R2
  for n in N:
    m.addConstr((quicksum(x[n, f] for f in F) == 1), name=f"R2[{n}]")

  # R3
  for i in I:
    for f in F:
      exp = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1))
      m.addConstr(exp == 1, name=f"R3[{i},{f}]")

  # R4
  if local_patterns:
    m.addConstrs((quicksum(y[i][s] for s in S[i]) == 1 for i in I), name="R4")

  # R5
  if local_patterns:
    for f in F:
      for i in I:
        _exp1 = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] == 1))
        _exp2 = LinExpr(quicksum(y[i][s] for s in S[i] if L[s][f] == 1))
        m.addConstr(_exp1 == _exp2, name=f"R5[{f},{i}]")

  # R6
  if local_patterns:
    for f in F:
      for i in I:
        _exp1 = LinExpr(quicksum(x[n, f] for n in N if EV[i][n] == 1))
        _exp2 = LinExpr(quicksum(y[i][s] for s in S[i] if L[s][f] == 0))
        m.addConstr(_exp1 == _exp2, name=f"R6[{f},{i}]")

  # R7
  for i in I:
    for l in F:
      _exp = LinExpr(quicksum(alpha_m[j, i, l] for j in I if i != j))
      m.addConstr(beta_m[i, l] == len(I) - _exp, name=f"R7[{i},{l}]")

  # R8
  for i in I:
    for l in F:
      _exp = LinExpr(quicksum(1 - alpha_p[j, i, l] for j in I if i != j))
      m.addConstr(beta_p[i, l] == 1 + _exp, name=f"R8[{i},{l}]")

  # R?
  for n, f in product(N, F):
    m.addConstr(x[n, f] >= 0)
    m.addConstr(x[n, f] <= 1)

  # R?
  for i in I:
    for s in S[i]:
      m.addConstr(y[i][s] >= 0)
      m.addConstr(y[i][s] <= 1)

  for i, j, f in product(I, I, F):
    m.addConstr(alpha_m[i, j, f] >= 0)
    m.addConstr(alpha_m[i, j, f] <= 1)

    m.addConstr(alpha_p[i, j, f] >= 0)
    m.addConstr(alpha_p[i, j, f] <= 1)

  _obj = quicksum(l * quicksum(beta_p[i, l] - beta_m[i, l] for i in I) for l in F[:-1])
  m.setObjective(_obj, GRB.MAXIMIZE)

  m.update()

  return m, variables
