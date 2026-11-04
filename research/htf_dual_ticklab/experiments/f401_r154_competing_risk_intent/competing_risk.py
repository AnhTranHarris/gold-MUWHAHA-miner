"""R154: causal competing-first-touch research primitive (UNAPPROVED).

Inputs are an actual pre-submission intent and a strictly prior quote prefix.
Outcome labels and later quotes are forbidden as policy inputs. This module
does not infer or manufacture a historical R9 OrderSend intent.
"""
from dataclasses import dataclass
from math import exp, isfinite
from typing import Sequence

@dataclass(frozen=True)
class Quote:
    ts_ms: int
    bid: float
    ask: float

@dataclass(frozen=True)
class Intent:
    ts_ms: int
    side: int  # +1 BUY, -1 SELL
    order_sent: bool = False

@dataclass(frozen=True)
class Hazard:
    favorable_rate: float
    adverse_rate: float
    horizon_s: float

def validate_prefix(intent: Intent, quotes: Sequence[Quote]) -> None:
    if intent.order_sent:
        raise ValueError("Already submitted: no retroactive veto")
    if intent.side not in (-1, 1):
        raise ValueError("Invalid side")
    last = -1
    for q in quotes:
        if not (0 <= q.ts_ms < intent.ts_ms and q.ts_ms > last):
            raise ValueError("Quote prefix must be strictly prior and ordered")
        if not (isfinite(q.bid) and isfinite(q.ask) and 0 < q.bid <= q.ask):
            raise ValueError("Invalid bid/ask")
        last = q.ts_ms

def fit_hazard_from_matured_training_counts(
    favorable: int, adverse: int, exposure_s: float, horizon_s: float
) -> Hazard:
    """Training-only competing cause-specific exponential hazard estimate.

    Maturity/purge and frozen chronology are responsibilities of caller.
    """
    if min(favorable, adverse) < 0 or exposure_s <= 0 or horizon_s <= 0:
        raise ValueError("Invalid exposure")
    return Hazard(favorable / exposure_s, adverse / exposure_s, horizon_s)

def first_touch_probabilities(h: Hazard) -> tuple[float, float, float]:
    """P(favorable first), P(adverse first), P(no touch) over horizon."""
    if min(h.favorable_rate, h.adverse_rate) < 0 or h.horizon_s <= 0:
        raise ValueError("Invalid hazard")
    rate = h.favorable_rate + h.adverse_rate
    if rate == 0:
        return (0.0, 0.0, 1.0)
    untouched = exp(-rate * h.horizon_s)
    return ((1 - untouched) * h.favorable_rate / rate,
            (1 - untouched) * h.adverse_rate / rate, untouched)

def side_aware_first_touch(
    intent: Intent, prefix: Sequence[Quote], future: Sequence[Quote],
    favorable_usd: float, adverse_usd: float
) -> str:
    """OFFLINE LABEL ONLY. Never call this inside policy/inference path.

    Uses executable exit bid for BUY and exit ask for SELL, compared to
    pre-intent executable entry ask for BUY or bid for SELL. Earliest touch wins.
    """
    validate_prefix(intent, prefix)
    if not prefix or min(favorable_usd, adverse_usd) <= 0:
        raise ValueError("Need quote and positive touch distances")
    entry = prefix[-1].ask if intent.side == 1 else prefix[-1].bid
    last = intent.ts_ms - 1
    for q in future:
        if q.ts_ms <= last or q.ts_ms < intent.ts_ms:
            raise ValueError("Future quote chronology invalid")
        if not (0 < q.bid <= q.ask):
            raise ValueError("Invalid future spread")
        last = q.ts_ms
        exit_px = q.bid if intent.side == 1 else q.ask
        pnl = intent.side * (exit_px - entry)
        if pnl >= favorable_usd:
            return "favorable"
        if pnl <= -adverse_usd:
            return "adverse"
    return "unresolved"
