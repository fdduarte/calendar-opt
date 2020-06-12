from modules.model_stats import ModelStats

LOGS = ["16-19", "16-20", "16-21", "16-24", "16-26", "16-27", "16-30"]
PATH = "SSTPA/V4/logs/"
NAME = "V4"

plotter = ModelStats(PATH, NAME)
plotter.parse_logs(LOGS)
plotter.gen_linear_reg_scatter()
plotter.gen_poli_funct_plot()
plotter.gen_exp_funct_plot()

