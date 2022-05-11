import json
import os
from gurobipy import Model, GRB, quicksum, LinExpr
from .parse_params import parse_params
from ...types import SSTPAParams
from ...libs.argsparser import args


# pylint: disable=invalid-name
def create_model():
  """
  Funcion que crea modelo de optimizacion de multiples posiciones sin descomposicion
  """
  start_date = args.start_date
  filepath = args.filepath
  time_limit = args.time_limit
  mip_focus = args.mip_focus
  mip_gap = args.mip_gap

  m = Model("SSTPA V3")

  m.setParam('TimeLimit', time_limit)
  m.setParam('MIPFocus', mip_focus)
  m.setParam('MIPGap', mip_gap)

  # Parse params dict to variables
  params = parse_params(filepath, start_date)

  N = params['N']
  F = params['F']
  S = params['S']
  I = params['I']
  R = params['R']
  L = params['L']
  M = 10 ** 10
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
  x = m.addVars(N, F, vtype=GRB.BINARY, name="x")

  # y_is: y[equipo][patron_localias]
  # 1 si al equipo i se le asigna el patron
  # de localias s
  # 0 en otro caso
  y = {i: m.addVars(S[i], vtype=GRB.BINARY, name="y") for i in I}

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f
  # con la info de los resultados hasta la fecha l inclusive
  # en el MEJOR conjunto de resultados futuros para el equipo i
  p_m = m.addVars(I, I, F, F, vtype=GRB.INTEGER, name="p_m")

  # p_jilf: P[equipo, equipo, fecha, fecha]
  # discreta, cant de puntos del equipo j al finalizar la fecha f
  # con la info de los resultados hasta la fecha l inclusive
  # en el PEOR conjunto de resultados futuros para el equipo i
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

  # beta_il: beta[equipo,fecha]
  # discreta, indica la mejor posicion
  # que puede alcanzar el equipo i al final del 
  # torneo, mirando desde la fecha l en el MEJOR
  # conjunto de resultados futuros para el equipo i
  beta_m = m.addVars(I, F, vtype=GRB.INTEGER, name="beta_m")

  # beta_il: beta[equipo, fecha]
  # discreta, indica la mejor posicion
  # que puede alcanzar el equipo i al final del 
  # torneo, mirando desde la fecha l en el PEOR
  # conjunto de resultados futuros para el equipo i
  beta_p = m.addVars(I, F, vtype=GRB.INTEGER, name="beta_p")

  #####################
  # * RESTRICCIONES * #
  #####################

  # R2
  for n in N:
    m.addConstr((quicksum(x[n, f] for f in F) == 1), name=f"R2-{n}")

  # R3
  for i in I:
    for f in F:
      _exp = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1))
      m.addConstr(_exp == 1, name=f"R3-{i}-{f}")

  # R4
  m.addConstrs((quicksum(y[i][s] for s in S[i]) == 1 for i in I), name="R4")

  # R6
  for f in F:
    for i in I:
      _exp1 = LinExpr(quicksum(x[n, f] for n in N if EL[i][n] == 1))
      _exp2 = LinExpr(quicksum(y[i][s] for s in S[i] if L[s][f] == 1))
      m.addConstr(_exp1 == _exp2, name=f"R6-{f}-{i}")

  # R7
  for f in F:
    for i in I:
      _exp1 = LinExpr(quicksum(x[n, f] for n in N if EV[i][n] == 1))
      _exp2 = LinExpr(quicksum(y[i][s] for s in S[i] if L[s][f] == 0))
      m.addConstr(_exp1 == _exp2, name=f"R7-{f}-{i}")

  # R8
  for n in N:
    for i in I:
      for f in F:
        for l in F:
          if f > l:
            _exp = LinExpr(v_m[n, i, l, f] + e_m[n, i, l, f] + a_m[n, i, l, f])
            m.addConstr(x[n, f] == _exp, name=f"R8-{n}-{i}-{f}-{l}")

  # R8
  for n in N:
    for i in I:
      for f in F:
        for l in F:
          if f > l:
            _exp = LinExpr(v_p[n, i, l, f] + e_p[n, i, l, f] + a_p[n, i, l, f])
            m.addConstr(x[n, f] == _exp, name=f"R9-{n}-{i}-{f}-{l}")

  # R10
  for j in I:
    for i in I:
      for f in F:
        for l in F:
          _exp1 = LinExpr(quicksum(quicksum(R[j][n] * x[n, theta]
                                   for n in N if EL[j][n] + EV[j][n] == 1)
                          for theta in F if theta <= l))
          _exp2 = LinExpr(quicksum(quicksum(3 * v_m[n, i, l, theta]
                                   for theta in F if theta > l and theta <= f)
                          for n in N if EL[j][n] == 1))
          _exp3 = LinExpr(quicksum(quicksum(3 * a_m[n, i, l, theta]
                                   for theta in F if theta > l and theta <= f)
                          for n in N if EV[j][n] == 1))
          _exp4 = LinExpr(quicksum(quicksum(e_m[n, i, l, theta]
                                   for theta in F if theta > l and theta <= f)
                          for n in N if EL[j][n] + EV[j][n] == 1))
          m.addConstr(p_m[j, i, l, f] == PI[j] + _exp1 + _exp2 + _exp3 + _exp4,
                      name=f"R10-{j}-{i}-{f}-{l}")

  # R10
  for j in I:
    for i in I:
      for f in F:
        for l in F:
          _exp1 = LinExpr(quicksum(quicksum(R[j][n] * x[n, theta]
                                   for n in N if EL[j][n] + EV[j][n] == 1)
                          for theta in F if theta <= l))
          _exp2 = LinExpr(quicksum(quicksum(3 * v_p[n, i, l, theta]
                                   for theta in F if theta > l and theta <= f)
                          for n in N if EL[j][n] == 1))
          _exp3 = LinExpr(quicksum(quicksum(3 * a_p[n, i, l, theta]
                                   for theta in F if theta > l and theta <= f)
                          for n in N if EV[j][n] == 1))
          _exp4 = LinExpr(quicksum(quicksum(e_p[n, i, l, theta]
                                   for theta in F if theta > l and theta <= f)
                          for n in N if EL[j][n] + EV[j][n] == 1))
          m.addConstr(p_p[j, i, l, f] == PI[j] + _exp1 + _exp2 + _exp3 + _exp4,
                      name=f"R11-{j}-{i}-{f}-{l}")

  # R12
  for l in F:
    for i in I:
      for j in I:
        if j != i:
          m.addConstr(M - M * alfa_m[j, i, l] >= 1 + p_m[j, i, l, F[-1]] - p_m[i, i, l, F[-1]],
                      name=f"R12-{l}-{i}-{j}")

  # R13
  for l in F:
    for i in I:
      for j in I:
        if j != i:
          m.addConstr(M * alfa_p[j, i, l] >= 1 + p_p[j, i, l, F[-1]] - p_p[i, i, l, F[-1]],
                      name=f"R13-{l}-{i}-{j}")

  # R14
  for i in I:
    for l in F:
      _exp = LinExpr(quicksum(alfa_m[j, i, l] for j in I if i != j))
      m.addConstr(beta_m[i, l] == len(I) - _exp, name=f"R14-{i}-{l}")

  # R15
  for i in I:
    for l in F:
      _exp = LinExpr(quicksum(alfa_p[j, i, l] for j in I if i != j))
      m.addConstr(beta_p[i, l] == len(I) - _exp, name=f"R15-{i}-{l}")

  ########################
  # * FUNCION OBJETIVO * #
  ########################

  _obj = quicksum(quicksum(beta_p[i, l] - beta_m[i, l] for i in I) for l in F)
  m.setObjective(_obj, GRB.MAXIMIZE)

  return m
