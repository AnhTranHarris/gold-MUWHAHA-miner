import unittest,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data')
from r152_paired_action_replay import limit_replay,first_future_index,original,PINS,ROOT,sha
from r151_t1_core import action_t1_index,first_touch
from r120_multiclock_geometry import build_states
from r120_htf_bridge import make_macro_native
from r152_fit_freeze_action_portfolio import actions,FAMILIES

class R152Contracts(unittest.TestCase):
 def test_t1_strict_window(self):
  t=np.array([10000,24999,25000,25999,26000],np.int64)
  np.testing.assert_array_equal(action_t1_index(t,np.array([10000,11000,12000],np.int64)),[2,4,-1])
 def test_t2_wait_strict(self):
  t=np.array([100,5099,5100,6099,6100],np.int64)
  np.testing.assert_array_equal(first_future_index(t,np.array([100,100],np.int64),np.array([True,False]),5000,1000),[2,-1])
 def test_buy_limit_never_worse_than_target(self):
  t=np.array([0,100,200,300,400],np.int64);b=np.array([1000,800,1000,1500,1700],np.int32);a=b+100
  f,c,g=limit_replay(t,b,a,np.array([0],np.int64),np.array([1],np.int8),200,250,300,200,1000)
  self.assertEqual(int(f[0]),1);self.assertEqual(int(c[0]),1);self.assertGreaterEqual(int(g[0]),300)
 def test_sell_limit_symmetric(self):
  t=np.array([0,100,200,300,400],np.int64);b=np.array([3000,3300,3100,2700,2400],np.int32);a=b+100
  f,c,g=limit_replay(t,b,a,np.array([0],np.int64),np.array([-1],np.int8),200,250,300,200,1000)
  self.assertEqual(int(f[0]),1);self.assertEqual(int(c[0]),1);self.assertGreaterEqual(int(g[0]),300)
 def test_limit_no_touch(self):
  t=np.array([0,100,200,300],np.int64);b=np.array([1000,1100,1200,1300],np.int32);a=b+100
  f,c,g=limit_replay(t,b,a,np.array([0],np.int64),np.array([1],np.int8),500,250,300,200,1000)
  self.assertEqual(int(f[0]),-1);self.assertEqual(int(c[0]),-9);self.assertEqual(int(g[0]),0)
 def test_same_millisecond_no_fill(self):
  t=np.array([0,0,100],np.int64);b=np.array([1000,0,1200],np.int32);a=b+100
  f,c,g=limit_replay(t,b,a,np.array([0],np.int64),np.array([1],np.int8),500,250,300,200,1000)
  self.assertEqual(int(f[0]),-1)
 def test_future_quote_cannot_change_past_limit(self):
  t=np.array([0,100,200,4000],np.int64);b=np.array([1000,800,1500,1000],np.int32);a=b+100
  args=(t,b,a,np.array([0],np.int64),np.array([1],np.int8))
  one=limit_replay(*args,200,250,300,200,1000)
  b[-1]=-10000;a[-1]=-9900
  two=limit_replay(*args,200,250,300,200,1000)
  for x,y in zip(one,two):np.testing.assert_array_equal(x,y)
 def test_r120_prefix_independence(self):
  t=np.array([1000,1500,2000,3000,4500,8000,60000,61000,65000,70000],np.int64)
  b=np.array([1000,1010,1020,1030,1040,1050,1060,1070,1080,1090],np.int32)
  a=b+100;av=np.ones(len(t),np.float32);bv=np.ones(len(t),np.float32)
  ev=np.array([5500,65500],np.int64);side=np.array([1,-1],np.int8)
  x=build_states(t,b,a,av,bv,ev,side);h,_,_=make_macro_native(t,b,a,ev,side)
  b2=b.copy();a2=a.copy();b2[-1]=999999;a2[-1]=1000099
  xx=build_states(t,b2,a2,av,bv,ev,side);hh,_,_=make_macro_native(t,b2,a2,ev,side)
  np.testing.assert_array_equal(x,xx);np.testing.assert_array_equal(h,hh)
 def test_all_four_original_identity_and_masks(self):
  for m in ('01','02','06','07'):
   t0,side,truth=original(m)
   with np.load(ROOT/f'R152_DK_{m}_FEATURES_AND_ACTIONS.npz') as a:
    for k,v in [('t0',t0),('side',side),('truth',truth)]:np.testing.assert_array_equal(a[k],v)
    self.assertEqual(a['X'].shape,(len(t0),128))
   with np.load(ROOT/f'R152_DK_{m}_FROZEN_POLICY_ACTION_MASKS.npz') as a:
    np.testing.assert_array_equal(a['t0'],t0)
    for family in FAMILIES:
     self.assertTrue(np.isin(a['action_'+family],(0,1,2,3)).all())
 def test_policies_frozen_before_exposed_months(self):
  p=json.loads((ROOT/'R152_FEB_FROZEN_POLICIES.json').read_text())
  self.assertEqual(set(p),set(FAMILIES))
  for name,record in p.items():self.assertIn(record['threshold'],FAMILIES[name])
 def test_raw_source_pins(self):
  for m,pin in PINS.items():self.assertEqual(sha(Path(f'/mnt/data/XAUUSD_DUKAS_2026_{m}_ticks.csv.gz')),pin)

if __name__=='__main__':unittest.main(verbosity=2)