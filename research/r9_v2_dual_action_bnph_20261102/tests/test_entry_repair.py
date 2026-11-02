import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from decision import Prediction,OpportunityPrediction,DualActionPolicy,AsymmetricEntryPolicy,Limits,select_dual
from repaired_features import (QuotePoint,LaggedQuoteGeometry,compose_repaired_features,
                               repaired_action_views,REPAIRED_FEATURE_COUNT,GRID_NAMES)

def _p(side,correct,wrong,net):
    return Prediction(side,correct,wrong,max(0.,1.-correct-wrong),net)

def test_eligibility_first_valid_sell_not_masked_by_invalid_stronger_buy():
    limits=Limits(min_correct=.80,max_wrong=.20,min_margin=.08,min_expected_net=0.)
    buy=_p(1,.95,.02,-.10)
    sell=_p(-1,.84,.05,.20)
    rule=DualActionPolicy(.80,.80,limits)
    assert rule.decide(buy,sell,.20)[0] == -1
    p=np.array([[[.02,.03,.95],[.05,.11,.84]]],dtype=float)
    net=np.array([[-.10,.20]])
    assert select_dual(p,net,[.80,.80],limits).tolist() == [-1]

def test_negative_expected_net_stays_fail_closed():
    rule=DualActionPolicy(.70,.70,Limits(min_correct=.80,min_margin=.01))
    assert rule.decide(_p(1,.96,.01,-.01),_p(-1,.95,.01,-.02),.20)[0] == 0

def test_opportunity_wait_is_independent_of_direction():
    limits=Limits(min_correct=.80,min_opportunity=.80,min_margin=.05)
    rule=AsymmetricEntryPolicy(.70,.70,.70,limits)
    buy=_p(1,.91,.04,.20);sell=_p(-1,.40,.40,-.10)
    assert rule.decide(OpportunityPrediction(.60),buy,sell,.20)[0] == 0
    assert rule.decide(OpportunityPrediction(.90),buy,sell,.20)[0] == 1

def _build_path(levels):
    g=LaggedQuoteGeometry()
    times=[0,250,500,750,1000,4000,4500,4750,5000]
    for t,m in zip(times,levels):
        g.append(QuotePoint(t,m-.10,m+.10))
    return g

def _dummy_hawkes():
    return dict(raw_multi_tau=np.zeros((5,6)),direction=0.,spread_pressure=0.,entropy=0.)

def test_repaired_grid_distinguishes_ordered_paths_that_share_terminal_state():
    a=_build_path([100,101,100,99,100,100,100,100,100])
    b=_build_path([100,99,100,101,100,100,100,100,100])
    za=compose_repaired_features(np.zeros(102,np.float32),a,_dummy_hawkes())
    zb=compose_repaired_features(np.zeros(102,np.float32),b,_dummy_hawkes())
    assert za.shape == zb.shape == (REPAIRED_FEATURE_COUNT,)
    assert not np.array_equal(za,zb)
    diff=np.flatnonzero(za!=zb)
    assert np.all(diff>=102)
    assert any('geom_extreme_order_5s' == GRID_NAMES[i-102] for i in diff if i-102 < len(GRID_NAMES))

def test_repaired_action_views_score_buy_and_sell_from_same_market_state():
    g=_build_path([100,101,100,99,100,100,100,100,100])
    x=compose_repaired_features(np.zeros(102,np.float32),g,_dummy_hawkes())
    z=repaired_action_views(x)
    assert z.shape==(2,REPAIRED_FEATURE_COUNT+1)
    assert z[0,-1]==1 and z[1,-1]==-1
    assert z[0,0]==z[1,0]
    x2=x.copy();x2[1]=2.0
    z2=repaired_action_views(x2)
    assert z2[0,1]==2.0 and z2[1,1]==-2.0  # preserve legacy directional semantics
    assert np.isfinite(z).all()
