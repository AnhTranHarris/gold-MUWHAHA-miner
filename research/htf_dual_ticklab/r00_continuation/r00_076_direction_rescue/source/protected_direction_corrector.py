"""R00-076 direction-only arbiter guard.

This is an event-preservation invariant and paired-score evaluator, not a fitted
model or an evidence-backed flip policy. All posterior scores must come from a
separately frozen, point-in-time trained research model (no future labels).
Do NOT feed the true outcome into the arbiter. Neutral labels are used only in
post-event evaluation. Uses no broker-engine side effects.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class DirectionDecision:
    event_id: np.ndarray
    source_quote_index: np.ndarray
    event_time_ms: np.ndarray
    side: np.ndarray
    was_flipped: np.ndarray


def preserve_and_correct(event_id, source_quote_index, event_time_ms,
                         original_side, calibrated_p_up, calibrated_p_down,
                         advantage_threshold=0.0) -> DirectionDecision:
    """Choose BUY/SELL at *each unchanged original event*; never skip/delay.

    A nonnegative threshold, frozen BEFORE transfer, is allowed to protect the
    baseline against weak posterior disagreement; there is never a 'no trade'
    branch. Probabilities must be event-time causal and separately calibrated.
    """
    ids=np.asarray(event_id)
    quotes=np.asarray(source_quote_index, dtype=np.int64)
    t=np.asarray(event_time_ms, dtype=np.int64)
    base=np.asarray(original_side, dtype=np.int8)
    pu=np.asarray(calibrated_p_up, dtype=np.float64)
    pd=np.asarray(calibrated_p_down, dtype=np.float64)
    n=len(base)
    if any(len(x)!=n for x in (ids,quotes,t,pu,pd)):
        raise ValueError('event arrays must have identical lengths')
    if np.any(~np.isin(base,[-1,1])) or np.any(~np.isfinite(pu+pd)):
        raise ValueError('original side must be BUY or SELL and probabilities finite')
    if np.any((pu<0)|(pu>1)|(pd<0)|(pd>1)|(pu+pd>1+1e-10)):
        raise ValueError('probability input invalid')
    if not np.isfinite(advantage_threshold) or advantage_threshold<0:
        raise ValueError('threshold must be a nonnegative frozen value')
    if np.any(quotes<0) or np.any(np.diff(t)<0):
        raise ValueError('invalid event quote index/chronology')
    advantage=(pd-pu)*base
    flip=advantage>advantage_threshold
    final=np.where(flip,-base,base).astype(np.int8)
    return DirectionDecision(ids.copy(),quotes.copy(),t.copy(),final,flip)


def paired_direction_score(original_side, decision: DirectionDecision, future_label):
    """Post-event forensic score. The outcome is never an input to routing."""
    base=np.asarray(original_side,dtype=np.int8)
    y=np.asarray(future_label,dtype=np.int8)
    if len(base)!=len(y) or len(y)!=len(decision.side) or np.any(~np.isin(y,[-1,0,1])):
        raise ValueError('labels/sides invalid')
    flips=base!=decision.side
    if not np.array_equal(flips,decision.was_flipped):
        raise ValueError('flip provenance mismatch')
    rescued=flips&(y==decision.side)
    damaged=flips&(y==base)
    neutral_flipped=flips&(y==0)
    assert not np.any(flips & ~(rescued|damaged|neutral_flipped))
    return {
        'opportunities':len(base), 'emitted':len(decision.side),
        'flips':int(flips.sum()), 'rescued':int(rescued.sum()),
        'damaged':int(damaged.sum()), 'neutral_flipped':int(neutral_flipped.sum()),
        'net_corrected':int(rescued.sum()-damaged.sum()),
        'baseline_correct':int(np.sum(base==y)),
        'corrected_correct':int(np.sum(decision.side==y))
    }
