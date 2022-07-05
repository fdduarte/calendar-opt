import os
import sys
import unittest
import io
# Se agrega path a param_generator
path_to_parser = os.path.join(os.getcwd())
sys.path.append(path_to_parser)

from src.models import sstpa_mp_benders_create_model
from src.params import sstpa_mp_benders_generate_params
from src.libs.argsparser import args

OBJVAL = 8


class TestSSTPABendersSmall(unittest.TestCase):
  """Test suit para el modelo de benders"""
  def setUp(self):
    filename = "campeonato_6_1"

    args.model = 5
    args.start_date = 9
    args.verbose = False
    args.filepath = f"data/{filename}.xlsx"
    sstpa_mp_benders_generate_params()

  def test_benders(self):
    """Test del modelo base mas cortes de benders"""
    args.local_patterns = False
    args.preprocess = False
    args.IIS = True
    args.benders_cuts = True
    m = sstpa_mp_benders_create_model()
    m.optimize()
    self.assertEqual(m.objVal(), OBJVAL)

  def test_preprocess_benders(self):
    """Test del modelo base más preproceso mas cortes de benders"""
    args.local_patterns = False
    args.preprocess = True
    args.IIS = True
    args.benders_cuts = True
    m = sstpa_mp_benders_create_model()
    m.optimize()
    self.assertEqual(m.objVal(), OBJVAL)

  def test_preprocess_patterns(self):
    """Test del modelo base más cortes de benders mas patrones"""
    args.local_patterns = True
    args.preprocess = False
    args.IIS = True
    args.benders_cuts = True
    m = sstpa_mp_benders_create_model()
    m.optimize()
    self.assertEqual(m.objVal(), OBJVAL)

  def test_full_model(self):
    """Test del modelo con todo"""
    args.local_patterns = True
    args.preprocess = True
    args.IIS = True
    args.benders_cuts = True
    m = sstpa_mp_benders_create_model()
    m.optimize()
    self.assertEqual(m.objVal(), OBJVAL)


if __name__ == '__main__':
  unittest.main()
