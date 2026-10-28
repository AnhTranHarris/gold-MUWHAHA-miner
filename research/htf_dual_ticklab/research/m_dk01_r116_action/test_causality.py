import unittest
import numpy as np
from run import features, ordered_signatures, action_paths, splits, choose


class CausalContracts(unittest.TestCase):
    def tape(self):
        tm=np.arange(0,15000000,1000,dtype=np.int64)
        bid=2000+.2*np.sin(np.arange(len(tm))*.1)+np.arange(len(tm))*.001
        return tm,bid,bid+.1

    def test_future_and_duplicate_timestamp_invariance(self):
        tm,bid,ask=self.tape(); et=np.array([14000100],np.int64); side=np.array([1],np.int8)
        x,*_=features(tm,bid,ask,et,side)
        mutated=bid.copy(); mutated[tm>=et[0]]+=200
        y,*_=features(tm,mutated,mutated+.1,et,side)
        np.testing.assert_array_equal(x,y)
        # At exact timestamp, ALL quotes at that time are excluded.
        et=np.array([14000000],np.int64); x,*_=features(tm,bid,ask,et,side)
        ti=np.searchsorted(tm,et[0]); t2=np.insert(tm,ti,et[0])
        b2=np.insert(bid,ti,99999.); a2=np.insert(ask,ti,100000.)
        y,*_=features(t2,b2,a2,et,side)
        np.testing.assert_array_equal(x,y)

    def test_incomplete_bar_exclusion(self):
        tm,bid,ask=self.tape(); et=np.array([14000100],np.int64); side=np.array([1],np.int8)
        x,*_=features(tm,bid,ask,et,side)
        # Alter later ticks in the current bar. No published input can change.
        b2=bid.copy(); b2[(tm>=et[0])&(tm<14040000)]+=100
        y,*_=features(tm,b2,b2+.1,et,side)
        np.testing.assert_array_equal(x,y)

    def test_signature_distinguishes_update_order(self):
        tm=np.array([0,1,2],np.int64); side=np.array([1]); idx=np.array([2])
        a=ordered_signatures(tm,np.array([1.,2.,2.]),np.array([3.,3.,4.]),idx,side)
        b=ordered_signatures(tm,np.array([1.,1.,2.]),np.array([3.,4.,4.]),idx,side)
        self.assertFalse(np.array_equal(a,b))
        # Equal final displacement; unequal ordered cross integral.
        np.testing.assert_allclose(a[0,:2],b[0,:2])
        self.assertNotEqual(a[0,5],b[0,5])

    def test_latency_and_no_same_quote_entry(self):
        tm=np.array([0,100,200,349,350,500,32100],np.int64)
        bid=np.ones(len(tm))*10; ask=bid+.1
        et=np.array([100],np.int64); s=np.array([1]); idx=np.array([0]); d=np.array([.35])
        t,_=action_paths(tm,bid,ask,et,s,idx,d,0); self.assertEqual(t[0,0],2)
        t,_=action_paths(tm,bid,ask,et,s,idx,d,250); self.assertEqual(t[0,0],4)

    def test_retest_requires_three_ordered_phases(self):
        tm=np.array([0,100,200,300,400,500,32100],np.int64)
        ask=np.array([10.,10.,10.4,10.1,10.12,10.17,10.5]); bid=ask-.1
        t,_=action_paths(tm,bid,ask,np.array([100]),np.array([1]),np.array([0]),np.array([.35]),0)
        self.assertEqual(t[0,3],5)
        # A monotonic breakout has no retest entry.
        ask=np.array([10.,10.,10.4,10.45,10.5,10.6,10.7]); bid=ask-.1
        t,_=action_paths(tm,bid,ask,np.array([100]),np.array([1]),np.array([0]),np.array([.35]),0)
        self.assertEqual(t[0,3],-1)

    def test_split_embargo(self):
        t=np.arange(1000)*5000; m=splits(t)
        for left,right in [('FIT','CAL'),('CAL','VAL'),('VAL','SHADOW')]:
            self.assertLess(t[m[left]].max()+40000,t[m[right]].min())

    def test_policy_has_market_fallback(self):
        p=np.zeros((2,5,3)); p[:,:,1]=.5;p[:,:,2]=.1
        np.testing.assert_array_equal(choose(p,100),np.zeros(2))


if __name__=='__main__': unittest.main()
