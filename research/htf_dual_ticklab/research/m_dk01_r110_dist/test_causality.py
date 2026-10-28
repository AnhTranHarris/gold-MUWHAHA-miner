import unittest
import numpy as np
from run import event_features, structure, prequential, cutoff, leaf_cdf


class CausalContracts(unittest.TestCase):
    def setUp(self):
        self.t = np.arange(0, 4000001, 1000, dtype=np.int64)
        self.bid = 2000 + .2 * np.sin(np.arange(len(self.t)) / 17)
        self.ask = self.bid + .1
        self.et = np.array([3700000, 3760000], dtype=np.int64)
        self.side = np.array([1, -1], dtype=np.int8)

    def test_future_ticks_cannot_change_features(self):
        before = event_features(self.t,self.bid,self.ask,self.et,self.side)[0]
        for i,event in enumerate(self.et):
            bid,ask=self.bid.copy(),self.ask.copy()
            bid[self.t>event]+=100;ask[self.t>event]+=100
            after=event_features(self.t,bid,ask,self.et[:i+1],self.side[:i+1])[0]
            np.testing.assert_array_equal(before[:i+1],after)

    def test_later_equal_timestamp_quote_excluded(self):
        original=event_features(self.t,self.bid,self.ask,self.et,self.side)[0]
        j=np.searchsorted(self.t,self.et[-1])+1
        t=np.insert(self.t,j,self.et[-1]);bid=np.insert(self.bid,j,2500);ask=np.insert(self.ask,j,2500.1)
        changed=event_features(t,bid,ask,self.et,self.side)[0]
        np.testing.assert_array_equal(original,changed)

    def test_completed_structure_excludes_open_bar(self):
        idx=np.searchsorted(self.t,self.et)
        mid=(self.bid+self.ask)/2
        before=structure(self.t,mid,self.et,idx,self.side,np.ones(2))[0]
        changed=mid.copy()
        # Change unseen part of current minute, including later geometry.
        changed[self.t>self.et[-1]]+=500
        after=structure(self.t,changed,self.et,idx,self.side,np.ones(2))[0]
        np.testing.assert_array_equal(before,after)

    def test_maturity_boundary(self):
        t=np.array([0,33000,33001],dtype=np.int64)
        p=np.full(3,.4);side=np.ones(3,np.int8)
        a=prequential(t,np.zeros(3,np.int8),p,side,0)
        b=prequential(t,np.ones(3,np.int8),p,side,0)
        np.testing.assert_array_equal(a[:2],b[:2])
        self.assertGreater(a[2],b[2])

    def test_future_labels_cannot_change_online_prefix(self):
        t=np.arange(80,dtype=np.int64)*5000
        y=np.zeros(80,np.int8);p=np.full(80,.4);s=np.ones(80,np.int8)
        a=prequential(t,y,p,s,0)
        y[40:]=1
        b=prequential(t,y,p,s,0)
        np.testing.assert_array_equal(a[:47],b[:47])

    def test_frozen_ties_cannot_overspend(self):
        risk=np.r_[np.zeros(50),np.ones(50)]
        cut=cutoff(risk,np.ones(100,bool),.01)
        self.assertLessEqual(np.sum(risk>cut),1)

    def test_leaf_cdf_monotonic(self):
        leaf=np.zeros(4,np.int64);start=np.array([0]);end=np.array([100])
        cdf=leaf_cdf(leaf,start,end,np.linspace(-1,1,100),np.array([-2.,-.1,.1,2.]))
        self.assertTrue(np.all(np.diff(cdf)>=0))
        self.assertTrue(np.all((cdf>=0)&(cdf<=1)))


if __name__=='__main__':unittest.main()
