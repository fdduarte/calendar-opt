from gurobipy import Model, GRB, quicksum
from params import N, F, S, I, EL, EV, W, L

m = Model("SSTPA")



x = m.addVars(N, F, vtype=GRB.BINARY, name="x")
y = m.addVars(I, S, vtype=GRB.BINARY, name="y")


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

########################
#*  FUNCION OBJETIVO  *#
########################


# POR AHORA SUMA
m.setObjective(quicksum(x[n, f] for n in N for f in F), GRB.MAXIMIZE)

m.optimize()

for var in m.getVars():
  print(var)


