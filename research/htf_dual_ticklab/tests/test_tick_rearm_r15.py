"""R15 actual-tick source tests: completed S1, quote triggers, filled rearm."""
from htf_ticklab.tick_rearm_r15 import TickRearmSource,TickRearmParameters
from htf_ticklab.feeds import Quote
from htf_ticklab.signal_bus import AccountView
import pytest

def qt(ms,bid,ask=None,broker='coinexx'):
    return Quote(ms,bid,bid+.20 if ask is None else ask,broker)

def av(ms,side=0,pending=False,broker='coinexx'):
    return AccountView(broker,ms,100.,100.,side,pending,0.)

def test_no_same_second_future_data_and_tick_trigger():
    s=TickRearmSource()
    all_signals=[]
    for i in range(12):
        t=120000+i*1000
        out=s.on_tick(qt(t,100.+i*.10),av(t))
        all_signals.extend(out)
    assert len(all_signals)>=1
    assert all(q.observed_ms>=129000 for q in all_signals)
    assert all(q.side==1 for q in all_signals)

def test_opposite_rearm_only_after_observed_filled_position():
    s=TickRearmSource()
    for i in range(12):
        t=120000+i*1000
        s.on_tick(qt(t,100.+i*.10),av(t))
    # A real account position (not a mere queued proposal) observed later.
    s.on_tick(qt(132000,101.2),av(132000,side=1))
    for i in range(12):
        t=133000+i*1000
        s.on_tick(qt(t,101.2-i*.10),av(t,side=1))
    assert s.mode==2
    close_t=145000
    result=s.on_tick(qt(close_t,100.0),av(close_t))
    assert s.mode==-1 and s.rearms==1
    if result:
        assert result[0].side==-1
    assert s.counts['opposite_rearms']==1

def test_stale_gap_breaks_completed_second_window():
    s=TickRearmSource()
    for i in range(9):
        t=120000+i*1000
        s.on_tick(qt(t,100.+i*.10),av(t))
    s.on_tick(qt(145000,100.9),av(145000))
    assert s.on_tick(qt(146000,101.0),av(146000))==()

def test_broker_isolation():
    s=TickRearmSource()
    s.on_tick(qt(120000,100.),av(120000))
    with pytest.raises(ValueError,match='cross-broker'):
        s.on_tick(qt(121000,100.,broker='dukascopy'),av(121000,broker='dukascopy'))

def test_pending_order_prevents_duplicate_submissions():
    s=TickRearmSource()
    for i in range(12):
        t=120000+i*1000
        s.on_tick(qt(t,100.+i*.1),av(t,pending=True))
    assert s.counts['signals']==0

def test_invalid_parameters_fail_before_backtesting():
    with pytest.raises(ValueError):
        TickRearmParameters(min_efficiency=0)
    with pytest.raises(ValueError):
        TickRearmParameters(lookback_seconds=2)
