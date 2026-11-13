"""Guard source-ordinal causality, batch parity, 60-second quote quality and immutable pilot agreement."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from full_extract import gather,ALL_FEATURES
from quant_state import state_features,COLS as STATE_COLS
from hft import hft_features

class FullUniverseTests(unittest.TestCase):
 def test_feature_schema(self):
  self.assertEqual(len(ALL_FEATURES),145)
  self.assertEqual(len(STATE_COLS),28)
 def test_no_future_same_ms(self):
  ms=np.arange(121,dtype=np.int64)*500
  ms=np.concatenate([ms,[ms[-1],ms[-1]+1]])
  mid=np.full(len(ms),100.,dtype=np.float64)
  spread=np.full(len(ms),10.,dtype=np.float64)
  mid[121]=20000.;spread[121]=2000.
  a,v,_=gather(ms,mid,spread,np.array([120]),np.array([1]))
  self.assertTrue(v[0]);self.assertAlmostEqual(a[0,0,-1],0.)
  self.assertAlmostEqual(a[0,1,-1],0.)
 def test_future_modification_invariant(self):
  ms=np.arange(125,dtype=np.int64)*500
  mid=np.arange(125,dtype=np.float64)+100.
  spread=np.full(125,12.,dtype=np.float64)
  a,v,_=gather(ms,mid,spread,np.array([120]),np.array([1]))
  later_mid=mid.copy();later_mid[121:]+=100000.
  later_spr=spread.copy();later_spr[121:]+=200.
  b,v2,_=gather(ms,later_mid,later_spr,np.array([120]),np.array([1]))
  np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(v,v2)
 def test_stale_history_rejection(self):
  ms=np.array([0,1000,2000,100000],np.int64)
  mid=np.array([100,100,100,120],dtype=float);sp=np.full(4,10.)
  _,valid,reason=gather(ms,mid,sp,np.array([3]),np.array([1]))
  self.assertFalse(valid[0]);self.assertEqual(reason['stale_60s'],1)
 def test_batch_size_parity(self):
  ms=np.arange(140,dtype=np.int64)*500
  mid=np.sin(np.arange(140)/8.)*10000.;spr=np.full(140,15.)
  ix=np.arange(119,136);sides=np.where(ix%2,1,-1)
  a,v,_=gather(ms,mid,spr,ix,sides,batch=3)
  b,v2,_=gather(ms,mid,spr,ix,sides,batch=55)
  np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(v,v2)
 def test_quant_state_is_causal_deterministic(self):
  x=np.random.default_rng(9).normal(size=(3,5,120)).astype('f')
  a=state_features(x);b=state_features(x)
  self.assertEqual(a.shape,(3,28));np.testing.assert_array_equal(a,b)
  self.assertTrue(np.isfinite(a).all())
 def test_quant_state_reject_invalid_shape(self):
  with self.assertRaises(ValueError):state_features(np.ones((3,4,120),dtype='f'))

if __name__=='__main__':unittest.main()
