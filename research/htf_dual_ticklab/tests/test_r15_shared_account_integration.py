"""Official Replay integration: tick source must reach actual queued and filled order."""
from htf_ticklab.feeds import Quote
from htf_ticklab.engine import Replay,BrokerConfig
from htf_ticklab.tick_rearm_r15 import TickRearmSource
from htf_ticklab.signal_bus import SharedSignalArbiter
from htf_ticklab.economic_exit import CostAwareLifecycle,ExitProfile
from htf_ticklab.cli import parse_args

def test_tick_r15_reaches_funded_engine_with_subsequent_actual_quote_fill():
    source=TickRearmSource()
    router=SharedSignalArbiter({'r15_tick_rearm':source})
    econ=CostAwareLifecycle(router,ExitProfile(
        max_hold_ms=60000,activate_net_usd=2.1,
        min_locked_net_usd=.2,trail_floor_price=1.3))
    cfg=BrokerConfig(name='coinexx',initial_balance=100.,
        order_latency_ms=100,commission_per_lot_side=3.5,
        adverse_slippage_price=.10,max_spread_price=.9)
    sim=Replay(cfg,econ,(5,60,300))
    t=1767315600000
    for i in range(14):
        sim.on_quote(Quote(t+i*1000,100+i*.10,100.2+i*.10,'coinexx'))
    assert router.decisions
    assert any(x['decision']=='queued_not_filled' for x in router.decisions)
    assert sim.position is not None
    assert sim.position.entry_ms>router.decisions[0]['event_ms']
    assert sim.position.entry_reason.endswith('causal_tick_minute_bracket_s1')
    assert sim.stopouts==0

def test_both_r15_research_modes_are_opt_in_and_default_off():
    base=['--broker','coinexx','--input','fixture.csv.gz',
          '--output','out.json']
    assert parse_args(base).strategy=='none'
    for mode in ('tick-rearm-r15','tick-triad-r15'):
        p=parse_args(base+['--strategy',mode,'--research-risk-cap','.05',
                    '--research-margin-cap','.4','--research-daily-loss-cap','.2',
                    '--research-peak-loss-cap','.35'])
        assert p.strategy==mode
