from itertools import product
from gurobipy import Model, GRB, quicksum, LinExpr


# pylint: disable=invalid-name
def subproblem(i, l, s, params):
  """Genera el subproblema de SSTPA relajado"""

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
  p = m.addVars(I, [i], [l], F, vtype=GRB.CONTINUOUS, name="p")

  # v_nilf : v[partido, equipo, fecha, fecha]
  # binaria,  1 si el equipo local gana el partido n de la
  # fecha f teniendo informacion finalizada la fecha l en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  v = m.addVars(N, [i], [l], F, vtype=GRB.CONTINUOUS, name="v")

  # a_nilf: a[partido,equipo,fecha,fecha]
  # 1 si el equipo visitante gana el partido n de la fecha f
  # teniendo información finalizada la fecha l
  # en el MEJOR/PEOR conjunto de resultados para el equipo i
  a = m.addVars(N, [i], [l], F, vtype=GRB.CONTINUOUS, name="a")

  # e_nilf: e[partido,equipo,fecha,fecha]
  # binaria, toma el valor 1 si se empata el partido n de la fecha f,
  # con la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el euqipo i
  e = m.addVars(N, [i], [l], F, vtype=GRB.CONTINUOUS, name="e")

  #####################
  # * RESTRICCIONES * #
  #####################

  res = {}

  # R13
  res['R3'] = {}
  for n, f, in product(N, F):
    if f > l:
      _exp = LinExpr(v[n, i, l, f] + e[n, i, l, f] + a[n, i, l, f])
      r = m.addConstr(_exp == 0, name=f"R3[{n},{i},{f},{l}]")
      res['R3'][n, i, f, l] = r

  # R14
  res['R4'] = {}
  for j, f in product(I, F):
    if f > l:
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
                      name=f"R4[{j},{i},{f},{l}]")
      res['R4'][j, i, f, l] = r

  # R17
  res['R5M'] = {}
  if s == 'm':
    for j in I:
      if j != i:
        r = m.addConstr(p[i, i, l, F[-1]] - p[j, i, l, F[-1]] >= 0, name=f"R5M[{l},{i},{j}]")
        res['R5M'][l, i, j] = r

  res['R5P'] = {}
  if s == 'p':
    for j in I:
      if j != i:
        r = m.addConstr(p[j, i, l, F[-1]] - p[i, i, l, F[-1]] >= 0, name=f"R5P[{l},{i},{j}]")
        res['R5P'][l, i, j] = r

  for n, f in product(N, F):
    m.addConstr(v[n, i, l, f] >= 0)
    m.addConstr(e[n, i, l, f] >= 0)
    m.addConstr(a[n, i, l, f] >= 0)

  m.update()

  return m, res
