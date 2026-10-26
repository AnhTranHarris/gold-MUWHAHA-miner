import unittest
import numpy as np
from f401_preorder_marked_information import marked_seconds,features_at_t0,bayesian_poisson_changepoint

class CausalTests(unittest.TestCase):
    def source(self,post=0):
        t=np.array([10000,10100,11000,12900,13000,13500],dtype='int64')
        bid=np.array([100.,101.,101.,102.,102.,103.]);ask=np.array([101.,102.,103.,104.,104.,105.])
        if post:
            bid[-1]+=post;ask[-1]+=post
        return marked_seconds([(t[:3],bid[:3],ask[:3]),(t[3:],bid[3:],ask[3:])],8,16)

    def test_mark_identity_and_chunk_boundary(self):
        d=self.source();i=11-8
        self.assertEqual(d.counts['ask_only'][i],1)
        self.assertEqual(d.counts['joint'][i],0)
        self.assertEqual(d.source_rows,6)
        self.assertEqual(int(sum(int(a.sum()) for k,a in d.counts.items() if k in ('bid_only','ask_only','joint','unchanged'))),5)

    def test_post_t0_mutation_not_visible(self):
        ev=np.array([13000],dtype='int64');side=np.array([1],dtype=np.int8)
        a,n=features_at_t0(self.source(),ev,side,compute_cp=False)
        b,n2=features_at_t0(self.source(post=999),ev,side,compute_cp=False)
        self.assertEqual(n,n2);np.testing.assert_array_equal(a,b)

    def test_same_second_excluded(self):
        a,n=features_at_t0(self.source(),np.array([13500]),np.array([1]),compute_cp=False)
        b,n=features_at_t0(self.source(post=500),np.array([13500]),np.array([1]),compute_cp=False)
        np.testing.assert_array_equal(a,b)

    def test_bayesian_prefix_causality(self):
        x=np.array([1,0,2,8,0,1,3,2]);a,r=bayesian_poisson_changepoint(x)
        b,s=bayesian_poisson_changepoint(np.r_[x,99,99])
        np.testing.assert_array_equal(a,b[:len(x)])
        np.testing.assert_array_equal(r,s[:len(x)])
        self.assertTrue(np.all((a>=0)&(a<=1)))

if __name__=='__main__':unittest.main()
