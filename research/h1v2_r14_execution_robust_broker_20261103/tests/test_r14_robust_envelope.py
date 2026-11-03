import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
import numpy as np
from r14_robust_envelope import evaluate_independent_stress,greedy_nonoverlap,additional_prefix_lane,quarter_metrics,REFERENCE


def _ticks():
 t=np.arange(0,35001,100,dtype=np.int64)
 b=np.full(len(t),100000,np.int32);a=np.full(len(t),100050,np.int32)
 b[t>=1000]=100400;a[t>=1000]=100450
 return t,b,a

def test_strict_executable_buy_asks_bid_sensitivity():
 t,b,a=_ticks();ix=np.array([0],np.int64);side=np.array([1],np.int8)
 c,f,e,net=evaluate_independent_stress(t,b,a,ix,side,1500,0,0)
 assert c.tolist()==[1] and e[0]>=0 and net[0]>=100

def test_delay_crossing_slippage_veto():
 t,b,a=_ticks();ix=np.array([0],np.int64);side=np.array([1],np.int8)
 c,_,_,_=evaluate_independent_stress(t,b,a,ix,side,1500,500,0)
 assert c.tolist()==[1]
 c,_,_,_=evaluate_independent_stress(t,b,a,ix,side,1500,1500,0)
 assert c.tolist()==[0] # fill after price jump, no subsequent positive first hit

def test_original_zero_adverse_never_weakened():
 t,b,a=_ticks();b[t>=15000]=99700;a[t>=15000]=99750
 c,_,_,_=evaluate_independent_stress(t,b,a,np.array([0]),np.array([1],np.int8),1500,0,0)
 assert c.tolist()==[0]

def test_sell_cash_price_geometry_and_fees():
 t,b,a=_ticks();b[t>=1000]=99500;a[t>=1000]=99550
 c,_,_,net=evaluate_independent_stress(t,b,a,np.array([0]),np.array([-1],np.int8),1500,0,20)
 assert c.tolist()==[1] and net[0]>=100

def test_gap_censors_without_making_false_good():
 t,b,a=_ticks();keep=(t<5000)|(t>26000);t=t[keep];b=b[keep];a=a[keep]
 c,_,_,_=evaluate_independent_stress(t,b,a,np.array([0]),np.array([1],np.int8),1500,0,0)
 assert c.tolist()==[-3]

def test_spread_reject_after_delay():
 t,b,a=_ticks();a[(t>=100)&(t<2000)]=b[(t>=100)&(t<2000)]+2000
 c,f,_,_=evaluate_independent_stress(t,b,a,np.array([0]),np.array([1],np.int8),1500,100,0)
 assert c.tolist()==[-1] and f.tolist()==[-1]

def test_greedy_interval_cardinality_and_boundary():
 s=np.array([0,10,11,22],np.int64);e=np.array([20,11,21,23],np.int64)
 out=greedy_nonoverlap(s,e)
 assert out.tolist()==[1,3] # strict next start > previous end

def test_asof_spread_relief_no_future_candidate():
 ix=np.array([0,1,2]);flags=np.array([1,2,0],np.int8)
 b=np.array([100000,100000,100000]);a=np.array([102000,100500,100400]);e300=np.array([2000.,2000.,2000.]);e15=np.array([2000.,1800.,1800.]);mb=np.array([0,100,100]);ma=np.array([0,100,100])
 assert additional_prefix_lane(ix,flags,b,a,e300,e15,mb,ma).tolist()==[False,True,False]

def test_quarter_optimistic_bound_preserves_zero():
 import r13_crossbroker_horizon_lanes as r13
 t=np.array([r13.T0+1000],np.int64);ix=np.array([0]);ok=np.array([True]);ends=t+100
 q=quarter_metrics(t,ix,ok,ends,np.array([9]),9)
 assert len(q)==4 and q[0]['independent_isolated_quarter_upper']==1 and q[1]['independent_isolated_quarter_upper']==0
 assert q[0]['minimum_source_quarter_deficit']==REFERENCE[0]-1


def test_prefix_candidate_and_lane_future_mutation_invariance():
 import r13_crossbroker_horizon_lanes as r13
 t=np.arange(0,400001,100,dtype=np.int64)
 b=100000+(np.arange(len(t))//25).astype(np.int32)*3
 a=b+800+(np.arange(len(t))%29).astype(np.int32)
 ix,flags,e300,e15,mb,ma=r13.prefix_candidates(t,b,a)
 half=t.searchsorted(340000)
 b2=b.copy();a2=a.copy();b2[half:]+=700;a2[half:]+=1000
 ix2,f2,e300b,e15b,mbb,mab=r13.prefix_candidates(t,b2,a2)
 cut=t[ix]<340000;cut2=t[ix2]<340000
 assert np.array_equal(ix[cut],ix2[cut2])
 assert np.array_equal(flags[cut],f2[cut2])
 assert np.allclose(e300[ix[cut]],e300b[ix2[cut2]])
 assert np.allclose(e15[ix[cut]],e15b[ix2[cut2]])
 assert np.array_equal(mb[ix[cut]],mbb[ix2[cut2]])
 assert np.array_equal(ma[ix[cut]],mab[ix2[cut2]])
