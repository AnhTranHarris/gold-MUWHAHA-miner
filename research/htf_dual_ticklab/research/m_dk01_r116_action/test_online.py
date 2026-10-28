import unittest
import numpy as np
from online import correct


class OnlineCausality(unittest.TestCase):
    def fixture(self):
        n=50;t=np.arange(n,dtype=np.int64)*1000
        side=np.ones(n,dtype=np.int8);reg=np.zeros(n,dtype=np.int64)
        y=np.zeros(n,dtype=np.int8);touch=np.full((n,5),-1,np.int64)
        p=np.full((n,5,3),1/3,np.float32);p[:,0]=[1,0,0]
        return t,side,reg,y,touch,p,np.ones(n,dtype=np.bool_)

    def test_future_label_prefix_and_maturity(self):
        args=self.fixture();a=correct(*args)
        y=args[3].copy();y[0]=1
        b=correct(args[0],args[1],args[2],y,*args[4:])
        np.testing.assert_array_equal(a[:34],b[:34])
        self.assertFalse(np.array_equal(a[34:],b[34:]))
        y=args[3].copy();y[20:]=1
        b=correct(args[0],args[1],args[2],y,*args[4:])
        np.testing.assert_array_equal(a,b)

    def test_no_eligible_updates_is_identity(self):
        args=list(self.fixture());args[-1][:]=False
        out=correct(*args)
        np.testing.assert_allclose(out,args[5])
        np.testing.assert_allclose(out.sum(axis=2),1)


if __name__=='__main__':unittest.main()
