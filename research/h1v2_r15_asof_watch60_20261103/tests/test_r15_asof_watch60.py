"""Adversarial causal-prefix, price-side, gap, horizon and occupancy checks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from r15_asof_watch60 import watch60_first_observed,independent_labels,selected_schedule,quarter_count,STAGED,REFERENCE


def test_first_confirmation_is_later_observed_quote_and_no_backdated_fill():
 t=np.arange(0,62000,250,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),103000,np.int32)
 a[4:]=101000
 ix=np.arange(len(t),dtype=np.int64)
 flags=np.ones(len(t),dtype=np.int8)
 ema300=np.full(len(t),2500.,dtype=float);ema15=np.full(len(t),2300.,dtype=float)
 move=np.zeros(len(t),np.int32)
 observed,starts,confirms,ex,reset=watch60_first_observed(t,b,a,ix,flags,ema300,ema15,move,move)
 assert observed[0,4] and not observed[0,0]
 assert t[ix[np.flatnonzero(observed[0])[0]]]==1000
 assert int(confirms[0])==1 and int(starts[0])==1


def test_mutating_future_cannot_change_prior_asof_confirmation():
 t=np.arange(0,10000,250,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),103000,np.int32)
 a[6:]=101000
 ix=np.arange(len(t),dtype=np.int64);flags=np.ones(len(t),np.int8)
 e300=np.full(len(t),2800.,dtype=float);e15=np.full(len(t),2500.,dtype=float)
 mv=np.zeros(len(t),np.int32)
 s1,*_=watch60_first_observed(t,b,a,ix,flags,e300,e15,mv,mv)
 aa=a.copy();aa[25:]=103500
 s2,*_=watch60_first_observed(t,b,aa,ix,flags,e300,e15,mv,mv)
 assert np.array_equal(s1[:,:25],s2[:,:25])


def test_quote_gap_cancels_watch_before_later_confirmation():
 t=np.array([0,250,500,800,16000,32001,32251],dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.array([103000,103000,103000,103000,103000,101000,101000],np.int32)
 ix=np.arange(len(t),dtype=np.int64);flags=np.ones(len(t),np.int8)
 e=np.full(len(t),3200.,dtype=float);mv=np.zeros(len(t),np.int32)
 s,start,conf,ex,res=watch60_first_observed(t,b,a,ix,flags,e,e,mv,mv)
 assert conf[0]==0 and res[0]>=1


def test_60s_horizon_no_adverse_after_30s_is_distinct_from_original():
 t=np.arange(0,126000,200,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),100600,np.int32)
 i=np.searchsorted(t,6000)
 entry_ask=int(a[i]);assert entry_ask==100600
 b[t>=8000]=100750;a[t>=8000]=101350
 # Post-exit adverse after 40s: ORIGINAL SAFE30 accepts, SAFE60 rejects.
 b[t>=49000]=99850;a[t>=49000]=100450
 out,original=independent_labels(t,b,a,np.array([i],np.int64))
 assert original['BUY_strict'][0]
 assert not out[60000]['BUY_strict'][0]
 assert not out[45000]['BUY_strict'][0]
 assert out[30000]['BUY_strict'][0]


def test_distinct_60s_success_not_allowed_to_count_as_original_15s():
 t=np.arange(0,180000,500,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),100600,np.int32)
 i=np.searchsorted(t,6000)
 b[t>=27000]=100750;a[t>=27000]=101350
 out,original=independent_labels(t,b,a,np.array([i],np.int64))
 assert not original['BUY_strict'][0]
 assert out[30000]['BUY_strict'][0]
 assert out[60000]['BUY_strict'][0]


def test_firstTP_uses_true_bid_ask_fee_and_one_position():
 t=np.arange(0,90000,100,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),100500,np.int32)
 i=np.searchsorted(t,5000);j=np.searchsorted(t,5200)
 # Correct BUY TP = entry ask 100500 + fee20 + target100 == 100620.
 b[t>=5300]=100620;a[t>=5300]=101120
 idx,side,ex,net=selected_schedule(t,b,a,np.array([i],np.int64),np.array([True]),np.array([False]),15000)
 assert len(idx)==1 and int(side[0])==1
 assert t[ex[0]]==5300 and int(net[0])==100


def test_quarter_reference_not_divided_by_four():
 assert REFERENCE==(28,27,25,24)


def test_favorability_does_not_allow_spread_cost_waiver():
 t=np.arange(0,130000,500,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),103000,np.int32)
 i=np.searchsorted(t,5000)
 # Future bid up $0.5 gross from opening liquidation, but price still below entry Ask.
 b[t>=15000]=100500;a[t>=15000]=103500
 out,orig=independent_labels(t,b,a,np.array([i],np.int64))
 assert not orig['BUY_strict'][0]
 assert not out[60000]['BUY_strict'][0]
