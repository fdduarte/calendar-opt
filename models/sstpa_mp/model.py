
from gurobipy import Model, GRB, quicksum
import time
from .params import get_params

def create_model(start_date, end_date, time_limit, pattern_generator, champ_stats, mip_focus=1, mip_gap=0.3):
  m = Model("SSTPA V3")

  m.setParam('TimeLimit', time_limit)
  m.setParam('MIPFocus', mip_focus)
  m.setParam('MIPGap', mip_gap)


  params = get_params(start_date, end_date, pattern_generator, champ_stats)

  # Parse params dict to variables

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
  S_F = params['S_F']

  start_model = time.time()


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

  #p_jilf: P[equipo, equipo, fecha, fecha]
  #discreta, cant de puntos del equipo j al finalizar la fecha f
  #con la info de los resultados hasta la fecha l inclusive
  #en el MEJOR conjunto de resultados futuros para el equipo i
  p_m = m.addVars(I, I, F, F, vtype=GRB.INTEGER, name="p_m")

  #p_jilf: P[equipo, equipo, fecha, fecha]
  #discreta, cant de puntos del equipo j al finalizar la fecha f
  #con la info de los resultados hasta la fecha l inclusive
  #en el PEOR conjunto de resultados futuros para el equipo i
  p_p = m.addVars(I, I, F, F, vtype=GRB.INTEGER, name="p_p")


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


  #e_nilf: e[partido,equipo,fecha,fecha]
  #binaria, toma el valor 1 si se empata el 
  #partido n de la fecha f, con la info
  #de los resultados hasta la fecha l inclusive
  # en el MEJOR conjunto de resultados futuros para el euqipo i
  e_m = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="e_m")

  #e_nilf: e[partido,equipo,fecha,fecha]
  #binaria, toma el valor 1 si se empata el 
  #partido n de la fecha f, con la info
  #de los resultados hasta la fecha l inclusive
  # en el PEOR- conjunto de resultados futuros para el euqipo i
  e_p = m.addVars(N, I, F, F, vtype=GRB.BINARY, name="e_p")


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


  print(f"** VARIABLES TIME: {time.time() - start_model}")


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
  m.addConstrs((x[n,f] == (v_m[n,i,l,f] + e_m[n,i,l,f] + a_m[n,i,l,f])
                                                                  for n in N
                                                                  for i in I
                                                                  for f in F
                                                                  for l in F
                                                                  if  f > l),name="R8")
  
  # R9
  m.addConstrs((x[n,f] == (v_p[n,i,l,f] + e_p[n,i,l,f] + a_p[n,i,l,f])
                                                                  for n in N
                                                                  for i in I
                                                                  for f in F
                                                                  for l in F
                                                                  if  f > l),name="R9")

  # R10
  m.addConstrs(((p_m[j,i,l,f] == PI[j] + quicksum(quicksum(R[j][n] * x[n,theta] for n in N if EL[j][n] + EV[j][n]  == 1) for theta in F if theta > 5 and theta <= l)
          + quicksum(quicksum(3 * v_m[n,i,l,theta] for theta in F if theta > l and theta <= f) for n in N if EL[j][n] == 1)
          + quicksum(quicksum(3 * a_m[n,i,l,theta] for theta in F if theta > l and theta <= f) for n in N if EV[j][n] == 1)
          + quicksum(quicksum(e_m[n,i,l,theta] for theta in F if theta > l and theta <= f) for n in N if EL[j][n] + EV[j][n] == 1))
                          for j in I 
                          for i in I 
                          for f in F 
                          for l in F), name="R10")

  # R11
  m.addConstrs(((p_p[j,i,l,f] == PI[j] + quicksum(quicksum(R[j][n] * x[n,theta] for n in N if EL[j][n] + EV[j][n]  == 1) for theta in F if theta > 5 and theta <= l)
          + quicksum(quicksum(3 * v_p[n,i,l,theta] for theta in F if theta > l and theta <= f) for n in N if EL[j][n] == 1)
          + quicksum(quicksum(3 * a_p[n,i,l,theta] for theta in F if theta > l and theta <= f) for n in N if EV[j][n] == 1)
          + quicksum(quicksum(e_p[n,i,l,theta] for theta in F if theta > l and theta <= f) for n in N if EL[j][n] + EV[j][n] == 1))
                          for j in I 
                          for i in I 
                          for f in F 
                          for l in F), name="R11")

  #R12
  m.addConstrs((((M * (alfa_m[j, i, l]) >= p_m[i, i, l, F[-1]] - p_m[j, i, l, F[-1]])) for i in I
                                                                          for j in I
                                                                          for l in F), name="R12")
  # R13
  m.addConstrs((((M - M * alfa_m[j,i, l] >= p_m[j, i, l, F[-1]] - p_m[i, i, l, F[-1]])) for i in I
                                                                          for j in I
                                                                          for l in F), name="R13")

  # R14
  m.addConstrs((((M * (alfa_p[j, i, l]) >= p_p[i, i, l, F[-1]] - p_p[j, i, l, F[-1]])) for i in I
                                                                          for j in I
                                                                          for l in F), name="R14")
  #R15
  m.addConstrs((((M - M * alfa_p[j, i, l] >= p_p[j, i, l, F[-1]] - p_p[i, i, l, F[-1]])) for i in I
                                                                          for j in I
                                                                          for l in F), name="R15")

  #R16
  for i in I:
    m.addConstrs(((beta_m[i,l]==len(I)-(quicksum(alfa_m[j,i,l] for j in I if i!=j))) for l in F),name="R16")


  # R17
  for i in I:
    m.addConstrs(((beta_p[i,l]== 1+(quicksum((1-alfa_p[j,i,l]) for j in I if i!=j))) for l in F),name="R17")

  print(f"** RESTRICTIONS TIME: {time.time() - start_model}")

  ########################
  #*  FUNCION OBJETIVO  *#
  ########################

  m.setObjective(quicksum(quicksum(beta_p[i,l]-beta_m[i,l] for i in I) for l in F), GRB.MAXIMIZE)

  return m, S_F