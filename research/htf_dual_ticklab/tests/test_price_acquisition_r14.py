"""Causal price acquisition source regression on bid/ask quotes."""
from types import SimpleNamespace
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.signal_bus import SignalIntent
from htf_ticklab.price_acquisition_r14 import CausalPriceAcquisition,PriceAcquisitionConfig

def q(ms,bid,ask=None,broker='coinexx'):
    return Quote(ms,bid,ask if ask is not None else bid+.2,broker)

class OneSource:
    def __init__(self,side=1):
        self.side=side
        self.sent=False
    def on_bar(self,*args):return ()
    def on_tick(self,quote,account):
        if self.sent:return ()
        self.sent=True
        return (SignalIntent('source',quote.ms,self.side,.01,1.,3.,
                             priority=2,reason='test_event'),)

account=SimpleNamespace(position_side=0,pending_entry=False)

def test_long_price_improvement_requires_subsequent_quote():
    s=CausalPriceAcquisition(OneSource(1),PriceAcquisitionConfig(.30,3000))
    assert s.on_tick(q(100000,100,100.2),account)==()
    assert s.on_tick(q(100100,99.9,100.1),account)==()
    assert s.on_tick(q(100200,99.65,99.85),account)==()
    assert s.on_tick(q(100200,99.64,99.84),account)==()
    v=s.on_tick(q(100201,99.7,99.9),account)
    assert len(v)==1 and v[0].side==1 and v[0].observed_ms==100201
    assert s.counters['emitted']==1
    assert s.on_tick(q(100300,99.6,99.8),account)==()

def test_short_has_opposite_bid_condition():
    s=CausalPriceAcquisition(OneSource(-1),PriceAcquisitionConfig(.3,3000))
    assert s.on_tick(q(100000,100,100.2),account)==()
    assert s.on_tick(q(100100,100.31,100.51),account)==()
    signals=s.on_tick(q(100200,100.40,100.60),account)
    assert len(signals)==1 and signals[0].side==-1

def test_expiry_prevents_late_profitable_looking_tick():
    s=CausalPriceAcquisition(OneSource(),PriceAcquisitionConfig(.30,1000))
    s.on_tick(q(100000,100,100.2),account)
    assert s.on_tick(q(101100,99.5,99.7),account)==()
    assert s.counters['expired']==1
    assert s.counters['emitted']==0

def test_cross_broker_and_backdating_fails_closed():
    s=CausalPriceAcquisition(OneSource())
    s.on_tick(q(100000,100,100.2),account)
    with pytest.raises(ValueError,match="cross-broker"):
        s.on_tick(q(100100,100,100.2,'dukascopy'),account)
    with pytest.raises(ValueError,match="out-of-order"):
        s.on_tick(q(99999,100,100.2),account)

def test_busy_cancels_pending_campaign():
    s=CausalPriceAcquisition(OneSource(),PriceAcquisitionConfig(.3,3000))
    s.on_tick(q(100000,100,100.2),account)
    busy=SimpleNamespace(position_side=1,pending_entry=False)
    assert s.on_tick(q(100200,99.4,99.6),busy)==()
    assert s.armed is None

def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        PriceAcquisitionConfig(improvement_price=0)
