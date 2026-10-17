"""R12 opt-in geometry and economic-exit source contracts (not P&L parity)."""
import pytest
from htf_ticklab.cli import parse_args
from htf_ticklab.portfolio_r12 import R12RunnerGeometry,deferred_runner_profile
from htf_ticklab.signal_bus import SignalIntent

class Fixed:
    def on_bar(self,bar,quote,account): return ()
    def on_tick(self,quote,account):
        return (SignalIntent('probe',quote.ms,1,.01,.9,1.5,priority=5,
                             reason='probe'),)

class Quote:
    ms=12345

def test_r12_geometry_changes_stop_target_not_direction_or_lot():
    o=R12RunnerGeometry(Fixed()).on_tick(Quote(),None)[0]
    assert (o.side,o.lots,o.observed_ms,o.priority)==(1,.01,12345,5)
    assert o.stop_distance==pytest.approx(1.8)
    assert o.target_distance==pytest.approx(5.)
    assert o.reason=='probe'

def test_r12_runner_has_delay_activation_and_wider_trailing_than_old_r04():
    p=deferred_runner_profile()
    assert p.max_hold_ms==60000
    assert p.activate_net_usd==pytest.approx(2.10)
    assert p.trail_floor_price==pytest.approx(1.30)
    assert p.min_locked_net_usd==pytest.approx(.20)

def test_r12_only_explicitly_selected():
    args=['--broker','coinexx','--input','fixture.csv.gz','--output','test.json']
    a=parse_args(args)
    assert a.strategy=='none'
    b=parse_args(args+['--strategy','campaign-portfolio-r12',
       '--research-risk-cap','.05','--research-margin-cap','.40',
       '--research-daily-loss-cap','.20','--research-peak-loss-cap','.35'])
    assert b.strategy=='campaign-portfolio-r12'
    assert b.research_margin_cap==pytest.approx(.40)

def test_r12_nonentry_intents_do_not_get_entry_stops():
    class Closer:
        def on_bar(self,*a):return ()
        def on_tick(self,q,account):
            return (SignalIntent('probe',q.ms,0,0,None,
                                 kind='close',reason='capital_release'),)
    o=R12RunnerGeometry(Closer()).on_tick(Quote(),None)[0]
    assert o.kind=='close' and o.stop_distance is None
