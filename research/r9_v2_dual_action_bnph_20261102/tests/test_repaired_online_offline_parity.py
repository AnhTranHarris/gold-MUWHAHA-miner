import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from repaired_features import LaggedQuoteGeometry,QuotePoint,excitation_vector
from competing_hawkes import CompetingQuoteHawkes
from raw_repaired_features import (
    build_grid_features,build_excitation_features,build_repaired_raw_features,
    decay_table,TAUS,A,BASELINE,
)
from build_repaired_matrix import build_grid_features as checkpoint_grid_features, build_excitation_features as checkpoint_excitation_features

def test_repaired_online_grid_and_excitation_match_offline_kernel():
    t=np.arange(0,301250,250,dtype=np.int64)
    k=np.arange(len(t),dtype=np.float64)
    mid=100.+.03*np.sin(k*.071)+.009*np.sin(k*.233)
    spread=.20+.01*np.sin(k*.041)
    bid=mid-spread*.5;ask=mid+spread*.5
    geom=LaggedQuoteGeometry();hawk=CompetingQuoteHawkes()
    for ti,bi,ai in zip(t,bid,ask):
        geom.append(QuotePoint(int(ti),float(bi),float(ai)))
        hawk.observe(int(ti),float(bi),float(ai))
    idx=np.array([len(t)-1],np.int64)
    offline_grid=build_grid_features(t,bid,ask,idx)[0]
    dec=decay_table();offline_exc,hit=build_excitation_features(t,bid,ask,idx,dec,TAUS,A,BASELINE)
    checkpoint_grid=checkpoint_grid_features(t,bid,ask,idx)[0]
    checkpoint_exc,checkpoint_hit=checkpoint_excitation_features(t,bid,ask,idx,dec)
    assert hit==1 and checkpoint_hit==1
    np.testing.assert_allclose(geom.snapshot(),offline_grid,atol=2e-6,rtol=2e-6)
    np.testing.assert_allclose(checkpoint_grid,offline_grid,atol=0.,rtol=0.)
    np.testing.assert_allclose(excitation_vector(hawk.features()),offline_exc[0],atol=2e-6,rtol=2e-6)
    np.testing.assert_allclose(checkpoint_exc[0],offline_exc[0],atol=2e-6,rtol=2e-6)

def test_later_same_millisecond_quote_cannot_change_current_repaired_features():
    t=np.arange(0,301250,250,dtype=np.int64)
    mid=100.+.02*np.sin(np.arange(len(t))*.08);bid=mid-.1;ask=mid+.1
    # Candidate is the first source row at 300000ms; append a later row at the same ms.
    t=np.insert(t,-1,t[-2]);bid=np.insert(bid,-1,bid[-2]+5.);ask=np.insert(ask,-1,ask[-2]+5.)
    idx=np.array([len(t)-3],np.int64)
    a=build_repaired_raw_features(t,bid,ask,idx)
    bid2=bid.copy();ask2=ask.copy();bid2[idx[0]+1]-=20.;ask2[idx[0]+1]-=20.
    b=build_repaired_raw_features(t,bid2,ask2,idx)
    np.testing.assert_allclose(a,b,atol=0.,rtol=0.)


def test_quote_gap_resets_online_and_offline_subminute_state_identically():
    pre=np.arange(0,5000,250,dtype=np.int64)
    post=np.arange(25000,30000,250,dtype=np.int64)
    t=np.concatenate((pre,post))
    k=np.arange(len(t),dtype=np.float64);mid=100.+.01*k;bid=mid-.1;ask=mid+.1
    geom=LaggedQuoteGeometry();hawk=CompetingQuoteHawkes()
    for ti,bi,ai in zip(t,bid,ask):
        geom.append(QuotePoint(int(ti),float(bi),float(ai)));hawk.observe(int(ti),float(bi),float(ai))
    idx=np.array([len(t)-1],np.int64)
    grid=build_grid_features(t,bid,ask,idx)[0]
    exc,hit=build_excitation_features(t,bid,ask,idx,decay_table(),TAUS,A,BASELINE)
    assert hit==1
    assert geom.coverage_ms()==int(post[-1]-post[0])
    np.testing.assert_allclose(geom.snapshot(),grid,atol=2e-6,rtol=2e-6)
    np.testing.assert_allclose(excitation_vector(hawk.features()),exc[0],atol=2e-6,rtol=2e-6)
