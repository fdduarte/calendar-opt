def set_cb_sol(master, sstpa):
    for var in master.getVars():
        value = sstpa.getVarByName(var.VarName).X
        master.cbSetSolution(var, value)