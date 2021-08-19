from gurobipy import Model, GRB, quicksum
from .params import get_params


def subproblem(x_opt, alfa_opt, start_date, end_date, pattern_generator, champ_stats):
  m = Model("SSTPA Benders subproblem")
  params = get_params(start_date, end_date, pattern_generator, champ_stats)
  m.setParam('LogToConsole', 0)

  # Parse params dict to values
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

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f con
  # la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  p = m.addVars(I, I, F, F, vtype=GRB.INTEGER, name="p")

  # v_nilf : v[partido, equipo, fecha, fecha]
  # binaria,  1 si el equipo local gana el partido n de la
  # fecha f teniendo informacion finalizada la fecha l en el
  # MEJOR/PEOR conjunto de resultados futuros para el equipo i
  v = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="v")

  # a_nilf: a[partido,equipo,fecha,fecha]
  # 1 si el equipo visitante gana el partido n de la fecha f
  # teniendo información finalizada la fecha l
  # en el MEJOR/PEOR conjunto de resultados para el equipo i
  a = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="a")

  # e_nilf: e[partido,equipo,fecha,fecha]
  # binaria, toma el valor 1 si se empata el partido n de la fecha f,
  # con la info de los resultados hasta la fecha l inclusive en el
  # MEJOR/PEOR conjunto de resultados futuros para el euqipo i
  e = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="e")

  # alfa_jil : alfa[equipo, equipo, fecha]
  # binaria, toma el valor 1 si el equipo j termina con menos
  # puntos que el equipo i en el MEJOR/PEOR conjunto de
  # resultados futuros para el equipo i considerando que
  # se está en la fecha l
  alfa = m.addVars(I, I, F, vtype=GRB.BINARY, name="alfa")


  #####################
  #*  RESTRICCIONES  *#
  #####################

  # R14
  x_r = m.addConstrs((x[n, f] == x_opt[n, f] for n in N for f in F), name='R14')

  # R15
  a_r = m.addConstrs((alfa[i, j, f] == alfa_opt[i, j, f]
                                                for i in I
                                                for j in I
                                                for f in F), name='R15')

  # R16
  m.addConstrs((x[n, f] == (v[n, i, l, f] + e[n, i, l, f] + a[n, i, l, f]) 
                                                                for n in N
                                                                for i in I
                                                                for f in F
                                                                for l in F
                                                                if  f > l),name='R16')

  # R17
  m.addConstrs(((p[j, i, l, f] == PI[j]
                  + quicksum(quicksum(R[j][n] * x[n,theta] for n in N if EL[j][n] + EV[j][n]  == 1)
                                                           for theta in F if theta > 5 and theta <= l)
                  + quicksum(quicksum(3 * v[n, i, l, theta] for theta in F if theta > l and theta <= f)
                                                                          for n in N if EL[j][n] == 1)
                  + quicksum(quicksum(3 * a[n, i, l, theta] for theta in F if theta > l and theta <= f)
                                                                          for n in N if EV[j][n] == 1)
                  + quicksum(quicksum(e[n, i, l, theta] for theta in F if theta > l and theta <= f)
                                                              for n in N if EL[j][n] + EV[j][n] == 1))
                                                                              for j in I 
                                                                              for i in I 
                                                                              for f in F 
                                                                              for l in F), name="R10")

  # R18
  m.addConstrs((((M * (alfa[j, i, l]) >= p[i, i, l, F[-1]] - p[j, i, l, F[-1]]))
                                                                          for i in I
                                                                          for j in I
                                                                          for l in F), name="R12")
  # R19
  m.addConstrs((((M - M * alfa[j, i, l] >= p[j, i, l, F[-1]] - p[i, i, l, F[-1]]))
                                                                          for i in I
                                                                          for j in I
                                                                          for l in F), name="R13")

  return m, x_r, a_r
