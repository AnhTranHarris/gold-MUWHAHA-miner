"""Regression tests for the isolated shared-account signal bus prototype."""
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.engine import BrokerConfig, Replay
from htf_ticklab.signal_bus import ArbitrationPolicy, SharedSignalArbiter, SignalIntent


T0 = 1767315600000


class Once:
    def __init__(self, source_id, side=1, priority=0, stop=1.0, future=False):
        self.source_id = source_id
        self.side = side
        self.priority = priority
        self.stop = stop
        self.future = future
        self.calls = 0

    def on_tick(self, q, view):
        self.calls += 1
        if self.calls != 1:
            return ()
        return (SignalIntent(
            source_id=self.source_id,
            observed_ms=q.ms + (1000 if self.future else 0),
            side=self.side, lots=0.01, stop_distance=self.stop,
            target_distance=2.0, priority=self.priority),)

    def on_bar(self, bar, q, view):
        return ()


class BarOnce:
    def __init__(self, source_id, side=1, priority=0):
        self.source_id = source_id
        self.side = side
        self.priority = priority
        self.once = False

    def on_bar(self, bar, q, view):
        if self.once or bar.seconds != 5:
            return ()
        self.once = True
        return (SignalIntent(self.source_id, q.ms, self.side, 0.01, 1.0,
                             priority=self.priority),)

    def on_tick(self, q, view):
        return ()


class TickAt:
    def __init__(self, source_id, when, side, priority):
        self.source_id, self.when, self.side, self.priority = source_id, when, side, priority

    def on_bar(self, bar, q, view):
        return ()

    def on_tick(self, q, view):
        return (SignalIntent(self.source_id, q.ms, self.side, 0.01, 1.0,
                             priority=self.priority),) if q.ms == self.when else ()


def q(ms, bid=100.0, ask=100.2, broker="coinexx"):
    return Quote(ms, bid, ask, broker)


def sim_for(sources, policy=None, latency=0, max_spread=2.0):
    bus = SharedSignalArbiter(sources, policy)
    sim = Replay(BrokerConfig(name="coinexx", order_latency_ms=latency,
                              max_spread_price=max_spread), bus, (5, 15))
    return sim, bus


def test_bar_signals_compete_with_tick_signals_before_shared_order():
    sim, bus = sim_for({
        "bar": BarOnce("bar", 1, 1),
        "tick": TickAt("tick", T0 + 5000, -1, 3),
    })
    sim.on_quote(q(T0))
    sim.on_quote(q(T0 + 5000))  # completed S5 emits before on_tick
    assert len(sim.pending) == 1
    assert sim.pending[0].side == -1
    assert bus.decisions[-1]["source_id"] == "tick"
    sim.on_quote(q(T0 + 5001))
    assert sim.position.side == -1
    assert bus.decisions[0]["decision"] == "queued_not_filled"


def test_equal_priority_opposite_sides_fail_closed():
    sim, bus = sim_for({
        "a": Once("a", 1, 4),
        "b": Once("b", -1, 4),
    })
    sim.on_quote(q(T0))
    assert sim.position is None and sim.pending == []
    assert bus.rejections["opposed_equal_priority"] == 2


def test_one_broker_account_and_no_pending_entry_burst():
    sim, bus = sim_for({"a": Once("a"), "b": Once("b", priority=-1)}, latency=100)
    sim.on_quote(q(T0))
    assert len(sim.pending) == 1
    assert bus.decisions[-1]["proposals"] == 2
    sim.on_quote(q(T0 + 50))
    assert sim.position is None
    sim.on_quote(q(T0 + 100))
    assert sim.position is not None
    assert sim.events["filled_entries"] == 1
    assert sim.cfg.initial_balance == 100


def test_shared_stop_risk_cap_and_margin_headroom():
    sim, bus = sim_for({"a": Once("a", stop=15.0)},
                       ArbitrationPolicy(max_stop_risk_fraction=0.05))
    sim.on_quote(q(T0))
    assert sim.pending == []
    assert bus.rejections["shared_stop_risk_budget"] == 1
    sim2, bus2 = sim_for({"a": Once("a")},
                         ArbitrationPolicy(max_margin_fraction=0.001))
    sim2.on_quote(q(T0))
    assert bus2.rejections["shared_margin_budget"] == 1


def test_future_signal_timestamp_is_not_allowed():
    sim, _ = sim_for({"a": Once("a", future=True)})
    with pytest.raises(ValueError, match="noncausal"):
        sim.on_quote(q(T0))


def test_central_broker_spread_gate_and_protective_stop():
    sim, bus = sim_for({"a": Once("a")}, max_spread=0.1)
    sim.on_quote(q(T0))
    assert bus.rejections["spread_at_signal"] == 1
    sim2, bus2 = sim_for({"a": Once("a")})
    sim2.on_quote(q(T0))
    sim2.on_quote(q(T0 + 100, bid=100.1, ask=100.3))
    assert sim2.position is not None
    sim2.on_quote(q(T0 + 200, bid=99.1, ask=99.3))
    assert sim2.trades[0]["reason"] == "stop"
    assert sim2.trades[0]["broker"] == "coinexx"
    assert sim2.stopouts == 0


def test_protective_stop_mandatory_and_configuration_guarded():
    sim, _ = sim_for({"a": Once("a", stop=None)})
    with pytest.raises(ValueError, match="protective stop"):
        sim.on_quote(q(T0))
    with pytest.raises(ValueError):
        ArbitrationPolicy(max_stop_risk_fraction=2)
