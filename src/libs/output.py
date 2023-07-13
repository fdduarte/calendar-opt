def write_sol_file_from_dict(_dict, outfile_name, model_name="no-name", obj_val=-1):
  with open(outfile_name, 'w', encoding='utf-8') as outfile:
    outfile.write(f"# Solution for model {model_name}\n")
    outfile.write(f"# Objective value = {obj_val}\n")
    for key, value in _dict.items():
      outfile.write(f"{key} {value}\n")