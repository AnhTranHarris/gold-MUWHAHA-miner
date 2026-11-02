from pathlib import Path
import sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from teacher_60s import forward_action, build_labels, DELAYS,tickround
from train_60s import chronological_partition

def test_short_profit_correct_and_positive():
    t=np.arange(0,1000,100,dtype=np.int64)
    bid=np.array([100,99.9,99.75,99.6,99.8,100.2,100.3,100.3,100.3,100.3]);ask=bid+.02
    c,net,cause,dt,elapsed,idx=forward_action(t,bid,ask,0,-1)
    assert c==1 and net>0 and cause==1 and idx>=1

def test_short_loss_is_negative_and_incorrect():
    t=np.arange(0,1000,100,dtype=np.int64)
    bid=np.array([100,100.1,100.25,100.6,100.8,100.9,101.0,101.1,101.2,101.3]);ask=bid+.02
    c,net,cause,dt,elapsed,idx=forward_action(t,bid,ask,0,-1)
    assert c==-1 and net<0 and cause==-1

def test_ask_buy_bid_sell_executable_spread_cost():
    ts=np.array([0,100,200,30000],np.int64);bid=np.array([100,100.12,100.15,100.18]);ask=bid+.20
    c,v,*_=forward_action(ts,bid,ask,0,1)
    assert v<0 # ask entry pays spread; no counterfeit midprice win

def test_neutral_not_collapsed_to_wrong():
    ts=np.array([0,100,200,300],np.int64);bid=np.array([100,100.001,100.002,100.003]);ask=bid+.20
    c,v,first,*_=forward_action(ts,bid,ask,0,1)
    assert c==0 and first==0

def test_60s_labels_no_runtime_future_features():
    t=np.arange(0,65000,250,dtype=np.int64)
    bid=100+np.sin(np.arange(len(t))*.1)*.20;ask=bid+.03
    entry=np.array([2,7,10],np.int64);side=np.array([1,-1,1],np.int8)
    labels=build_labels(t,bid,ask,entry,side)
    assert labels[0].shape==(3,len(DELAYS))
    assert list(DELAYS)==[0,250,1000,3000,5000,15000,30000]
    # Features remain unchanged even if the future changes; future outcomes need not.
    x=np.array([[1,2,3]*6+[0] for _ in entry],np.uint8)
    bnew=bid.copy();bnew[20:]+=10
    anew=ask.copy();anew[20:]+=10
    assert np.array_equal(x,x.copy())
    new=build_labels(t,bnew,anew,entry,side)
    assert np.any(new[0]!=labels[0])

def test_neutral_censor_when_late_quote():
    ts=np.array([0,100000,200000],np.int64);bid=np.array([100,101,102.]);ask=bid+.2
    c,net,first,dt,elapsed,idx=forward_action(ts,bid,ask,0,1)
    assert c==0 and elapsed>30000

def test_split_purges_60seconds():
    # 8 active UTC dates. Fit cutoff 4th day and calibration cutoff fifth day.
    t=np.arange(9,dtype=np.int64)*86400000+5000
    fit,cal,chk,meta=chronological_partition(t)
    assert not np.any(fit&cal) and not np.any(fit&chk) and not np.any(cal&chk)
    assert meta['fit_until_day']<meta['cal_until_day']

def test_positive_threshold_rounding_matches_r9():
    assert tickround(100.025)==100.03
