import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from r23_causal_firstday_gate import ordered_grammar, future_gap, full_held_labels, wait10_labels

def test_strict_quote_ordinal_feature_prefix_invariance():
    # Later same-ms source ordinals do not change the current ordinal's history.
    t=np.array([0,100,100,105,200,300,400,500,600,700],np.int64)
    b=np.array([1000,1001,1001,1004,1006,1005,1007,1010,1000,1300],np.int32)
    a=b+30
    ix=np.array([3,5],np.int32)
    v=ordered_grammar(t,b,a,ix,np.array([0],np.int32))
    u=ordered_grammar(t[:6],b[:6],a[:6],ix,np.array([0],np.int32))
    assert np.array_equal(v,u)
    b2=b.copy();b2[6:]+=500;a2=a.copy();a2[6:]+=500
    w=ordered_grammar(t,b2,a2,ix,np.array([0],np.int32))
    assert np.array_equal(v,w)

def test_gap_crosses_horizon_after_horizon_quote():
    t=np.array([0,100,1000,5000,21000,22000],np.int64)
    f=np.array([1],np.int32)
    assert bool(future_gap(t,f,15000)[0]) is True
    assert bool(future_gap(t,f,3000)[0]) is False

def test_full_h_held_is_separate_from_first_target():
    t=np.array([0,100,1000,5000,7000,16000,17000],np.int64)
    b=np.array([1000,1000,1020,1120,880,900,900],np.int32)
    a=b+50
    f=np.array([1],np.int32)
    held=full_held_labels(t,b,a,f,15000)
    assert held.shape==(1,2)
    assert held[0,0]==0 # BUY reached favorable but then adverse before 15sec.
    assert held[0,1]==0

def test_wait_is_future_supervision_only():
    t=np.array([0,1000,2000,3000,20000],np.int64)
    l=np.zeros((5,2,3),np.int8)
    l[:]=0
    l[2,0,0]=1
    y=wait10_labels(t,l)
    assert y.tolist()==[1,1,0,0,0]
