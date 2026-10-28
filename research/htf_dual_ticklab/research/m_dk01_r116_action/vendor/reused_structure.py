"""Verbatim structure function from R110-DIST run.py; source pin recorded."""
import numpy as np

def structure(tm, mid, et, idx, side, scale):
    """New multi-bar transform. Only strictly completed contiguous bars enter."""
    columns, names = [], []
    for width in (60000, 300000, 900000, 3600000):
        bucket = tm // width
        starts = np.r_[0, np.flatnonzero(np.diff(bucket)) + 1]
        ends = np.r_[starts[1:], len(tm)]
        keys = bucket[starts]
        op, cl = mid[starts], mid[ends - 1]
        high = np.maximum.reduceat(mid, starts)
        low = np.minimum.reduceat(mid, starts)
        last = np.searchsorted(keys, et // width, side='left') - 1
        for n in (3, 5, 9):
            valid = last >= n - 1
            ix = np.maximum(last[:, None] - np.arange(n), 0)
            valid &= (keys[ix[:, 0]] - keys[ix[:, -1]] == n - 1)
            valid &= keys[ix[:, 0]] == et // width - 1
            hi, lo = high[ix].max(axis=1), low[ix].min(axis=1)
            span = np.maximum(hi - lo, .05)
            bodies = cl[ix] - op[ix]
            lastclose = cl[ix[:, 0]]
            vals = np.column_stack((
                side * (lastclose - op[ix[:, -1]]) / span,
                np.abs(bodies).sum(axis=1) / span,
                side * (mid[idx] - hi) / span,
                side * (mid[idx] - lo) / span,
                side * (mid[idx] - lastclose) / scale,
                np.mean(np.sign(bodies) * side[:, None], axis=1),
                np.log1p(span / scale),
                ((mid[idx] - lo) / np.maximum(.1, span / n)) % 1,
                valid.astype(float),
            ))
            vals[~valid, :8] = 0
            columns.append(vals.astype('float32'))
            names.extend(f'structure_{width}_{n}_{j}' for j in range(9))
    return np.column_stack(columns), names
