"""Synthetic future/decision-quote mutation tests for restored 36D causal HTF state."""
import sys,pathlib,numpy as np
sys.path.insert(0,'/mnt/data/r149_work/R147_PACKAGE/source')
from r147_build_source_features import htf_features,add_interactions

def keep(bid,ask,t,d,side):
    mid=(bid.astype(np.float64)+ask.astype(np.float64))*0.5
    j=np.searchsorted(t,d,side='left');q=mid[j]
    hf,names=htf_features(t,bid,ask,d,side,q)
    chosen=[i for i,name in enumerate(names) if any(name.endswith(z) for z in ('published','close_from_low','close_from_high','age_sec'))]
    assert len(chosen)==16
    dummy_m=np.ones((len(d),92),dtype=np.float32)
    dummy_p=np.ones((len(d),57),dtype=np.float32)
    ints,innames=add_interactions(dummy_m,hf,dummy_p)
    omit={'ix_m1_minus_h1_body','ix_m1_minus_h1_1bar','ix_wallclock_spread','ix_wallclock_quote_age'}
    keepi=[i for i,name in enumerate(innames) if name not in omit]
    assert len(keepi)==20
    return np.column_stack([hf[:,chosen],ints[:,keepi]])

def test_after_and_at_decision_quote_never_changes_published_features():
    t=np.arange(0,3_800_000,1000,dtype=np.int64)
    bid=np.full(len(t),2_500_000,dtype=np.int32)+np.arange(len(t),dtype=np.int32)%37
    ask=bid+220
    d=np.array([1_740_000,2_180_000,3_540_000],dtype=np.int64)
    side=np.array([1,-1,1],dtype=np.int8)
    original=keep(bid,ask,t,d,side)
    # Mutate t>= first decision for the first queried event; later events have their own
    # strictly preceding data, so evaluate independence one event at a time.
    for k in range(len(d)):
        bb=bid.copy();aa=ask.copy()
        changes=t>=d[k]
        bb[changes]+=12_345;aa[changes]+=13_500
        updated=keep(bb,aa,t,d[k:k+1],side[k:k+1])[0]
        np.testing.assert_array_equal(updated,original[k])

def test_no_teacher_or_truth_columns_exposed():
    from r150e_live_shadow import R150EFullStateShadow
    import inspect
    p=inspect.signature(R150EFullStateShadow.observe).parameters
    assert all(x not in p for x in ('truth','oracle','teacher','future_price','future_label'))
