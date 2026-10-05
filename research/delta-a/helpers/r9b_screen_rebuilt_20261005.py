from pathlib import Path
import numpy as np
import pandas as pd

RAW_BY_MONTH = {
    1: Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'),
}

def session_for_sec(sec: int) -> int:
    lon_off = 60 if (sec >= 1774746000 and sec < 1792890000) else 0
    ny_off = -240 if (sec >= 1772953200 and sec < 1793512800) else -300
    lm = ((int(sec) + lon_off * 60) % 86400) // 60
    nm = ((int(sec) + ny_off * 60) % 86400) // 60
    london = lm >= 480 and lm < 990
    ny = nm >= 480 and nm < 1020
    if london and ny: return 2
    if london: return 1
    if ny: return 3
    return 0

def load_ticks(month: int):
    p = RAW_BY_MONTH[int(month)]
    d = pd.read_csv(
        p, compression='gzip',
        usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
        dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'}
    )
    t = d.timestamp_ms_utc.to_numpy(np.int64, copy=False)
    ask = d.ask_raw.to_numpy(np.float64, copy=False) / 1000.0
    bid = d.bid_raw.to_numpy(np.float64, copy=False) / 1000.0
    return t, (ask + bid) * 0.5

def active_seconds(t, price):
    sec = t // 1000
    ch = np.empty(len(sec), dtype=bool); ch[0] = True; ch[1:] = sec[1:] != sec[:-1]
    ix = np.flatnonzero(ch); last = np.r_[ix[1:] - 1, len(sec) - 1]
    return sec[ix].astype(np.int64), t[ix].astype(np.int64), price[ix].astype(np.float64), np.maximum.reduceat(price, ix).astype(np.float64), np.minimum.reduceat(price, ix).astype(np.float64), price[last].astype(np.float64), ix.astype(np.int64), last.astype(np.int64)

def aggregate_tf_from_ticks(t, mid, tf_sec: int):
    bucket = t // (int(tf_sec) * 1000)
    ch = np.empty(len(bucket), dtype=bool); ch[0] = True; ch[1:] = bucket[1:] != bucket[:-1]
    ix = np.flatnonzero(ch); last = np.r_[ix[1:] - 1, len(bucket) - 1]
    ids = bucket[ix]; c = mid[last]; h = np.maximum.reduceat(mid, ix); l = np.minimum.reduceat(mid, ix)
    end = (ids + 1) * int(tf_sec); prev = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h-l, np.maximum(np.abs(h-prev), np.abs(l-prev)))
    atr = np.full(len(tr), np.nan, dtype=np.float64); e = np.nan
    for i, x in enumerate(tr):
        if not np.isfinite(x): continue
        e = x if not np.isfinite(e) else (13.0/14.0)*e + (1.0/14.0)*x
        if i >= 13: atr[i] = e
    return end.astype(np.int64), np.r_[np.nan, np.diff(c)].astype(np.float64), atr

def map_completed(sec_ids, end, values):
    j = np.searchsorted(end, sec_ids, side='right') - 1
    out = np.full(len(sec_ids), np.nan, dtype=np.float64)
    ok = j >= 0; out[ok] = values[j[ok]]
    return out

def build_s1_quality(sec_ids, high, low, close, lookback=10):
    N = len(sec_ids)
    disp = np.full(N, np.nan); eff = np.full(N, np.nan); rng = np.full(N, np.nan); turns = np.full(N, 99.0)
    L = int(lookback)
    for i in range(L, N):
        w = close[i-L+1:i+1]; d = np.diff(w); travel = np.abs(d).sum()
        disp[i] = w[-1] - w[0]; eff[i] = abs(disp[i]) / (travel + 1e-12)
        rng[i] = high[i-L+1:i+1].max() - low[i-L+1:i+1].min()
        nz = np.sign(d); nz = nz[nz != 0]
        turns[i] = np.sum(nz[1:] != nz[:-1]) if len(nz) > 1 else 0
    return disp, eff, rng, turns

def build_features(t, mid):
    sec_ids, first_t, o, h, l, c, first_ix, last_ix = active_seconds(t, mid)
    sd, se, sr, st = build_s1_quality(sec_ids, h, l, c, 10)
    e5, _, a5 = aggregate_tf_from_ticks(t, mid, 300)
    atrsec = map_completed(sec_ids, e5, a5)
    return {'sec_ids':sec_ids,'sec_open':o,'sec_high':h,'sec_low':l,'sec_close':c,'sec_first_ix':first_ix,'sec_last_ix':last_ix,'s1_disp':sd,'s1_eff':se,'s1_rng':sr,'s1_turns':st,'atrsec':atrsec}
