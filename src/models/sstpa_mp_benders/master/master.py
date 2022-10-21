from gurobipy import Model, GRB, quicksum, LinExpr
from itertools import product
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
  XI = params['XI']

  #################
  # *  VARIABLES  *#
  #################

  variables = {}

  # x_nf: x[partido, fecha]
  # 1 si el partido n se programa finalmente en la fecha f. 0 en otro caso.
  x = m.addVars(N, F, vtype=GRB.BINARY, name="x")
  variables['x'] = x

  # tau_inf: tau[equipo, partido, fecha]
  # 1 si el equipo i juega el partido n en la fecha f. 0 en otro caso
  tau = m.addVars(I, N, F, vtype=GRB.BINARY, name='tau')

  # gamma_ijf: gamma[equipo, equipo, fecha]
  # 1 si el equipo i juega contra el equipo j en la fecha f. 0 en otro caso
  gamma = m.addVars(I, I, F, vtype=GRB.BINARY, name='gamma')

  # epsilon_ijnf: epsilon[equipo, equipo, partido, fecha]
  # 1 si el equipo i juega contra el equipo j en el partido n programado en la fecha f.
  epsilon = m.addVars(I, I, N, F, vtype=GRB.BINARY, name='epsilon')

  if args.initial_sol:
    for n, f in product(N, F):
      x[n, f].start = XI[n][f]

  # y_is: y[equipo][patron_localias]
  # 1 si al equipo i se le asigna el patron de localias s. 0 en otro caso
  y = {}
  for i in I:
    for s in S[i]:
      y[i, s] = m.addVar(vtype=GRB.BINARY, name=f"y[{i},{s}]")
  variables['y'] = y

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j termina con menos puntos
  # que el equipo i en el
  # MEJOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha_m = m.addVars(I, I, F, vtype=GRB.BINARY, name="alpha_m")
  variables['alpha_m'] = alpha_m

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j tiene termina
  # con menos puntos que el equipo i, en el PEOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha_p = m.addVars(I, I, F, vtype=GRB.BINARY, name="alpha_p")
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
  for i, f in product(I, F):
    _exp = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1))
    m.addConstr(_exp == 1, name=f"R3[{i},{f}]")

  # R4
  if local_patterns:
    m.addConstrs((quicksum(y[i, s] for s in S[i]) == 1 for i in I), name="R4")

  # R5
  if local_patterns:
    for f, i in product(F, I):
      _exp1 = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] == 1))
      _exp2 = LinExpr(quicksum(y[i, s] for s in S[i] if L[s][f] == 1))
      m.addConstr(_exp1 == _exp2, name=f"R5[{f},{i}]")

  # R6
  if local_patterns:
    for f, i in product(F, I):
      _exp1 = LinExpr(quicksum(x[n, f] for n in N if EV[i][n] == 1))
      _exp2 = LinExpr(quicksum(y[i, s] for s in S[i] if L[s][f] == 0))
      m.addConstr(_exp1 == _exp2, name=f"R6[{f},{i}]")

  # R7
  for i, l in product(I, F):
    _exp = LinExpr(quicksum(alpha_m[j, i, l] for j in I if i != j))
    m.addConstr(beta_m[i, l] == len(I) - _exp, name=f"R7[{i},{l}]")

  # R8
  for i, l in product(I, F):
    _exp = LinExpr(quicksum(1 - alpha_p[j, i, l] for j in I if i != j))
    m.addConstr(beta_p[i, l] == 1 + _exp, name=f"R8[{i},{l}]")

  # RVI9
  for f in F:
    _exp = LinExpr(quicksum(quicksum(y[i, s] * L[s][f]for s in S[i]) for i in I))
    m.addConstr(_exp == len(I) // 2, name=f"R9[{f}]")

  # RVI12
  for i, n, f in product(I, N, F):
    _exp = (EL[i][n] + EV[i][n]) * x[n, f]
    m.addConstr(_exp == tau[i, n, f], name=f"RVI12[{i},{n},{f}]")

  # RVI13 and RVI14
  for i, j, n, f in product(I, I, N, F):
    m.addConstr(tau[i, n, f] + tau[j, n, f] <= 1 + epsilon[i, j, n, f],
                name=f"RVI13[{i},{j},{n},{f}]")
    m.addConstr(tau[i, n, f] + tau[j, n, f] >= 2 * epsilon[i, j, n, f],
                name=f"RVI14[{i},{j},{n},{f}]")

  # RV15
  for i, j, f in product(I, I, F):
    m.addConstr(quicksum(epsilon[i, j, n, f] for n in N) == gamma[i, j, f],
                name=f"RVI15[{i},{j},{f}]")

  # RVI16
  for i, j, k, f in product(I, I, I, F):
    if i != j and j != k and k != i:
      m.addConstr(gamma[i, j, f] + gamma[j, k, f] + gamma[k, i, f] <= 1,
                  name=f"RVI16[{i},{j},{k},{f}]")

  #########################
  # *  FUNCION OBJETIVO  *#
  #########################

  _obj = quicksum(l ** 2 * quicksum(beta_p[i, l] - beta_m[i, l] for i in I) for l in F[:-1])
  m.setObjective(_obj, GRB.MAXIMIZE)

  m.update()

  return m, variables
