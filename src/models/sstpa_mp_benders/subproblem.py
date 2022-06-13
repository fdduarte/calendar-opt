from gurobipy import Model, GRB, quicksum, LinExpr


# pylint: disable=invalid-name
def subproblem(i, l, s, params, relaxed=False):
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
  R = params['R']
  M = 61
  EL = params['EL']
  EV = params['EV']
  PI = params['PI']

  #################
  # * VARIABLES * #
  #################

  # x_nf: x[partido, fecha]
  # 1 si el partido n se programa finalmente
  # en la fecha f
  # 0 en otro caso.
  if relaxed:  # igual queda fija la variable a binaria por r14
    x = m.addVars(N, F, vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
  else:
    x = m.addVars(N, F, vtype=GRB.BINARY, name="x")

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f con
  # la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  if relaxed:
    p = m.addVars(I, [i], [l], F, vtype=GRB.CONTINUOUS, name="p")
  else:
    p = m.addVars(I, [i], [l], F, vtype=GRB.INTEGER, name="p")

  # v_nilf : v[partido, equipo, fecha, fecha]
  # binaria,  1 si el equipo local gana el partido n de la
  # fecha f teniendo informacion finalizada la fecha l en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  if relaxed:
    v = m.addVars(N, [i], [l], F, vtype=GRB.CONTINUOUS, name="v", lb=0, ub=1)
  else:
    v = m.addVars(N, [i], [l], F, vtype=GRB.BINARY, name="v")

  # a_nilf: a[partido,equipo,fecha,fecha]
  # 1 si el equipo visitante gana el partido n de la fecha f
  # teniendo información finalizada la fecha l
  # en el MEJOR/PEOR conjunto de resultados para el equipo i
  if relaxed:
    a = m.addVars(N, [i], [l], F, vtype=GRB.CONTINUOUS, name="a", lb=0, ub=1)
  else:
    a = m.addVars(N, [i], [l], F, vtype=GRB.BINARY, name="a")

  # e_nilf: e[partido,equipo,fecha,fecha]
  # binaria, toma el valor 1 si se empata el partido n de la fecha f,
  # con la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el euqipo i
  if relaxed:
    e = m.addVars(N, [i], [l], F, vtype=GRB.CONTINUOUS, name="e", lb=0, ub=1)
  else:
    e = m.addVars(N, [i], [l], F, vtype=GRB.BINARY, name="e")

  # alfa_jil : alfa[equipo, equipo, fecha]
  # binaria, toma el valor 1 si el equipo j termina con menos
  # puntos que el equipo i en el MEJOR/PEOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  if relaxed:
    alfa = m.addVars(I, [i], [l], vtype=GRB.CONTINUOUS, name="alfa", lb=0, ub=1)
  else:
    alfa = m.addVars(I, [i], [l], vtype=GRB.BINARY, name="alfa")

  #####################
  # * RESTRICCIONES * #
  #####################

  res = {}

  # R14
  m.addConstrs((x[n, f] == 0 for n in N for f in F), name='R14')

  # R15
  m.addConstrs((alfa[j, i, l] == 0 for j in I), name='R15')

  # R16
  res['R16'] = {}
  for n in N:
    for f in F:
      if f > l:
        _exp = LinExpr(v[n, i, l, f] + e[n, i, l, f] + a[n, i, l, f])
        r = m.addConstr(x[n, f] == _exp, name=f"R16[{n},{i},{f},{l}]")
        res['R16'][n, i, f, l] = r

  # R17
  res['R17'] = {}
  for j in I:
    for f in F:
      _exp1 = LinExpr(quicksum(quicksum(R[j][n] * x[n, theta]
                               for n in N if EL[j][n] + EV[j][n] == 1)
                      for theta in F if theta <= l))
      _exp2 = LinExpr(quicksum(quicksum(3 * v[n, i, l, theta]
                               for theta in F if theta > l and theta <= f)
                      for n in N if EL[j][n] == 1))
      _exp3 = LinExpr(quicksum(quicksum(3 * a[n, i, l, theta]
                               for theta in F if theta > l and theta <= f)
                      for n in N if EV[j][n] == 1))
      _exp4 = LinExpr(quicksum(quicksum(e[n, i, l, theta]
                               for theta in F if theta > l and theta <= f)
                      for n in N if EL[j][n] + EV[j][n] == 1))
      r = m.addConstr(p[j, i, l, f] == PI[j] + _exp1 + _exp2 + _exp3 + _exp4,
                      name=f"R17[{j},{i},{f},{l}]")
      res['R17'][j, i, f, l] = r

  # R18
  res['R18'] = {}
  if s == 'm':
    for j in I:
      if j != i:
        r = m.addConstr(M - M * alfa[j, i, l] >= 1 + p[j, i, l, F[-1]] - p[i, i, l, F[-1]],
                        name=f"R18[{l},{i},{j}]")
        res['R18'][l, i, j] = r
  else:
    for j in I:
      if j != i:
        r = m.addConstr(M * alfa[j, i, l] >= 1 + p[j, i, l, F[-1]] - p[i, i, l, F[-1]],
                        name=f"R18[{l},{i},{j}]")
        res['R18'][l, i, j] = r

  m.update()

  return m, res
