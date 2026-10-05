"""R037 source-default breaker-block retest entry screen 17CC-17CD.

Clean-room reconstruction of MetaQuotes Part 35 breaker-block state grammar on
fixed M5/M15 lanes, with the preregistered Part-48 deterministic 300-bar zone
lifetime bridge. Entries are evaluated under frozen DELTA P75 30-second
execution economics. No source-EA exit/risk settings are imported.
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
P75 = np.asarray([20, 20, 21, 21], np.int64)
SHA = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG = "cfcb44d1065a30f23aebee1b8193d749346a99d4"

CONSOLIDATION_BARS = 7
MAX_CONSOLIDATION_SPREAD_RAW = 50 * TICK
BARS_AFTER_BREAKOUT = 3
IMPULSE_MULT = 1.0
MOVE_AWAY_RAW = 50 * TICK
BLOCK_LIFETIME_BARS = 300
MAX_SPREAD = 250
STOP = 300
TRAIL_ACT = 100
TRAIL_DIST = 30
MAX_HOLD = 30


def sh(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix="." + path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as f:
            tmp_name = f.name
            json.dump(obj, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def sess(t: np.ndarray) -> np.ndarray:
    tod = t % DAY
    ls = np.where(t >= UK_DST, 7, 8) * HOUR
    le = ls + 30_600_000
    ns = np.where(t >= US_DST, 12, 13) * HOUR
    ne = ns + 32_400_000
    il = (tod >= ls) & (tod < le)
    ny = (tod >= ns) & (tod < ne)
    return np.where(il & ny, 2, np.where(il, 1, np.where(ny, 3, 0))).astype(np.int8)


def p75(t: np.ndarray, a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    sp = P75[sess(t)] * TICK
    m = a.astype(np.int64) + b.astype(np.int64)
    bid = ((m - sp + TICK) // (2 * TICK)) * TICK
    return (bid + sp).astype(np.int64), bid.astype(np.int64)


def bars(t: np.ndarray, a: np.ndarray, b: np.ndarray, tf: int) -> dict[str, np.ndarray]:
    mid = (a.astype(np.int64) + b.astype(np.int64)) // 2
    mid = ((mid + 5) // 10) * 10
    bucket = t // tf
    st = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    en = np.r_[st[1:], len(t)]
    return {
        "end": ((bucket[st] + 1) * tf).astype(np.int64),
        "o": mid[st].astype(np.int64),
        "h": np.maximum.reduceat(mid, st).astype(np.int64),
        "l": np.minimum.reduceat(mid, st).astype(np.int64),
        "c": mid[en - 1].astype(np.int64),
    }


def breaker_signals(t: np.ndarray, b: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    e, h, l, c = b["end"], b["h"], b["l"], b["c"]
    n = len(c)
    sig_idx: list[int] = []
    sig_side: list[int] = []
    sig_days: list[int] = []

    range_hi = None
    range_lo = None
    pending = None
    blocks: list[dict] = []

    d = {
        "bars": int(n),
        "consolidations": 0,
        "range_extensions": 0,
        "range_outside_without_close_break": 0,
        "breakouts": 0,
        "pending_overwrites": 0,
        "impulse_checks": 0,
        "bullish_impulses": 0,
        "bearish_impulses": 0,
        "no_impulse": 0,
        "blocks_created": 0,
        "blocks_expired": 0,
        "invalidation_conditions": 0,
        "invalidation_swing_pass": 0,
        "invalidation_swing_fail": 0,
        "move_aways": 0,
        "retest_conditions": 0,
        "retest_swing_pass": 0,
        "retest_swing_fail": 0,
        "same_bar_moveaway_retest": 0,
        "signals": 0,
    }

    for i in range(n):
        if range_hi is None and i >= CONSOLIDATION_BARS - 1:
            s = i - CONSOLIDATION_BARS + 1
            ok = True
            for k in range(s, i):
                if abs(int(h[k]) - int(h[k + 1])) > MAX_CONSOLIDATION_SPREAD_RAW or abs(int(l[k]) - int(l[k + 1])) > MAX_CONSOLIDATION_SPREAD_RAW:
                    ok = False
                    break
            if ok:
                range_hi = int(np.max(h[s : i + 1]))
                range_lo = int(np.min(l[s : i + 1]))
                d["consolidations"] += 1
        elif range_hi is not None:
            if int(h[i]) <= int(range_hi) and int(l[i]) >= int(range_lo):
                d["range_extensions"] += 1
            else:
                d["range_outside_without_close_break"] += 1

        if range_hi is not None:
            cc = int(c[i])
            if cc > int(range_hi) or cc < int(range_lo):
                if pending is not None:
                    d["pending_overwrites"] += 1
                pending = {"hi": int(range_hi), "lo": int(range_lo), "break_i": int(i)}
                d["breakouts"] += 1
                range_hi = None
                range_lo = None

        if pending is not None and i - int(pending["break_i"]) >= BARS_AFTER_BREAKOUT + 1:
            d["impulse_checks"] += 1
            hi0 = int(pending["hi"])
            lo0 = int(pending["lo"])
            threshold = int(round((hi0 - lo0) * IMPULSE_MULT))
            bull = False
            bear = False
            for k in range(i, max(-1, i - BARS_AFTER_BREAKOUT), -1):
                ck = int(c[k])
                if ck >= hi0 + threshold:
                    bull = True
                    break
                if ck <= lo0 - threshold:
                    bear = True
                    break
            if bull or bear:
                block_type = "OB-bullish" if bull else "OB-bearish"
                blocks.append(
                    {
                        "hi": hi0,
                        "lo": lo0,
                        "type": block_type,
                        "creation_i": int(i),
                        "expiry_i": int(i + BLOCK_LIFETIME_BARS),
                        "invalidated": False,
                        "invalidation_i": -1,
                        "invalidation_swing": 0,
                        "moved": False,
                        "move_i": -1,
                        "retested": False,
                    }
                )
                d["blocks_created"] += 1
                if bull:
                    d["bullish_impulses"] += 1
                else:
                    d["bearish_impulses"] += 1
            else:
                d["no_impulse"] += 1
            pending = None

        for block in reversed(blocks):
            if block["retested"]:
                continue
            is_bullish_bb = False
            invalid_cond = False
            if not block["invalidated"]:
                if block["type"] == "OB-bearish" and int(c[i]) > int(block["hi"]):
                    is_bullish_bb = True
                    invalid_cond = True
                elif block["type"] == "OB-bullish" and int(c[i]) < int(block["lo"]):
                    is_bullish_bb = False
                    invalid_cond = True
                if invalid_cond:
                    d["invalidation_conditions"] += 1
                    s = int(block["creation_i"]) + 1
                    valid = False
                    if i - s >= 1:
                        if is_bullish_bb:
                            valid = int(np.min(l[s:i])) < int(block["lo"])
                        else:
                            valid = int(np.max(h[s:i])) > int(block["hi"])
                    if valid:
                        block["invalidated"] = True
                        block["type"] = "Invalidated-bearish" if is_bullish_bb else "Invalidated-bullish"
                        block["invalidation_i"] = int(i)
                        block["invalidation_swing"] = int(h[i]) if is_bullish_bb else int(l[i])
                        block["moved"] = False
                        block["move_i"] = -1
                        d["invalidation_swing_pass"] += 1
                    else:
                        d["invalidation_swing_fail"] += 1

        kept = []
        for block in blocks:
            if i >= int(block["expiry_i"]):
                d["blocks_expired"] += 1
            else:
                kept.append(block)
        blocks = kept

        for block in reversed(blocks):
            if not block["invalidated"] or block["retested"]:
                continue
            if i <= int(block["invalidation_i"]):
                continue
            bullish = block["type"] == "Invalidated-bearish"
            if not block["moved"]:
                if bullish and int(c[i]) > int(block["hi"]) + MOVE_AWAY_RAW:
                    block["moved"] = True
                    block["move_i"] = int(i)
                    d["move_aways"] += 1
                elif (not bullish) and int(c[i]) < int(block["lo"]) - MOVE_AWAY_RAW:
                    block["moved"] = True
                    block["move_i"] = int(i)
                    d["move_aways"] += 1
            if not block["moved"]:
                continue

            retest = (bullish and int(l[i]) <= int(block["hi"]) and int(c[i]) > int(block["hi"])) or ((not bullish) and int(h[i]) >= int(block["lo"]) and int(c[i]) < int(block["lo"]))
            if not retest:
                continue
            d["retest_conditions"] += 1
            if int(block["move_i"]) == i:
                d["same_bar_moveaway_retest"] += 1

            s = int(block["invalidation_i"]) + 1
            valid = False
            if i - s >= 1:
                if bullish:
                    valid = int(np.max(h[s:i])) > int(block["invalidation_swing"])
                else:
                    valid = int(np.min(l[s:i])) < int(block["invalidation_swing"])
            if not valid:
                d["retest_swing_fail"] += 1
                continue

            j = int(np.searchsorted(t, int(e[i]), side="left"))
            if j < len(t):
                sig_idx.append(j)
                sig_side.append(1 if bullish else -1)
                sig_days.append((int(e[i]) - 1) // DAY)
                d["signals"] += 1
            block["retested"] = True
            block["type"] = "BB-bullish" if bullish else "BB-bearish"
            d["retest_swing_pass"] += 1

    return (
        np.asarray(sig_idx, np.int64),
        np.asarray(sig_side, np.int8),
        np.asarray(sig_days, np.int64),
        d,
    )


@njit(cache=True)
def qt(x):
    return ((int(x) + 5) // 10) * 10


@njit(cache=True)
def ev(idx, side, days, t, ask, bid):
    busy = -1
    tr = bs = sr = nd = lg = shrt = wins = 0
    gp = gl = net = 0.0
    st = mh = en = 0
    u = 0
    used = np.empty(idx.size, np.int64)
    for z in range(idx.size):
        i = int(idx[z])
        s = int(side[z])
        if i <= busy:
            bs += 1
            continue
        if int(ask[i] - bid[i]) > MAX_SPREAD:
            sr += 1
            continue
        tr += 1
        lg += s > 0
        shrt += s < 0
        used[u] = days[z]
        u += 1
        entry = int(ask[i]) if s > 0 else int(bid[i])
        stop = qt(int(bid[i]) - STOP if s > 0 else int(ask[i]) + STOP)
        sec0 = int(t[i]) // 1000
        raw = 0.0
        reason = 2
        last = i
        for k in range(i + 1, t.size):
            aa = int(ask[k])
            bb = int(bid[k])
            last = k
            if s > 0 and bb <= stop:
                raw = (bb - entry) / SCALE
                reason = 0
                break
            if s < 0 and aa >= stop:
                raw = (entry - aa) / SCALE
                reason = 0
                break
            if int(t[k]) // 1000 - sec0 >= MAX_HOLD:
                raw = ((bb - entry) if s > 0 else (entry - aa)) / SCALE
                reason = 1
                break
            fav = (bb - entry) if s > 0 else (entry - aa)
            if fav >= TRAIL_ACT:
                ns = qt(bb - TRAIL_DIST if s > 0 else aa + TRAIL_DIST)
                if (s > 0 and ns > stop) or (s < 0 and ns < stop):
                    stop = ns
        ex = raw - 0.01
        net += ex - 0.01
        wins += ex > 1e-12
        if raw > 0:
            gp += ex
        else:
            gl += ex
        if reason == 0:
            st += 1
        elif reason == 1:
            mh += 1
        else:
            en += 1
        busy = last
    if u:
        x = np.sort(used[:u])
        nd = 1
        for k in range(1, x.size):
            nd += x[k] != x[k - 1]
    return tr, bs, sr, nd, lg, shrt, wins, gp, gl, net, st, mh, en


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    hs = sh(args.source)
    if hs != SHA:
        raise SystemExit("canonical January SHA mismatch: " + hs)
    df = pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    df = df[df.timestamp_ms_utc < END]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t) != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit("Stage-A chronology/tick mismatch")
    ar = df.ask_raw.to_numpy(np.int64)
    br = df.bid_raw.to_numpy(np.int64)
    ask, bid = p75(t, ar, br)

    configs = {}
    for name, tf in (
        ("17CC_M5_BREAKER_BLOCK_RETEST", 300_000),
        ("17CD_M15_BREAKER_BLOCK_RETEST", 900_000),
    ):
        ix, sd, dy, diag = breaker_signals(t, bars(t, ar, br, tf))
        q = ev(ix, sd, dy, t, ask, bid)
        metrics = {
            "signals": int(ix.size),
            "trades": int(q[0]),
            "busy_skips": int(q[1]),
            "spread_rejects": int(q[2]),
            "distinct_days": int(q[3]),
            "long": int(q[4]),
            "short": int(q[5]),
            "official_wins": int(q[6]),
            "gross_profit": round(float(q[7]), 2),
            "gross_loss": round(float(q[8]), 2),
            "direct_net_usd": round(float(q[9]), 2),
            "exit_reasons": {"STOP": int(q[10]), "MAX_HOLD": int(q[11]), "END": int(q[12])},
        }
        gate = {
            "minimum_trades_20": metrics["trades"] >= 20,
            "minimum_distinct_days_5": metrics["distinct_days"] >= 5,
            "nonnegative_direct_net": metrics["direct_net_usd"] >= 0,
        }
        gate["screen_pass"] = all(gate.values())
        configs[name] = {"timeframe_ms": tf, "metrics": metrics, "gate": gate, "diagnostics": diag}

    survivors = [k for k, v in configs.items() if v["gate"]["screen_pass"]]
    out = {
        "schema": "delta-r037-breaker-block-retest-stage-a-17cc-17cd-v1",
        "status": "COMPLETE_FAST_CAUSAL_PRESCREEN",
        "unit": "R037_BREAKER_BLOCK_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CC_17CD",
        "family": "R037-BBR-v1",
        "parent_checkpoint": "R037_QUASIMODO_SOURCE_DEFAULT_STAGE_A_SCREEN_CHECKPOINT_17CA_17CB",
        "prereg_commit": PREREG,
        "source_basis": [
            "MQL5 Part 35 breaker-block source-default state grammar",
            "MQL5 Part 48 deterministic 300-bar lifetime bridge only",
        ],
        "source_sha256": hs,
        "stage_a_ticks": int(len(t)),
        "frozen_defaults": {
            "consolidation_bars": CONSOLIDATION_BARS,
            "max_consolidation_spread_points": 50,
            "bars_to_wait_after_breakout": BARS_AFTER_BREAKOUT,
            "impulse_multiplier": IMPULSE_MULT,
            "move_away_points": 50,
            "enable_swing_validation": True,
            "deterministic_block_lifetime_bars": BLOCK_LIFETIME_BARS,
        },
        "configs": configs,
        "finding": {
            "survivors": survivors,
            "decision": "ADVANCE_BREAKER_BLOCK_SURVIVOR" if survivors else "RETIRE_BREAKER_BLOCK_NO_STAGE_A_SURVIVOR",
            "next": "R037_BREAKER_BLOCK_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST",
        },
        "causal_note": "Entries occur only on first tick at/after completed retest bar. Source code may set move-away and retest on the same completed bar; diagnostic count is retained explicitly rather than hidden.",
        "numeric_retuning": False,
        "august_accessed": False,
        "mql5_authorized": False,
    }
    atomic(args.output, out)
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
                        "same_bar": v["diagnostics"]["same_bar_moveaway_retest"],
                        "pass": v["gate"]["screen_pass"],
                    }
                    for k, v in configs.items()
                },
                "finding": out["finding"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
