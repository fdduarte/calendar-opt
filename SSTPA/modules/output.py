def parse_output(model_vars, matches):
  file_lines = dict()
  for var in model_vars:
    if "x" in str(var):
      _, var, _, value = str(var).split()
      match, date = var.split(",")
      value = int(float(value.strip(")>")))
      match = int(match.strip("x["))
      date = int(date.strip("]"))
      if date not in file_lines.keys():
        file_lines[date] = list()
      if value:
        file_lines[date].append(f",{matches[match]['home']},{matches[match]['away']}\n")
  with open("programacion.csv", "w", encoding="UTF-8") as infile:
    infile.write("jornada, local, visita\n")
    for date in file_lines.keys():
      infile.write(f"{date},,\n")
      for line in file_lines[date]:
        infile.write(line)
