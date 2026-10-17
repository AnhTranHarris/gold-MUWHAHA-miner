"""As-of-time quote flow regression tests with original Quote contract."""
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.quote_flow import ClosedQuoteFlow

def q(ms,bid,ask,broker="coinexx"):
    return Quote(ms,bid,ask,broker)

def test_completed_second_only():
    s=ClosedQuoteFlow()
    assert s.update(q(100000,100.,100.3)) is None
    assert s.update(q(100200,100.1,100.3)) is None
    closed=s.update(q(102000,100.2,100.3))
    assert closed.second==100
    assert closed.bid_only_net==1 and closed.ask_only_net==0
    assert closed.quote_pressure>0
    assert len(s.history)==1

def test_spread_compression_and_same_ms_ticks():
    s=ClosedQuoteFlow()
    s.update(q(100000,100,100.6))
    s.update(q(100000,100.3,100.6))
    closed=s.update(q(101000,100.3,100.35))
    assert closed.spread_compression==pytest.approx(.3)
    assert closed.total_updates==2
    assert closed.bid_only_net==1

def test_broker_isolation_and_chronology():
    s=ClosedQuoteFlow()
    s.update(q(200000,100,100.1))
    with pytest.raises(ValueError,match="out-of-order"):
        s.update(q(199999,100,100.1))
    with pytest.raises(ValueError,match="cross-broker"):
        s.update(q(201000,100,100.1,"dukascopy"))

def test_gap_creates_no_fabricated_seconds():
    s=ClosedQuoteFlow()
    s.update(q(100000,100,100.1))
    x=s.update(q(110000,100,100.1))
    assert x.second==100
    assert len(s.history)==1
