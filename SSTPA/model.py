from gurobipy import Model, GRB, quicksum
from params import N, F, S, I, T, G, R, EL, EV, W, L, RP, E, EB, V, matches
from output import parse_output
import time

m = Model("SSTPA")

start = time.time()


#################
#*  VARIABLES  *#
#################

# x_nf: x[partido, fecha]
# 1 si el partido n se programa finalmente
# en la fecha f
# 0 en otro caso.
x = m.addVars(N, F, vtype=GRB.BINARY, name="x")

# y_is: y[equipo, patron_localias]
# 1 si al equipo i se le asigna el patron
# de localias s
# 0 en otro caso
y = m.addVars(I, S, vtype=GRB.BINARY, name="y")

# p_itf: P[equipo, puntos, fecha]
# 1 si el equipo i tiene t puntos al
# finalizar la fecha f.
# 0 en otro caso.
p = m.addVars(I, T, F, vtype=GRB.BINARY, name="p")

# z_ig: z[equipo, patron_resultados]
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

print(f"Variables Listas en {time.time() - start}")


#####################
#*  RESTRICCIONES  *#
#####################

# R2
m.addConstrs((quicksum(x[n, f] for f in F) == 1 for n in N), name="R2")

# R3
m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1) == 1 for i in I
                                                                            for f in F), name="R3")

# R4
m.addConstrs((quicksum(y[i, s] for s in S if W[i][s] == 1) == 1 for i in I), name="R4")

# R5
m.addConstrs((y[i, s] == 0 for i in I
                           for s in S
                           if W[i][s] == 0), name="R5")

# R6
m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] == 1) == quicksum(y[i, s] for s in S if L[s][f] == 1) for i in I
                                                                                                            for f in F), name="R6")

# R7
m.addConstrs((quicksum(x[n, f] for n in N if EV[i][n] == 1) == quicksum(y[i, s] for s in S if L[s][f] == 0) for i in I
                                                                                                            for f in F), name="R7")

# R8
m.addConstrs((quicksum(p[i, t, f] for t in T) == 1 for i in I
                                                   for f in F), name="R8")

# R9
m.addConstrs((quicksum(z[i][g] for g in G[i]) == 1 for i in I), name="R9")

print(f"R9 Lista en {time.time() - start}")

# R10
m.addConstrs((quicksum(x[n, f] * R[i][n] for n in N if EL[i][n] + EV[i][n]  == 1) == quicksum(z[i][g] * RP[g][f] for g in G[i]) for i in I for f in F), name="R10")

print(f"R10 Lista en {time.time() - start}")

# R11 B
t_r11 = lambda f, i, g: E[i] + sum([RP[g][l] for l in range(F[0], f + 1)])
for i in I:
  m.addConstrs((p[i, t_r11(f, i, g), f] >= z[i][g] for g in G[i]
                                                   for f in F), name="R11")

print(f"R11 Lista en {time.time() - start}")

# R12 B
m.addConstrs((a[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h <= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R12")

# R13 B
m.addConstrs((a[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h <= t + 3 * (31 - F[0])) for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R13")

# R15 B
m.addConstrs((a[i, f] <= a[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R15")

# R16 B
m.addConstrs((d[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h >= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R16")

# R17 B
m.addConstrs((d[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h >= t + 3 * (31 - F[0])) for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R17")

# R18 B

m.addConstrs((d[i, f] <= d[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R18")


print(f"Restricciones Listas en {time.time() - start}")



########################
#*  FUNCION OBJETIVO  *#
########################

m.setObjective(quicksum(quicksum(V[f] * (a[i, f] + d[i, f]) for i in I) for f in F), GRB.MAXIMIZE)

m.optimize()

parse_output(m.getVars(), matches)


