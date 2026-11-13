import sys,unittest,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from event_engine import build_features,first_passage_actions,barriers,FEATURE_NAMES,TREND_N,completed_second_qaf

class EventTests(unittest.TestCase):
 def test_schema(self):self.assertEqual(len(FEATURE_NAMES),77);self.assertEqual(TREND_N,46)
 def test_causal_same_ms(self):
  t=np.arange(1500,dtype=np.int64)*100;t=np.r_[t,[t[1400],t[1400],t[-1]+100]]
  bid=np.ones(len(t),dtype='i')*10000;ask=bid+20;entry=np.array([1400],dtype='i')
  a,_,_=build_features(t,bid,ask,entry)
  b=bid.copy();s=ask.copy();b[1500:]=50000;s[1500:]=50020
  c,_,_=build_features(t,b,s,entry)
  np.testing.assert_allclose(a,c,equal_nan=True)
 def test_causal_quote_oscillation(self):
  t=np.arange(1200,dtype=np.int64)*100
  bid=10000+(np.arange(len(t))%4==3).astype('i')*20
  ask=bid+20
  f,_,_=build_features(t,bid,ask,np.array([1100],dtype='i'))
  self.assertTrue(np.isfinite(f[0,0]))
  self.assertGreater(f[0,1],0)
 def test_ongoing_completed_second_never_used(self):
  t=np.array([0,100,500,1000,1200,1500,1700,2000,2100,2200],dtype=np.int64)
  mid=np.array([100,102,104,105,105,105,108,101,110,5000],dtype='i')
  q=completed_second_qaf(t,mid,np.array([2100],dtype=np.int64))
  mid2=mid.copy();mid2[-1]=999999
  z=completed_second_qaf(t,mid2,np.array([2100],dtype=np.int64))
  np.testing.assert_allclose(q,z,equal_nan=True)
 def test_spread_dynamic(self):
  s,t=barriers(np.array([20,40]),np.array([0,100]))
  np.testing.assert_array_equal(s,[40,150]);np.testing.assert_array_equal(t,[64,240])
 def test_entry_spread_instant_stop(self):
  t=np.array([0,100,200],dtype=np.int64)
  b=np.array([10000,10010,10040],dtype='i');a=b+50
  y,hit,r=first_passage_actions(t,b,a,np.array([0]),np.array([30],dtype='i'),np.array([50],dtype='i'),horizon_ms=200)
  self.assertEqual(y[0,0],2);self.assertEqual(y[0,1],2)
  self.assertEqual(hit[0,0],0)
 def test_future_labels_can_see_future(self):
  t=np.arange(21,dtype=np.int64)*100
  b=np.full(len(t),10000,dtype='i');a=b+20
  entry=np.array([0])
  y,_,_=first_passage_actions(t,b,a,entry,np.array([40],dtype='i'),np.array([50],dtype='i'),2000)
  b[5:]+=100;a[5:]+=100
  y2,_,_=first_passage_actions(t,b,a,entry,np.array([40],dtype='i'),np.array([50],dtype='i'),2000)
  self.assertEqual(y[0,0],0);self.assertEqual(y2[0,0],1)
  self.assertEqual(y2[0,1],2)
 def test_regional_without_complete_history(self):
  t=np.array([100000,100100,100200,100300],dtype=np.int64);b=np.array([1,2,3,4],dtype='i')+10000
  f,_,_=build_features(t,b,b+20,np.array([3]))
  self.assertTrue(np.isnan(f[0,6*6]));self.assertTrue(np.isfinite(f[0,0]))
 def test_gap_censor(self):
  t=np.array([0,200,12000,14000],dtype=np.int64)
  b=np.full(len(t),10000,dtype='i');a=b+20
  y,_,_=first_passage_actions(t,b,a,np.array([0]),np.array([40],dtype='i'),np.array([50],dtype='i'),15000)
  self.assertEqual(y[0,0],-1)

if __name__=='__main__':unittest.main()
