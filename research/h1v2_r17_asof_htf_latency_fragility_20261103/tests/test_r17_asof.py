from pathlib import Path
import importlib.util
import numpy as np
p=Path(__file__).resolve().parents[1]/'src/r17_asof_htf_latency.py'
s=importlib.util.spec_from_file_location('r17_test_module',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def synthetic():
 t=np.arange(0,25000,1000,dtype=np.int64);b=np.arange(len(t),dtype=np.int32)*200+2500000
 a=b+500; return t,b,a

def test_asof_has_no_future_quote_lookahead():
 t,b,a=synthetic();ix=np.array([4,10,20]);side=np.array([1,-1,1])
 # 15m,1h,4h not yet available; must fail closed without any fabricated anchor.
 f=m.htf_asof_features(t,b,a,ix,side)
 assert all(np.all(~f[f'has_asof_{name}']) for name in ('15m','1h','4h'))
 assert all(np.all(f[f'anchor_{name}_ordinal']==-1) for name in ('15m','1h','4h'))

def test_past_price_only_changes_htf_asof_signal():
 t=np.arange(0,21_000_000,1000,dtype=np.int64);b=np.arange(len(t),dtype=np.int32)*10+2500000;a=b+500
 ix=np.array([20_000]);side=np.array([1]);ref=m.htf_asof_features(t,b,a,ix,side)
 b2=b.copy();a2=a.copy();b2[20_001:]+=1_000_000;a2[20_001:]+=1_000_000
 same=m.htf_asof_features(t,b2,a2,ix,side)
 for k in ref:assert np.array_equal(ref[k],same[k]),k
 assert all(ref['side_aligned_'+n][0] for n in ('15m','1h','4h'))

def test_actual_anchor_at_or_before_horizon_cutoff():
 t=np.array([0,400000,800000,1000000,1300000,1900000,4400000,14500000,20000000],dtype=np.int64)
 b=np.arange(len(t),dtype=np.int32)+2000000;a=b+500
 ix=np.array([7,8],np.int64);s=np.array([1,-1],np.int64)
 q=m.htf_asof_features(t,b,a,ix,s)
 for n,ms in zip(('15m','1h','4h'),m.HORIZONS):
  for j,i in enumerate(ix):
   pos=q['anchor_'+n+'_ordinal'][j]
   if pos>=0:assert pos<i and t[pos]<=t[i]-ms

def test_eligibility_is_side_and_cost_aware_without_future_labels():
 v=np.array([900,2000,2200,900]);e15=np.array([1000,1500,1000,400]);e300=np.array([1100,2500,2400,1000]);
 mb3=np.array([1500,3000,-3000,100]);ma3=np.array([1500,3000,-3000,100]);side=np.array([1,1,-1,1]);
 h={'side_aligned_15m':np.array([True,True,True,False]),'side_aligned_1h':np.array([True,True,False,False]),'side_aligned_4h':np.array([True,False,True,False])}
 q=m.asof_gate_masks(v,e15,e300,mb3,ma3,side,h)
 assert len(q)==len(m.GATES)
 assert bool(q['HTF_15M_1H_4H_SIDE_ALIGNED'][0])
 assert not q['HTF_15M_1H_4H_SIDE_ALIGNED'][1]
 assert bool(q['SPREAD_RELIEF_080_AND_3S_FLOW'][1])
 assert not bool(q['SPREAD_RELIEF_080_AND_3S_FLOW'][3])

def test_nonfinite_ema_fails_closed():
 n=1;htf={k:np.array([True]) for k in ('side_aligned_15m','side_aligned_1h','side_aligned_4h')}
 q=m.asof_gate_masks(np.array([700]),np.array([float('nan')]),np.array([1000.]),np.array([1500]),np.array([1500]),np.array([1]),htf)
 assert all(not bool(x[0]) for x in q.values())
