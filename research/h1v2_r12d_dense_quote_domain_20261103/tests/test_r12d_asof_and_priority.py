"""R12D/R12DQ new additive as-of and source-contract adversarial tests.

These are mechanical logic tests, not a real-market predictive model fit.
"""
import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path('/mnt/data/h1v2_r12/source');sys.path.insert(0,str(ROOT))
from r12_dense_requote import asof_quote_clocks
from r12_tp_oracle import earliest_finish_schedule,quote_tp_first
from r12d_quota_priority import _quarter_ms


def test_asof_prefix_future_mutation_never_rewrites_past_decision():
    t=np.arange(0,360001,1000,dtype=np.int64)
    b=np.full(len(t),5000000,dtype=np.int32);a=b+500
    j0,f0=asof_quote_clocks(t,b,a)
    tt=np.r_[t,np.array([360050,360150,360225,360275,361000],np.int64)]
    bb=np.r_[b,np.array([6000000,0,7000000,-10000000,4500000],np.int32)]
    aa=np.r_[a,np.array([6000400,200,7000400,-9999800,4500600],np.int32)]
    j1,f1=asof_quote_clocks(tt,bb,aa)
    assert np.array_equal(j1[:len(j0)],j0) and np.array_equal(f1[:len(f0)],f0)


def test_no_same_ms_and_first_250_first_50_flags():
    t=np.r_[np.arange(0,310001,1000,dtype=np.int64),np.array([310003,310003,310006,310053,310251],np.int64)]
    b=np.full(len(t),4999500,np.int32);a=b+500
    ix,flag=asof_quote_clocks(t,b,a)
    assert np.array_equal(ix,np.unique(ix))
    assert not np.any(t[ix[1:]]==t[ix[:-1]])
    m={int(t[i]):int(f) for i,f in zip(ix,flag)}
    assert 310003 in m and 310006 in m and 310053 in m and 310251 in m
    assert m[310003]&1==0 and m[310003]&2==0
    assert not (m[310006]&1) and not (m[310006]&2)
    assert m[310053]&2


def test_adverse_gap_resets_entry_warmup_300sec():
    t=np.r_[np.arange(0,305001,1000,dtype=np.int64),np.arange(325002,630003,1000,dtype=np.int64)]
    b=np.full(len(t),5000000,np.int32);a=b+600
    ix,_=asof_quote_clocks(t,b,a)
    got=t[ix]
    assert np.any(got<325002)
    assert not np.any((got>=325002)&(got<625002))
    assert np.any(got>=625002)


def test_spread_gate_and_asof_narrowing_flag():
    t=np.r_[np.arange(0,310001,1000,dtype=np.int64),np.array([310010,310020,310030],dtype=np.int64)]
    b=np.full(len(t),5000000,dtype=np.int32);a=b+1500
    a[-2]=5001470
    ix,flag=asof_quote_clocks(t,b,a)
    flags={int(t[i]):int(f) for i,f in zip(ix,flag)}
    assert flags[310020]&4
    a[-2:]=b[-2:]+1600
    ix2,_=asof_quote_clocks(t,b,a)
    assert not np.any(np.isin(t[ix2],[310020,310030]))


def test_buy_sell_tp_on_actual_later_observed_quote():
    t=np.array([0,100,200,500,700],dtype=np.int64)
    b=np.array([10000,10050,10120,9910,9800],dtype=np.int32)
    a=np.array([10050,10100,10170,9960,9850],dtype=np.int32)
    ix=np.array([0,2],np.int64);entrya=a[ix];entryb=b[ix];side=np.array([1,-1],np.int8)
    xi,xt=quote_tp_first(t,b,a,ix,entrya,entryb,side,horizon=15000,thr=120)
    assert xi[0]==-1 # no Bid quote >=10050+120
    assert xi[1]==3  # SELL Ask 9960 <= entry Bid(10120)-120
    assert xt[1]==t[3]


def test_strict_interval_ends_prevent_simultaneous_second_trade():
    starts=np.array([0,2,4,9,10],dtype=np.int64)
    ends=np.array([10,5,7,10,13],dtype=np.int64)
    v=earliest_finish_schedule(starts,ends)
    assert np.all(starts[v[1:]]>ends[v[:-1]])
    assert len(v)==2


def test_utc_quarter_exactness():
    assert _quarter_ms('2026-02-16T13:00:00Z')==1771246800000
    assert _quarter_ms('2026-06-01T00:00:00Z')%900000==0


def test_empty_history_produces_no_future_candidate():
    i,f=asof_quote_clocks(np.array([],np.int64),np.array([],np.int32),np.array([],np.int32))
    assert len(i)==len(f)==0
