"""Adversarial, artificial quote-source fixtures. NOT market performance."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import r25_broker_adaptive as p


def window(t,b,a,signals):
    t=np.array(t,dtype=np.int64);b=np.array(b,dtype=np.int32);a=np.array(a,dtype=np.int32)
    gaps=np.flatnonzero(np.r_[True,np.diff(t)>15000]).astype(np.int32)
    return p.Window('DUKASCOPY_RAW','01',1,1000,t,b,a,np.array(signals,np.int32),gaps,np.zeros(96,np.int32),np.arange(96,dtype=np.int64)*900000)


def check_first(w,tp,st):
    return p.offline_labels(w,np.asarray(tp,np.int32),np.asarray(st,np.int32))


def test_source_exact_buy_target_after_real_delayed_fill():
    t=[0,100,200,15300,30100,60100]
    b=[10000,10000,10340,10350,10320,10340]
    a=[10200,10200,10540,10550,10520,10540]
    w=window(t,b,a,[0]);res=check_first(w,[[100,100,100]],[[100,100,100]])
    assert res['fill'].tolist()==[1]
    assert res['cause'][0,0,:].tolist()==[p.TARGET,p.TARGET,p.TARGET]
    assert res['exit'][0,0,:].tolist()==[2,2,2]
    assert np.all(res['net'][0,0,:]>0)
    # Under source-specific ask 10200 at fill, Bid 10340 exit, fee 20 => +120 raw.
    assert res['net'][0,0,0]==120.0


def test_first_stopped_not_relabelled_target_after_recovery():
    w=window([0,100,200,350,15500,30000,60000],
             [10000,10000,9800,10500,10500,10500,10500],
             [10200,10200,10000,10700,10700,10700,10700],[0])
    r=check_first(w,[[100,100,100]],[[100,100,100]])
    assert np.all(r['cause'][0,0,:]==p.STOP)
    assert np.all(r['exit'][0,0,:]==2)
    assert np.all(r['net'][0,0,:]<0)


def test_horizon_timeout_has_actual_quote_exit_and_gap_censor():
    good=window([0,100,200,15000,15200,30200,45100,55200,60200],
                [10000]*9,[10200]*9,[0])
    r=check_first(good,[[100,100,100]],[[100,100,100]])
    assert r['cause'][0,0,:].tolist()==[p.TIMEOUT,p.TIMEOUT,p.TIMEOUT]
    assert r['exit'][0,0,:].tolist()==[4,5,8]
    # After +100ms first actual fill, a later >15s observed quote drought censors
    # unless a first barrier was reached on a quote before the gap.
    gap=window([0,100,200,20000,20100,40200,61000],
               [10000]*7,[10200]*7,[0])
    cens=check_first(gap,[[100,100,100]],[[100,100,100]])
    assert np.all(cens['cause'][0,0,:]==p.CENSORED)
    assert np.all(cens['exit'][0,0,:]==-1)


def test_future_appends_cannot_change_past_features_or_geometry():
    t=np.arange(0,200000,100,dtype=np.int64)
    bid=100000+np.cumsum(np.where(np.arange(len(t))%4==0,20,-5)).astype(np.int32)
    ask=bid+100
    w1=window(t,bid,ask,[350,750,1200]);x1=p.asof_features(w1);tp1,st1=p.quote_geometry(w1,x1)
    # Append future observations and make them absurdly volatile; the as-of feature
    # vector, including original 64 quote mark grammar, must be IDENTICAL.
    t2=np.r_[t,t[-1]+np.arange(1,1001,dtype=np.int64)*100]
    b2=np.r_[bid,bid[-1]+np.arange(1,1001,dtype=np.int32)*10000]
    a2=b2+100
    w2=window(t2,b2,a2,[350,750,1200]);x2=p.asof_features(w2);tp2,st2=p.quote_geometry(w2,x2)
    assert np.array_equal(x1,x2)
    assert np.array_equal(tp1,tp2) and np.array_equal(st1,st2)


def test_same_ms_later_ordinal_never_enters_decision_prefix():
    t=np.arange(0,80000,100,dtype=np.int64)
    b=np.full(len(t),10000,np.int32);a=b+100
    w=window(t,b,a,[500]);x=p.asof_features(w)
    t2=np.r_[t[:501], [t[500],t[500],t[500]],t[501:]]
    b2=np.r_[b[:501],[12345,30000,1],b[501:]].astype(np.int32)
    a2=np.r_[a[:501],[12445,30100,101],a[501:]].astype(np.int32)
    # Change strictly future (later original same-ms quote ordinals) cannot change
    # the state available to the signal at original index500.
    w2=window(t2,b2,a2,[500]);x2=p.asof_features(w2)
    assert np.array_equal(x,x2)


def test_oracle_global_nonoverlap_and_not_double_crediting_two_sides():
    w=window([0,100,200,300,400,15100,15300,30200,60200],
             [10000,10000,10400,10400,10400,10400,10400,10400,10400],
             [10200,10200,10600,10600,10600,10600,10600,10600,10600], [0])
    r=check_first(w,[[100,100,100]],[[100,100,100]])
    got=p.hindsight_cardinality(w,r)
    assert len(got)<=1
    assert np.all(w.t[got[:,3]]<w.t[got[:,4]]) if len(got) else True


def test_action_features_have_source_broker_and_six_independent_side_lanes():
    x=np.zeros((2,len(p.r24.FEATURE_NAMES)+28),np.float32)
    x[:,0]=1; x[:,1]=200
    tp=np.array([[100,250,500],[150,300,600]],np.int32);st=tp//2
    z=p.action_features(x,tp,st,'MT5_BROKER_EXPORT')
    assert z.shape==(12,x.shape[1]+5)
    assert (z[:6,x.shape[1]]==[1,1,1,-1,-1,-1]).all()
    assert (z[:6,x.shape[1]+1]==[15,30,60,15,30,60]).all()
    assert (z[:6,x.shape[1]+2]==[100,250,500,100,250,500]).all()


def test_fail_closed_gap_and_independent_calendar_reference_after_action():
    w=window([0,100,200,20000,20100,40200,61000],
             [10000]*7,[10200]*7,[0,3])
    r=check_first(w,np.array([[100,100,100],[100,100,100]]),np.array([[100,100,100],[100,100,100]]))
    choices=np.array([[0,1],[0,1]],np.float64)
    tr,receipt=p.one_position_replay(w,r,choices)
    assert receipt['attempts']==1
    assert len(tr)==1 and tr[0]['status']==p.CENSORED
    q,h=p.hourly_quarter_report(w,tr)
    assert len(q)==96 and len(h)==24
    assert not any(r['joint_80_and_volume'] for r in q+h)


def test_invalid_source_order_and_spread_fails_closed():
    w=window([0,100,50],[100,100,100],[110,110,110],[0])
    with pytest.raises(ValueError):p.asof_features(w)
