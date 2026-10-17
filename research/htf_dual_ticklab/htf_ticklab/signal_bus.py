"""Causal, centrally arbitrated multi-signal bus for the single-account tick replay.

This is an additive engineering prototype. It preserves the existing Replay's
single-position execution, mark-to-market, margin, protective stops and fees.
No independent strategy is profitable/certified merely by producing an intent.
This phase does not support order time-in-force expiry or multiple positions.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Protocol

from .bars import Bar
from .feeds import Quote


@dataclass(frozen=True, slots=True)
class AccountView:
    broker: str
    event_ms: int
    balance: float
    equity: float
    position_side: int
    pending_entry: bool
    margin_used: float


@dataclass(frozen=True, slots=True)
class SignalIntent:
    source_id: str
    observed_ms: int
    side: int  # -1 short, +1 long, 0 close
    lots: float
    stop_distance: float | None
    target_distance: float | None = None
    priority: int = 0
    kind: str = "entry"  # entry or close
    reason: str = "signal"


@dataclass(frozen=True, slots=True)
class ArbitrationPolicy:
    """Optional research caps are NOT investor-ratified risk limits.

    Stop protection and real replay's broker/margin gates always apply.
    A finite user-approved risk limit must be supplied before investor scoring.
    """
    max_stop_risk_fraction: float | None = None
    max_margin_fraction: float | None = None

    def __post_init__(self) -> None:
        for name in ("max_stop_risk_fraction", "max_margin_fraction"):
            value = getattr(self, name)
            if value is not None and (not isfinite(value) or not 0 < value <= 1):
                raise ValueError(name + " must be in (0, 1]")


class SignalSource(Protocol):
    def on_bar(self, bar: Bar, quote: Quote, account: AccountView) -> Iterable[SignalIntent]: ...
    def on_tick(self, quote: Quote, account: AccountView) -> Iterable[SignalIntent]: ...


class SharedSignalArbiter:
    """Arbitrate all tick and completed-bar intents before one order request.

    Replay calls all on_bar callbacks before on_tick on the same observed quote.
    Consequently higher-priority signals emitted by a different completed bar
    cannot be trumped by an earlier callback. Equal-priority opposite signals
    cancel rather than selecting a direction by naming convention.
    """

    def __init__(self, sources: dict[str, SignalSource],
                 policy: ArbitrationPolicy | None = None,
                 funded_circuit: object | None = None) -> None:
        if not sources or any(not k or not isinstance(k, str) for k in sources):
            raise ValueError("sources must have nonempty unique identifiers")
        self.sources = dict(sorted(sources.items()))
        self.policy = policy if policy is not None else ArbitrationPolicy()
        self.funded_circuit = funded_circuit
        self._pending: list[SignalIntent] = []
        self._pending_quote: tuple[int, float, float] | None = None
        self.decisions: list[dict[str, object]] = []
        self.rejections: dict[str, int] = {}

    def _reject(self, reason: str, q: Quote, signals: int = 1) -> None:
        self.rejections[reason] = self.rejections.get(reason, 0) + signals
        self.decisions.append({"event_ms": q.ms, "decision": "rejected",
                               "reason": reason, "signals": signals})

    @staticmethod
    def _view(q: Quote, engine: object) -> AccountView:
        cfg = engine.cfg
        if q.broker != cfg.name:
            raise ValueError("cross-broker account contamination")
        position = engine.position
        margin = (abs((q.ask if position.side == 1 else q.bid)
                      * position.lots * cfg.contract_size / cfg.leverage)
                  if position is not None else 0.0)
        return AccountView(
            broker=q.broker, event_ms=q.ms, balance=engine.balance,
            equity=engine.equity,
            position_side=position.side if position is not None else 0,
            pending_entry=any(p.kind == "entry" for p in engine.pending),
            margin_used=margin)

    def _accept(self, identity: str, intents: Iterable[SignalIntent] | None,
                q: Quote) -> None:
        if intents is None:
            return
        for candidate in intents:
            if not isinstance(candidate, SignalIntent):
                raise TypeError("signal sources may emit only SignalIntent")
            if candidate.source_id != identity:
                raise ValueError("intent source_id differs from registered source")
            if candidate.observed_ms != q.ms:
                raise ValueError("noncausal/stale signal observed_ms")
            if candidate.kind not in ("entry", "close"):
                raise ValueError("unrecognized order intent kind")
            if (not isinstance(candidate.priority, int) or
                    isinstance(candidate.priority, bool)):
                raise ValueError("priority must be an integer")
            if candidate.kind == "entry":
                if candidate.side not in (-1, 1):
                    raise ValueError("entry side must be -1 or +1")
                if (not isfinite(candidate.lots) or candidate.lots <= 0 or
                        candidate.stop_distance is None or
                        not isfinite(candidate.stop_distance) or
                        candidate.stop_distance <= 0):
                    raise ValueError("entry requires finite lots and protective stop")
                if candidate.target_distance is not None and (
                    not isfinite(candidate.target_distance) or
                    candidate.target_distance <= 0):
                    raise ValueError("target distance must be positive and finite")
            elif candidate.side != 0 or candidate.lots != 0:
                raise ValueError("close intent uses side=0, lots=0")
            self._pending.append(candidate)

    def on_bar(self, bar: Bar, q: Quote, engine: object) -> None:
        if bar.end_ms > q.ms:
            raise ValueError("incomplete/future candle delivered to signal bus")
        key = (q.ms, q.bid, q.ask)
        if self._pending_quote is not None and self._pending_quote != key:
            raise ValueError("unflushed bar intents across quote events")
        self._pending_quote = key
        view = self._view(q, engine)
        for identity, source in self.sources.items():
            method = getattr(source, "on_bar", None)
            if method is not None:
                self._accept(identity, method(bar, q, view), q)

    def on_tick(self, q: Quote, engine: object) -> None:
        key = (q.ms, q.bid, q.ask)
        if self._pending_quote is not None and self._pending_quote != key:
            raise ValueError("bar/tick source chronology mismatch")
        view = self._view(q, engine)
        if self.funded_circuit is not None:
            self.funded_circuit.observe(q.ms, view.equity)
        for identity, source in self.sources.items():
            method = getattr(source, "on_tick", None)
            if method is not None:
                self._accept(identity, method(q, view), q)
        candidates = self._pending
        self._pending = []
        self._pending_quote = None
        if not candidates:
            return
        closes = [c for c in candidates if c.kind == "close"]
        if closes:
            chosen = sorted(closes, key=lambda c: (-c.priority, c.source_id))[0]
            if engine.position is None:
                self._reject("close_without_position", q, len(candidates))
                return
            engine.request_close("arbiter:" + chosen.source_id + ":" + chosen.reason)
            self.decisions.append({"event_ms": q.ms, "decision": "close_requested",
                                   "source_id": chosen.source_id,
                                   "suppressed": len(candidates) - 1})
            return
        if engine.position is not None or view.pending_entry:
            self._reject("shared_account_busy", q, len(candidates))
            return
        ranked = sorted(candidates, key=lambda c: (-c.priority, c.source_id))
        highest = [c for c in ranked if c.priority == ranked[0].priority]
        if {c.side for c in highest} == {-1, 1}:
            self._reject("opposed_equal_priority", q, len(candidates))
            return
        chosen = ranked[0]
        cfg = engine.cfg
        price = q.ask if chosen.side == 1 else q.bid
        if not engine._validate_lots(chosen.lots):
            self._reject("invalid_broker_lots", q, len(candidates))
            return
        if q.ask - q.bid > cfg.max_spread_price:
            self._reject("spread_at_signal", q, len(candidates))
            return
        if chosen.stop_distance < cfg.min_stop_distance_price or (
            chosen.target_distance is not None
            and chosen.target_distance < cfg.min_stop_distance_price):
            self._reject("broker_stop_level", q, len(candidates))
            return
        if view.equity <= 0:
            self._reject("no_equity", q, len(candidates))
            return
        margin = abs(price * chosen.lots * cfg.contract_size / cfg.leverage)
        if margin > view.equity or (
            self.policy.max_margin_fraction is not None
            and margin > view.equity * self.policy.max_margin_fraction):
            self._reject("shared_margin_budget", q, len(candidates))
            return
        estimated_stop_loss = (
            (chosen.stop_distance + 2 * cfg.adverse_slippage_price)
            * chosen.lots * cfg.contract_size
            + 2 * cfg.commission_per_lot_side * chosen.lots)
        if (self.policy.max_stop_risk_fraction is not None and
                estimated_stop_loss > view.equity
                * self.policy.max_stop_risk_fraction):
            self._reject("shared_stop_risk_budget", q, len(candidates))
            return
        if self.funded_circuit is not None:
            allowed, reason = self.funded_circuit.approve(
                q.ms, view.equity, estimated_stop_loss, margin)
            if not allowed:
                self._reject("funded_circuit:" + reason, q, len(candidates))
                return
        queued = engine.request_entry(
            chosen.side, chosen.lots,
            stop_distance=chosen.stop_distance,
            target_distance=chosen.target_distance,
            reason="arbiter:" + chosen.source_id + ":" + chosen.reason)
        if not queued:
            self._reject("engine_declined", q, len(candidates))
            return
        self.decisions.append({
            "event_ms": q.ms, "decision": "queued_not_filled",
            "source_id": chosen.source_id, "side": chosen.side,
            "proposals": len(candidates), "estimated_stop_loss": estimated_stop_loss,
            "estimated_margin": margin, "priority": chosen.priority})
