# BETA064-R1B1 research harness excerpt
# Reconstructs completed-H4 P5 structural entry and regime-conditioned failed-ignition HOLD.
# Requires beta064_01_1s.pkl ... beta064_07_1s.pkl causal screening caches.
# Research only. August intentionally excluded.

import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache

ROOT = Path("/mnt/data")
FEE = 0.02
FAIL_AGE_SECONDS = 3600
FAIL_MFE_ATR = 0.10
FAIL_VR_MAX = 1.20

@lru_cache(maxsize=2)
def load_month(month):
    return pd.read_pickle(ROOT / f"beta064_{month:02d}_1s.pkl")

def h4_signals():
    bars = []
    for month in range(1, 8):
        d = load_month(month)
        bars.append(pd.DataFrame({
            "high": d.high_mid.resample("4h").max(),
            "low": d.low_mid.resample("4h").min(),
            "close": d.mid.resample("4h").last(),
        }).dropna())
    b = pd.concat(bars).sort_index()
    prev = b.close.shift(1)
    tr = pd.concat([(b.high-b.low), (b.high-prev).abs(), (b.low-prev).abs()], axis=1).max(axis=1)
    b["atr"] = tr.rolling(14, min_periods=14).mean()
    b["atr_mean20"] = b.atr.shift(1).rolling(20, min_periods=20).mean()
    b["vr"] = b.atr / b.atr_mean20
    b["prior_high"] = b.high.shift(1).rolling(6, min_periods=6).max()
    b["prior_low"] = b.low.shift(1).rolling(6, min_periods=6).min()
    b["side"] = np.where(
        (b.close > b.prior_high) & (b.vr <= 2.0), 1,
        np.where((b.close < b.prior_low) & (b.vr <= 2.0), -1, 0)
    )
    return [(t + pd.Timedelta(hours=4), int(r.side), float(r.atr), float(r.vr))
            for t, r in b.iterrows() if r.side and np.isfinite(r.atr)]

def get_path(start, end):
    parts = []
    for month in range(start.month, min(end.month, 7)+1):
        d = load_month(month)
        lo, hi = max(start, d.index[0]), min(end, d.index[-1])
        if lo <= hi:
            parts.append(d.loc[lo:hi])
    if not parts:
        return None
    return pd.concat(parts) if len(parts) > 1 else parts[0]

def replay(use_hold_specialist=True):
    last_exit = pd.Timestamp("1900-01-01", tz="UTC")
    rows = []
    for entry_time, side, atr, vr in h4_signals():
        if entry_time < last_exit or entry_time.month > 7:
            continue
        d = load_month(entry_time.month)
        if entry_time not in d.index:
            continue

        entry = float(d.at[entry_time, "ask" if side > 0 else "bid"])
        hard_stop = entry - side * 1.5 * atr
        end = min(entry_time + pd.Timedelta(hours=24),
                  pd.Timestamp("2026-08-01", tz="UTC") - pd.Timedelta(seconds=1))
        path = get_path(entry_time, end)
        if path is None or len(path) < 2:
            continue

        prices = (path.bid if side > 0 else path.ask).to_numpy(float)
        times = path.index
        favorable = (prices-entry)*side
        mfe = np.maximum.accumulate(favorable)
        armed = mfe >= 0.25*atr

        if side > 0:
            peak = np.maximum.accumulate(prices)
            active_stop = np.where(armed, np.maximum(hard_stop, peak-atr), hard_stop)
            stop_hit = prices <= active_stop
        else:
            peak = np.minimum.accumulate(prices)
            active_stop = np.where(armed, np.minimum(hard_stop, peak+atr), hard_stop)
            stop_hit = prices >= active_stop
        stop_hit[0] = False

        fail = np.zeros(len(prices), dtype=bool)
        if use_hold_specialist and vr <= FAIL_VR_MAX:
            age = (times-times[0]).total_seconds().to_numpy()
            fail = (age >= FAIL_AGE_SECONDS) & (mfe < FAIL_MFE_ATR*atr) & (favorable < 0)
            fail[0] = False

        hits = np.where(stop_hit | fail)[0]
        j = int(hits[0]) if len(hits) else len(prices)-1
        reason = "failed_ignition" if fail[j] and not stop_hit[j] else (
            "trail_or_hard_stop" if stop_hit[j] else "timeout"
        )
        exit_time = times[j]
        exit_price = float(prices[j])
        pnl = (exit_price-entry)*side - FEE
        rows.append((entry_time, exit_time, side, atr, vr, entry, exit_price, pnl, reason))
        last_exit = exit_time

    out = pd.DataFrame(rows, columns=[
        "entry","exit","side","atr","vr","entry_px","exit_px","pnl","reason"
    ])
    out["month"] = out.entry.dt.month
    return out

if __name__ == "__main__":
    for label, enabled in [("baseline", False), ("r1b1", True)]:
        t = replay(enabled)
        gp = t.loc[t.pnl>0,"pnl"].sum()
        gl = -t.loc[t.pnl<0,"pnl"].sum()
        print(label, len(t), t.pnl.sum(), gp/gl if gl else float("inf"))
        print(t.groupby("month").pnl.sum())
