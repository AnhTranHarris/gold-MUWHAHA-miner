"""DELTA R037 volatility squeeze breakout/release Stage-A screen — 17AN.

Preregistered source: classic Bollinger-inside-Keltner volatility compression
followed by the first completed-bar squeeze release. Direction is the release
close relative to the 20-bar SMA basis. Two frozen signal timeframes are
screened: M1 and M5.

Research-only:
- canonical January Dukascopy XAUUSD;
- Stage-A only;
- P75 execution;
- frozen 30-second lifecycle;
- no parameter sweep, rescue filters, August, or MQL5.

Crash safety:
- canonical source hash gate;
- chronological tick gate;
- atomic JSON output (temp file -> flush -> fsync -> os.replace);
- compact stdout only.
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

DAY_MS = 86_400_000
TICK_RAW = 10
SCALE = 1000
STAGE_A_END_MS = 1_768_737_600_000
US_DST_START_2026_MS = 1_772_953_200_000
UK_DST_START_2026_MS = 1_774_746_000_000
P75_POINTS = np.asarray([20, 20, 21, 21], dtype=np.int64)
CANONICAL_JAN_SHA256 = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT = "7c323efa14fc6bcdcfdb38402e7f4c478cdf8996"

LOOKBACK = 20
BB_MULT = 2.0
KC_ATR_MULT = 1.5
MAX_SPREAD_RAW = 25 * TICK_RAW
STOP_RAW = 300
TRAIL_ACTIVATION_RAW = 100
TRAIL_DISTANCE_RAW = 30
MAX_HOLD_SECONDS = 30

PROFILES = (
    ("C01_M1", 60_000),
    ("C02_M5", 300_000),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as f:
            temp_name = f.name
            json.dump(payload, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass


def session_code(t: np.ndarray) -> np.ndarray:
    tod = t % DAY_MS
    london_start = np.where(t >= UK_DST_START_2026_MS, 7, 8) * 3_600_000
    london_end = london_start + 8 * 3_600_000 + 30 * 60_000
    ny_start = np.where(t >= US_DST_START_2026_MS, 12, 13) * 3_600_000
    ny_end = ny_start + 9 * 3_600_000
    in_london = (tod >= london_start) & (tod < london_end)
    in_ny = (tod >= ny_start) & (tod < ny_end)
    return np.where(
        in_london & in_ny,
        2,
        np.where(in_london, 1, np.where(in_ny, 3, 0)),
    ).astype(np.int8)


def p75(t: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray):
    s = session_code(t)
    spread = P75_POINTS[s] * TICK_RAW
    mid2 = ask_raw.astype(np.int64) + bid_raw.astype(np.int64)
    bid = ((mid2 - spread + TICK_RAW) // (2 * TICK_RAW)) * TICK_RAW
    ask = bid + spread
    return ask.astype(np.int64), bid.astype(np.int64)


def q_tick(x: int) -> int:
    return ((int(x) + TICK_RAW // 2) // TICK_RAW) * TICK_RAW


def bars(t: np.ndarray, price: np.ndarray, tf_ms: int) -> dict:
    bucket = t // tf_ms
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:], len(t)]
    return {
        "end_ms": ((bucket[starts] + 1) * tf_ms).astype(np.int64),
        "open": price[starts].astype(np.int64),
        "high": np.maximum.reduceat(price, starts).astype(np.int64),
        "low": np.minimum.reduceat(price, starts).astype(np.int64),
        "close": price[ends - 1].astype(np.int64),
    }


def squeeze_features(b: dict) -> dict:
    h = b["high"].astype(np.float64)
    l = b["low"].astype(np.float64)
    c = b["close"].astype(np.float64)

    s = pd.Series(c)
    basis = s.rolling(LOOKBACK, min_periods=LOOKBACK).mean().to_numpy(np.float64)
    std = s.rolling(LOOKBACK, min_periods=LOOKBACK).std(ddof=0).to_numpy(np.float64)

    prev = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    tr[0] = h[0] - l[0]
    atr = pd.Series(tr).rolling(LOOKBACK, min_periods=LOOKBACK).mean().to_numpy(np.float64)

    squeeze = np.isfinite(basis) & np.isfinite(std) & np.isfinite(atr)
    squeeze &= (BB_MULT * std) < (KC_ATR_MULT * atr)
    return {"basis": basis, "atr": atr, "std": std, "squeeze": squeeze}


def generate_proposals(
    t: np.ndarray,
    ask: np.ndarray,
    bid: np.ndarray,
    tf_ms: int,
):
    b = bars(t, bid, tf_ms)
    f = squeeze_features(b)
    e = b["end_ms"]
    c = b["close"]
    basis = f["basis"]
    sq = f["squeeze"]

    proposals = []
    stage = {
        "bars": int(len(e)),
        "squeeze_bars": int(np.count_nonzero(sq)),
        "release_bars": 0,
        "directional_releases": 0,
    }

    for j in range(1, len(e)):
        if not (sq[j - 1] and not sq[j]):
            continue
        stage["release_bars"] += 1

        if not np.isfinite(basis[j]):
            continue
        if c[j] > basis[j]:
            side = 1
        elif c[j] < basis[j]:
            side = -1
        else:
            continue

        stage["directional_releases"] += 1
        edge = int(e[j])
        if edge >= STAGE_A_END_MS:
            continue

        i = int(np.searchsorted(t, edge, side="left"))
        if i >= len(t) or int(t[i]) >= STAGE_A_END_MS:
            proposals.append({"eligible": False, "reason": "NO_EXEC", "edge_ms": edge})
            continue
        if int(ask[i] - bid[i]) > MAX_SPREAD_RAW:
            proposals.append({"eligible": False, "reason": "SPREAD", "edge_ms": edge})
            continue

        proposals.append(
            {
                "eligible": True,
                "decision_index": i,
                "side": side,
                "day": int(t[i] // DAY_MS),
                "edge_ms": edge,
            }
        )

    return proposals, stage


def simulate_trade(ev: dict, t: np.ndarray, ask: np.ndarray, bid: np.ndarray) -> dict:
    i = int(ev["decision_index"])
    side = int(ev["side"])
    entry = int(ask[i]) if side > 0 else int(bid[i])
    stop = q_tick(int(bid[i]) - STOP_RAW if side > 0 else int(ask[i]) + STOP_RAW)
    entry_sec = int(t[i]) // 1000

    net = -0.01
    gross_profit = 0.0
    gross_loss = -0.01
    official_win = 0
    last = i
    reason = "END"
    raw = 0.0

    for k in range(i + 1, len(t)):
        aa = int(ask[k])
        bb = int(bid[k])
        sec = int(t[k]) // 1000
        last = k

        if side > 0 and bb <= stop:
            raw = (bb - entry) / SCALE
            reason = "STOP"
            break
        if side < 0 and aa >= stop:
            raw = (entry - aa) / SCALE
            reason = "STOP"
            break

        if sec - entry_sec >= MAX_HOLD_SECONDS:
            raw = ((bb - entry) if side > 0 else (entry - aa)) / SCALE
            reason = "MAX_HOLD"
            break

        favorable = (bb - entry) if side > 0 else (entry - aa)
        if favorable >= TRAIL_ACTIVATION_RAW:
            new_stop = q_tick(bb - TRAIL_DISTANCE_RAW if side > 0 else aa + TRAIL_DISTANCE_RAW)
            if (side > 0 and new_stop > stop) or (side < 0 and new_stop < stop):
                stop = new_stop
    else:
        aa = int(ask[last])
        bb = int(bid[last])
        raw = ((bb - entry) if side > 0 else (entry - aa)) / SCALE

    exit_deal = raw - 0.01
    net += exit_deal
    if exit_deal > 1e-12:
        official_win = 1

    if raw > 0:
        gross_profit += exit_deal
    else:
        gross_loss += exit_deal

    return {
        "net": net,
        "gp": gross_profit,
        "gl": gross_loss,
        "official": official_win,
        "reason": reason,
        "exit_index": last,
    }


def evaluate(proposals: list[dict], t: np.ndarray, ask: np.ndarray, bid: np.ndarray) -> dict:
    eligible = [x for x in proposals if x.get("eligible")]
    accepted = []
    rows = []
    busy_until = -1

    for ev in eligible:
        i = int(ev["decision_index"])
        if i <= busy_until:
            continue
        tr = simulate_trade(ev, t, ask, bid)
        rows.append(tr)
        accepted.append(ev)
        busy_until = int(tr["exit_index"])

    rejection_counts = {}
    for ev in proposals:
        if not ev.get("eligible"):
            reason = ev.get("reason", "UNKNOWN")
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1

    return {
        "proposals": int(len(proposals)),
        "eligible": int(len(eligible)),
        "trades": int(len(rows)),
        "distinct_days": int(len({x["day"] for x in accepted})),
        "long": int(sum(x["side"] > 0 for x in accepted)),
        "short": int(sum(x["side"] < 0 for x in accepted)),
        "rejections": rejection_counts,
        "official_wins": int(sum(x["official"] for x in rows)),
        "gross_profit": round(float(sum(x["gp"] for x in rows)), 2),
        "gross_loss": round(float(sum(x["gl"] for x in rows)), 2),
        "direct_net_usd": round(float(sum(x["net"] for x in rows)), 2),
        "exit_reasons": {
            name: int(sum(x["reason"] == name for x in rows))
            for name in ("STOP", "MAX_HOLD", "END")
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source_sha = sha256_file(args.source)
    if source_sha != CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df = pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    df = df[df.timestamp_ms_utc < STAGE_A_END_MS]
    t = df.timestamp_ms_utc.to_numpy(np.int64)

    if len(t) != 4_205_709:
        raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:] < t[:-1]):
        raise SystemExit("Stage-A chronology mismatch")

    ask, bid = p75(
        t,
        df.ask_raw.to_numpy(np.int64),
        df.bid_raw.to_numpy(np.int64),
    )

    configs = {}
    ordinary = []
    strong = []

    for name, tf_ms in PROFILES:
        props, stage = generate_proposals(t, ask, bid, tf_ms)
        metrics = evaluate(props, t, ask, bid)
        gate = {
            "minimum_trades_6": metrics["trades"] >= 6,
            "minimum_distinct_days_4": metrics["distinct_days"] >= 4,
            "direct_net_min_minus_1": metrics["direct_net_usd"] >= -1.0,
        }
        gate["screen_pass"] = all(gate.values())
        gate["strong_pass"] = gate["screen_pass"] and metrics["direct_net_usd"] >= 0.0

        configs[name] = {
            "timeframe_seconds": int(tf_ms // 1000),
            "stage_counts": stage,
            "metrics": metrics,
            "gate": gate,
        }
        if gate["screen_pass"]:
            ordinary.append(name)
        if gate["strong_pass"]:
            strong.append(name)

    def rank_key(name: str):
        m = configs[name]["metrics"]
        return (m["direct_net_usd"], m["official_wins"], m["trades"])

    strong.sort(key=rank_key, reverse=True)
    ordinary.sort(key=rank_key, reverse=True)

    if strong:
        leader = strong[0]
        decision = "ADVANCE_STRONG_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        next_unit = "R037_VSBR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader = ordinary[0]
        decision = "ADVANCE_ORDINARY_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        next_unit = "R037_VSBR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader = None
        decision = "RETIRE_VSBR_STAGE_A_NO_SURVIVOR"
        next_unit = "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    out = {
        "schema": "delta-r037-vsbr-stage-a-screen-17an-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_VOLATILITY_SQUEEZE_BREAKOUT_RELEASE_STAGE_A_SCREEN",
        "family": "R037-VSBR-v1",
        "parent_checkpoint": "R037_ASRB_C02_LATER_JAN_CHECKPOINT_17AM",
        "prereg_commit": PREREG_COMMIT,
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning": False,
        "august_accessed": False,
        "configs": configs,
        "ranking": ordinary,
        "finding": {
            "leading_config": leader,
            "ordinary_survivors": ordinary,
            "strong_survivors": strong,
            "decision": decision,
            "next": next_unit,
        },
        "mql5_authorized": False,
    }

    atomic_write_json(args.output, out)
    print(
        json.dumps(
            {
                "finding": out["finding"],
                "metrics": {k: v["metrics"] for k, v in configs.items()},
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
