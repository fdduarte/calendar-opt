import json
from ...libs.logger import log


def load_policy(filename):
  """Loads the policy of filename"""
  with open('data/policy.json', 'r', encoding='utf-8') as infile:
    policies = json.load(infile)["data"]
  policies_filtered = list(filter(lambda x: x['file'] == filename, policies))
  if len(policies_filtered) != 1:
    log('policy', f'politica para {filename} no encontrada, resolviendo con default')
    return None
  log('policy', f'politica para {filename} cargada: {policies_filtered[0]["policy"]}')
  return policies_filtered[0]['policy']
