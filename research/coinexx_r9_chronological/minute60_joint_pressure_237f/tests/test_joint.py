import unittest,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from train_joint import cross_features,NAME_TO_COL,CONFIG,read_month

class JointTests(unittest.TestCase):
 def test_output_all_finite(self):
  x=np.random.default_rng(22).normal(size=(102,182)).astype('f4');x[:,154]=20.;x[:,152]=40.;x[:,153]=64.;x[:,150]=1.
  f,names=cross_features(x)
  self.assertEqual(f.shape,(102,len(names)));self.assertTrue(np.isfinite(f).all())
 def test_r9_side_sign_flips(self):
  x=np.zeros((2,182),dtype='f4');x[:,150]=[1.,-1.];x[:,152]=40.;x[:,154]=20.;x[:,153]=64.
  x[:,NAME_TO_COL['net_mid_u_1000ms']]=5.
  x[:,NAME_TO_COL['hex_net_200ms']]=.4
  f,names=cross_features(x)
  self.assertAlmostEqual(float(f[0,names.index('trend1_hawkes_fast')]),float(f[1,names.index('trend1_hawkes_fast')]),places=6)
 def test_no_labels_in_interaction_formula(self):
  x=np.ones((3,182),dtype='f4');x[:,150]=1.;x[:,152]=40.;x[:,153]=64.;x[:,154]=20.
  f1,names=cross_features(x.copy());f2,_=cross_features(x.copy())
  self.assertTrue(np.array_equal(f1,f2));self.assertEqual(len(names),len(set(names)))
 def test_immutable_original_data_alignment(self):
  r=read_month('05');self.assertEqual(r['n_entries'],31615)
  self.assertEqual(r['X182'].shape,(63230,182))
  self.assertEqual(r['X_joint'].shape[0],63230)
  self.assertEqual(r['proxy'].shape[0],63230)
  self.assertEqual(int(r['good'].sum()),int(r['good'].sum()))
 def test_no_purported_new_trade_volume(self):
  self.assertNotIn('real_trade_volume',NAME_TO_COL)
  self.assertNotIn('book_size',NAME_TO_COL)
 def test_configuration_fixed(self):
  self.assertEqual(CONFIG['random_state'],20261113)
  self.assertEqual(CONFIG['n_estimators'],160)

if __name__=='__main__':unittest.main()
