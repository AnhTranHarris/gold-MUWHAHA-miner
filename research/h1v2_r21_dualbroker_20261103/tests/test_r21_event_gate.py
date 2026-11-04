import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r21_event_information_gate as r
import numpy as np

def test_event_time_features_are_past_quote_prefix_only():
    t=np.arange(0,121000,1000,dtype=np.int64)
    b=np.arange(len(t),dtype=np.int32)*3+100000
    a=b+np.arange(len(t),dtype=np.int32)%5+50
    ix=np.array([40,70,100],dtype=np.int32)
    v=r.observed_prefix_metrics(t,b,a,ix)
    # Append future bid/ask with wildly mutated prices: earlier outputs invariant.
    t2=np.r_[t,t[-1]+1000,t[-1]+2000,t[-1]+3000]
    b2=np.r_[b,110000,20000,999999];a2=np.r_[a,110050,20050,1000049]
    w=r.observed_prefix_metrics(t2,b2,a2,ix)
    for x,y in zip(v,w):assert np.array_equal(x,y)

def test_recent30_count_does_not_count_future_rows():
    t=np.arange(0,150001,5000,dtype=np.int64)
    b=np.ones(len(t),np.int32)*100000;a=b+50
    (n,mean,flow,sp)=r.observed_prefix_metrics(t,b,a,np.array([10],np.int32))
    assert n[0]==7 and mean[0]==50 and sp[0]==50 and not flow[0]

def test_spread_stable_uses_historical_15s_average():
    t=np.arange(0,100001,1000,dtype=np.int64)
    b=np.ones(len(t),np.int32)*100000;a=b+50
    a[-1]=100500
    n,mean,flow,spread=r.observed_prefix_metrics(t,b,a,np.array([len(t)-1],np.int32))
    assert spread[0]>1.2*mean[0] and n[0]>=8

def test_r21E_case_set_predeclared_and_original_60s_control():
    names=[x[0] for x in r.CASES]
    assert len(names)==len(set(names))==7
    assert r.CASES[0][1]==60000 and r.CASES[0][3]==4000
    assert all(x[1] in (30000,45000,60000) for x in r.CASES)
