import pytest
from mdk01_quote_regime_features_research import (
 Quote,CompletedBar,MaturedEvent,MissingAsOfQuote,source_native_dk01_features
)
E=1600000100000
Q=[Quote(E-2000,0,1800,1800.25),Quote(E-1000,1,1800.2,1800.4),Quote(E,2,1800.3,1800.55)]
BASE=dict(broker='dukascopy',event_msc=E,original_quote_ordinal=2,original_side=1,
          quotes=Q,completed_bars=[],matured_events=[])
def run(**kw):return source_native_dk01_features(**(BASE|kw))
def test_has_causal_features():
 f=run();assert len(f)>100 and f['w5000ms_side_mid_delta']>0 and f['original_side']==1.
def test_future_quote_ignored():
 f=run(); assert run(quotes=Q+[Quote(E+1,3,1900,1900.2)])==f
def test_same_millisecond_future_ordinal_ignored():
 f=run(); assert run(quotes=Q+[Quote(E,3,1900,1900.2)])==f
def test_original_tick_identity_required():
 with pytest.raises(MissingAsOfQuote):run(original_quote_ordinal=3)
def test_unpublished_htf_cannot_leak():
 pub=CompletedBar(900,E-1,1800,1801,1799,1800.8)
 future=CompletedBar(900,E+1,1790,1820,1780,1820)
 assert run(completed_bars=[pub,future])==run(completed_bars=[pub])
def test_only_matured_previous_outcomes():
 good=MaturedEvent(E-35000,1,0);future=MaturedEvent(E+1,1,1)
 assert run(matured_events=[good,future])==run(matured_events=[good])
def test_side_sign_relations():
 a=run();b=run(original_side=-1)
 assert a['w5000ms_side_mid_delta']==-b['w5000ms_side_mid_delta']
def test_source_dealer_separation():
 with pytest.raises(ValueError):run(broker='coinexx')
def test_corrupt_original_quote_rejected():
 with pytest.raises(ValueError):run(quotes=[Quote(E,2,1801,1800)])
def test_order_must_be_preserved():
 with pytest.raises(ValueError):run(quotes=[Q[1],Q[0],Q[2]])
