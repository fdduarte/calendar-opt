from itertools import product
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
  EL = params['EL']
  EV = params['EV']

  #################
  # * VARIABLES * #
  #################

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

  #####################
  # * RESTRICCIONES * #
  #####################

  res = {}

  # R13
  res['R13'] = {}
  for n in N:
    for f in F:
      if f > l:
        _exp = LinExpr(v[n, i, l, f] + e[n, i, l, f] + a[n, i, l, f])
        r = m.addConstr(_exp == 0, name=f"R13[{n},{i},{f},{l}]")
        res['R13'][n, i, f, l] = r

  # R14
  res['R14'] = {}
  for j in I:
    for f in F:
      _exp2 = LinExpr(quicksum(quicksum(3 * v[n, i, l, theta]
                               for theta in F if theta > l and theta <= f)
                      for n in N if EL[j][n] == 1))
      _exp3 = LinExpr(quicksum(quicksum(3 * a[n, i, l, theta]
                               for theta in F if theta > l and theta <= f)
                      for n in N if EV[j][n] == 1))
      _exp4 = LinExpr(quicksum(quicksum(e[n, i, l, theta]
                               for theta in F if theta > l and theta <= f)
                      for n in N if EL[j][n] + EV[j][n] == 1))
      r = m.addConstr(p[j, i, l, f] - _exp2 - _exp3 - _exp4 == 0,
                      name=f"R14[{j},{i},{f},{l}]")
      res['R14'][j, i, f, l] = r

  # R17
  res['R15'] = {}
  if s == 'm':
    for j in I:
      if j != i:
        r = m.addConstr(p[j, i, l, F[-1]] - p[i, i, l, F[-1]] <= 0, name=f"R15[{l},{i},{j}]")
        res['R15'][l, i, j] = r

  res['R16'] = {}
  if s == 'p':
    for j in I:
      if j != i:
        r = m.addConstr(p[j, i, l, F[-1]] - p[i, i, l, F[-1]] <= 0, name=f"R16[{l},{i},{j}]")
        res['R16'][l, i, j] = r

  if relaxed:
    for j, f in product(I, F):
      m.addConstr(p[j, i, l, f] >= 0)
    for n, f in product(N, F):
      m.addConstr(v[n, i, l, f] >= 0)
      m.addConstr(e[n, i, l, f] >= 0)
      m.addConstr(a[n, i, l, f] >= 0)

  m.update()

  return m, res
