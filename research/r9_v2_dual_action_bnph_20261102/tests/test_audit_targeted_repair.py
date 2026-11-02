import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from decision import select_dual,Limits
from ordered_quote_geometry import OrderedQuoteGeometry,GEOMETRY_NAMES
from live_dual_router import ExactQuoteState
from router_v2_features import Quote

def _state(deltas):
    st=ExactQuoteState();geom=OrderedQuoteGeometry()
    v=100.;t=0
    for d in [0.,*deltas]:
        v+=d
        q=Quote(t,v,v+.2)
        st.append(q);geom.append(t,v,v+.2);t+=30
    return st.vector(),geom.snapshot(),geom

def test_audit_102_feature_collision_has_ordered_geometry_counterexample():
    a,ax,_=_state([+.2,-.2,+.1,-.1,+.1])
    b,bx,_=_state([-.2,+.2,-.1,+.1,+.1])
    np.testing.assert_array_equal(a,b)  # verify actual original failure
    assert not np.array_equal(ax,bx)     # verify the repair restores order
    assert ax[GEOMETRY_NAMES.index('max_favorable_up_250ms')]!=bx[GEOMETRY_NAMES.index('max_favorable_up_250ms')]

def test_no_future_data_and_same_millisecond_order():
    a=OrderedQuoteGeometry();b=OrderedQuoteGeometry()
    for q in [(1000,100.,100.2),(1000,100.3,100.5),(1000,100.2,100.4)]:
        a.append(*q);b.append(*q)
    before=b.snapshot().copy()
    a.append(1000,99.8,100.)
    np.testing.assert_array_equal(before,b.snapshot())
    assert not np.array_equal(before,a.snapshot())
    with pytest.raises(ValueError):a.append(999,100.,100.2)

def test_bid_ask_lead_lag_survives_slot():
    bid_first=OrderedQuoteGeometry();ask_first=OrderedQuoteGeometry()
    for t,b,a in [(0,100.,100.2),(10,100.1,100.2),(20,100.1,100.3)]:bid_first.append(t,b,a)
    for t,b,a in [(0,100.,100.2),(10,100.,100.3),(20,100.1,100.3)]:ask_first.append(t,b,a)
    ba=bid_first.snapshot();ab=ask_first.snapshot()
    assert ba[GEOMETRY_NAMES.index('bid_leads_ask_250ms')]==1
    assert ab[GEOMETRY_NAMES.index('ask_leads_bid_250ms')]==1

def test_250ms_30s_60s_5m_windows_explicit():
    for t in ('first_extreme_250ms','first_extreme_30000ms','first_extreme_60000ms','first_extreme_300000ms'):
        assert t in GEOMETRY_NAMES

def test_vectorized_independently_eligible_sell_survives_bad_buy():
    p=np.asarray([[[.02,.03,.95],[.05,.11,.84]],[[.01,.01,.98],[.01,.01,.98]]])
    net=np.asarray([[-.10,.20],[-.2,-.2]])
    assert select_dual(p,net,[.80,.80]).tolist()==[-1,0]

def test_invalid_and_uncalibrated_probabilities_never_trade():
    p=np.array([[[np.nan,0,.95],[.05,.11,.84]]]);net=np.array([[.2,.2]])
    assert select_dual(p,net,[.8,np.inf]).tolist()==[0]

def test_shadow_uses_frozen_model_contract_and_causal_tape():
    from live_dual_router import DualObservedRouter
    from router_v2_features import Quote
    rr=DualObservedRouter(track_ordered_geometry=True)
    assert rr.last_ordered_geometry is None
    for i in range(1300):
        q=Quote(i*250,100+.01*np.sin(i/11),100.2+.01*np.sin(i/11))
        rr.on_quote(q)
    assert rr.last_ordered_geometry is not None
    assert len(rr.last_ordered_geometry)==len(GEOMETRY_NAMES)
    assert rr.count['selected_research_actions']==0
    assert len(rr.quotes.vector())==102
