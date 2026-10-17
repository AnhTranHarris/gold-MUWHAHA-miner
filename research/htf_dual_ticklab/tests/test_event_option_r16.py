"""Causal R16 event path decisions and default-off account integration."""
from types import SimpleNamespace
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.signal_bus import SignalIntent
from htf_ticklab.event_option_r16 import EventOptionSource, Options
from htf_ticklab.cli import parse_args

account=SimpleNamespace(position_side=0,pending_entry=False)
def q(ms,bid,ask=None,broker='coinexx'):
    return Quote(ms,bid,bid+.2 if ask is None else ask,broker)
class OneShot:
    def __init__(self): self.done=False
    def on_bar(self,*args): return ()
    def on_tick(self,quote,account):
        if self.done:return ()
        self.done=True
        return (SignalIntent('r15_tick_rearm',quote.ms,1,.01,1.,3.,
                             priority=5,reason='research_probe'),)

def test_bid_ask_improvement_requires_observed_rebound():
    s=EventOptionSource(OneShot())
    assert s.on_tick(q(100000,100.),account)==()
    assert s.on_tick(q(100100,99.6),account)==()
    a=s.on_tick(q(100200,99.75),account)
    assert len(a)==1 and a[0].side==1
    assert a[0].reason=='r16_improved'
    assert a[0].observed_ms==100200
    assert a[0].target_distance==4.
    assert s.counts['improved']==1

def test_exhaustion_reversal_is_distinct_from_price_improvement():
    s=EventOptionSource(OneShot())
    s.on_tick(q(100000,100.),account)
    assert s.on_tick(q(100100,99.2),account)==()
    a=s.on_tick(q(100200,98.9),account)
    assert len(a)==1 and a[0].side==-1
    assert a[0].reason=='r16_reversal'
    assert a[0].stop_distance==1.6

def test_continuation_needs_previously_completed_quote_flow():
    s=EventOptionSource(OneShot())
    s.on_tick(q(100000,100.),account)
    assert s.on_tick(q(100300,100.35),account)==()
    a=s.on_tick(q(101000,100.5),account)
    assert len(a)==1 and a[0].side==1
    assert a[0].reason=='r16_continuation'

def test_late_quote_cannot_execute_expired_token():
    s=EventOptionSource(OneShot(),Options(ttl=1000))
    s.on_tick(q(100000,100.),account)
    assert s.on_tick(q(101001,99.4),account)==()
    assert s.counts['expired']==1

def test_no_cross_broker_or_backdating():
    s=EventOptionSource(OneShot())
    s.on_tick(q(100000,100.),account)
    with pytest.raises(ValueError,match='broker'):
        s.on_tick(q(100100,100.,broker='dukascopy'),account)
    with pytest.raises(ValueError,match='noncausal'):
        s.on_tick(q(99999,100.),account)

def test_r16_experimental_cli_never_activates_implicitly():
    a=['--broker','coinexx','--input','test.csv.gz','--output','a.json']
    assert parse_args(a).strategy=='none'
    b=parse_args(a+['--strategy','tick-event-r16',
        '--research-risk-cap','.05','--research-margin-cap','.4',
        '--research-daily-loss-cap','.2','--research-peak-loss-cap','.35'])
    assert b.strategy=='tick-event-r16'
