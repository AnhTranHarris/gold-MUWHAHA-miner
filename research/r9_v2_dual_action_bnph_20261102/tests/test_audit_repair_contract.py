"""Regression contract derived directly from the 2026-11-02 entry-asymmetry audit.

Each test corresponds to a reproduced audit failure. These tests protect mechanics;
they do not assert trading profitability or authorize policy promotion.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from decision import Prediction,OpportunityPrediction,DualActionPolicy,AsymmetricEntryPolicy,Limits,select_dual
from repaired_features import CONTEXT_NAMES,REPAIRED_FEATURE_NAMES,LaggedQuoteGeometry,QuotePoint,compose_repaired_features
from build_repaired_matrix import load_checkpoint

def _p(side,pc,pw,net):
    return Prediction(side,pc,pw,max(0.,1.-pc-pw),net)

def test_audit_direction_nomination_removed_from_repaired_contract():
    assert 'evidence' not in CONTEXT_NAMES
    assert 'lane_reversal' not in CONTEXT_NAMES
    assert 'evidence' not in REPAIRED_FEATURE_NAMES
    assert 'lane_reversal' not in REPAIRED_FEATURE_NAMES

def test_audit_eligibility_first_runtime_and_vectorized_match():
    limits=Limits(min_correct=.80,max_wrong=.20,min_margin=.08,min_expected_net=0.)
    buy=_p(1,.95,.02,-.10);sell=_p(-1,.84,.05,.20)
    assert DualActionPolicy(.80,.80,limits).decide(buy,sell,.20)[0]==-1
    p=np.array([[[.02,.03,.95],[.05,.11,.84]]],dtype=float)
    net=np.array([[-.10,.20]],dtype=float)
    assert select_dual(p,net,[.80,.80],limits).tolist()==[-1]

def test_audit_negative_calibration_payoff_cannot_be_thresholded_into_trade():
    rule=DualActionPolicy(.0,.0,Limits(min_correct=.80,max_wrong=.20,min_margin=0.,min_expected_net=0.))
    assert rule.decide(_p(1,.999,.001,-1e-6),_p(-1,.10,.80,-.2),.20)[0]==0

def test_audit_opportunity_wait_is_separate_from_direction():
    limits=Limits(min_correct=.80,max_wrong=.20,min_margin=.05,min_expected_net=0.,min_opportunity=.80)
    rule=AsymmetricEntryPolicy(.70,.70,.70,limits)
    buy=_p(1,.92,.03,.20);sell=_p(-1,.25,.60,-.2)
    assert rule.decide(OpportunityPrediction(.60),buy,sell,.20)[0]==0
    assert rule.decide(OpportunityPrediction(.90),buy,sell,.20)[0]==1

def _geometry(levels):
    g=LaggedQuoteGeometry()
    times=[0,250,500,750,1000,4000,4500,4750,5000]
    for t,m in zip(times,levels):g.append(QuotePoint(t,m-.1,m+.1))
    return g

def test_audit_ordered_path_collision_is_broken():
    # Same terminal state, opposite early high/low order: legacy aggregate collision
    # must not remain a collision in repaired geometry.
    a=_geometry([100,101,100,99,100,100,100,100,100])
    b=_geometry([100,99,100,101,100,100,100,100,100])
    legacy=np.zeros(102,np.float32)
    h=dict(raw_multi_tau=np.zeros((5,6)),direction=0.,spread_pressure=0.,entropy=0.)
    za=compose_repaired_features(legacy,a,h);zb=compose_repaired_features(legacy,b,h)
    assert not np.array_equal(za,zb)

def test_audit_corrupted_250ms_sell_teacher_is_rejected(tmp_path):
    bad=tmp_path/'R9_V2_250MS_ACTION_TIMING_COINEXX_2026_01_FULL_CHECKPOINT.zip'
    bad.write_bytes(b'not-a-valid-source')
    with pytest.raises(ValueError,match='paired-action FULL_CHECKPOINT'):
        load_checkpoint(bad,'coinexx','01')
