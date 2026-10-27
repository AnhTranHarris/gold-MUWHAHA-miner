"""Deterministic source-independent as-of tests for R37 pre-t0 feature producer."""
import numpy as np
import pytest
from r37_native_pre_t0_features import feature_matrix

def fixture():
 t=np.arange(0,140000,100,dtype=np.int64)
 b=1500+np.cumsum(np.sin(np.arange(len(t))*.41))*.01
 a=b+.35+np.sin(np.arange(len(t))*.02)*.01
 e=np.array([25000,67000,113000],dtype=np.int64)
 side=np.array([1,-1,1],dtype=np.int8)
 return t,b,a,e,side

def test_future_quotes_never_modify_pre_t0_features():
 t,b,a,e,s=fixture(); X,n,v=feature_matrix(t,b,a,e,s)
 bp=b.copy();ap=a.copy();bp[t>=e[1]]+=700;ap[t>=e[1]]+=700
 Y,n2,v2=feature_matrix(t,bp,ap,e,s)
 assert n==n2 and np.array_equal(X[0],Y[0]) and bool(v[0])

def test_same_millisecond_quote_excluded():
 t,b,a,e,s=fixture();idx=np.where(t==e[0])[0][0]
 bp=b.copy();ap=a.copy();bp[idx]+=200;ap[idx]+=200
 X,_,_=feature_matrix(t,b,a,e,s);Y,_,_=feature_matrix(t,bp,ap,e,s)
 assert np.array_equal(X[0],Y[0])

def test_prefix_features_have_no_current_label_api():
 t,b,a,e,s=fixture()
 X,n,v=feature_matrix(t,b,a,e,s)
 assert len(n)==X.shape[1]==70 and np.all(np.isfinite(X)) and np.all(v)
 assert not any('truth' in x or 'label' in x or 'teacher' in x for x in n)

def test_no_future_candle():
 t,b,a,e,s=fixture()
 X,n,_=feature_matrix(t,b,a,e,s)
 cut=int((e[0]//60000)*60000)
 bp=b.copy();ap=a.copy();bp[t>=cut]+=123;ap[t>=cut]+=123
 Y,_,_=feature_matrix(t,bp,ap,e,s)
 k=n.index('completed_60000ms_side_close_change')
 assert X[0,k]==Y[0,k]

def test_unsorted_ticks_and_side_rejected():
 t,b,a,e,s=fixture()
 with pytest.raises(ValueError):feature_matrix(t[::-1],b[::-1],a[::-1],e,s)
 with pytest.raises(ValueError):feature_matrix(t,b,a,e,np.array([1,0,1]))
