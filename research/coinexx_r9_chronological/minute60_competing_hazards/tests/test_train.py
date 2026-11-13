import sys,unittest,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from train import expanded_at_risk,bin_index,cumulative_incidence,MODELS,select_features,BINS
from event_engine import TREND_N,FEATURE_NAMES

class SurvivalTests(unittest.TestCase):
 def test_competing_intervals(self):
  x=np.arange(15,dtype='f').reshape(3,5)
  y=np.array([1,2,0],dtype=np.int8);h=np.array([100,5000,-1],dtype=np.int32)
  xx,yy=expanded_at_risk(x,y,h,max_per_bin=50)
  self.assertEqual(len(yy),1+4+5)
  self.assertEqual((yy==1).sum(),1);self.assertEqual((yy==2).sum(),1)
  self.assertEqual((yy==0).sum(),8)
  self.assertEqual(yy[0],1)
 def test_censored_not_exposure(self):
  x=np.array([[1.],[2.]],dtype='f');y=np.array([-1,0],dtype=np.int8);h=np.array([-1,-1],dtype=np.int32)
  xx,yy=expanded_at_risk(x,y,h)
  self.assertEqual(len(yy),len(BINS));self.assertTrue(np.all(yy==0))
 def test_sampling_independent_of_labels(self):
  x=np.arange(1000,dtype='f').reshape(1000,1)
  y=np.zeros(1000,dtype=np.int8);h=np.full(1000,-1,dtype='i')
  xx,yy=expanded_at_risk(x,y,h,max_per_bin=100)
  self.assertEqual(xx.shape,(500,2))
  self.assertEqual(xx[0,0],0.)
  self.assertEqual(xx[99,0],999.)
 def test_cumulative_incidence_monotonic(self):
  class Fake:
   def predict_proba(self,x):return np.broadcast_to(np.array([.5,.2,.3]),(len(x),3))
  z=cumulative_incidence(Fake(),np.ones((5,3),dtype='f'))
  self.assertAlmostEqual(z[5000]['p_fav'][0],.375)
  self.assertAlmostEqual(z[5000]['p_adv'][0],.5625)
  self.assertAlmostEqual(z[15000]['p_fav'][0],.3875)
  self.assertTrue(np.all(z[15000]['p_alive']<z[5000]['p_alive']))
 def test_feature_family_nested(self):
  X=np.zeros((4,145+len(FEATURE_NAMES)+5),dtype='f')
  lens=[select_features(X,n).shape[1] for n in MODELS]
  self.assertEqual(lens,[19,44,44+TREND_N,44+len(FEATURE_NAMES)])
 def test_side_specific_action_in_every_model(self):
  X=np.zeros((2,145+len(FEATURE_NAMES)+5),dtype='f')
  X[:,-5]=[1,-1]
  for name in MODELS:
   a=select_features(X,name)
   self.assertEqual(a[0,-5],1);self.assertEqual(a[1,-5],-1)

if __name__=='__main__':unittest.main()
