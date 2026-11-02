"""Side-independent BUY/SELL/WAIT arbitration for R9 v2 repair.

The contract is deliberately eligibility-first: each side must independently pass
probability, bad-entry, calibration and executable expected-net gates before any
BUY-vs-SELL arbitration occurs. A stronger but ineligible side must never mask a
weaker eligible side. WAIT remains a first-class action.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Limits:
    min_correct: float = .80
    max_wrong: float = .20
    min_margin: float = .08
    min_expected_net: float = 0.
    max_spread: float = 1.50
    min_n_calibration: int = 150
    min_opportunity: float = .80

@dataclass(frozen=True)
class Prediction:
    side: int
    p_correct: float
    p_incorrect: float
    p_neutral: float
    expected_net: float
    hawkes_edge: float = 0.

@dataclass(frozen=True)
class OpportunityPrediction:
    p_any_tradeable: float

def _prediction_base_eligible(p: Prediction, threshold: float, limits: Limits) -> bool:
    """Per-side eligibility. No comparison with the opposite side belongs here."""
    vals = (p.p_correct, p.p_incorrect, p.p_neutral, p.expected_net, threshold)
    if not np.isfinite(vals).all():
        return False
    return bool(
        p.p_correct >= limits.min_correct
        and p.p_correct > threshold
        and p.p_incorrect <= limits.max_wrong
        and p.expected_net > limits.min_expected_net
    )

class DualActionPolicy:
    def __init__(self, buy_threshold=1., sell_threshold=1., limits=Limits()):
        self.thresholds = {1: float(buy_threshold), -1: float(sell_threshold)}
        self.limits = limits

    def decide(self, buy: Prediction, sell: Prediction, spread: float):
        if buy.side != 1 or sell.side != -1:
            raise ValueError('independent BUY+SELL required')
        if not np.isfinite(spread) or spread > self.limits.max_spread:
            return 0, 'SPREAD'
        eligible = [
            p for p in (buy, sell)
            if _prediction_base_eligible(p, self.thresholds[p.side], self.limits)
        ]
        if not eligible:
            return 0, 'NO_ELIGIBLE_SIDE'
        if len(eligible) == 1:
            winner = eligible[0]
            return winner.side, 'BUY' if winner.side == 1 else 'SELL'
        if abs(buy.p_correct - sell.p_correct) < self.limits.min_margin:
            return 0, 'AMBIGUOUS_DUAL_SIGNAL'
        winner = max(eligible, key=lambda p: (p.expected_net, p.p_correct))
        return winner.side, 'BUY' if winner.side == 1 else 'SELL'

class AsymmetricEntryPolicy:
    """Separate opportunity timing from direction selection."""
    def __init__(self, buy_threshold=1., sell_threshold=1., opportunity_threshold=1., limits=Limits()):
        self.direction = DualActionPolicy(buy_threshold, sell_threshold, limits)
        self.opportunity_threshold = float(opportunity_threshold)
        self.limits = limits

    def decide(self, opportunity: OpportunityPrediction, buy: Prediction, sell: Prediction, spread: float):
        p = float(opportunity.p_any_tradeable)
        if not np.isfinite(p):
            return 0, 'INVALID_OPPORTUNITY'
        if p < self.limits.min_opportunity or p <= self.opportunity_threshold:
            return 0, 'WAIT_NO_OPPORTUNITY'
        return self.direction.decide(buy, sell, spread)

def calibrate_np(scores, y, alpha=.10, min_bad=150):
    """Side-specific empirical bad-entry cutoff, calibration ONLY."""
    bad = np.asarray(scores)[np.asarray(y) != 2]
    if len(bad) < min_bad:
        return float('inf'), dict(status='FAIL_CLOSED', bad_n=len(bad))
    bad = np.sort(bad)
    index = min(len(bad)-1, int(np.ceil((1-alpha)*len(bad))))
    return float(bad[index]), dict(
        status='CALIBRATED_RESEARCH_ONLY', bad_n=len(bad), alpha=alpha,
        observed_exceedance=float(np.mean(bad > bad[index]))
    )

def calibrate_binary_np(scores, positive, alpha=.10, min_bad=150):
    """Direction-neutral opportunity cutoff from calibration chronology only."""
    scores = np.asarray(scores, dtype=np.float64)
    positive = np.asarray(positive, dtype=bool)
    bad = scores[~positive]
    if len(bad) < min_bad:
        return float('inf'), dict(status='FAIL_CLOSED', bad_n=len(bad))
    bad = np.sort(bad)
    index = min(len(bad)-1, int(np.ceil((1-alpha)*len(bad))))
    return float(bad[index]), dict(
        status='CALIBRATED_RESEARCH_ONLY', bad_n=len(bad), alpha=alpha,
        observed_exceedance=float(np.mean(bad > bad[index]))
    )

def select_dual(p, net, alpha_cutoff, limits=Limits()):
    """Vectorized eligibility-first BUY/SELL/WAIT selection."""
    p = np.asarray(p)
    net = np.asarray(net)
    assert p.ndim == 3 and p.shape[1:] == (2, 3)
    assert net.shape == p.shape[:2]
    cutoff = np.asarray(alpha_cutoff, dtype=np.float64)
    if cutoff.shape != (2,):
        raise ValueError('two side-specific cutoffs required')
    prob = p[:, :, 2]
    bad = p[:, :, 0]
    eligible = (
        np.isfinite(prob) & np.isfinite(bad) & np.isfinite(net)
        & (prob >= limits.min_correct)
        & (bad <= limits.max_wrong)
        & (net > limits.min_expected_net)
        & (prob > cutoff.reshape(1, 2))
    )
    count = eligible.sum(axis=1)
    out = np.zeros(len(p), dtype=np.int8)
    only_buy = eligible[:, 0] & ~eligible[:, 1]
    only_sell = eligible[:, 1] & ~eligible[:, 0]
    out[only_buy] = 1
    out[only_sell] = -1
    both = count == 2
    if np.any(both):
        clear = both & (np.abs(prob[:, 0] - prob[:, 1]) >= limits.min_margin)
        rows = np.where(clear)[0]
        for i in rows:
            if net[i, 0] > net[i, 1]:
                out[i] = 1
            elif net[i, 1] > net[i, 0]:
                out[i] = -1
            else:
                out[i] = 1 if prob[i, 0] >= prob[i, 1] else -1
    return out
