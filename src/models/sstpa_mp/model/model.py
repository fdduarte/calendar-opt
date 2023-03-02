from itertools import product
from gurobipy import Model, GRB, quicksum, LinExpr
from ..parse_params import parse_params
from ....libs.argsparser import args
from ....libs.array_tools import closed_interval


# pylint: disable=invalid-name
def create_model(log=True, gap=True):
  """
  Funcion que crea modelo de optimizacion de multiples posiciones sin descomposicion
  """
  start_date = args.start_date
  filepath = args.filepath
  time_limit = args.time_limit
  mip_focus = args.mip_focus
  mip_gap = args.mip_gap
  local_patterns = args.local_patterns

  m = Model("SSTPA V3")

  if not args.verbose or not log:
    m.Params.LogToConsole = 0
  m.Params.TimeLimit = time_limit
  m.Params.MIPFocus = mip_focus
  if gap:
    m.Params.MIPGap = mip_gap
  else:
    m.Params.MIPGap = 0

  # Parse params dict to variables
  params = parse_params(filepath, start_date)

  fixed_x = args.fixed_x

  N = params['N']
  F = params['F']
  S = params['S']
  I = params['I']
  R = params['R']
  L = params['L']
  M = params['M']
  EL = params['EL']
  EV = params['EV']
  PI = params['PI']
  P = params['P']
  RF = params['RF']
  Rlb = params['Rlb']
  Rub = params['Rub']
  Rp = params['Rp']
  if fixed_x:
    x_bar = params['x_bar']

  #################
  # * VARIABLES * #
  #################

  variables = {}

  # x_nf: x[partido, fecha]
  # 1 si el partido n se programa finalmente
  # en la fecha f
  # 0 en otro caso.
  x = m.addVars(N, F, vtype=GRB.BINARY, name="x")
  variables['x'] = x

  # y_is: y[equipo][patron_localias]
  # 1 si al equipo i se le asigna el patron
  # de localias s
  # 0 en otro caso
  y = {}
  for i in I:
    for s in S[i]:
      y[i, s] = m.addVar(vtype=GRB.BINARY, name=f"y[{i},{s}]")
  variables['y'] = y

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f
  # con la info de los resultados hasta la fecha l inclusive
  # en el MEJOR conjunto de resultados futuros para el equipo i
  p_m = m.addVars(I, I, F, F, vtype=GRB.CONTINUOUS, name="p_m")

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f
  # con la info de los resultados hasta la fecha l inclusive
  # en el PEOR conjunto de resultados futuros para el equipo i
  p_p = m.addVars(I, I, F, F, vtype=GRB.CONTINUOUS, name="p_p")

  # v_nilf : v[partido, equipo, fecha, fecha]
  # binaria,  1 si el equipo local gana el partido n
  # de la fecha f teniendo informacion finalizada la fecha l
  # en el MEJOR conjunto de resultados futuros para el equipo i
  v_m = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="v_m")

  # v_nilf : v[partido, equipo, fecha, fecha]
  # binaria,  1 si el equipo local gana el partido n
  # de la fecha f teniendo informacion finalizada la fecha l
  # en el MEJOR conjunto de resultados futuros para el equipo i
  v_p = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="v_p")

  # a_nilf: a[partido,equipo,fecha,fecha]
  # 1 si el equipo visitante gana el partido n de la fecha f
  # teniendo información finalizada la fecha l
  # en el MEJOR conjunto de resultados para el equipo i
  a_m = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="a_m")

  # a_nilf: a[partido,equipo,fecha,fecha]
  # 1 si el equipo visitante gana el partido n de la fecha f
  # teniendo información finalizada la fecha l
  # en el PEOR conjunto de resultados para el equipo i
  a_p = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="a_p")

  # e_nilf: e[partido,equipo,fecha,fecha]
  # binaria, toma el valor 1 si se empata el
  # partido n de la fecha f, con la info
  # de los resultados hasta la fecha l inclusive
  # en el MEJOR conjunto de resultados futuros para el euqipo i
  e_m = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="e_m")

  # e_nilf: e[partido,equipo,fecha,fecha]
  # binaria, toma el valor 1 si se empata el
  # partido n de la fecha f, con la info
  # de los resultados hasta la fecha l inclusive
  # en el PEOR- conjunto de resultados futuros para el euqipo i
  e_p = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="e_p")

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j termina con menos puntos
  # que el equipo i en el
  # MEJOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha_m = m.addVars(I, I, F, vtype=GRB.BINARY, name="alpha_m")

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j tiene termina
  # con menos puntos que el equipo i, en el PEOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha_p = m.addVars(I, I, F, vtype=GRB.BINARY, name="alpha_p")

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
  variables['beta_p'] = beta_p

  # z_iluv: z[equipo, fecha, pos, pos]
  # variable binaria que indica si el equipo i en la fecha l
  # puede alcanzar u como mejor posición y v como peor posición
  z = m.addVars(I, F, P, P, vtype=GRB.BINARY, name='z')

  #####################
  # * RESTRICCIONES * #
  #####################

  if fixed_x:
    for n in N:
      for f in F:
        m.addConstr(x[n, f] == x_bar[str(n)][str(f)])

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
  for n, i, f, l in product(N, I, F, F):
    if f > l:
      _exp = LinExpr(v_m[n, i, l, f] + e_m[n, i, l, f] + a_m[n, i, l, f])
      m.addConstr(_exp == x[n, f], name=f"R7[{n},{i},{f},{l}]")

  # R8
  for n, i, f, l in product(N, I, F, F):
    if f > l:
      _exp = LinExpr(v_p[n, i, l, f] + e_p[n, i, l, f] + a_p[n, i, l, f])
      m.addConstr(_exp == x[n, f], name=f"R8[{n},{i},{f},{l}]")

  # R9
  for j, i, f, l in product(I, I, F, F):
    if f > l:
      _exp1 = LinExpr(quicksum(quicksum(R[j][n] * x[n, theta]
                      for n in N if EL[j][n] + EV[j][n] == 1) for theta in F if theta <= l))
      _exp2 = LinExpr(quicksum(quicksum(3 * v_m[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EL[j][n]))
      _exp3 = LinExpr(quicksum(quicksum(3 * a_m[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EV[j][n]))
      _exp4 = LinExpr(quicksum(quicksum(e_m[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EL[j][n] + EV[j][n]))
      m.addConstr(p_m[j, i, l, f] - _exp2 - _exp3 - _exp4 == PI[j] + _exp1,
                  name=f"R9[{j},{i},{f},{l}]")

  # R10
  for j, i, f, l in product(I, I, F, F):
    if f > l:
      _exp1 = LinExpr(quicksum(quicksum(R[j][n] * x[n, theta]
                      for n in N if EL[j][n] + EV[j][n] == 1) for theta in F if theta <= l))
      _exp2 = LinExpr(quicksum(quicksum(3 * v_p[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EL[j][n]))
      _exp3 = LinExpr(quicksum(quicksum(3 * a_p[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EV[j][n]))
      _exp4 = LinExpr(quicksum(quicksum(e_p[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EL[j][n] + EV[j][n]))
      m.addConstr(p_p[j, i, l, f] - _exp2 - _exp3 - _exp4 == PI[j] + _exp1,
                  name=f"R10[{j},{i},{f},{l}]")

  # R11
  for l, i, j in product(F, I, I):
    if j != i:
      m.addConstr(p_m[j, i, l, F[-1]] - p_m[i, i, l, F[-1]] <= M[j] * (1 - alpha_m[j, i, l]),
                  name=f"R11[{l},{i},{j}]")

  # R12
  for l, i, j in product(F, I, I):
    if j != i:
      m.addConstr(p_p[i, i, l, F[-1]] - p_p[j, i, l, F[-1]] <= M[i] * alpha_p[j, i, l],
                  name=f"R12[{l},{i},{j}]")

  # R13
  for i, l in enumerate(Rp):
    if i + 1 < len(Rp):
      lp1 = Rp[i + 1]
    elif l != F[-1]:
      lp1 = F[-1] + 1
    else:
      continue
    for _l in closed_interval(l, lp1):
      for i, j in product(I, I):
        if j != i:
          m.addConstr(p_m[i, j, l, F[-1]] == p_m[i, j, _l, F[-1]], name=f"R13[{l},{_l},{i},{j}]")

  # R14
  for i, l in enumerate(Rp):
    if i + 1 < len(Rp):
      lp1 = Rp[i + 1]
    elif l != F[-1]:
      lp1 = F[-1] + 1
    else:
      continue
    for _l in closed_interval(l, lp1):
      for i, j in product(I, I):
        if j != i:
          m.addConstr(p_p[i, j, l, F[-1]] == p_p[i, j, _l, F[-1]], name=f"R14[{l},{_l},{i},{j}]")

  # R15
  for i, l in product(I, F):
    m.addConstr(quicksum(quicksum(z[i, l, u, v] for u in P) for v in P) == 1, name=f'R15[{i},{l}]')

  # R16
  for i, l in product(I, F):
    m.addConstr(quicksum(quicksum(u * z[i, l, u, v] for u in P)
                for v in P) == beta_p[i, l], name=f'R16[{i},{l}]')

  # R17
  for i, l in product(I, F):
    m.addConstr(quicksum(quicksum(v * z[i, l, u, v] for u in P)
                for v in P) == beta_m[i, l], name=f'R17[{i},{l}]')

  # R18
  for i, l in product(I, F):
    _exp = LinExpr(quicksum(alpha_m[j, i, l] for j in I if i != j))
    m.addConstr(beta_m[i, l] == len(I) - _exp, name=f"R18[{i},{l}]")

  # R19
  for i, l in product(I, F):
    _exp = LinExpr(quicksum(1 - alpha_p[j, i, l] for j in I if i != j))
    m.addConstr(beta_p[i, l] == 1 + _exp, name=f"R19[{i},{l}]")

  # R20
  for i, l in product(I, F):
    m.addConstr(beta_m[i, l] <= beta_p[i, l], name=f"R20[{i},{l}]")

  ########################
  # * FUNCION OBJETIVO * #
  ########################
  _obj = LinExpr()
  for u, v, l, i in product(P, P, F, I):
    _obj += RF[u, v, l, i] * z[i, l, u, v]
  m.setObjective(_obj, GRB.MAXIMIZE)

  m.update()

  return m, variables
