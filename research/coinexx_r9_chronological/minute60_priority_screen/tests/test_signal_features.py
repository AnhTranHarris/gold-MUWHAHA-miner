import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from signal_features import sequential_state,action_barrier_features,gambler_upper,FEATURE_NAMES,ACTION_NAMES

class CausalTests(unittest.TestCase):
  def fixture(self):
    # repeated milliseconds deliberately retained in source ordinal order
    t=np.array([0,100,100,100,200,400,800,1000,1050,3000,7000,7001],dtype=np.int64)
    b=np.array([1000,1001,1002,1001,1003,1003,1006,1005,1007,1007,1006,1040],dtype=np.int32)
    a=b+20
    return t,b,a
  def test_same_timestamp_source_order_usable(self):
    t,b,a=self.fixture()
    f=sequential_state(t,b,a,np.array([1,2,3],np.int64))
    self.assertNotEqual(f[0,0],f[1,0]);self.assertNotEqual(f[1,0],f[2,0])
  def test_future_appends_do_not_change_past_state(self):
    t,b,a=self.fixture(); ix=np.array([3,6,8],np.int64)
    orig=sequential_state(t,b,a,ix)
    extra=sequential_state(np.r_[t,[9000,9100]],np.r_[b,[1030,2000]],np.r_[a,[1050,3000]],ix)
    np.testing.assert_array_equal(orig,extra)
  def test_past_quote_mutation_changes_features(self):
    t,b,a=self.fixture(); ix=np.array([6],np.int64)
    orig=sequential_state(t,b,a,ix);bx=b.copy();ax=a.copy();bx[4]+=15;ax[4]+=15
    other=sequential_state(t,bx,ax,ix)
    self.assertFalse(np.array_equal(orig,other))
  def test_gap_resets_recent_state(self):
    t,b,a=self.fixture();t[-1]=100000
    state=sequential_state(t,b,a,np.array([len(t)-1],np.int64))
    self.assertAlmostEqual(float(state[0,0]),0.)
    self.assertAlmostEqual(float(state[0,7]),0.)
  def test_zero_changes_do_not_create_signed_pressure(self):
    t=np.arange(20,dtype=np.int64)*100
    b=np.full(20,1000,np.int32);a=b+20
    f=sequential_state(t,b,a,np.array([19],np.int64))
    self.assertEqual(float(f[0,2]),0.)
    self.assertEqual(float(f[0,6]),0.)
  def test_feature_dimensions_and_finiteness(self):
    t,b,a=self.fixture()
    f=sequential_state(t,b,a,np.array([3,6,8],np.int64))
    self.assertEqual(f.shape,(3,len(FEATURE_NAMES)))
    self.assertTrue(np.isfinite(f).all())
  def test_unbiased_brownian_probability(self):
    p=gambler_upper(np.array([0.]),np.array([10.]),np.array([30.]),np.array([20.]))
    self.assertAlmostEqual(float(p[0]),.4,places=6)
  def test_positive_drift_increases_upper_hit(self):
    mu=np.array([-.5,0,.5]); v=np.array([25.,25.,25.]);g=np.full(3,30.);l=np.full(3,20.)
    vals=gambler_upper(mu,v,g,l)
    self.assertTrue(vals[0]<vals[1]<vals[2])
  def test_extreme_negative_drift_goes_to_zero(self):
    mu=np.array([-1000.,1000.]); v=np.array([1.,1.]);up=np.array([80.,80.]);down=np.array([40.,40.])
    p=gambler_upper(mu,v,up,down)
    self.assertLess(float(p[0]),1e-10)
    self.assertGreater(float(p[1]),.999999)
  def test_correct_side_geometry(self):
    v=np.zeros((2,77),np.float32)
    v[:,24]=10;v[:,30]=30;v[:,27]=12;v[:,33]=28
    result=action_barrier_features(v,np.array([20,20]),np.array([40,40]),np.array([64,64]),np.array([1,-1]))
    self.assertEqual(result.shape,(2,len(ACTION_NAMES)))
    self.assertTrue(result[0,0]>result[1,0])
  def test_analytical_only_no_future_label_dependency(self):
    r=np.random.default_rng(20261113)
    f=r.normal(size=(100,77)).astype(np.float32)
    f[:,27]=np.abs(f[:,27])+2.;f[:,33]=np.abs(f[:,33])+2.
    side=r.choice([-1,1],size=100)
    a=action_barrier_features(f,np.full(100,18),np.full(100,40),np.full(100,64),side)
    self.assertTrue(np.isfinite(a).all())
    self.assertTrue(((a[:,0]>=0)&(a[:,0]<=1)).all())
    self.assertTrue(((a[:,5:9]>=0)&(a[:,5:9]<=1)).all())

if __name__=='__main__':unittest.main()
