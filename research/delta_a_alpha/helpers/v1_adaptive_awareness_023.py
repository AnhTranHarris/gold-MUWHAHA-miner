#!/usr/bin/env python3
"""V1 023 causal awareness interface, OBSERVE_ONLY until funded parity certification.
The permanent implementation/test archive is also checkpointed in project Library.
"""
from dataclasses import dataclass
from typing import Optional, Sequence

@dataclass(frozen=True)
class CompletedM5:
    completed_at_ms: int
    hi: float
    lo: float
    cl: float
    tick_count: int

@dataclass(frozen=True)
class ClosedFundedChild:
    exit_ms: int
    net_pnl_usd: float
    hold_seconds: float
    funded: bool = True

@dataclass(frozen=True)
class MarketAwareness:
    time_ms: int
    completed_m5_count: int
    tail10_last12: Optional[float]
    tail10_last48: Optional[float]
    tail10_last144: Optional[float]
    median_range_last12: Optional[float]
    recent_auction_width_usd: Optional[float]
    observed_spread_usd: float
    quote_friction_ratio: Optional[float]
    previous_funded_child_win: Optional[bool]
    previous_funded_child_hold_seconds: Optional[float]
    activation_time_eligible: bool
    mode: str = "OBSERVE_ONLY_NO_ORDER_EFFECT"

def market_awareness(now_ms: int, bid: float, ask: float, bars: Sequence[CompletedM5],
                     closed_child: Optional[ClosedFundedChild] = None,
                     anchor_session_ready: bool = True,
                     htf_completed_ready: bool = True) -> MarketAwareness:
    if ask < bid or bid <= 0: raise ValueError("bad quote")
    if closed_child is not None:
        if closed_child.exit_ms > now_ms: raise ValueError("future child outcome leakage")
        if not closed_child.funded: raise ValueError("shadow outcome is not funded evidence")
    valid = tuple(b for b in bars if b.completed_at_ms <= now_ms)
    if any(valid[i].completed_at_ms >= valid[i + 1].completed_at_ms for i in range(len(valid) - 1)):
        raise ValueError("M5 bar ordering")
    ranges = [b.hi - b.lo for b in valid]
    if any(x < 0 for x in ranges): raise ValueError("invalid completed M5")
    def tail(k):
        if len(ranges) < k: return None
        return sum(x >= 10. for x in ranges[-k:]) / k
    last = sorted(ranges[-12:]) if len(ranges) >= 12 else []
    med = (last[5] + last[6]) / 2. if last else None
    width = max(b.hi for b in valid[-12:]) - min(b.lo for b in valid[-12:]) if last else None
    spread = ask - bid
    return MarketAwareness(
        time_ms=now_ms, completed_m5_count=len(valid), tail10_last12=tail(12),
        tail10_last48=tail(48), tail10_last144=tail(144), median_range_last12=med,
        recent_auction_width_usd=width, observed_spread_usd=spread,
        quote_friction_ratio=(spread / width if width and width > 0 else None),
        previous_funded_child_win=(None if closed_child is None else closed_child.net_pnl_usd > 0),
        previous_funded_child_hold_seconds=(None if closed_child is None else closed_child.hold_seconds),
        activation_time_eligible=bool(anchor_session_ready and htf_completed_ready))

def cold_start_initial_scout_eligible(state: MarketAwareness,
                                      signal_qualified: bool, broker_margin_ok: bool,
                                      portfolio_heat_ok: bool) -> bool:
    # NEVER require POS maturity or prior funded winning streak to admit a first scout.
    return bool(state.activation_time_eligible and signal_qualified
                and broker_margin_ok and portfolio_heat_ok)

def renewal_observation(state: MarketAwareness) -> dict:
    # Explicitly no order send, no forecast-derived physical capacity override.
    return dict(previous_funded_child_win=state.previous_funded_child_win,
                previous_funded_child_hold_seconds=state.previous_funded_child_hold_seconds,
                tail10_last12=state.tail10_last12,
                quote_friction_ratio=state.quote_friction_ratio,
                mode="OBSERVE_ONLY_NO_ORDER_EFFECT")
