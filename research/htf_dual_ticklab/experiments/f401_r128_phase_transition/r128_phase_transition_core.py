"""R128 strictly-as-of-t0 frozen phase transition feature adapter.

This is a source-published state adapter, NOT a trading filter or original
F395 source replacement. Phase IDs must be computed by the frozen R120
quote-native 24 micro / 12 completed-HTF unsupervised codebooks.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def last_change_age(t, state):
    n = len(t)
    age = np.empty(n, np.float32)
    dwell = np.empty(n, np.float32)
    changed = np.zeros(n, np.int8)
    last_switch = t[0]
    prior = 0.0
    i = 0
    while i < n:
        j = i + 1
        while j < n and t[j] == t[i]:
            j += 1
        previous = state[i - 1] if i > 0 else state[i]
        any_change = False
        for k in range(i, j):
            if i > 0 and state[k] != previous:
                changed[k] = 1
                age[k] = 0.0
                dwell[k] = min(3600., (t[i] - last_switch) / 1000.)
                any_change = True
            else:
                age[k] = min(3600., (t[i] - last_switch) / 1000.)
                dwell[k] = prior
        if any_change:
            prior = min(3600., (t[i] - last_switch) / 1000.)
            last_switch = t[i]
        i = j
    return age, dwell, changed

def phase_transition_features(t, side, micro, product):
    """Compute event-state features without truth or teacher-score inputs.

    All lagged state references use strictly earlier timestamps.
    R120's state at the current t0 already excludes quotes at/after t0.
    """
    t = np.asarray(t, dtype=np.int64)
    side = np.asarray(side, dtype=np.int8)
    micro = np.asarray(micro, dtype=np.int16)
    product = np.asarray(product, dtype=np.uint16)
    assert len(t) == len(side) == len(micro) == len(product)
    assert np.all(t[1:] >= t[:-1])
    assert np.array_equal(product // 12, micro)
    macro = (product % 12).astype(np.int16)
    prev = np.searchsorted(t, t, side="left") - 1
    old = np.maximum(prev, 0)
    result = {
        "side": side.astype(np.float32),
        "micro_phase": micro.astype(np.float32),
        "htf_phase": macro.astype(np.float32),
        "product_phase": product.astype(np.float32),
    }
    for name, state, windows in (
        ("micro", micro, (15, 60)),
        ("htf", macro, (60, 300)),
        ("product", product, (15, 60)),
    ):
        age, dwell, changed = last_change_age(t, state)
        result[f"{name}_age_s"] = age
        result[f"{name}_last_dwell_s"] = dwell
        result[f"{name}_changed"] = changed
        result[f"prev_{name}"] = np.where(prev >= 0, state[old], -1)
        cum = np.cumsum(changed.astype(np.int32))
        churn_windows = (300,) if name == "htf" else (30, 300)
        for seconds in sorted(set(windows) | set(churn_windows)):
            j = np.searchsorted(t, t - seconds * 1000, side="left")
            if seconds in windows:
                lag = j - 1
                result[f"{name}_lag_{seconds}s"] = np.where(
                    lag >= 0, state[np.maximum(lag, 0)], -1
                )
            if seconds in churn_windows:
                before = np.where(j > 0, cum[np.maximum(j - 1, 0)], 0)
                prior = np.where(prev >= 0, cum[old], 0)
                result[f"{name}_churn_{seconds}s"] = prior - before
    return result
