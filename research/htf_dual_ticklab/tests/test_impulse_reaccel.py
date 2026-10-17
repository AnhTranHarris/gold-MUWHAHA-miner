"""Causal smoke/regression tests for the additive R05 event-time source."""
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.bars import Bar
from htf_ticklab.signal_bus import AccountView
from htf_ticklab.impulse_reaccel import ReaccelConfig, ImpulseRetracementExpert

BASE=5_000_000

def view(t,position=0,pending=False):
    return AccountView(broker="coinexx",event_ms=t,balance=100,
                       equity=100,position_side=position,
                       pending_entry=pending,margin_used=0)

def candle(seconds,start,px,ticks=200):
    return Bar(seconds,start,start+seconds*1000,
               px-.1,px+.08,px-.20,px-.1,
               px+.1,px+.28,px,px+.1,ticks)

def quote(t,mid):
    return Quote(t,mid-.1,mid+.1,"coinexx")

def ready_expert():
    e=ImpulseRetracementExpert(ReaccelConfig(
        impulse_min=.25,efficiency_min=.3,atr_min=.2,
        relative_quote_activity_min=0,
        fib_pullback=.382,rebound=.07))
    for i in range(14):
        b=candle(300,(i+1)*300000,100+i*.1)
        t=b.end_ms+100
        assert e.on_bar(b,quote(t,100+i*.1),view(t))==()
    for j,px in enumerate((100,100.12,100.33,100.82)):
        b=candle(5,BASE+j*5000,px)
        t=b.end_ms+100
        e.on_bar(b,quote(t,px),view(t))
        e.on_tick(quote(t,px),view(t))
    assert e.arm is not None and e.arm["side"]==1
    return e

def test_two_stage_never_uses_same_tick_or_future_quote():
    e=ready_expert()
    target=e.arm["pullback"]-.02
    # Price first comes back into the earlier Fibonacci zone.
    r=e.on_tick(quote(BASE+20150,target),view(BASE+20150))
    assert r==() and e.counters["pullbacks"]==1
    # Only the *later* observed acceleration produces a market intent.
    t=BASE+20200
    events=e.on_tick(quote(t,target+.10),view(t))
    assert len(events)==1
    assert events[0].observed_ms==t and events[0].side==1
    assert events[0].target_distance>events[0].stop_distance
    assert e.counters["signals"]==1

def test_incomplete_candle_is_quarantined():
    e=ImpulseRetracementExpert()
    with pytest.raises(ValueError,match="incomplete"):
        e.on_bar(candle(5,0,100),quote(4999,100),view(4999))

def test_pending_order_blocks_additional_signals():
    e=ready_expert()
    t=BASE+20150
    e.on_tick(quote(t,e.arm["pullback"]-.02),view(t,pending=True))
    assert e.arm is None
    assert e.counters["signals"]==0

def test_wrongway_or_invalid_settings_fail_closed():
    with pytest.raises(ValueError):
        ReaccelConfig(fib_pullback=1.0)
    e=ImpulseRetracementExpert()
    e.on_tick(quote(BASE,100),view(BASE))
    with pytest.raises(ValueError,match="reversal"):
        e.on_tick(quote(BASE-1,100),view(BASE-1))

def test_r05_can_be_explicitly_selected_but_never_defaulted():
    from htf_ticklab.cli import parse_args
    basic=['--broker','coinexx','--input','fixture.csv.gz','--output','out.json']
    assert parse_args(basic).strategy=='none'
    assert parse_args(basic+['--strategy','reaccel-r05']).strategy=='reaccel-r05'
