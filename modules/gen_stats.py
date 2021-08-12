from modules.model_stats import ModelStats


LOGS = [f"{i}-30" for i in range(18, 24)]
PATH = "SSTPA/logs/13-6"
NAME = "V3-t"

plotter = ModelStats(PATH, NAME)
plotter.parse_logs(LOGS)
plotter.gen_linear_reg_scatter()
plotter.gen_poli_funct_plot()
plotter.gen_exp_funct_plot()
plotter.gen_csv()

