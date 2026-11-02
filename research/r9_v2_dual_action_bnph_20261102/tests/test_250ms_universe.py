import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from raw_repaired_features import candidate_indices_250ms
from full_250ms_universe import replay_candidate_pairs,timing_labels

def test_candidate_universe_uses_first_observed_quote_per_250ms_slot_and_neutral_spread_gate():
    t=np.array([0,100,260,300,520,760,1000],np.int64)
    b=np.array([100,100,100,100,100,100,100],float)
    a=np.array([100.2,100.2,100.2,102.0,100.2,100.2,100.2],float)
    idx=candidate_indices_250ms(t,b,a,warmup_ms=0,max_spread=1.5)
    assert idx.tolist()==[0,2,4,5,6]
    assert len({int(t[i]//250) for i in idx})==len(idx)

def test_sell_teacher_sign_is_not_inverted():
    t=np.arange(0,30250,250,dtype=np.int64)
    bid=100.-np.arange(len(t))*0.002
    ask=bid+.2
    net,good,*_=replay_candidate_pairs(t,bid,ask,np.array([0],np.int64))
    assert np.isfinite(net).all()
    assert net[0,1]>0
    assert net[0,0]<0

def test_later_same_millisecond_source_record_is_observed():
    # BUY opens at ask 100.20. A later source record with the same timestamp
    # immediately trades through the hard stop; source index order must win.
    t=np.array([1000,1000,31000],np.int64)
    bid=np.array([100.0,99.5,100.0])
    ask=np.array([100.2,99.7,100.2])
    net,good,neutral,cause,exit_ms,*_=replay_candidate_pairs(t,bid,ask,np.array([0],np.int64))
    assert exit_ms[0,0]==1000
    assert net[0,0]<0

def test_wait_teacher_targets_only_next_observed_candidate():
    ts=np.array([1000,1250,2000],np.int64)
    good=np.array([[0,0],[1,0],[0,1]],np.uint8)
    net=np.array([[-.2,-.3],[.2,-.1],[-.1,.3]],np.float32)
    z=timing_labels(ts,good,net)
    assert z['next_dt_ms'].tolist()==[250,750,-1]
    assert z['next_any_good'].tolist()==[1,1,0]
    assert z['wait_improves_strict'].tolist()==[1,0,0]
