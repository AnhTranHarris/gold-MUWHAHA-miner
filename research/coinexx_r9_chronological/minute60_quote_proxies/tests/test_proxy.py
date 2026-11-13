import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from proxy_features import proxy_states,FEATURE_NAMES

class QuoteOnlyProxyTests(unittest.TestCase):
 def test_feature_count(self):self.assertEqual(len(FEATURE_NAMES),27)
 def test_no_future(self):
  ms=np.arange(0,10000,17,dtype=np.int64)
  bid=np.asarray(20000+np.cumsum(np.sin(np.arange(len(ms))*.25)>0.4),dtype=np.int32)
  ask=bid+20
  entry=np.array([100,250,400],dtype=np.int64)
  before=proxy_states(ms,bid,ask,entry)
  b2=bid.copy();a2=ask.copy();b2[401:]+=np.arange(len(b2)-401,dtype=np.int32)%3;a2[401:]+=np.arange(len(a2)-401,dtype=np.int32)%3
  after=proxy_states(ms,b2,a2,entry)
  np.testing.assert_array_equal(before,after)
 def test_order_of_same_millisecond_events(self):
  t=np.array([0,0,0,1,2],dtype=np.int64);b=np.array([100,102,101,101,103],dtype=np.int32);a=b+20
  x=proxy_states(t,b,a,np.array([1,2],np.int64))
  self.assertTrue(np.isfinite(x).all());self.assertGreater(x[0,0],0)
  self.assertGreater(x[1,1],0)
 def test_zero_move(self):
  t=np.arange(0,1800,10,dtype=np.int64);b=np.full(len(t),100,np.int32);a=b+20
  x=proxy_states(t,b,a,np.array([99,150],np.int64))
  self.assertTrue(np.isfinite(x).all());self.assertEqual(x[1,0],0);self.assertEqual(x[1,1],0)
 def test_widen_and_recover(self):
  t=np.array([0,100,200,300,400,500,600,700],np.int64)
  b=np.full(len(t),10000,np.int32);a=b+np.array([20,20,20,50,48,35,21,20],np.int32)
  x=proxy_states(t,b,a,np.array([3,5,7],np.int64))
  self.assertGreater(x[0,22],0);self.assertGreaterEqual(x[1,23],0.)
  self.assertLess(x[2,22],x[0,22])
 def test_gap_reset(self):
  t=np.array([0,100,200,300,20000,20100],np.int64)
  b=np.array([100,105,110,115,117,117],np.int32);a=b+20
  x=proxy_states(t,b,a,np.array([3,4,5],np.int64))
  self.assertGreater(x[0,0],0);self.assertEqual(x[1,0],0)
 def test_no_nan_and_boundary(self):
  t=np.arange(0,65000,35,dtype=np.int64);b=(10000+20*np.sin(t/1000)).astype(np.int32);a=b+np.maximum(5,(20+8*np.sin(t/210))).astype(np.int32)
  x=proxy_states(t,b,a,np.arange(10,len(t),100,dtype=np.int64))
  self.assertTrue(np.isfinite(x).all())
 def test_strict_entries(self):
  t=np.arange(20,dtype=np.int64);b=np.arange(20,dtype=np.int32)+100;a=b+20
  with self.assertRaises(ValueError):proxy_states(t,b,a,np.array([3,3,8],np.int64))
if __name__=='__main__':unittest.main()
