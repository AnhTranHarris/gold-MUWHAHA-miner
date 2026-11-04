import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r21_quota_aware_interval_exchange as m
import numpy as np

def test_exact_interval_cardinality_not_start_order():
    s=np.array([0,1,4,8],dtype=np.int64);e=np.array([8,3,5,9],dtype=np.int64)
    idx=m.exact_cardinality(s,e)
    assert idx.tolist()==[1,2,3]

def test_strict_overlap_and_identical_fill():
    s=np.array([1,1,2,4]);e=np.array([2,3,4,5]);idx=m.exact_cardinality(s,e)
    assert idx.tolist()==[0,3]

def test_source_gap_fresh_does_not_fabricate_cross_gap_history():
    t=np.array([0,100000,400000,400010,700020],dtype=np.int64)
    ix=np.arange(5,dtype=np.int32)
    assert m.gap_fresh(t,ix).tolist()==[False,False,False,False,False]

def test_halo_candidate_includes_last_observed_ms_before_quarter():
    t=np.r_[np.arange(500000,900000,10000),899900,900000,900005,900005,900600,1200000].astype(np.int64)
    ix,c=m.candidate_quote_ix(t,np.array([1]),np.array([0]),halo_ms=200)
    assert len(ix)>=3 and set([len(t)-6,len(t)-5,len(t)-4]).issubset(set(ix)) and len(t)-3 not in ix

def test_quota_exchange_prefers_coverage_does_not_touch_other_quarter():
    q=np.array([0,1],dtype=np.int64)
    t=np.array([10,12,19,30,100,200,900005,900009,900015],dtype=np.int64)
    oldf=np.array([0,6],dtype=np.int32);olde=np.array([3,8],dtype=np.int32)
    tf=np.array([1,4],dtype=np.int32);te=np.array([2,5],dtype=np.int32)
    f,e,rows,c0,c1,changed=m.local_capacity(t,oldf,olde,q,np.array([2,1]),np.array([0]),tf,te)
    assert c1[0]>=c0[0] and c1[1]==c0[1]
    assert len(f)>len(oldf) and changed==[0]
    assert all(t[f[i+1]]>t[e[i]] for i in range(len(f)-1))
