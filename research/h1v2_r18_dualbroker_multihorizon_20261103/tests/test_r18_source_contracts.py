"""Deterministic source/ordinal/causal-contract adversarial R18 regressions."""
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import r18_broker_multihorizon as r


def quotes(n=400,start=1_000_000):
 t=start+np.arange(n,dtype=np.int64)*1000
 b=np.full(n,100_000,np.int32);a=b+200
 return t,b,a

def test_upstream_sha_contracts():
 r.verify_upstreams()


def test_exact_executable_bidask_first_touch_not_midprice():
 t,b,a=quotes();i=0
 # BUY needs future BID >= ASK0 + fee20 + target100 = 100320.
 b[10]=100319;a[10]=100519
 b[30]=100320;a[30]=100520
 o=r.first_pass_labels(t,b,a,np.array([i],dtype=np.int64))
 assert int(o['BUY_tp'][0])==30
 assert bool(o['BUY_good'][0]) # 60s competing first touch; not original first15


def test_exact_buy_with_post_exit_adverse_original_s1_differs():
 t,b,a=quotes(500)
 b[10]=100320;a[10]=100520
 b[25]=99899;a[25]=100099  # bid -$0.101 after TP, before full30 end
 ix=np.array([0],dtype=np.int64)
 o=r.first_pass_labels(t,b,a,ix)
 gB,gS=r.original_s1_labels(t,b,a,ix)
 assert int(o['BUY_tp'][0])==10 and bool(o['BUY_good'][0])
 assert not bool(gB[0]) # original full30 safe vetoes later retreat
 assert not bool(gS[0])


def test_adverse_before_target_not_hindsight_success():
 t,b,a=quotes(500)
 b[5]=99899;a[5]=100099
 b[10]=100320;a[10]=100520
 o=r.first_pass_labels(t,b,a,np.array([0],dtype=np.int64))
 assert int(o['BUY_adverse'][0])==5
 assert int(o['BUY_tp'][0])==10
 assert not bool(o['BUY_good'][0])


def test_first_target_longer_horizon_has_distinct_60s_label():
 t,b,a=quotes(500)
 b[55]=100350;a[55]=100550
 ix=np.array([0],dtype=np.int64)
 o=r.first_pass_labels(t,b,a,ix)
 assert int(o['BUY_tp'][0])==55 and bool(o['BUY_good'][0])
 assert not bool(r.original_s1_labels(t,b,a,ix)[0][0])
 assert not bool(t[o['BUY_tp'][0]]<=t[ix[0]]+45000)
 assert bool(t[o['BUY_tp'][0]]<=t[ix[0]]+60000)


def test_same_millisecond_future_quote_is_not_executable_exit():
 t,b,a=quotes(500)
 t[1]=t[0] # later ordinal, same ms as entry, must be excluded
 b[1]=100450;a[1]=100650
 b[21]=100350;a[21]=100550
 ix=np.array([0],dtype=np.int64)
 o=r.first_pass_labels(t,b,a,ix)
 assert int(o['BUY_tp'][0])==21
 assert bool(o['BUY_good'][0])


def test_cross_gap_target_censored_not_automatically_good():
 t,b,a=quotes(500)
 t[11:]+=16000  # first future quote after an unobserved >15sec gap
 b[12]=100400;a[12]=100600
 o=r.first_pass_labels(t,b,a,np.array([0],dtype=np.int64))
 assert int(o['BUY_tp'][0])==12
 assert not bool(o['BUY_good'][0])


def test_two_way_sell_geometry_and_side():
 t,b,a=quotes(500)
 # SELL entry BID100000, cover Ask <= 99880.
 b[15]=99679;a[15]=99879
 o=r.first_pass_labels(t,b,a,np.array([0],dtype=np.int64))
 assert int(o['SELL_tp'][0])==15 and bool(o['SELL_good'][0])
 assert not bool(o['BUY_good'][0])


def test_hindsight_onepos_future_interval_and_candidate_side():
 t,b,a=quotes(500)
 ix=np.array([0,4,18,35],np.int64)
 buy=np.array([True,True,True,True]);sell=np.zeros(4,bool)
 exits=np.array([10,9,21,40],np.int32)
 ids,side,ex,n=r.selected_count(t,ix,np.ones(4,bool),buy,sell,exits,np.zeros(4,np.int32),60000)
 assert n==4 and np.array_equal(ix[ids],np.array([4,18,35]))
 assert np.array_equal(side,np.ones(3,np.int8))
 assert np.all(t[ix[ids[1:]]]>t[ex[:-1]])


def test_asof_volatility_invariant_under_future_quote_mutations():
 t,b,a=quotes(500)
 ix=np.array([310,320,321],dtype=np.int64)
 original=r.preentry_volatility(t,b,a,ix)
 b[400:]+=12000;a[400:]+=12000
 changed=r.preentry_volatility(t,b,a,ix)
 for x,y in zip(original,changed):assert np.array_equal(x,y)


def test_watch_signal_does_not_use_future_quote():
 t,b,a=quotes(700)
 # Full prefix 300 sec; first250 every second, wide seed >$1.5.
 a[310]=b[310]+3000
 # subsequent two observed spread-compression revisions with correct 1000 raw.
 a[311]=b[311]+1200;a[312]=b[312]+1100
 ix=np.arange(300,350,dtype=np.int64);flags=np.ones(len(ix),np.int8)
 e15=np.full(len(t),2000.0);e300=np.full(len(t),3000.0)
 m3b=np.full(len(t),1000,np.int32);m3a=m3b.copy()
 v15=np.full(len(ix),2500,np.int32);v60=v15.copy()
 out=r.watch_states(t,b,a,ix,flags,e15,e300,m3b,m3a,v15,v60)
 a[400:]+=100000
 out2=r.watch_states(t,b,a,ix,flags,e15,e300,m3b,m3a,v15,v60)
 for x,y in zip(out,out2): assert np.array_equal(x,y)


def test_month_calendar_and_utc_shift():
 lo,hi=r.month_range('02')
 assert (hi-lo)==28*86400000
 assert r.OFFSETS['02']==-2 and r.OFFSETS['07']==-3
 assert r.LANES[0]=='BASE_250_1500' and len(r.CONTRACTS)==5
