import numpy as np
from r00_054_a01_chronological_session_hazard import features,split,HEADS,_past_mean,_matured_rates

def fixture():
    t=np.array([1600000000000,1600000001000,1600000030000,1600000033000,1600000033000,1600000065000],dtype='int64')
    return dict(t=t,side=np.array([1,-1,1,1,-1,1],dtype='int8'),truth=np.array([1,2,0,1,2,0],dtype='int8'),
      OOF_good=np.array([.3,.6,.4,.5,.7,.8],dtype='float32'),
      OOF_opp_guard=np.array([.5,.8,.7,.9,.6,.8],dtype='float32'),
      OOF_neutral_guard=np.array([.9,.6,.8,.7,.8,.9],dtype='float32'))

def test_strict_suffix_independence():
    a=fixture();f=features(a);i=3
    prefix={k:v[:i+1] for k,v in a.items()}
    np.testing.assert_allclose(features(prefix)[i],f[i],atol=0,rtol=0)

def test_future_truth_mutation_cannot_change_anchor():
    a=fixture();b={k:v.copy() for k,v in a.items()};b['truth'][4:]=[0,1]
    np.testing.assert_array_equal(features(a)[3],features(b)[3])

def test_not_yet_matured_truth_is_excluded():
    a=fixture();b={k:v.copy() for k,v in a.items()};b['truth'][2]=2
    # anchor index 5 at t+65s; index2 t+30s => only 35s old, matured,
    # so choose anchor index3 (t+33s), index2 is only 3s old.
    np.testing.assert_array_equal(features(a)[3],features(b)[3])

def test_matured_prior_label_is_included():
    a=fixture();b={k:v.copy() for k,v in a.items()};b['truth'][0]=0
    assert not np.array_equal(features(a)[5],features(b)[5])

def test_same_ms_ordinal_ambiguity_not_consumed_in_rolling_scores():
    a=fixture();b={k:v.copy() for k,v in a.items()};b['OOF_good'][3]=.99
    # row4 shares timestamp with row3; row3 must not enter row4's past score state.
    np.testing.assert_array_equal(features(a)[4],features(b)[4])

def test_future_scores_do_not_affect_past():
    a=fixture();b={k:v.copy() for k,v in a.items()};b['OOF_opp_guard'][4:]=.01
    np.testing.assert_array_equal(features(a)[3],features(b)[3])

def test_teacher_score_is_not_a_feature():
    a=fixture();b={k:v.copy() for k,v in a.items()};b['score']=np.linspace(0,1,len(a['t']))
    np.testing.assert_array_equal(features(a),features(b))

def test_side_unchanged_by_producer():
    a=fixture();before=a['side'].copy();features(a);np.testing.assert_array_equal(a['side'],before)

def test_chronological_split_no_overlap():
    f,c,v=split(101)
    assert sum(f)==60 and sum(c)==20 and sum(v)==21
    assert np.all((f.astype(int)+c.astype(int)+v.astype(int))==1)

def test_missing_f44_source_head_fails():
    a=fixture();a.pop(HEADS[1]);
    try:features(a)
    except KeyError:return
    raise AssertionError('missing score head must fail')

def test_maturity_boundary_exact():
    t=np.array([100000,133000,133001],dtype='int64')
    side=np.ones(3,dtype='int8');truth=np.array([1,0,0],dtype='int8')
    r,_=_matured_rates(t,side,truth,600000)
    assert r[1,1]==1/3 and r[2,1]>1/3
