def upgraded_position_cuts(self, model, variables):
  """Función principal que agrega cortes al modelo"""
  dates_left = len(self.params['F'])
  F = self.params['F']
  PI = self.params['PI']
  R = self.params['R']
  I = self.params['I']

  # Se calculan los resultados ordenados para cada equipo
  good_results = {}
  bad_results = {}
  for i in I:
    results_i = list(R[i].values())
    results_i.sort(reverse=True)
    results_i = results_i[:dates_left]

    results_i.sort()
    bad_results_i = dict(zip(F, results_i))

    results_i.sort(reverse=True)
    good_results_i = dict(zip(F, results_i))

    good_results[i] = good_results_i
    bad_results[i] = bad_results_i

  # para cada fecha, se calcula el mejor y peor lugar
  for f in range(F[0], F[-1]):
    for i in I:
      max_points = PI[i] + _get_sum_results(good_results[i], F[0], f) + 3 * (F[-1] - f)
      min_points = PI[i] + _get_sum_results(bad_results[i], F[0], f)

      teams_above_best_case = 0
      teams_above_worst_case = 0

      for j in I:
        if i != j:
          if max_points <= PI[j] + _get_sum_results(bad_results[i], F[0], f):
            teams_above_best_case += 1
          if min_points < PI[j] + _get_sum_results(good_results[i], F[0], f) + 3 * (F[-1] - f):
            teams_above_worst_case += 1
      p_max = 1 + teams_above_best_case
      p_min = 1 + teams_above_worst_case
      beta_m = variables['beta_m']
      beta_p = variables['beta_p']
      model.addConstr(beta_m[i, f] >= p_max, name=f'PR1[{i},{f},m]')
      model.addConstr(beta_p[i, f] >= p_max, name=f'PR1[{i},{f},p]')
      model.addConstr(beta_m[i, f] <= p_min, name=f'PR2[{i},{f},m]')
      model.addConstr(beta_p[i, f] <= p_min, name=f'PR2[{i},{f},p]')
  model.update()


def _get_sum_results(results_sorted, start_date, current_date):
  val = 0
  for i in range(start_date, current_date + 1):
    val += results_sorted[i]
  return val


def normal_position_cuts(self):
  """Agrega cortes normales (sin considerar información de los resultados)"""
  dates_left = len(self.params['F'])
  F = self.params['F']
  PI = self.params['PI']
  I = self.params['I']
  for i in I:
    max_points = PI[i] + 3 * dates_left
    min_points = PI[i]

    teams_above_best_case = 0
    teams_above_worst_case = 0

    for j in I:
      if i != j:
        if max_points <= PI[j]:
          teams_above_best_case += 1
        if min_points < PI[j] + 3 * dates_left:
          teams_above_worst_case += 1
    p_max = 1 + teams_above_best_case
    p_min = 1 + teams_above_worst_case
    beta_m = self.master_vars['beta_m']
    beta_p = self.master_vars['beta_p']
    for f in range(F[0], F[-1]):
      self.master_model.addConstr(beta_m[i, f] >= p_max, name=f'PR-1-{i}-{f}-m')
      self.master_model.addConstr(beta_p[i, f] >= p_max, name=f'PR-1-{i}-{f}-p')
      self.master_model.addConstr(beta_m[i, f] <= p_min, name=f'PR-2-{i}-{f}-m')
      self.master_model.addConstr(beta_p[i, f] <= p_min, name=f'PR-2-{i}-{f}-p')
  self.master_model.update()
