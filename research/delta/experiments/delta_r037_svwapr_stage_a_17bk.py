"""DELTA R037 Session VWAP Pullback Reclaim Stage-A screen — Checkpoint 17BK.

Fixed preregistration:
- session-reset VWAP using completed native-mid M1/M5 bars;
- typical price=(H+L+C)/3, bar tick count as volume proxy;
- cumulative volume-weighted sigma;
- arm beyond +/-1 sigma with same-direction VWAP slope;
- first subsequent VWAP interaction consumes the event;
- confirm only when open/close remain trend-side, candle closes in trend direction,
  and VWAP slope remains trend-side;
- fresh excursion required to rearm after consumption;
- at most one executed trade per side per session;
- frozen DELTA P75 30-second execution.

Research only. No post-result tuning. August is not accessed. MQL5 is not authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

DAY = 86_400_000
HOUR = 3_600_000
TICK = 10
SCALE = 1000
END = 1_768_737_600_000
US_DST = 1_772_953_200_000
UK_DST = 1_774_746_000_000
P75_POINTS = np.asarray([20, 20, 21, 21], np.int64)
CANONICAL_SHA = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT = "464a536e3fe7b5249877218e628fc2f047a6a4ce"
MAX_SPREAD = 250
STOP = 300
TRAIL_ACT = 100
TRAIL_DIST = 30
MAX_HOLD = 30

PROFILES = (
    ("17BK_C01_LONDON_M1_FIRST_TOUCH_RECLAIM", "LONDON", 60_000),
    ("17BK_C02_NEWYORK_M1_FIRST_TOUCH_RECLAIM", "NEW_YORK", 60_000),
    ("17BK_C03_LONDON_M5_FIRST_TOUCH_RECLAIM", "LONDON", 300_000),
    ("17BK_C04_NEWYORK_M5_FIRST_TOUCH_RECLAIM", "NEW_YORK", 300_000),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_name = tmp.name
            json.dump(payload, tmp, indent=2)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def session_code(t: np.ndarray) -> np.ndarray:
    tod = t % DAY
    london_start = np.where(t >= UK_DST, 7, 8) * HOUR
    london_end = london_start + 30_600_000
    ny_start = np.where(t >= US_DST, 12, 13) * HOUR
    ny_end = ny_start + 32_400_000
    in_london = (tod >= london_start) & (tod < london_end)
    in_ny = (tod >= ny_start) & (tod < ny_end)
    return np.where(in_london & in_ny, 2, np.where(in_london, 1, np.where(in_ny, 3, 0))).astype(np.int8)


def p75_surface(t: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray):
    spread = P75_POINTS[session_code(t)] * TICK
    mid2 = ask_raw.astype(np.int64) + bid_raw.astype(np.int64)
    bid = ((mid2 - spread + TICK) // (2 * TICK)) * TICK
    ask = bid + spread
    return ask.astype(np.int64), bid.astype(np.int64)


def make_bars(t: np.ndarray, mid: np.ndarray, tf_ms: int):
    bucket = t // tf_ms
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:], len(t)]
    return {
        "end_ms": ((bucket[starts] + 1) * tf_ms).astype(np.int64),
        "open": mid[starts].astype(np.int64),
        "high": np.maximum.reduceat(mid, starts).astype(np.int64),
        "low": np.minimum.reduceat(mid, starts).astype(np.int64),
        "close": mid[ends - 1].astype(np.int64),
        "ticks": (ends - starts).astype(np.int64),
    }


def tick_at_or_after(t: np.ndarray, tm: int) -> int:
    j = int(np.searchsorted(t, int(tm), side="left"))
    return j if j < len(t) else -1


def session_bounds(day_ms: int, session_name: str, ref_ms: int):
    if session_name == "LONDON":
        open_hour = 7 if ref_ms >= UK_DST else 8
        start = day_ms + open_hour * HOUR
        end = start + 30_600_000
    elif session_name == "NEW_YORK":
        open_hour = 12 if ref_ms >= US_DST else 13
        start = day_ms + open_hour * HOUR
        end = start + 32_400_000
    else:
        raise ValueError(session_name)
    return int(start), int(end)


def svwap_signals(t: np.ndarray, b: dict, session_name: str):
    e = b["end_ms"]
    o = b["open"].astype(np.float64)
    h = b["high"].astype(np.float64)
    l = b["low"].astype(np.float64)
    c = b["close"].astype(np.float64)
    vol = b["ticks"].astype(np.float64)

    sig_idx = []
    sig_side = []
    sig_day = []
    diagnostics = {
        "session_days": 0,
        "bars_in_session": 0,
        "arm_long": 0,
        "arm_short": 0,
        "interaction_long": 0,
        "interaction_short": 0,
        "confirmed_long": 0,
        "confirmed_short": 0,
        "failed_first_touch_long": 0,
        "failed_first_touch_short": 0,
    }

    if len(e) == 0:
        return np.empty(0, np.int64), np.empty(0, np.int8), np.empty(0, np.int64), diagnostics

    first_day = int((e[0] - 1) // DAY)
    last_day = int((e[-1] - 1) // DAY)

    for day in range(first_day, last_day + 1):
        day_ms = day * DAY
        start, end = session_bounds(day_ms, session_name, day_ms)
        lo = int(np.searchsorted(e, start, side="right"))
        hi = int(np.searchsorted(e, end, side="right"))
        if hi <= lo:
            continue
        diagnostics["session_days"] += 1
        diagnostics["bars_in_session"] += hi - lo

        sum_v = 0.0
        sum_pv = 0.0
        sum_p2v = 0.0
        prev_vwap = np.nan
        armed_long = False
        armed_short = False
        arm_long_at = -1
        arm_short_at = -1

        for i in range(lo, hi):
            tp = (h[i] + l[i] + c[i]) / 3.0
            vv = vol[i]
            sum_v += vv
            sum_pv += tp * vv
            sum_p2v += tp * tp * vv
            if sum_v <= 0:
                continue
            vwap = sum_pv / sum_v
            var = max(0.0, sum_p2v / sum_v - vwap * vwap)
            sigma = var ** 0.5
            slope = 0.0 if np.isnan(prev_vwap) else vwap - prev_vwap

            if armed_long and i > arm_long_at and l[i] <= vwap:
                diagnostics["interaction_long"] += 1
                confirm = o[i] > vwap and c[i] > vwap and c[i] > o[i] and slope > 0
                armed_long = False
                arm_long_at = -1
                if confirm:
                    j = tick_at_or_after(t, int(e[i]))
                    if j >= 0:
                        sig_idx.append(j)
                        sig_side.append(1)
                        sig_day.append(day)
                        diagnostics["confirmed_long"] += 1
                else:
                    diagnostics["failed_first_touch_long"] += 1

            if armed_short and i > arm_short_at and h[i] >= vwap:
                diagnostics["interaction_short"] += 1
                confirm = o[i] < vwap and c[i] < vwap and c[i] < o[i] and slope < 0
                armed_short = False
                arm_short_at = -1
                if confirm:
                    j = tick_at_or_after(t, int(e[i]))
                    if j >= 0:
                        sig_idx.append(j)
                        sig_side.append(-1)
                        sig_day.append(day)
                        diagnostics["confirmed_short"] += 1
                else:
                    diagnostics["failed_first_touch_short"] += 1

            if sigma > 0 and slope > 0 and not armed_long and c[i] >= vwap + sigma:
                armed_long = True
                arm_long_at = i
                diagnostics["arm_long"] += 1
            if sigma > 0 and slope < 0 and not armed_short and c[i] <= vwap - sigma:
                armed_short = True
                arm_short_at = i
                diagnostics["arm_short"] += 1

            prev_vwap = vwap

    if not sig_idx:
        return np.empty(0, np.int64), np.empty(0, np.int8), np.empty(0, np.int64), diagnostics

    idx = np.asarray(sig_idx, np.int64)
    side = np.asarray(sig_side, np.int8)
    days = np.asarray(sig_day, np.int64)
    order = np.argsort(idx, kind="stable")
    return idx[order], side[order], days[order], diagnostics


@njit(cache=True)
def quote_tick(x):
    return ((int(x) + 5) // 10) * 10


@njit(cache=True)
def evaluate(idx, side, sig_day, t, ask, bid):
    busy_until = -1
    trades = busy_skips = spread_rejects = session_limit_skips = 0
    longs = shorts = wins = stop_exits = hold_exits = end_exits = 0
    gp = gl = net = 0.0
    trade_days = np.empty(idx.size, np.int64)
    ndn = 0
    last_long_day = -10**12
    last_short_day = -10**12

    for z in range(idx.size):
        i = int(idx[z])
        s = int(side[z])
        day = int(sig_day[z])

        if i <= busy_until:
            busy_skips += 1
            continue
        if s > 0 and day == last_long_day:
            session_limit_skips += 1
            continue
        if s < 0 and day == last_short_day:
            session_limit_skips += 1
            continue
        if int(ask[i] - bid[i]) > MAX_SPREAD:
            spread_rejects += 1
            continue

        trades += 1
        if s > 0:
            longs += 1
            last_long_day = day
        else:
            shorts += 1
            last_short_day = day
        trade_days[ndn] = day
        ndn += 1

        entry = int(ask[i]) if s > 0 else int(bid[i])
        stop = quote_tick(int(bid[i]) - STOP if s > 0 else int(ask[i]) + STOP)
        sec0 = int(t[i]) // 1000
        raw = 0.0
        reason = 2
        last = i

        for k in range(i + 1, t.size):
            aa = int(ask[k])
            bb = int(bid[k])
            sec = int(t[k]) // 1000
            last = k
            if s > 0 and bb <= stop:
                raw = (bb - entry) / SCALE
                reason = 0
                break
            if s < 0 and aa >= stop:
                raw = (entry - aa) / SCALE
                reason = 0
                break
            if sec - sec0 >= MAX_HOLD:
                raw = ((bb - entry) if s > 0 else (entry - aa)) / SCALE
                reason = 1
                break
            fav = (bb - entry) if s > 0 else (entry - aa)
            if fav >= TRAIL_ACT:
                new_stop = quote_tick(bb - TRAIL_DIST if s > 0 else aa + TRAIL_DIST)
                if (s > 0 and new_stop > stop) or (s < 0 and new_stop < stop):
                    stop = new_stop
        else:
            aa = int(ask[last])
            bb = int(bid[last])
            raw = ((bb - entry) if s > 0 else (entry - aa)) / SCALE

        exit_after_commission = raw - 0.01
        net += exit_after_commission - 0.01
        wins += exit_after_commission > 1e-12
        if raw > 0:
            gp += exit_after_commission
        else:
            gl += exit_after_commission
        if reason == 0:
            stop_exits += 1
        elif reason == 1:
            hold_exits += 1
        else:
            end_exits += 1
        busy_until = last

    distinct_days = 0
    if ndn:
        x = np.sort(trade_days[:ndn])
        distinct_days = 1
        for k in range(1, x.size):
            distinct_days += x[k] != x[k - 1]

    return trades, busy_skips, spread_rejects, session_limit_skips, distinct_days, longs, shorts, wins, gp, gl, net, stop_exits, hold_exits, end_exits


def metrics(idx, side, sig_day, t, ask, bid):
    tr, bs, sr, sls, nd, lg, sh, w, gp, gl, net, st, mh, en = evaluate(idx, side, sig_day, t, ask, bid)
    m = {
        "signals": int(idx.size),
        "busy_skips": int(bs),
        "spread_rejects": int(sr),
        "session_limit_skips": int(sls),
        "trades": int(tr),
        "distinct_days": int(nd),
        "long": int(lg),
        "short": int(sh),
        "official_wins": int(w),
        "gross_profit": round(float(gp), 2),
        "gross_loss": round(float(gl), 2),
        "direct_net_usd": round(float(net), 2),
        "exit_reasons": {"STOP": int(st), "MAX_HOLD": int(mh), "END": int(en)},
    }
    g = {
        "minimum_trades_20": tr >= 20,
        "minimum_distinct_days_5": nd >= 5,
        "direct_net_min_minus_1": m["direct_net_usd"] >= -1.0,
        "nonnegative_direct_net": m["direct_net_usd"] >= 0.0,
    }
    g["screen_pass"] = bool(g["minimum_trades_20"] and g["minimum_distinct_days_5"] and g["nonnegative_direct_net"])
    return m, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source_sha = sha256_file(args.source)
    if source_sha != CANONICAL_SHA:
        raise SystemExit("canonical January SHA mismatch: " + source_sha)

    d = pd.read_csv(args.source, compression="gzip", usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"], dtype=np.int64)
    d = d[d.timestamp_ms_utc < END]
    t = d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t) != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit("Stage-A chronology/tick mismatch")

    ask_raw = d.ask_raw.to_numpy(np.int64)
    bid_raw = d.bid_raw.to_numpy(np.int64)
    native_mid = (ask_raw + bid_raw) // 2
    exec_ask, exec_bid = p75_surface(t, ask_raw, bid_raw)

    bars_by_tf = {
        60_000: make_bars(t, native_mid, 60_000),
        300_000: make_bars(t, native_mid, 300_000),
    }

    configs = {}
    survivors = []
    for name, session_name, tf_ms in PROFILES:
        idx, side, sig_day, diag = svwap_signals(t, bars_by_tf[tf_ms], session_name)
        m, g = metrics(idx, side, sig_day, t, exec_ask, exec_bid)
        configs[name] = {"session": session_name, "timeframe_ms": int(tf_ms), "metrics": m, "gate": g, "event_diagnostics": diag}
        if g["screen_pass"]:
            survivors.append(name)

    decision = "ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "RETIRE_SVWAPR_NO_STAGE_A_SURVIVOR"
    next_unit = "R037_SVWAPR_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"
    out = {
        "schema": "delta-r037-svwapr-stage-a-screen-17bk-v1",
        "status": "COMPLETE_FAST_CAUSAL_PRESCREEN",
        "unit": "R037_SVWAPR_STAGE_A_SCREEN_CHECKPOINT_17BK",
        "parent_checkpoint": "R037_CONTINUATION_FAST_HARVEST_CHECKPOINT_17BH_17BJ",
        "prereg_commit": PREREG_COMMIT,
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "signal_surface": "NATIVE_DUKAS_COMPLETED_BAR_MID",
        "execution_surface": "DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning": False,
        "august_accessed": False,
        "feature_definition": {
            "typical_price": "(high+low+close)/3",
            "volume": "completed-bar tick count",
            "vwap": "session cumulative sum(typical_price*volume)/sum(volume)",
            "sigma": "sqrt(sum(typical_price^2*volume)/sum(volume)-VWAP^2)",
            "arm": "close beyond +/-1 sigma with same-direction VWAP slope",
            "trigger": "first subsequent VWAP interaction; confirm same-side open/close plus directional body and slope",
            "consumption": "first interaction consumes event whether confirm or fail",
            "rearm": "fresh +/-1 sigma completed-bar excursion required",
            "session_limit": "at most one executed trade per side per session",
        },
        "configs": configs,
        "finding": {"survivors": survivors, "decision": decision, "next": next_unit},
        "mql5_authorized": False,
    }
    atomic_json(args.output, out)
    print(json.dumps({
        "configs": {k: {
            "signals": v["metrics"]["signals"],
            "trades": v["metrics"]["trades"],
            "days": v["metrics"]["distinct_days"],
            "wins": v["metrics"]["official_wins"],
            "net": v["metrics"]["direct_net_usd"],
            "pass": v["gate"]["screen_pass"],
        } for k, v in configs.items()},
        "finding": out["finding"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
