import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from timing_transition_features import build_timing_features,wait_improves_target,TIMING_FEATURE_COUNT,TIMING_FEATURE_NAMES
from repaired_features import REPAIRED_FEATURE_COUNT,REPAIRED_FEATURE_NAMES

def test_timing_view_is_causal_prefix_stable():
    rng=np.random.default_rng(7);X=rng.normal(size=(12,REPAIRED_FEATURE_COUNT)).astype(np.float32);ts=np.arange(12,dtype=np.int64)*250
    a=build_timing_features(X[:8],ts[:8]);b=build_timing_features(X,ts)
    np.testing.assert_allclose(a,b[:8])

def test_future_feature_mutation_cannot_change_past_timing_row():
    rng=np.random.default_rng(8);X=rng.normal(size=(10,REPAIRED_FEATURE_COUNT)).astype(np.float32);ts=np.arange(10,dtype=np.int64)*250
    a=build_timing_features(X,ts);X[8:]*=1000;b=build_timing_features(X,ts)
    np.testing.assert_allclose(a[:8],b[:8])

def test_wait_target_does_not_filter_rows_by_current_future_label():
    d={'good':np.array([[0,0],[1,0],[0,0],[0,0]],np.uint8),
       'next_dt_ms':np.array([250,250,1250,-1]),'next_any_good':np.array([1,1,1,0],np.uint8)}
    y,valid=wait_improves_target(d,1000)
    assert y.tolist()==[1,0,0,0]
    assert valid.tolist()==[True,True,False,False]
    assert len(y)==4

def test_timing_feature_contract_unique_and_finite():
    X=np.zeros((5,REPAIRED_FEATURE_COUNT),np.float32);ts=np.arange(5,dtype=np.int64)*250
    X[:,REPAIRED_FEATURE_NAMES.index('last_mid_move')]=[0,1,-1,1,-1]
    z=build_timing_features(X,ts)
    assert z.shape==(5,TIMING_FEATURE_COUNT)
    assert np.isfinite(z).all()
    assert len(TIMING_FEATURE_NAMES)==len(set(TIMING_FEATURE_NAMES))
