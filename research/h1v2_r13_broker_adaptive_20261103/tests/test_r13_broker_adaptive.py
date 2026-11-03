from pathlib import Path
import csv,sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r13_crossbroker_horizon_lanes as m
import r13_delayed_executable_stress as s


def two_min_prefix():
 # 8 minutes, observed quote every 250ms, well after 300s warmup.
 t=np.arange(m.T0-480000,m.T0,250,dtype=np.int64)
 b=(3000000+np.arange(len(t),dtype=np.int32)//30).astype(np.int32)
 a=b+200
 return t,b,a


def test_future_quotes_cannot_change_past_candidates_or_features():
 t,b,a=two_min_prefix()
 k=len(t)-150
 ix,flags,ema300,ema15,b3,a3=m.prefix_candidates(t,b,a)
 bm=b.copy();am=a.copy();bm[k:]+=100;am[k:]+=200
 ix2,fl2,e3002,e15_2,bm3,am3=m.prefix_candidates(t,bm,am)
 before=ix<k
 assert np.array_equal(ix[before],ix2[ix2<k])
 assert np.array_equal(flags[before],fl2[ix2<k])
 assert np.allclose(ema300[:k],e3002[:k])
 assert np.allclose(ema15[:k],e15_2[:k])
 assert np.array_equal(b3[:k],bm3[:k])
 assert np.array_equal(a3[:k],am3[:k])


def test_same_millisecond_future_quote_not_backdated():
 t,b,a=two_min_prefix()
 # Extend all-source observations after 6 mins so within 300s warmup filter passes.
 now=t[-1]+250
 t=np.r_[t,now,now,now+250]
 b=np.r_[b,b[-1],b[-1]+30,b[-1]+40].astype(np.int32)
 a=np.r_[a,a[-1],a[-1]+15,a[-1]+30].astype(np.int32)
 ix,flags,*_=m.prefix_candidates(t,b,a)
 assert len(ix)==len(np.unique(t[ix]))
 assert len(np.flatnonzero(ix==len(t)-2))==0


def test_quote_gap_forces_full_fresh_history():
 t,b,a=two_min_prefix()
 t=np.r_[t,t[-1]+20000+np.arange(1000,dtype=np.int64)*250]
 b=np.r_[b,np.full(1000,b[-1],np.int32)]
 a=np.r_[a,np.full(1000,a[-1],np.int32)]
 ix,_,*_=m.prefix_candidates(t,b,a)
 # 1000*250ms only 250sec after gap -> NO candidate after that gap.
 assert int(np.count_nonzero(ix>=len(t)-1000))==0


def test_spread_aware_source_geometry_not_free_spread():
 t,b,a=two_min_prefix()
 ix,fl,e300,e15,b3,a3=m.prefix_candidates(t,b,a)
 lanes=m.lane_membership(ix,fl,b,a,e300,e15,b3,a3)
 assert lanes['BASE_250_1500'].all()
 # widening ASK past max gate should reject original and even diagnostic
 a2=a.copy();a2[-1000:]+=5000
 ix2,fl2,*_=m.prefix_candidates(t,b,a2)
 assert len(ix2)<len(ix)


def test_exact_one_position_first_target_interval_schedule():
 st=np.array([10,20,30,41,45,80],dtype=np.int64)
 ex=np.array([40,35,45,70,50,100],dtype=np.int64)
 sel=m.exact_interval_schedule(st,ex)
 assert np.all(st[sel[1:]]>ex[sel[:-1]])
 assert len(sel)==3  # 20->35, 41->70, 80->100 (or 45->50)


def test_first_tp_ask_bid_and_fee_long_short():
 start=m.T0
 t=np.array([start,start+200,start+400],dtype=np.int64)
 b=np.array([3000000,3000320,2999000],dtype=np.int32)
 a=np.array([3000200,3000520,2999200],dtype=np.int32)
 ix=np.array([0,0],dtype=np.int64)
 sides=np.array([1,-1],dtype=np.int8)
 j,ex=m.first_tp(t,b,a,ix,sides,5000)
 assert j.tolist()==[1,2]
 assert ex.tolist()==[int(t[1]),int(t[2])]
 assert b[1]-a[0]-20==100   # BUY pays ASK on entry, exits BID
 assert b[0]-a[2]-20>100   # SELL receives BID, covers ASK


def test_delayed_fill_no_future_reentry_and_slippage_downside():
 start=m.T0
 t=np.array([start,start+100,start+200,start+30100,start+30101],dtype=np.int64)
 b=np.array([3000000,3000000,3000500,3000500,3000500],dtype=np.int32)
 a=b+100
 sig=np.array([0,1],dtype=np.int64)
 side=np.array([1,1],dtype=np.int8)
 codes,fills,exits,net=s.stressed_frozen_signal(t,b,a,sig,side,100,0,1500)
 assert codes[0] in (0,1,-3)
 assert codes[1]==-2  # busy after first attempted position
 assert fills[0]==1  # no fill before lagged market quote


def test_source_regression_baseline_counts_and_latency():
 result=m.OUT/'R13_ALL_45_SOURCE_LANE_HORIZON_RESULTS.csv'
 stress=m.OUT/'R13_ALL_135_NEW_LANE_LATENCY_SLIPPAGE_SCENARIOS.csv'
 if not result.exists() or not stress.exists():return
 rows=list(csv.DictReader(result.open()))
 actual={r['source']:int(r['future_selected_nonoverlap_firstTP']) for r in rows if r['lane']=='BASE_250_1500' and r['first_favorable_horizon_ms']=='15000'}
 assert actual=={'R9_REAL_MT5_TESTER':705,'R9_SYNTH_MT5_TESTER':1853,'DUKASCOPY_RAW':6}
 srows=list(csv.DictReader(stress.open()))
 at100={r['source']:(int(r['strict_good_delayed_quotes']),int(r['completed_failure'])) for r in srows if r['lane']=='BASE_250_1500' and r['latency_ms']=='100' and r['per_leg_slippage_raw_0p001']=='0'}
 assert at100=={'R9_REAL_MT5_TESTER':(135,73),'R9_SYNTH_MT5_TESTER':(1128,28),'DUKASCOPY_RAW':(1,1)}


def test_three_source_full_135_scenario_accounting():
 p=m.OUT/'R13_ALL_135_NEW_LANE_LATENCY_SLIPPAGE_SCENARIOS.csv'
 if not p.exists():return
 rows=list(csv.DictReader(p.open()))
 assert len(rows)==135
 for r in rows:
  n=int(r['frozen_future_selected_signals'])
  cnt=sum(int(r[k]) for k in ('strict_good_delayed_quotes','completed_failure','source_censored','quote_or_spread_reject','occupied_skip'))
  assert cnt==n
  assert r['future_known_signal_not_real_model']=='True'

