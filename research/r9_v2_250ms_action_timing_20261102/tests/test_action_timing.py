import importlib.util
from pathlib import Path
import numpy as np
path=Path(__file__).resolve().parents[1]/'src_action_timing.py'
spec=importlib.util.spec_from_file_location('new_source_exact_action_timing',path)
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

def test_event_selection_no_baseline_lane():
    t=np.array([0,250,500,750,1000,300000,300250,300500,300750,301000],np.int64)
    b=np.array([1,1.02,1.06,1.09,1.12,1.15,1.18,1.2,1.23,1.27]);a=b+.03
    ix=s.quote_events(t,b,a)
    assert ix.tolist()==[5,6,7,8,9]

def test_trade_order_and_neutral():
    t=np.array([0,100,200,300,400],np.int64)
    b=np.array([100.,100.14,100.25,100.09,100.00]);a=b+.02
    y,net,dt,c,ft=s.label_trade(t,b,a,0,1)
    assert y==1 and net>0 and c==1
    b=np.array([100.,99.84,100.25,100.09,100.00]);a=b+.02
    y,net,dt,c,ft=s.label_trade(t,b,a,0,1)
    assert c==-1 and y==-1
    b=np.array([100.,100.01,100.02,100.01,100.00]);a=b+.02
    y,net,dt,c,ft=s.label_trade(t,b,a,0,1)
    assert y==0 and c==0

def test_no_future_to_entry():
    t=np.arange(0,1000,100,dtype=np.int64);b=100+np.arange(len(t))*.02;a=b+.02
    idx=np.array([1,3],np.int64)
    at=s.align_delays(t,idx,np.array([0,250,1000,3000],np.int64))
    assert at[0,0]==1 and at[0,1]==4 and at[0,2]==-1
    assert at[1,1]==6

def test_represented_actions_are_mutually_exclusive_at_entry():
    t=np.arange(0,3000,100,dtype=np.int64);b=100+np.arange(len(t))*.01;a=b+.02
    at=s.align_delays(t,np.array([0],np.int64),np.array([0,250,1000,3000],np.int64))
    y,net,dt,c,ft=s.label_actions(t,b,a,at)
    assert y.shape==(1,4,2)
    assert np.isnan(net[0,3,0])

def test_three_class_causal_bins_exclude_future():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    import src_three_class_student as m
    t=np.arange(0,500000,250,dtype=np.int64)
    b=100+np.sin(np.arange(len(t))*.1)*.02;a=b+.20
    ix=np.array([1200,1500],np.int64)
    x=m.category_features(t,b,a,ix)
    bb=b.copy();bb[1501:]+=5.0
    aa=a.copy();aa[1501:]+=5.0
    z=m.category_features(t,bb,aa,ix)
    np.testing.assert_array_equal(x,z)
    assert x.shape==(2,2,len(m.NAMES))

def test_three_class_neutral_is_a_separate_class():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    import src_three_class_student as m
    x=np.zeros((3,2,len(m.NAMES)),np.uint8)
    y=np.array([[1,-1],[0,0],[-1,-1]],np.int8)
    day=np.array([1,1,2])
    days,counts=m.prefix_stats(x,y,day)
    assert counts[0,0,2].sum()==1
    assert counts[0,0,1].sum()==2
    assert counts[0,0,0].sum()==1
    p=m.score(x.reshape(-1,len(m.NAMES)),counts.sum(axis=0))
    assert p.shape==(6,3)
    np.testing.assert_allclose(p.sum(axis=1),1.,atol=1e-6)
