import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from structural_5m_features import build_structural_5m_features,STRUCTURAL_5M_COUNT,STRUCTURAL_5M_NAMES

def _raw(levels,step=1000):
    t=np.arange(len(levels),dtype=np.int64)*step
    m=np.asarray(levels,float)
    return t,m-.1,m+.1

def test_structural_contract_unique_and_finite():
    t=np.arange(0,400000,1000,dtype=np.int64);m=100+np.sin(np.arange(len(t))*.1)
    z=build_structural_5m_features(t,m-.1,m+.1,np.array([350],np.int64),chunk_rows=1000)
    assert z.shape==(1,STRUCTURAL_5M_COUNT) and np.isfinite(z).all()
    assert len(STRUCTURAL_5M_NAMES)==len(set(STRUCTURAL_5M_NAMES))

def test_future_mutation_cannot_change_past_structural_row():
    t=np.arange(0,500000,1000,dtype=np.int64);m=100+np.sin(np.arange(len(t))*.07)
    idx=np.array([350],np.int64)
    a=build_structural_5m_features(t,m-.1,m+.1,idx,chunk_rows=1000)
    m2=m.copy();m2[351:]+=1000
    b=build_structural_5m_features(t,m2-.1,m2+.1,idx,chunk_rows=1000)
    np.testing.assert_allclose(a,b)

def test_later_same_millisecond_record_is_not_current_state():
    # candidate index 350 is first of two rows at same timestamp; row 351 is later source order.
    t=np.arange(0,400000,1000,dtype=np.int64);m=100+np.sin(np.arange(len(t))*.05)
    t=np.insert(t,351,t[350]);m=np.insert(m,351,500.)
    a=build_structural_5m_features(t,m-.1,m+.1,np.array([350],np.int64),chunk_rows=1000)
    m[351]=-500.
    b=build_structural_5m_features(t,m-.1,m+.1,np.array([350],np.int64),chunk_rows=1000)
    np.testing.assert_allclose(a,b)

def test_same_endpoint_different_full_path_is_distinguished():
    # Two 5m paths share start/end/range but reverse the order of the high and low.
    t=np.arange(0,305000,5000,dtype=np.int64)
    a=np.full(len(t),100.,float);b=a.copy()
    a[20]=102.;a[40]=98.;b[20]=98.;b[40]=102.
    za=build_structural_5m_features(t,a-.1,a+.1,np.array([60],np.int64),chunk_rows=1000)
    zb=build_structural_5m_features(t,b-.1,b+.1,np.array([60],np.int64),chunk_rows=1000)
    assert not np.array_equal(za,zb)
    j=STRUCTURAL_5M_NAMES.index('path_extreme_order_300s')
    assert za[0,j]==-zb[0,j] and za[0,j]!=0