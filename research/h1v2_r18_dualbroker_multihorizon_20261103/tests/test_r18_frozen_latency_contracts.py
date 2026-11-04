"""Adversarial execution semantics, no claim of alpha or actual broker fills."""
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from r18_frozen_latency_economic_stress import (frozen_replay, GOOD, STOP,
                                                TIMEOUT, REJECT, BUSY, CENSOR)


def prices(length=16,step=5000):
 t=np.arange(length,dtype=np.int64)*step
 b=np.full(length,100000,np.int32)
 a=np.full(length,100020,np.int32)
 return t,b,a


def replay(t,b,a,signals=(0,),side=(1,),fills=None,slip=0):
 ix=np.array(signals,dtype=np.int32)
 f=ix.copy() if fills is None else np.array(fills,dtype=np.int32)
 return frozen_replay(t,b,a,ix,np.array(side,dtype=np.int8),f,slip)


def test_buy_ask_entry_bid_exit_and_profit_fee():
 t,b,a=prices();b[1]=100160
 state,filled,ex,pnl=replay(t,b,a)
 assert state.tolist()==[GOOD] and ex.tolist()==[1]
 assert pnl[0]==100160-100020-20


def test_sell_bid_entry_ask_exit_and_profit_fee():
 t,b,a=prices();a[1]=99850;b[1]=99830
 state,filled,ex,pnl=replay(t,b,a,side=(-1,))
 assert state.tolist()==[GOOD] and ex.tolist()==[1]
 assert pnl[0]==100000-99850-20


def test_trade_that_hits_adverse_first_stops_and_realizes_net_loss():
 t,b,a=prices();b[1]=99890
 state,filled,ex,pnl=replay(t,b,a)
 assert state.tolist()==[STOP] and ex.tolist()==[1]
 assert pnl[0]==99890-100020-20


def test_slippage_paid_on_both_legs():
 t,b,a=prices();b[1]=100160
 _,_,_,normal=replay(t,b,a,slip=0)
 _,_,_,costly=replay(t,b,a,slip=20)
 assert normal.tolist()==[120]
 assert costly.tolist()==[-80] # forced 60s timeout after 80-raw early net fails +100 TP
 # The 40 raw-unit friction turns the original 120 raw unit quote win into
 # an 80 raw unit position, so the model cannot falsely call it +100 TP.
 state,_,exit_idx,_=replay(t,b,a,slip=20)
 assert state.tolist()!=[GOOD] and exit_idx.tolist()!=[1]


def test_no_tp_or_stop_times_out_at_first_quote_after_60s():
 t,b,a=prices(length=15,step=5000)
 state,filled,ex,pnl=replay(t,b,a)
 assert state.tolist()==[TIMEOUT] and ex.tolist()==[13]
 assert pnl.tolist()==[-40]


def test_gap_greater_than_15_seconds_censored():
 t,b,a=prices(length=4,step=16000)
 state,filled,ex,pnl=replay(t,b,a)
 assert state.tolist()==[CENSOR] and ex.tolist()==[-1]
 assert pnl.tolist()==[-2147483647]


def test_spread_at_fill_above_4_dollars_rejected():
 t,b,a=prices();a[0]=104001
 state,filled,ex,pnl=replay(t,b,a)
 assert state.tolist()==[REJECT] and filled.tolist()==[-1]


def test_position_occupancy_prevents_second_entry():
 t,b,a=prices(length=20,step=1000);b[4]=100160
 state,filled,ex,pnl=replay(t,b,a,signals=(0,1),side=(1,1))
 assert state.tolist()==[GOOD,BUSY] and ex.tolist()==[4,-1]


def test_same_millisecond_future_quote_cannot_instantaneously_fill_tp():
 t=np.array([0,0,1000,2000,3000],dtype=np.int64)
 b=np.array([100000,101000,100160,100160,100160],dtype=np.int32)
 a=np.array([100020,101020,100180,100180,100180],dtype=np.int32)
 state,filled,ex,pnl=replay(t,b,a)
 assert state.tolist()==[GOOD] and ex.tolist()==[2]
 assert pnl.tolist()==[120]
