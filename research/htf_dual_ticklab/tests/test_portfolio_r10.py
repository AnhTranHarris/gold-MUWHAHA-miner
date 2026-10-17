"""R10 integrated causal quote-flow + funded-circuit regression tests."""
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.signal_bus import SignalIntent
from htf_ticklab.portfolio_r10 import (
    CircuitCaps,FundedCircuit,FlowPrioritySource)
from htf_ticklab.cli import parse_args

class Stub:
    def on_bar(self,bar,quote,account):
        return ()
    def on_tick(self,quote,account):
        return (SignalIntent('test',quote.ms,1,.01,1.,2.,
                             priority=10,reason='probe'),)

def q(ms,bid=100.,ask=100.2,broker='coinexx'):
    return Quote(ms,bid,ask,broker)

def test_flow_source_uses_only_completed_seconds():
    s=FlowPrioritySource(Stub())
    first=s.on_tick(q(100000,100.,100.3),None)
    assert first[0].priority==10
    s.on_tick(q(100200,100.2,100.3),None)
    signals=s.on_tick(q(101000,100.3,100.35),None)
    assert signals[0].priority>=10
    state=s.flow.snapshot()
    assert state.second==100 and state.bid_only_net==1

def test_new_broker_quote_cannot_cross_contaminate():
    s=FlowPrioritySource(Stub())
    s.on_tick(q(100000),None)
    with pytest.raises(ValueError,match='cross-broker'):
        s.on_tick(q(101000,broker='dukascopy'),None)

def test_daily_pause_resets_and_peak_circuit_persists():
    c=FundedCircuit(CircuitCaps(.10,.30))
    t=1_700_000_000_000
    c.observe(t,100.)
    assert c.approve(t,100.,1.,10.)[0]
    c.observe(t+1000,89.)
    assert c.approve(t+1000,89.,1.,10.)==(False,'daily_equity_circuit')
    nxt=(t//86_400_000+1)*86_400_000+1
    c.observe(nxt,95.)
    assert c.approve(nxt,95.,1.,10.)[0]
    c.observe(nxt+1000,65.)
    assert c.approve(nxt+1000,65.,1.,10.)==(False,'peak_equity_circuit')
    more=(nxt//86_400_000+1)*86_400_000+1
    c.observe(more,110.)
    assert c.approve(more,110.,1.,10.)==(False,'peak_equity_circuit')

def test_noncausal_account_observation_rejected():
    c=FundedCircuit(CircuitCaps(.1,.3))
    c.observe(1000,100.)
    with pytest.raises(ValueError,match='noncausal'):
        c.observe(999,101.)

def test_r10_is_opt_in_with_explicit_research_caps():
    a=parse_args(['--broker','coinexx','--input','Jan.csv.gz',
                  '--output','report.json'])
    assert a.strategy=='none'
    b=parse_args(['--broker','coinexx','--input','Jan.csv.gz',
                  '--output','report.json','--strategy','campaign-portfolio-r10',
                  '--research-risk-cap','.05','--research-margin-cap','.4',
                  '--research-daily-loss-cap','.2','--research-peak-loss-cap','.35'])
    assert b.strategy=='campaign-portfolio-r10'
    assert b.research_risk_cap==pytest.approx(.05)
    with pytest.raises(ValueError):
        CircuitCaps(0.,.25)
