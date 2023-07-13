from itertools import product
from gurobipy import Model, GRB, quicksum, LinExpr


# pylint: disable=invalid-name
def subproblem(i, l, s, params):
  """Genera el subproblema de SSTPA"""

  m = Model(f"SSTPA Benders subproblem: {i}-{l}-{s}")
  m.Params.LogToConsole = 0
  m.Params.InfUnbdInfo = 1
  m.Params.LazyConstraints = 1
  m.Params.IISMethod = 0

  # Parse params dict to values
  N = params['N']
  F = params['F']
  I = params['I']
  EL = params['EL']
  EV = params['EV']
  R = params['R']
  PI = params['PI']
  M = params['M']

  #################
  # * VARIABLES * #
  #################

  variables = {}

  # x_nf: x[partido, fecha]
  # 1 si el partido n se programa finalmente
  # en la fecha f
  # 0 en otro caso.
  x = m.addVars(N, F, vtype=GRB.CONTINUOUS, name="x")

  # alpha_jil : alfa[equipo,equipo,fecha]
  # binaria, toma el valor 1 si el equipo j tiene termina
  # con menos puntos que el equipo i, en el PEOR/MEJOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alpha = m.addVars(I, [i], [l], vtype=GRB.CONTINUOUS, name="alpha")

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f con
  # la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  p = m.addVars(I, [i], [l], F, vtype=GRB.CONTINUOUS, name="p")
  variables['p'] = p

  # v_nilf : v[partido, equipo, fecha, fecha]
  # binaria,  1 si el equipo local gana el partido n de la
  # fecha f teniendo informacion finalizada la fecha l en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  v = m.addVars(N, [i], [l], F, vtype=GRB.BINARY, name="v")

  # a_nilf: a[partido,equipo,fecha,fecha]
  # 1 si el equipo visitante gana el partido n de la fecha f
  # teniendo información finalizada la fecha l
  # en el MEJOR/PEOR conjunto de resultados para el equipo i
  a = m.addVars(N, [i], [l], F, vtype=GRB.BINARY, name="a")

  # e_nilf: e[partido,equipo,fecha,fecha]
  # binaria, toma el valor 1 si se empata el partido n de la fecha f,
  # con la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el euqipo i
  e = m.addVars(N, [i], [l], F, vtype=GRB.BINARY, name="e")

  #####################
  # * RESTRICCIONES * #
  #####################

  res = {}

  res['R1'] = {}
  # R1
  for n, f, in product(N, F):
    r = m.addConstr(x[n, f] == 0, name=f"R1[{n},{i},{f},{l}]")
    res['R1'][n, f] = r

  # R2
  res['R2'] = {}
  for j in I:
    r = m.addConstr(alpha[j, i, l] == 0, name=f"R2[{j},{i},{l}]")
    res['R2'][j, i, l] = r

  # R3
  res['R3'] = {}
  for n, f, in product(N, F):
    if f > l:
      _exp = LinExpr(v[n, i, l, f] + e[n, i, l, f] + a[n, i, l, f])
      r = m.addConstr(_exp == x[n, f], name=f"R3[{n},{i},{f},{l}]")
      res['R3'][n, i, f, l] = r

  # R4
  res['R4'] = {}
  for j, f in product(I, F):
    if f > l:
      _exp1 = LinExpr(quicksum(quicksum(R[j][n] * x[n, theta]
                      for n in N if EL[j][n] + EV[j][n] == 1) for theta in F if theta <= l))
      _exp2 = LinExpr(quicksum(quicksum(3 * v[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EL[j][n]))
      _exp3 = LinExpr(quicksum(quicksum(3 * a[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EV[j][n]))
      _exp4 = LinExpr(quicksum(quicksum(e[n, i, l, theta]
                      for theta in F if l < theta <= f) for n in N if EL[j][n] + EV[j][n]))
      m.addConstr(p[j, i, l, f] - _exp2 - _exp3 - _exp4 == PI[j] + _exp1,
                  name=f"R9[{j},{i},{f},{l}]")
      res['R4'][j, i, f, l] = r

  # R5M
  res['R5M'] = {}
  if s == 'm':
    for j in I:
      if j != i:
        r = m.addConstr(p[j, i, l, F[-1]] - p[i, i, l, F[-1]] <= M[j] * (1 - alpha[j, i, l]),
                        name=f"R5M[{l},{i},{j}]")
        res['R5M'][l, i, j] = r

  res['R5P'] = {}
  if s == 'p':
    for j in I:
      if j != i:
        r = m.addConstr(p[i, i, l, F[-1]] - p[j, i, l, F[-1]] <= M[i] * alpha[j, i, l],
                        name=f"R5P[{l},{i},{j}]")
        res['R5P'][l, i, j] = r

  m.update()

  return m, res, variables
