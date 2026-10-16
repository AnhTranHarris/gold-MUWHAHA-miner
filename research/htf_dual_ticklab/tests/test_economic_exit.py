"""Economic-exit regression tests: causal, central, funded account only."""
import pytest
from htf_ticklab.bars import Bar
from htf_ticklab.feeds import Quote
from htf_ticklab.engine import BrokerConfig, Replay
from htf_ticklab.signal_bus import SharedSignalArbiter, SignalIntent
from htf_ticklab.economic_exit import CostAwareLifecycle, ExitProfile

T=1767315600000

class EntryOnce:
    def __init__(self,side=1):
        self.side=side
        self.fired=False
    def on_bar(self,bar,q,account): return ()
    def on_tick(self,q,account):
        if self.fired:return ()
        self.fired=True
        return (SignalIntent('signal',q.ms,self.side,.01,1.,3.,priority=4,
                             reason='pulse_continuation'),)

def q(ms,bid,ask=None):
    return Quote(ms,bid,bid+.2 if ask is None else ask,'coinexx')

def construct(side=1,latency=100, minstop=0):
    router=SharedSignalArbiter({'signal':EntryOnce(side)})
    supervisor=CostAwareLifecycle(router,ExitProfile(max_hold_ms=30000,
                              activate_net_usd=.35,min_locked_net_usd=.10,
                              trail_floor_price=.30))
    cfg=BrokerConfig(name='coinexx',initial_balance=100,
        order_latency_ms=latency,commission_per_lot_side=3.5,
        adverse_slippage_price=.10,max_spread_price=1.,
        min_stop_distance_price=minstop)
    return Replay(cfg,supervisor,(5,15,300)),supervisor

def test_long_cost_floor_and_delayed_modification():
    sim,sup=construct()
    sim.on_quote(q(T,100))
    assert sim.position is None and len(sim.pending)==1
    sim.on_quote(q(T+100,100))
    p=sim.position
    assert p is not None and p.entry==pytest.approx(100.3)
    original=p.stop
    sim.on_quote(q(T+200,100.35))
    assert p.stop==original
    assert not any(r.kind=='modify_stop' for r in sim.pending)
    sim.on_quote(q(T+300,101.6))
    assert p.stop==original
    assert any(r.kind=='modify_stop' for r in sim.pending)
    sim.on_quote(q(T+399,101.61))
    assert p.stop==original
    sim.on_quote(q(T+400,101.65))
    assert p.stop>p.entry and p.stop<101.65
    assert sim.events['stop_modifications_filled']==1
    sim.on_quote(q(T+500,p.stop-.05))
    assert len(sim.trades)==1 and sim.trades[0]['net_pnl']>0
    assert 'pulse_continuation' in sim.trades[0]['entry_reason']
    assert sim.stopouts==0

def test_short_cost_floor():
    sim,sup=construct(-1)
    sim.on_quote(q(T,100))
    sim.on_quote(q(T+100,100))
    p=sim.position; original=p.stop
    sim.on_quote(q(T+200,98.5))
    assert p.stop==original
    sim.on_quote(q(T+300,98.45))
    assert p.stop==original
    sim.on_quote(q(T+400,98.4))
    assert p.stop<p.entry
    sim.on_quote(q(T+500,p.stop-.1,ask=p.stop+.05))
    assert sim.trades and sim.trades[0]['net_pnl']>0

def test_stop_relaxation_rejected():
    sim,_=construct()
    sim.on_quote(q(T,100))
    sim.on_quote(q(T+100,100))
    old=sim.position.stop
    assert not sim.request_modify_stop(old-1.)
    assert sim.rejections['stop_relaxation_or_no_change']==1

def test_broker_minimum_stop_level_fails_closed_at_fill():
    sim,_=construct(minstop=.4)
    sim.on_quote(q(T,100))
    sim.on_quote(q(T+100,100))
    old=sim.position.stop
    # Stop improvement is below broker-required quote-side distance at ACK.
    assert sim.request_modify_stop(100.3)
    sim.on_quote(q(T+200,100.6))
    assert sim.position.stop==old
    assert sim.rejections['stop_modify_broker_level']==1

def test_max_hold_only_requests_delayed_close():
    router=SharedSignalArbiter({'signal':EntryOnce()})
    controller=CostAwareLifecycle(router,ExitProfile(max_hold_ms=150,activate_net_usd=999))
    sim=Replay(BrokerConfig(name='coinexx',initial_balance=100,
               order_latency_ms=100),controller,(5,15,300))
    sim.on_quote(q(T,100))
    sim.on_quote(q(T+100,100))
    sim.on_quote(q(T+250,100))
    assert sim.position is not None
    assert len([r for r in sim.pending if r.kind=='close'])==1
    sim.on_quote(q(T+350,100))
    assert sim.position is None and sim.trades[0]['reason']=='specialist_max_hold:pulse_continuation'
