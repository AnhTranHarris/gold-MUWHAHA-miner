import numpy as np
import pytest
from train_entry_survival import _replay_30sec

def test_reservation_and_side_correctness():
    t=np.array([0,1000,30001,31000,61005],np.int64)
    pb=np.array([.8,.2,.2,.9,.2],np.float32)
    ps=np.array([.1,.9,.95,.1,.95],np.float32)
    b=np.array([2,0,0,2,0],np.uint8)
    s=np.array([0,2,2,0,2],np.uint8)
    covered=np.array([1,1,1,1,1],bool)
    rows,side,w,n,bad,c=_replay_30sec(t,pb,ps,b,s,covered,.5)
    assert rows.tolist()==[0,2,4]
    assert side.tolist()==[0,1,1]
    assert (w,n,bad,c)==(3,0,0,0)

def test_censor_not_mislabeled_loss():
    t=np.array([0,30005],np.int64);p=np.array([.8,.8],np.float32)
    z=np.array([0,0],np.uint8);cov=np.array([False,True])
    rows,side,w,n,bad,c=_replay_30sec(t,p,p,z,z,cov,.5)
    assert (w,n,bad,c)==(0,0,1,1)

