"""Synthetic, local-only causality and label-horizon regression fixtures."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from r00_066_horizon_contract import observe_horizon
from r00_066_native_innovations import extract_quote_innovations


def test_10s_gain_30s_loss_not_confused():
    t=np.array([0,10_000,30_000,30_200,40_000],dtype=np.int64)
    price=np.array([100,101,99,98,99],dtype=float)
    got=observe_horizon(t,price,np.array([0]),np.array([0]))
    assert got.known_future.tolist()==[True]
    assert got.future_index.tolist()==[2]
    assert got.direction.tolist()==[-1]
    assert got.markout.tolist()==[-1.0]
    # Demonstrate the original R00-064/065 offset chooses index 1, not 2.
    assert int(np.searchsorted(t,10_000,side='left'))==1


def test_future_sparse_tape_and_boundary_are_missing():
    t=np.array([0,29_000,32_000,33_000],dtype=np.int64)
    price=np.array([100,100,110,120.],dtype=float)
    got=observe_horizon(t,price,np.array([0]),np.array([0]))
    assert not got.known_future[0]
    assert got.direction[0]==0
    assert np.isnan(got.markout[0])


def test_neutral_and_small_displacements_are_wrong():
    t=np.array([0,30_000,60_000],dtype=np.int64)
    neutral=observe_horizon(t,np.array([100.,100.,100.]),np.array([0]),np.array([0]))
    assert neutral.direction.tolist()==[0]
    small=observe_horizon(t,np.array([100.,100.09,100.09]),np.array([0]),np.array([0]))
    assert small.direction.tolist()==[0]
    positive=observe_horizon(t,np.array([100.,100.11,100.11]),np.array([0]),np.array([0]))
    assert positive.direction.tolist()==[1]


def test_quote_features_prefix_invariant_and_quote_types():
    t=np.array([0,100,200,350,800,1200],dtype=np.int64)
    b=np.array([100,100.1,100.1,100.2,100.2,100.2])
    a=np.array([100.5,100.5,100.6,100.7,100.7,100.7])
    full=extract_quote_innovations(t,b,a)
    assert full.update_kind.tolist()==[0,1,2,3,0,0]
    for n in range(1,len(t)+1):
        pref=extract_quote_innovations(t[:n],b[:n],a[:n])
        for key in pref.__dataclass_fields__:
            np.testing.assert_array_equal(getattr(pref,key),getattr(full,key)[:n])
        assert np.all(pref.max_observed_feature_time_ms<=t[:n])
