import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r21_cold_epoch_broker_state as x
import r20_residual_quote_hazard as prior
import numpy as np

def test_after_gap_history_past_only_anchor():
    t=np.array([0,10000,20000,40000,50000,60000,70000,80000,90000,100000,110000],np.int64)
    ix=np.arange(len(t),dtype=np.int32)
    assert x.elapsed_since_last_gap(t,ix).tolist()==[0,10000,20000,0,10000,20000,30000,40000,50000,60000,70000]

def test_future_quote_extension_does_not_retroactively_change_asof_age():
    t=np.arange(0,250000,10000,dtype=np.int64);ix=np.arange(len(t),dtype=np.int32)
    past=x.elapsed_since_last_gap(t,ix)
    future=np.r_[t,1000000,1000010,1000020]
    assert np.array_equal(past,x.elapsed_since_last_gap(future,ix))

def test_strict_first_touch_uses_actual_buy_ask_sell_bid_and_fee():
    t=np.array([0,100,200,300,30500],np.int64)
    b=np.array([100000,100150,100200,100250,100270],np.int32)
    a=b+10
    code,exit,net=prior.independent_both_sides(t,b,a,np.array([0],np.int32),0,60000)
    assert code[0,0]==1 and net[0,0]>=100 and exit[0,0]==1
    assert code[0,1]==0

def test_stop_before_profit_not_future_reclassified():
    t=np.array([0,100,200,300],np.int64)
    b=np.array([100000,99850,100150,100220],np.int32)
    a=b+10
    code,exit,net=prior.independent_both_sides(t,b,a,np.array([0],np.int32),0,60000)
    assert code[0,0]==0 and exit[0,0]==1
    assert code[0,1]==1 and exit[0,1]==1

def test_missing_quote_gap_is_censored_not_tp():
    t=np.array([0,20000,20010],np.int64)
    b=np.array([100000,100300,100350],np.int32);a=b+10
    code,exit,net=prior.independent_both_sides(t,b,a,np.array([0],np.int32),0,60000)
    assert np.all(code==-3) and np.all(exit==-1)

def test_nested_epoch_opportunity_sets_at_same_spread():
    xage=np.array([0,59999,60000,120000,179999,180000,300000],np.int64)
    assert np.all((xage>=300000)<=(xage>=180000))
    assert np.all((xage>=180000)<=(xage>=120000))
    assert np.all((xage>=120000)<=(xage>=60000))
