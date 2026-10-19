"""Synthetic chronology fixtures: no historical forecast, execution or profit claim."""
import numpy as np
from research.htf_dual_ticklab.r00_continuation.r00_076d3_continuation.source.purged_original_january_folds import folds

def test_32_second_purged_label_maturity_and_train_validation_isolation():
    t=np.arange(1000,dtype=np.int64)*1000
    f=folds(t)
    assert len(f)==5
    for train,validation in f:
        assert len(train)>0 and len(validation)>0
        assert t[train[-1]]+32000<=t[validation[0]]
        assert np.intersect1d(train,validation).size==0

def test_future_chronology_changes_do_not_change_earlier_original_folds():
    t=np.arange(1000,dtype=np.int64)*1000
    before=folds(t)
    t[800:]+=200000
    after=folds(t)
    for i in range(3):
        np.testing.assert_array_equal(before[i][0],after[i][0])
        np.testing.assert_array_equal(before[i][1],after[i][1])
