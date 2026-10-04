"""DELTA R037 previous-day Volume Profile failed-auction + CVD screen — 17BL–17BN.

Preregistered unit:
R037_PVACVD_FAILED_AUCTION_STAGE_A_SCREEN_CHECKPOINT_17BL_17BN

Profiles:
- 17BL C01: prior-day VAH/VAL failed auction on completed S5, price only.
- 17BM C02: same S5 event plus same-bar directional tick-delta sign.
- 17BN C03: completed M1 event plus same-bar directional tick-delta sign.

The profile uses the prior available UTC trading day only, exact frozen $0.01
midpoint price rows, tick count as volume, POC=max-volume row, and a 70% value
area expanded causally outward from POC. No row-size, VA%, delta threshold,
session, side, weekday, stop, trail, or hold tuning is permitted.

Research only. August is sealed. MQL5 is not authorized.
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
PREREG_COMMIT = "ef0f21e67d6c389024f88d60bd6768d1e2d3c191"

MAX_SPREAD = 250
STOP = 300
TRAIL_ACT = 100
TRAIL_DIST = 30
MAX_HOLD = 30

PROFILES = (
    ("17BL_C01_PVA_S5_PRICE_FAILED_AUCTION", 5_000, False),
    ("17BM_C02_PVA_S5_DELTA_FAILED_AUCTION", 5_000, True),
    ("17BN_C03_PVA_M1_DELTA_FAILED_AUCTION", 60_000, True),
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
    return np.where(
        in_london & in_ny,
        2,
        np.where(in_london, 1, np.where(in_ny, 3, 0)),
    ).astype(np.int8)


def p75_surface(t: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray):
    spread = P75_POINTS[session_code(t)] * TICK
    mid2 = ask_raw.astype(np.int64) + bid_raw.astype(np.int64)
    bid = ((mid2 - spread + TICK) // (2 * TICK)) * TICK
    ask = bid + spread
    return ask.astype(np.int64), bid.astype(np.int64)


def quantize_mid(ask_raw: np.ndarray, bid_raw: np.ndarray) -> np.ndarray:
    mid = (ask_raw.astype(np.int64) + bid_raw.astype(np.int64)) // 2
    return ((mid + TICK // 2) // TICK) * TICK


def tick_direction(mid: np.ndarray) -> np.ndarray:
    out = np.zeros(mid.size, dtype=np.int8)
    if mid.size > 1:
        d = mid[1:] - mid[:-1]
        out[1:] = np.where(d > 0, 1, np.where(d < 0, -1, 0)).astype(np.int8)
    return out


def make_bars(t: np.ndarray, mid: np.ndarray, tick_dir: np.ndarray, tf_ms: int):
    bucket = t // tf_ms
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:], len(t)]
    return {
        "end_ms": ((bucket[starts] + 1) * tf_ms).astype(np.int64),
        "open": mid[starts].astype(np.int64),
        "high": np.maximum.reduceat(mid, starts).astype(np.int64),
        "low": np.minimum.reduceat(mid, starts).astype(np.int64),
        "close": mid[ends - 1].astype(np.int64),
        "delta": np.add.reduceat(tick_dir.astype(np.int64), starts).astype(np.int64),
        "ticks": (ends - starts).astype(np.int64),
    }


def value_profile(levels: np.ndarray) -> tuple[int, int, int, int]:
    lo_price = int(levels.min())
    hi_price = int(levels.max())
    nrows = (hi_price - lo_price) // TICK + 1
    row = ((levels - lo_price) // TICK).astype(np.int64)
    counts = np.bincount(row, minlength=nrows).astype(np.int64)
    poc = int(np.argmax(counts))
    total = int(counts.sum())
    target = int(np.ceil(0.70 * total))
    included = int(counts[poc])
    lo = poc
    hi = poc
    while included < target and (lo > 0 or hi + 1 < nrows):
        below = int(counts[lo - 1]) if lo > 0 else -1
        above = int(counts[hi + 1]) if hi + 1 < nrows else -1
        if below >= above:
            if lo > 0:
                lo -= 1
                included += int(counts[lo])
            elif hi + 1 < nrows:
                hi += 1
                included += int(counts[hi])
        else:
            if hi + 1 < nrows:
                hi += 1
                included += int(counts[hi])
            elif lo > 0:
                lo -= 1
                included += int(counts[lo])
    poc_price = lo_price + poc * TICK
    val = lo_price + lo * TICK
    vah = lo_price + hi * TICK
    return int(poc_price), int(val), int(vah), total


def build_prior_day_profiles(t: np.ndarray, mid: np.ndarray) -> dict[int, dict]:
    days = t // DAY
    uniq, starts = np.unique(days, return_index=True)
    ends = np.r_[starts[1:], len(t)]
    profiles_by_day = {}
    day_profiles = {}
    for d, s, e in zip(uniq, starts, ends):
        poc, val, vah, total = value_profile(mid[s:e])
        day_profiles[int(d)] = {
            "poc": poc,
            "val": val,
            "vah": vah,
            "ticks": total,
        }
    ordered = [int(x) for x in uniq]
    for k in range(1, len(ordered)):
        profiles_by_day[ordered[k]] = {
            "source_day": ordered[k - 1],
            **day_profiles[ordered[k - 1]],
        }
    return profiles_by_day


def tick_at_or_after(t: np.ndarray, tm: int) -> int:
    j = int(np.searchsorted(t, int(tm), side="left"))
    return j if j < len(t) else -1


def failed_auction_signals(
    t: np.ndarray,
    b: dict,
    profiles: dict[int, dict],
    delta_required: bool,
):
    e = b["end_ms"]
    o = b["open"]
    h = b["high"]
    l = b["low"]
    c = b["close"]
    delta = b["delta"]

    idx = []
    side = []
    days = []
    diag = {
        "profile_days": 0,
        "bars_with_profile": 0,
        "short_price_events": 0,
        "long_price_events": 0,
        "short_delta_rejects": 0,
        "long_delta_rejects": 0,
        "short_signals": 0,
        "long_signals": 0,
        "short_rearms": 0,
        "long_rearms": 0,
    }

    current_day = -1
    short_armed = True
    long_armed = True
    counted_profile_day = False

    for i in range(len(e)):
        day = int((int(e[i]) - 1) // DAY)
        prof = profiles.get(day)
        if prof is None:
            continue

        if day != current_day:
            current_day = day
            short_armed = True
            long_armed = True
            counted_profile_day = False
        if not counted_profile_day:
            diag["profile_days"] += 1
            counted_profile_day = True

        diag["bars_with_profile"] += 1
        vah = int(prof["vah"])
        val = int(prof["val"])

        if not short_armed and int(h[i]) < vah:
            short_armed = True
            diag["short_rearms"] += 1
        if not long_armed and int(l[i]) > val:
            long_armed = True
            diag["long_rearms"] += 1

        if short_armed and int(h[i]) > vah and int(c[i]) < vah and int(c[i]) < int(o[i]):
            diag["short_price_events"] += 1
            short_armed = False
            if delta_required and int(delta[i]) >= 0:
                diag["short_delta_rejects"] += 1
            else:
                j = tick_at_or_after(t, int(e[i]))
                if j >= 0:
                    idx.append(j)
                    side.append(-1)
                    days.append(day)
                    diag["short_signals"] += 1

        if long_armed and int(l[i]) < val and int(c[i]) > val and int(c[i]) > int(o[i]):
            diag["long_price_events"] += 1
            long_armed = False
            if delta_required and int(delta[i]) <= 0:
                diag["long_delta_rejects"] += 1
            else:
                j = tick_at_or_after(t, int(e[i]))
                if j >= 0:
                    idx.append(j)
                    side.append(1)
                    days.append(day)
                    diag["long_signals"] += 1

    if not idx:
        return (
            np.empty(0, np.int64),
            np.empty(0, np.int8),
            np.empty(0, np.int64),
            diag,
        )

    idx = np.asarray(idx, np.int64)
    side = np.asarray(side, np.int8)
    days = np.asarray(days, np.int64)
    order = np.argsort(idx, kind="stable")
    return idx[order], side[order], days[order], diag


@njit(cache=True)
def quote_tick(x):
    return ((int(x) + 5) // 10) * 10


@njit(cache=True)
def evaluate(idx, side, sig_day, t, ask, bid):
    busy_until = -1
    trades = busy_skips = spread_rejects = 0
    longs = shorts = wins = stop_exits = hold_exits = end_exits = 0
    gp = gl = net = 0.0
    trade_days = np.empty(idx.size, np.int64)
    ndn = 0

    for z in range(idx.size):
        i = int(idx[z])
        s = int(side[z])
        day = int(sig_day[z])

        if i <= busy_until:
            busy_skips += 1
            continue
        if int(ask[i] - bid[i]) > MAX_SPREAD:
            spread_rejects += 1
            continue

        trades += 1
        longs += s > 0
        shorts += s < 0
        trade_days[ndn] = day
        ndn += 1

        entry = int(ask[i]) if s > 0 else int(bid[i])
        stop = quote_tick(
            int(bid[i]) - STOP if s > 0 else int(ask[i]) + STOP
        )
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
                raw = (
                    (bb - entry) if s > 0 else (entry - aa)
                ) / SCALE
                reason = 1
                break

            fav = (bb - entry) if s > 0 else (entry - aa)
            if fav >= TRAIL_ACT:
                new_stop = quote_tick(
                    bb - TRAIL_DIST if s > 0 else aa + TRAIL_DIST
                )
                if (
                    (s > 0 and new_stop > stop)
                    or (s < 0 and new_stop < stop)
                ):
                    stop = new_stop
        else:
            aa = int(ask[last])
            bb = int(bid[last])
            raw = (
                (bb - entry) if s > 0 else (entry - aa)
            ) / SCALE

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

    return (
        trades,
        busy_skips,
        spread_rejects,
        distinct_days,
        longs,
        shorts,
        wins,
        gp,
        gl,
        net,
        stop_exits,
        hold_exits,
        end_exits,
    )


def metrics(idx, side, sig_day, t, ask, bid):
    tr, bs, sr, nd, lg, sh, w, gp, gl, net, st, mh, en = evaluate(
        idx, side, sig_day, t, ask, bid
    )
    m = {
        "signals": int(idx.size),
        "busy_skips": int(bs),
        "spread_rejects": int(sr),
        "trades": int(tr),
        "distinct_days": int(nd),
        "long": int(lg),
        "short": int(sh),
        "official_wins": int(w),
        "gross_profit": round(float(gp), 2),
        "gross_loss": round(float(gl), 2),
        "direct_net_usd": round(float(net), 2),
        "exit_reasons": {
            "STOP": int(st),
            "MAX_HOLD": int(mh),
            "END": int(en),
        },
    }
    g = {
        "minimum_trades_20": tr >= 20,
        "minimum_distinct_days_5": nd >= 5,
        "nonnegative_direct_net": m["direct_net_usd"] >= 0.0,
    }
    g["screen_pass"] = bool(
        g["minimum_trades_20"]
        and g["minimum_distinct_days_5"]
        and g["nonnegative_direct_net"]
    )
    return m, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source_sha = sha256_file(args.source)
    if source_sha != CANONICAL_SHA:
        raise SystemExit("canonical January SHA mismatch: " + source_sha)

    d = pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    d = d[d.timestamp_ms_utc < END]
    t = d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t) != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit("Stage-A chronology/tick mismatch")

    ask_raw = d.ask_raw.to_numpy(np.int64)
    bid_raw = d.bid_raw.to_numpy(np.int64)
    native_mid_unquantized = (ask_raw.astype(np.int64) + bid_raw.astype(np.int64)) // 2
    profile_mid = quantize_mid(ask_raw, bid_raw)
    tdir = tick_direction(native_mid_unquantized)
    exec_ask, exec_bid = p75_surface(t, ask_raw, bid_raw)
    profiles = build_prior_day_profiles(t, profile_mid)

    bars_by_tf = {
        5_000: make_bars(t, profile_mid, tdir, 5_000),
        60_000: make_bars(t, profile_mid, tdir, 60_000),
    }

    configs = {}
    survivors = []

    for name, tf_ms, require_delta in PROFILES:
        idx, side, sig_day, diag = failed_auction_signals(
            t,
            bars_by_tf[tf_ms],
            profiles,
            require_delta,
        )
        m, g = metrics(idx, side, sig_day, t, exec_ask, exec_bid)
        configs[name] = {
            "timeframe_ms": int(tf_ms),
            "delta_required": bool(require_delta),
            "metrics": m,
            "gate": g,
            "event_diagnostics": diag,
        }
        if g["screen_pass"]:
            survivors.append(name)

    c01 = configs["17BL_C01_PVA_S5_PRICE_FAILED_AUCTION"]["metrics"]
    c02 = configs["17BM_C02_PVA_S5_DELTA_FAILED_AUCTION"]["metrics"]
    delta_effect = {
        "signals_change": int(c02["signals"] - c01["signals"]),
        "trades_change": int(c02["trades"] - c01["trades"]),
        "wins_change": int(c02["official_wins"] - c01["official_wins"]),
        "net_change_usd": round(
            float(c02["direct_net_usd"] - c01["direct_net_usd"]), 2
        ),
    }

    decision = (
        "ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION"
        if survivors
        else "RETIRE_PVACVD_NO_STAGE_A_SURVIVOR"
    )
    next_unit = (
        "R037_PVACVD_SURVIVOR_INDEPENDENT_LATER_JAN_VALIDATION"
        if survivors
        else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"
    )

    out = {
        "schema": "delta-r037-pvacvd-failed-auction-stage-a-17bl-17bn-v1",
        "status": "COMPLETE_FAST_CAUSAL_PRESCREEN",
        "unit": "R037_PVACVD_FAILED_AUCTION_STAGE_A_SCREEN_CHECKPOINT_17BL_17BN",
        "parent_checkpoint": "R037_SVWAPR_STAGE_A_SCREEN_CHECKPOINT_17BK",
        "prereg_commit": PREREG_COMMIT,
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "signal_surface": "NATIVE_DUKAS_TICK_ROOTED_S5_M1",
        "execution_surface": "DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning": False,
        "august_accessed": False,
        "profile_semantics": {
            "source": "prior available UTC trading day",
            "row_size_raw": TICK,
            "value_area_fraction": 0.70,
            "volume": "one count per source tick",
            "poc_tie_break": "lower price",
            "value_area_tie_break": "lower price",
        },
        "delta_semantics": {
            "tick_up": 1,
            "tick_down": -1,
            "unchanged": 0,
            "threshold": "sign only",
        },
        "configs": configs,
        "delta_incremental_effect_s5": delta_effect,
        "finding": {
            "survivors": survivors,
            "decision": decision,
            "next": next_unit,
        },
        "mql5_authorized": False,
    }
    atomic_json(args.output, out)

    print(
        json.dumps(
            {
                "configs": {
                    k: {
                        "signals": v["metrics"]["signals"],
                        "trades": v["metrics"]["trades"],
                        "days": v["metrics"]["distinct_days"],
                        "wins": v["metrics"]["official_wins"],
                        "net": v["metrics"]["direct_net_usd"],
                        "pass": v["gate"]["screen_pass"],
                    }
                    for k, v in configs.items()
                },
                "delta_effect_s5": delta_effect,
                "finding": out["finding"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
