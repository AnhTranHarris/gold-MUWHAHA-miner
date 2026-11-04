"""R22 adversarial invariants. All original R9 v5 and R11 labels remain immutable."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r22_nine_residual')
import r22_source_exact_rescue_v2 as r

def test_only_observed_past_counts_and_future_does_not_rewrite():
 t=np.array([0,100,200,450,700,1000,1540,2000,31000,31020,31100],dtype=np.int64)
 ix=np.array([3,7,9],dtype=np.int32)
 c,age=r.before_quote_metrics(t,ix)
 t2=t.copy(); t2[-1]+=90000
 d,age2=r.before_quote_metrics(t2,ix[:2])
 assert np.array_equal(d,c[:2])
 assert np.array_equal(age2,age[:2])
 assert c[0]==4

def test_gap_reset_does_not_create_synthetic_prefix():
 t=np.array([0,100,200,1000,17000,17100,17200,17250,17300],np.int64)
 ix=np.array([3,5,8],dtype=np.int32)
 count,age=r.before_quote_metrics(t,ix)
 assert age[1]==100 and age[2]==300
 assert count[1]==2 and count[2]==5

def test_fill_must_arrive_after_delay_and_from_actual_quote():
 t=np.array([0,0,99,100,150,200,1201,1300],np.int64)
 b=np.array([1000]*len(t),np.int32);a=b+100
 sig,fi=r.delay_fill(t,b,a,np.array([0,2],np.int32),100,4000)
 assert np.array_equal(sig,np.array([0,2],np.int32))
 assert np.array_equal(fi,np.array([3,5],np.int32))

def test_fill_reject_if_spread_widens():
 t=np.array([0,100,200],np.int64);b=np.array([1000,1000,1000],np.int32)
 a=np.array([1100,6000,1100],np.int32)
 s,fi=r.delay_fill(t,b,a,np.array([0],np.int32),100,4000)
 assert len(s)==0 and len(fi)==0

def test_two_side_future_does_not_make_wrong_side_correct():
 t=np.array([0,100,200,300,400,500],np.int64)
 b=np.array([10000,10000,10220,10220,10220,10220],np.int32)
 a=b+50
 fill=np.array([0],dtype=np.int32)
 f,e,s,n,c,ex,net=r.winner_intervals(t,b,a,fill,500,0)
 assert c.shape==(1,2)
 assert c[0,0]==1 and c[0,1]==0
 assert len(f)==1 and s[0]==1 and n[0]>=100
 assert t[e[0]]>t[f[0]]

def test_quote_gap_future_censors_not_profit():
 t=np.array([0,100,200,60000],np.int64)
 b=np.array([10000,10001,10002,10500],np.int32);a=b+50
 f,e,s,n,c,ex,net=r.winner_intervals(t,b,a,np.array([0],np.int32),90000,0)
 assert (c[0]==-3).all() and len(f)==0

def test_no_noquote_candidate_materialized():
 t=np.array([0,100,200,300,450],np.int64);b=np.ones(len(t),np.int32)*1000;a=b+25
 qkeys=np.array([0,1,2],np.int64)
 result,metrics=r.trial_from_residual(t,b,a,qkeys,np.array([1],np.int32),0,1,4000,100)
 assert result is None
 assert metrics['raw']==0

def test_changed_lane_not_silently_original_300s():
 assert all(x[1]<300000 for x in r.CASES)
 assert all('R22' not in x[0] for x in r.CASES)
 assert len({x[0] for x in r.CASES})==len(r.CASES)
 assert any(x[2]==8 and x[3]==120000 for x in r.CASES)
