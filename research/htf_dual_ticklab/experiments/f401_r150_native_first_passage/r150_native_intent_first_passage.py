"""F401-R150: source-native bid/ask pending-intent first-passage SHADOW.

Additive research-only module; it does not replace R24/R148B/R149, does not
send MT5 orders, and cannot cancel or retroactively veto an already submitted
or filled R9 trade. Every policy input must be published strictly before the
first genuine native quote in [t0+15000,t0+16000). Outcomes are NEW action-
time bid/ask economic labels, never original t0+30..32 source classes.

Only integer quote prices, real source timestamps and original ordinal event
identifiers are accepted. No fabricated bar, true volume, or L2 information.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Sequence, Optional
import hashlib
import json
import math


class IntentState(str, Enum):
    NEVER_SUBMITTED = "NEVER_SUBMITTED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class Action(str, Enum):
    KEEP_PARENT = "KEEP_PARENT"
    PLACE_UNSENT_LIMIT = "PLACE_UNSENT_LIMIT"
    WAIT_RECONFIRM = "WAIT_RECONFIRM"
    CANCEL_NEVER_SENT = "CANCEL_NEVER_SENT"
    PROTECT_CORRECT = "PROTECT_CORRECT"


@dataclass(frozen=True)
class Quote:
    time_ms: int
    bid: int
    ask: int
    def __post_init__(self):
        if self.time_ms < 0 or self.bid <= 0 or self.ask < self.bid:
            raise ValueError("invalid native bid/ask quote")


@dataclass(frozen=True)
class Intent:
    broker: str
    source_event_id: int
    intent_id: str
    t0_ms: int
    side: int
    state: IntentState
    created_ms: int
    lot: float = .01
    def __post_init__(self):
        if self.side not in (-1, 1) or self.t0_ms < 0 or self.created_ms > self.t0_ms:
            raise ValueError("invalid original intent/side/clock")
        if not self.intent_id or not self.broker or not math.isfinite(self.lot) or self.lot <= 0:
            raise ValueError("invalid intent identity or lot")


@dataclass(frozen=True)
class FrozenCausalState:
    """External R120/R147/R149 published geometry, never computed from future."""
    published_before_ms: int
    micro_direction: float
    htf_direction: float
    session_direction: float
    grid_distance_ticks: int
    quote_staleness_ms: int
    spread_ticks: int
    parent_veto: bool
    parent_score: float
    def __post_init__(self):
        vals = (self.micro_direction, self.htf_direction, self.session_direction,
                self.parent_score)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("invalid causal state")
        if min(self.grid_distance_ticks, self.quote_staleness_ms, self.spread_ticks) < 0:
            raise ValueError("invalid geometry")


@dataclass(frozen=True)
class Proposal:
    intent_id: str
    action: Action
    decision_ms: int
    reason: str
    eligible: bool
    parent_veto: bool
    limit_ticks: Optional[int] = None


@dataclass(frozen=True)
class ReplayResult:
    intent_id: str
    action: str
    activated_ms: int
    fill_ms: Optional[int]
    fill_ticks: Optional[int]
    exit_ms: Optional[int]
    exit_ticks: Optional[int]
    exit_reason: str
    gross_usd: Optional[float]
    net_usd: Optional[float]
    first_favorable_ms: Optional[int]
    first_adverse_ms: Optional[int]
    source_ticks_consumed: int


def assert_native_quote_sequence(quotes: Sequence[Quote]) -> None:
    if not quotes:
        raise ValueError("empty quote sequence")
    if any(quotes[i].time_ms > quotes[i+1].time_ms for i in range(len(quotes)-1)):
        raise ValueError("out-of-order native quote stream")


def first_decision_index(quotes: Sequence[Quote], t0_ms: int) -> Optional[int]:
    """First actual quote >= t0+15s; none if it is outside the 1s window."""
    assert_native_quote_sequence(quotes)
    start, end = t0_ms + 15000, t0_ms + 16000
    lo, hi = 0, len(quotes)
    while lo < hi:
        mid = (lo + hi) // 2
        if quotes[mid].time_ms < start:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo < len(quotes) and quotes[lo].time_ms < end else None


def propose_unsubmitted(intent: Intent, quotes: Sequence[Quote], state: FrozenCausalState,
                        *, grid_retest_max_ticks: int = 120, spread_cap_ticks: int = 150,
                        max_staleness_ms: int = 1000) -> Proposal:
    """Deterministic structural action candidate, not a fitted rejection model.

    The parent veto is IMMUTABLE; this is only a proposed NEW intent action.
    Strict source clock gate prevents consuming any quote at or after decision
    for the state computation. A submitted/filled order is never touched.
    """
    if intent.state is not IntentState.NEVER_SUBMITTED:
        return Proposal(intent.intent_id, Action.KEEP_PARENT, intent.t0_ms,
                        "EXISTING_ORDER_IMMUTABLE", False, state.parent_veto)
    ix = first_decision_index(quotes, intent.t0_ms)
    if ix is None:
        return Proposal(intent.intent_id, Action.KEEP_PARENT, intent.t0_ms,
                        "NO_NATIVE_DECISION_QUOTE", False, state.parent_veto)
    decision = quotes[ix]
    if not (state.published_before_ms < decision.time_ms and
            state.published_before_ms >= intent.created_ms):
        return Proposal(intent.intent_id, Action.KEEP_PARENT, decision.time_ms,
                        "STATE_NOT_STRICTLY_PUBLISHED_BEFORE_DECISION", False,
                        state.parent_veto)
    if state.spread_ticks > spread_cap_ticks or state.quote_staleness_ms > max_staleness_ms:
        return Proposal(intent.intent_id, Action.WAIT_RECONFIRM, decision.time_ms,
                        "SPREAD_OR_STALE_QUOTE", True, state.parent_veto)
    if state.parent_veto:
        return Proposal(intent.intent_id, Action.CANCEL_NEVER_SENT, decision.time_ms,
                        "FROZEN_PARENT_VETO", True, True)
    alignment = intent.side * (state.micro_direction + state.htf_direction + state.session_direction)
    if alignment >= 1.5 and state.grid_distance_ticks <= grid_retest_max_ticks:
        # Quote used ONLY as a hypothetical order price, not as causal input.
        # A limit buy is below ask; limit sell is above bid. No market fill assumed.
        px = decision.ask - max(1, state.grid_distance_ticks) if intent.side == 1 else decision.bid + max(1, state.grid_distance_ticks)
        return Proposal(intent.intent_id, Action.PLACE_UNSENT_LIMIT, decision.time_ms,
                        "CAUSAL_MULTICLOCK_SESSION_GRID_RETEST", True, False, px)
    if alignment <= -1.5:
        return Proposal(intent.intent_id, Action.WAIT_RECONFIRM, decision.time_ms,
                        "STRUCTURAL_DIRECTION_CONFLICT", True, False)
    return Proposal(intent.intent_id, Action.PROTECT_CORRECT, decision.time_ms,
                    "NO_HIGH_CONFIDENCE_VETO", True, False)


def replay_action_time(intent: Intent, proposal: Proposal, quotes: Sequence[Quote],
                       *, latency_ms: int, horizon_ms: int = 30000,
                       target_ticks: int = 1000, stop_ticks: int = 800,
                       commission_roundtrip_usd: float = .20,
                       slippage_ticks: int = 0, contract_oz_per_lot: float = 100.,
                       price_scale: int = 1000) -> ReplayResult:
    """New side-aware first-passage economics from action time, not original label.

    Execution is hypothetical L1 touch; true fills, queue position, broker
    stop semantics and price impact remain UNKNOWN. No interpolation between
    quote timestamps. Stop/target checks start only AFTER a hypothetical fill.
    """
    assert_native_quote_sequence(quotes)
    if latency_ms < 0 or horizon_ms <= 0 or target_ticks <= 0 or stop_ticks <= 0 or slippage_ticks < 0:
        raise ValueError("invalid replay configuration")
    if not math.isfinite(commission_roundtrip_usd) or commission_roundtrip_usd < 0:
        raise ValueError("invalid fees")
    if intent.state is not IntentState.NEVER_SUBMITTED or not proposal.eligible:
        return ReplayResult(intent.intent_id, proposal.action.value, proposal.decision_ms + latency_ms,
                            None, None, None, None, "INELIGIBLE_OR_EXISTING_ORDER", None, None, None, None, 0)
    if proposal.action is not Action.PLACE_UNSENT_LIMIT or proposal.limit_ticks is None:
        return ReplayResult(intent.intent_id, proposal.action.value, proposal.decision_ms + latency_ms,
                            None, None, None, None, "NO_NEW_LIMIT_SUBMITTED", None, None, None, None, 0)
    start = proposal.decision_ms + latency_ms
    end = start + horizon_ms
    fill_ms = fill_px = exit_ms = exit_px = favorable_ms = adverse_ms = None
    exit_reason = "UNFILLED_BY_ACTION_HORIZON"
    count = 0
    last_mark = None
    for q in quotes:
        # An order cannot fill against the decision quote or a same-ms quote.
        if q.time_ms < start or q.time_ms <= proposal.decision_ms:
            continue
        if q.time_ms > end:
            break
        count += 1
        last_mark = q
        if fill_ms is None:
            touched = (q.ask <= proposal.limit_ticks if intent.side == 1
                       else q.bid >= proposal.limit_ticks)
            if not touched:
                continue
            fill_ms = q.time_ms
            # Gap through limit fills at the quoted touch, not at the limit.
            fill_px = (min(proposal.limit_ticks, q.ask + slippage_ticks) if intent.side == 1
                       else max(proposal.limit_ticks, q.bid - slippage_ticks))
            exit_reason = "OPEN_NO_EXIT_QUOTE"
            # No same-tick exit: cannot establish temporal order inside quote.
            continue
        mark = q.bid if intent.side == 1 else q.ask
        move = intent.side * (mark - fill_px)
        if move >= target_ticks and favorable_ms is None:
            favorable_ms = q.time_ms
        if move <= -stop_ticks and adverse_ms is None:
            adverse_ms = q.time_ms
        if move >= target_ticks or move <= -stop_ticks:
            exit_ms = q.time_ms
            exit_px = mark - intent.side * slippage_ticks
            exit_reason = "FAVORABLE_FIRST" if move >= target_ticks else "ADVERSE_FIRST"
            break
    if fill_ms is None:
        return ReplayResult(intent.intent_id, proposal.action.value, start, None, None,
                            None, None, exit_reason, None, None, None, None, count)
    if exit_ms is None:
        # A position with no exit quote is UNRESOLVED, not invented a win/loss.
        return ReplayResult(intent.intent_id, proposal.action.value, start, fill_ms, fill_px,
                            None, None, "OPEN_UNRESOLVED", None, None, favorable_ms, adverse_ms, count)
    gross = intent.side * (exit_px - fill_px) / price_scale * contract_oz_per_lot * intent.lot
    net = gross - commission_roundtrip_usd
    return ReplayResult(intent.intent_id, proposal.action.value, start, fill_ms, fill_px,
                        exit_ms, exit_px, exit_reason, round(gross, 8), round(net, 8),
                        favorable_ms, adverse_ms, count)


def frozen_receipt(intent: Intent, proposal: Proposal, result: ReplayResult) -> str:
    """Deterministic integrity digest; never includes source future truth."""
    record = dict(broker=intent.broker, event_id=intent.source_event_id,
                  intent_id=intent.intent_id, t0_ms=intent.t0_ms, side=intent.side,
                  action=proposal.action.value, decision_ms=proposal.decision_ms,
                  reason=proposal.reason, result=result.__dict__)
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
