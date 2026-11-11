"""R161 isolated research-only pre-submission action and 30s offline label contract.
No original-order mutation. Future quotes never enter inference.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence

@dataclass(frozen=True)
class Quote:
    ts_ms: int
    bid: float
    ask: float

@dataclass(frozen=True)
class Intent:
    ts_ms: int
    side: int
    submitted: bool = False

def guard_action(intent: Intent, action: str, action_ts_ms: int, t1_ms: int | None = None,
                 quote_valid: bool = True, limit_eligible: bool = False) -> str:
    """T1 [t0+15,t0+16), T2 [T1+5,T1+6); fail closed for submitted intents."""
    if intent.submitted or intent.side not in (-1, 1) or not quote_valid:
        return 'ABSTAIN'
    if action not in ('ABSTAIN', 'T1', 'T2', 'LIMIT'):
        raise ValueError('Unknown action')
    if action == 'ABSTAIN':
        return action
    t1_ok = t1_ms is not None and intent.ts_ms+15000 <= t1_ms < intent.ts_ms+16000
    if action == 'T1' and t1_ok and action_ts_ms == t1_ms:
        return action
    if action == 'LIMIT' and t1_ok and limit_eligible and action_ts_ms == t1_ms:
        return action
    if action == 'T2' and t1_ok and t1_ms+5000 <= action_ts_ms < t1_ms+6000:
        return action
    return 'ABSTAIN'

def first_touch_offline(intent: Intent, prefix: Sequence[Quote], future: Sequence[Quote],
                        favorable_usd: float, adverse_usd: float, horizon_ms: int = 30000) -> str:
    """Offline outcome ONLY; side-aware executable bid/ask and exclusive cutoff."""
    if intent.submitted or intent.side not in (-1, 1):
        raise ValueError('Invalid or submitted intent')
    if not isinstance(horizon_ms, int) or horizon_ms <= 0:
        raise ValueError('Invalid horizon')
    if not (isfinite(favorable_usd) and isfinite(adverse_usd) and favorable_usd > 0 and adverse_usd > 0):
        raise ValueError('Invalid touch distances')
    if not prefix:
        raise ValueError('Missing pre-intent quote')
    prev = -1
    for q in prefix:
        if not (prev < q.ts_ms < intent.ts_ms and isfinite(q.bid) and isfinite(q.ask) and 0 < q.bid <= q.ask):
            raise ValueError('Invalid prefix')
        prev = q.ts_ms
    entry = prefix[-1].ask if intent.side == 1 else prefix[-1].bid
    prev = intent.ts_ms-1
    result = 'unresolved'
    for q in future:
        if not (q.ts_ms > prev and isfinite(q.bid) and isfinite(q.ask) and 0 < q.bid <= q.ask):
            raise ValueError('Invalid future quote')
        prev = q.ts_ms
        if q.ts_ms >= intent.ts_ms+horizon_ms:
            continue
        pnl = intent.side*((q.bid if intent.side == 1 else q.ask)-entry)
        if result == 'unresolved' and pnl >= favorable_usd:
            result = 'favorable'
        elif result == 'unresolved' and pnl <= -adverse_usd:
            result = 'adverse'
    return result
