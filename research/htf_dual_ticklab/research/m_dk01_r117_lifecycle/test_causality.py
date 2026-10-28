import unittest
import numpy as np
from run import transduce, lifecycle, gates

class Causality(unittest.TestCase):
    def tape(self):
        return np.array([0,10000,59000,60001,61000,62000,63000,64000],np.int64),np.array([100,101,100,102,100,102,103,99.],float)
    def test_published_and_sequence(self):
        t,m=self.tape();e=np.array([60000,61000,62000,63000,64000,65000])
        x=transduce(t,m-.01,m+.01,e,60000)
        self.assertEqual(x[0].sum(),0) # boundary not published by any prior quote yet
        self.assertEqual(list(x[1:5,0,1]),[1,2,3,3])
        self.assertEqual(x[3,0,3],1)
        self.assertEqual(x[1,0,9],np.float32(np.log1p(1)))
    def test_future_and_equal_mutations(self):
        t,m=self.tape();e=np.array([62000]);a=transduce(t,m-.01,m+.01,e,60000)
        mm=m.copy();mm[t>=62000]+=800
        b=transduce(t,mm-.01,mm+.01,e,60000);np.testing.assert_array_equal(a,b)
    def test_spread_confirmation(self):
        t=np.array([0,1000,59000,60001,61000],np.int64);b=np.array([99,100.9,99,100.9,100.9]);a=b+.2
        x=transduce(t,b,a,np.array([61000]),60000)
        self.assertEqual(x[0,0,1],0)
    def test_prior_quote_missing_and_side_mapping(self):
        t,m=self.tape();e=np.array([0,62000,62000]);side=np.array([1,1,-1])
        x=lifecycle(t,m-.01,m+.01,e,side)
        self.assertEqual(x[0].sum(),0)
        z=x.reshape(3,5,2,14);np.testing.assert_array_equal(z[1,:,0],z[2,:,1])
        self.assertTrue(gates(x)[1,0])

if __name__=='__main__':unittest.main()
