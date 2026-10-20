"""R00-054 F15: additive teacher-independent, event-time causal opportunity veto.

Never alter R00-054 event timestamps or original direction.
A historical label is usable at decision t only when its original source event
time is <= t-33000ms, so its observed +30..32-second quote midpoint outcome
has fully matured. The current event's future label is never an input.
This produces a *candidate* permit flag, not an MT5 order or guarantee.
"""
from __future__ import annotations
import numpy as np

def keep_from_matured_history(t_ms: np.ndarray, prior_event_label: np.ndarray) -> np.ndarray:
    """0=correct, 1=opposite, 2=neutral/missing.
    Consecutive event arrays must be chronological and from one broker source.
    Readout permits original candidate only if last two already matured
    historical outcomes were non-neutral (class 0 or 1).
    """
    t = np.asarray(t_ms, dtype=np.int64)
    y = np.asarray(prior_event_label, dtype=np.int8)
    if t.ndim != 1 or y.ndim != 1 or len(t) != len(y):
        raise ValueError("Expected aligned, one-dimensional original event arrays")
    if np.any(np.diff(t) < 0):
        raise ValueError("Original event time order changed")
    latest_matured = np.searchsorted(t, t - 33000, side="right") - 1
    j = np.maximum(latest_matured, 0)
    p = np.maximum(latest_matured - 1, 0)
    return (latest_matured >= 1) & (y[j] != 2) & (y[p] != 2)

def check_no_future_mutation() -> None:
    t = np.arange(100, dtype=np.int64) * 5000
    y = np.full(100, 2, dtype=np.int8)
    for i in (1, 10, 50):
        y.fill(2)
        y[i-1] = 0
        old = keep_from_matured_history(t, y)
        changed = y.copy()
        changed[i] = 0
        new = keep_from_matured_history(t, changed)
        assert np.array_equal(old[:i+7], new[:i+7])
        assert np.any(old[i+7:] != new[i+7:])

if __name__ == "__main__":
    check_no_future_mutation()
    print("F15 causal +33-second maturation invariant: PASS")
