from modules.model_stats import ModelStats

LOGS = ["20-30", "21-30", "22-30", "23-30", "24-30", "25-30"]
PATH = "SSTPA/V3/logs/12-6"
NAME = "V3"

plotter = ModelStats(PATH, NAME)
plotter.parse_logs(LOGS)
plotter.gen_linear_reg_scatter()
plotter.gen_poli_funct_plot()
plotter.gen_exp_funct_plot()
plotter.gen_csv()

