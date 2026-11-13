import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hft import hft_features
from rocket_fallback import FixedKernelPPV,KERNELS
from extract import make_sequences,first_passage

class ResearchTests(unittest.TestCase):
    def test_hft_deterministic(self):
        x=np.zeros((3,5,120),np.float32);x[:,0,:]=1.
        a=hft_features(x);self.assertEqual(a.shape,(3,103));self.assertTrue(np.isfinite(a).all());self.assertTrue(np.allclose(a[:,2],1.0,atol=1e-6))
    def test_hft_rejects_shape(self):
        with self.assertRaises(ValueError):hft_features(np.zeros((2,6,120),np.float32))
    def test_rocket_shape_and_fit(self):
        self.assertEqual(len(KERNELS),84)
        x=np.zeros((2,5,120),np.float32);x[1,0,-15:]=1.0
        r=FixedKernelPPV(train_bias_cases=2).fit(x)
        f=r.transform(x);self.assertEqual(f.shape,(2,84*4*5*3));self.assertTrue(np.isfinite(f).all());self.assertTrue(((f>=0)&(f<=1)).all())
    def test_no_future_entry_equal_timestamp(self):
        ms=np.arange(120)*500
        ms=np.append(ms,[ms[-1],ms[-1]+500])
        bid=np.full(len(ms),10000,np.int32);ask=bid+10
        bid[-2]=20000;ask[-2]=20010  # future quote same millisecond
        x,valid,_=make_sequences(ms,bid,ask,np.array([119]),np.array([1]))
        self.assertTrue(valid[0]);self.assertAlmostEqual(float(x[0,0,-1]),0.)
    def test_target_vs_stop_order(self):
        ms=np.array([0,100,150,200,1000,5000,15000,30000],np.int64)
        bid=np.array([1000,1010,1070,900,900,900,900,900],np.int32)
        ask=bid+10
        labs,hit,_=first_passage(ms,bid,ask,np.array([0],np.int64),np.array([1],np.int8),np.array([1010],np.int32))
        self.assertEqual(labs[0,0],1);self.assertEqual(hit[0,0],150)
        bid[2]=990
        labs,_,_=first_passage(ms,bid,ask,np.array([0],np.int64),np.array([1],np.int8),np.array([1010],np.int32))
        self.assertEqual(labs[0,0],0)
    def test_gap_censors_and_never_uses_future_quote(self):
        ms=np.array([0,100,20000,30000,60000],np.int64)
        bid=np.array([1000,1000,1300,1300,1300],np.int32);ask=bid+10
        labs,hit,_=first_passage(ms,bid,ask,np.array([0],np.int64),np.array([1],np.int8),np.array([1010],np.int32))
        self.assertEqual(labs[0,0],-1)
        self.assertEqual(labs[0,1],-1)
    def test_gold_short_liquidates_at_ask(self):
        ms=np.array([0,100,200,500,15000,30000],np.int64)
        bid=np.array([1000,1000,1000,1000,1000,1000],np.int32)
        ask=np.array([1010,1070,1070,1070,1070,1070],np.int32)
        labs,hit,_=first_passage(ms,bid,ask,np.array([0],np.int64),np.array([-1],np.int8),np.array([1000],np.int32))
        self.assertEqual(labs[0,0],0)
        self.assertEqual(hit[0,0],100)
    def test_future_source_change_does_not_change_asof_features(self):
        ms=np.arange(120)*500
        ms=np.append(ms,[ms[-1],ms[-1]+100])
        bid=np.full(len(ms),10000,np.int32);ask=bid+12
        bid[1:119]=10002
        x1,valid1,_=make_sequences(ms,bid,ask,np.array([119]),np.array([1]))
        bid2=bid.copy();ask2=ask.copy();bid2[120]=100000;ask2[120]=100020
        x2,valid2,_=make_sequences(ms,bid2,ask2,np.array([119]),np.array([1]))
        np.testing.assert_array_equal(x1,x2)
        self.assertTrue(valid1[0]);self.assertTrue(valid2[0])
    def test_rocket_biases_are_train_fit_only(self):
        train=np.zeros((4,5,120),np.float32);train[1,0,80:]=1
        mod=FixedKernelPPV(train_bias_cases=4).fit(train)
        baseline=mod.bias_.copy()
        test=np.full((2,5,120),100,np.float32)
        mod.transform(test)
        np.testing.assert_array_equal(mod.bias_,baseline)
if __name__=='__main__':unittest.main()
