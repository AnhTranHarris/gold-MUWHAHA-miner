import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/'source'))
from r150_stage1_bayes_bridge import NativeBayesPublisher

def test_native_bayes_prefix_quote_no_future():
    a=NativeBayesPublisher(max_run=8)
    for t,b,ask in [(100,3200000,3200004),(200,3200002,3200006),(300,3200006,3200010)]:
        a.update_native_quote(t,b,ask)
    observed=a.snapshot_prior_to(350,1)
    assert len(observed.features)==24 and np.isfinite(observed.features).all()
    with pytest.raises(ValueError): a.snapshot_prior_to(300,1)
    with pytest.raises(ValueError):a.update_native_quote(299,3200000,3200004)

def test_bayes_no_outcome_teacher_input():
    state=NativeBayesPublisher(max_run=8)
    state.update_native_quote(100,3200000,3200004)
    state.update_native_quote(200,3200003,3200007)
    first=state.snapshot_prior_to(250,-1)
    second=state.snapshot_prior_to(250,-1)
    np.testing.assert_array_equal(first.features,second.features)
    assert first.last_native_ms==200 and first.side==-1

def test_future_suffix_separate_unobserved():
    a=NativeBayesPublisher(max_run=8);b=NativeBayesPublisher(max_run=8)
    prefix=[(100,3200000,3200004),(200,3200003,3200007)]
    for t,bi,ask in prefix:
        a.update_native_quote(t,bi,ask);b.update_native_quote(t,bi,ask)
    x=a.snapshot_prior_to(250,1)
    y=b.snapshot_prior_to(250,1)
    np.testing.assert_array_equal(x.features,y.features)
    b.update_native_quote(300,3200002,3200006)
    with pytest.raises(ValueError): b.snapshot_prior_to(250,1)
