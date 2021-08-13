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
  T = params['T']
  G = params['G']
  R = params['R']
  H = params['H']
  L = params['L']
  V = params['V']
  EL = params['EL']
  EV = params['EV']
  RP = params['RP']
  EB = params['EB']
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

  # p_itf: P[equipo, puntos, fecha]
  # 1 si el equipo i tiene t puntos al
  # finalizar la fecha f.
  # 0 en otro caso.
  p = m.addVars(I, T, F, vtype=GRB.BINARY, name="p")

  # z_ig: z[equipo][patron_resultados]
  # 1 si al equipo i se le asigna el patron
  # de resultados g.
  # 0 en otro caso.
  z = {i: m.addVars(G[i], vtype=GRB.BINARY, name="z") for i in I}

  # a_if: a[equipo, fecha]
  # 1 si el partido del equipo i en la fecha f
  # es atractivo por salir campeon.
  # 0 en otro caso.
  a = m.addVars(I, F, vtype=GRB.BINARY, name="a")

  # d_if: d[equipo, fecha]
  # 1 si el partido del equipo i en la fecha f
  # es atractivo por poder descender.
  # 0 en otro caso.
  d = m.addVars(I, F, vtype=GRB.BINARY, name="d")

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
  m.addConstrs((quicksum(p[i, t, f] for t in T) == 1 for i in I
                                                    for f in F), name="R8")

  # R9
  m.addConstrs((quicksum(z[i][g] for g in G[i]) == 1 for i in I), name="R9")

  # R10
  m.addConstrs((quicksum(x[n, f] * R[i][n] for n in N if EL[i][n] + EV[i][n]  == 1) == quicksum(z[i][g] * RP[g][f] for g in G[i]) for i in I for f in F), name="R10")
                                                    
  # R11
  m.addConstrs( (p[i, t, f] == quicksum(z[i][g] for g in H[i][f][t]) for f in F
                                                                    for t in T
                                                                    for i in I), name="R11")

  # R12
  m.addConstrs((a[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h <= t + 3 * (31 - f)) for i in I
                                                                                                            for j in I
                                                                                                            for t in T
                                                                                                            for f in F
                                                                                                            if f > F[0] and j != i), name="R12")

  # R13
  m.addConstrs((a[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h <= t + 3 * (31 - F[0])) for i in I
                                                                                                      for j in I
                                                                                                      for t in T
                                                                                                      if j != i), name="R13")

  # R15
  m.addConstrs((a[i, f] <= a[i, f - 1] for i in I
                                      for f in F
                                      if f > F[0]), name="R15")

  # R16
  m.addConstrs((d[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h >= t - 3 * (31 - f)) for i in I
                                                                                                            for j in I
                                                                                                            for t in T
                                                                                                            for f in F
                                                                                                            if f > F[0] and j != i), name="R16")

  # R17
  m.addConstrs((d[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h >= t - 3 * (31 - F[0])) for i in I
                                                                                                      for j in I
                                                                                                      for t in T
                                                                                                      if j != i), name="R17")

  # R18
  m.addConstrs((d[i, f] <= d[i, f - 1] for i in I
                                      for f in F
                                      if f > F[0]), name="R18")


  print(f"** RESTRICTIONS TIME: {time.time() - start_model}")



  ########################
  #*  FUNCION OBJETIVO  *#
  ########################

  m.setObjective(quicksum(quicksum(V[f] * (a[i, f] + d[i, f]) for i in I) for f in F), GRB.MAXIMIZE)

  return m, S_F


