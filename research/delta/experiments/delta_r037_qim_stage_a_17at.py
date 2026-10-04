"""DELTA R037 queue-imbalance / microprice Stage-A screen — 17AT.

Preregistered independent entry-source family. Uses canonical Dukascopy
best-bid/ask quoted volumes to reconstruct level-1 queue imbalance:

    I = (bid_volume - ask_volume) / (bid_volume + ask_volume)

Profiles are frozen at |I| >= 0.25 / 0.50 / 0.75. A new event requires
prior tick below threshold or an opposite-sign strong regime. No Stage-A
threshold sweep, session/side rescue, exit retuning, August access, or MQL5.

Prediction diagnostics use source mid-price chronology. Executable economics
use the frozen Coinexx-like P75 quote surface and DELTA 30-second hold engine.
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

DAY_MS = 86_400_000
TICK_RAW = 10
SCALE = 1000
STAGE_A_END_MS = 1_768_737_600_000
US_DST_START_2026_MS = 1_772_953_200_000
UK_DST_START_2026_MS = 1_774_746_000_000
P75_POINTS = np.asarray([20, 20, 21, 21], dtype=np.int64)
CANONICAL_JAN_SHA256 = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT = "c2390a95eebf1c60c0a75f0d524916948211286a"

MAX_SPREAD_RAW = 25 * TICK_RAW
STOP_RAW = 300
TRAIL_ACTIVATION_RAW = 100
TRAIL_DISTANCE_RAW = 30
MAX_HOLD_SECONDS = 30

PROFILES = (
    ("C01_QI_025", 0.25),
    ("C02_QI_050", 0.50),
    ("C03_QI_075", 0.75),
)
HORIZONS_MS = (250, 1000, 5000)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
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
            tmp_name = f.name
            json.dump(payload, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def session_code(t: np.ndarray) -> np.ndarray:
    tod = t % DAY_MS
    ls = np.where(t >= UK_DST_START_2026_MS, 7, 8) * 3_600_000
    le = ls + 8 * 3_600_000 + 30 * 60_000
    ns = np.where(t >= US_DST_START_2026_MS, 12, 13) * 3_600_000
    ne = ns + 9 * 3_600_000
    il = (tod >= ls) & (tod < le)
    iny = (tod >= ns) & (tod < ne)
    return np.where(il & iny, 2, np.where(il, 1, np.where(iny, 3, 0))).astype(np.int8)


def p75(t: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    s = session_code(t)
    spread = P75_POINTS[s] * TICK_RAW
    mid2 = ask_raw.astype(np.int64) + bid_raw.astype(np.int64)
    bid = ((mid2 - spread + TICK_RAW) // (2 * TICK_RAW)) * TICK_RAW
    ask = bid + spread
    return ask.astype(np.int64), bid.astype(np.int64)


@njit(cache=True)
def q_tick_nb(x: int) -> int:
    return ((int(x) + TICK_RAW // 2) // TICK_RAW) * TICK_RAW


@njit(cache=True)
def evaluate_events(event_idx, event_side, t, ask, bid):
    busy = -1
    trades = 0
    busy_skips = 0
    spread_rejects = 0
    wins = 0
    longs = 0
    shorts = 0
    gp = 0.0
    gl = 0.0
    net = 0.0
    stop_count = 0
    hold_count = 0
    end_count = 0
    accepted_days = np.empty(event_idx.size, dtype=np.int64)
    accepted_day_n = 0

    for z in range(event_idx.size):
        i = int(event_idx[z])
        side = int(event_side[z])
        if i <= busy:
            busy_skips += 1
            continue
        if int(ask[i] - bid[i]) > MAX_SPREAD_RAW:
            spread_rejects += 1
            continue

        trades += 1
        if side > 0:
            longs += 1
        else:
            shorts += 1
        accepted_days[accepted_day_n] = int(t[i] // DAY_MS)
        accepted_day_n += 1

        entry = int(ask[i]) if side > 0 else int(bid[i])
        stop = q_tick_nb(int(bid[i]) - STOP_RAW if side > 0 else int(ask[i]) + STOP_RAW)
        entry_sec = int(t[i]) // 1000
        raw = 0.0
        reason = 2
        last = i

        for k in range(i + 1, t.size):
            aa = int(ask[k])
            bb = int(bid[k])
            sec = int(t[k]) // 1000
            last = k
            if side > 0 and bb <= stop:
                raw = (bb - entry) / SCALE
                reason = 0
                break
            if side < 0 and aa >= stop:
                raw = (entry - aa) / SCALE
                reason = 0
                break
            if sec - entry_sec >= MAX_HOLD_SECONDS:
                raw = ((bb - entry) if side > 0 else (entry - aa)) / SCALE
                reason = 1
                break
            favorable = (bb - entry) if side > 0 else (entry - aa)
            if favorable >= TRAIL_ACTIVATION_RAW:
                ns = q_tick_nb(bb - TRAIL_DISTANCE_RAW if side > 0 else aa + TRAIL_DISTANCE_RAW)
                if (side > 0 and ns > stop) or (side < 0 and ns < stop):
                    stop = ns
        else:
            aa = int(ask[last])
            bb = int(bid[last])
            raw = ((bb - entry) if side > 0 else (entry - aa)) / SCALE

        exit_deal = raw - 0.01
        trade_net = -0.01 + exit_deal
        net += trade_net
        if exit_deal > 1e-12:
            wins += 1
        if raw > 0:
            gp += exit_deal
        else:
            gl += exit_deal
        if reason == 0:
            stop_count += 1
        elif reason == 1:
            hold_count += 1
        else:
            end_count += 1
        busy = last

    if accepted_day_n == 0:
        distinct_days = 0
    else:
        d = np.sort(accepted_days[:accepted_day_n])
        distinct_days = 1
        for k in range(1, d.size):
            if d[k] != d[k - 1]:
                distinct_days += 1

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
        stop_count,
        hold_count,
        end_count,
    )


def event_indices(imbalance: np.ndarray, threshold: float) -> tuple[np.ndarray, np.ndarray]:
    strong = np.abs(imbalance) >= threshold
    sign = np.sign(imbalance).astype(np.int8)
    prev_strong = np.r_[False, strong[:-1]]
    prev_sign = np.r_[np.int8(0), sign[:-1]]
    event = strong & ((~prev_strong) | (sign != prev_sign)) & (sign != 0)
    idx = np.flatnonzero(event).astype(np.int64)
    return idx, sign[idx].astype(np.int8)


def prediction_metrics(idx: np.ndarray, side: np.ndarray, t: np.ndarray, source_mid2: np.ndarray) -> dict:
    if idx.size == 0:
        return {
            "events": 0,
            "next_nonzero_mid_move": {"eligible": 0, "correct": 0, "accuracy": None},
            "forward": {},
        }

    change_idx = np.flatnonzero(source_mid2[1:] != source_mid2[:-1]).astype(np.int64) + 1
    pos = np.searchsorted(change_idx, idx + 1, side="left")
    ok = pos < change_idx.size
    next_j = np.empty(idx.size, dtype=np.int64)
    next_j[ok] = change_idx[pos[ok]]
    actual = np.zeros(idx.size, dtype=np.int8)
    actual[ok] = np.sign(source_mid2[next_j[ok]] - source_mid2[idx[ok]]).astype(np.int8)
    elig = ok & (actual != 0)
    correct = int(np.sum(side[elig] == actual[elig]))
    eligible = int(np.sum(elig))

    out = {
        "events": int(idx.size),
        "next_nonzero_mid_move": {
            "eligible": eligible,
            "correct": correct,
            "accuracy": (float(correct / eligible) if eligible else None),
        },
        "forward": {},
    }
    for h in HORIZONS_MS:
        j = np.searchsorted(t, t[idx] + h, side="left")
        okh = j < t.size
        act = np.zeros(idx.size, dtype=np.int8)
        act[okh] = np.sign(source_mid2[j[okh]] - source_mid2[idx[okh]]).astype(np.int8)
        el = okh & (act != 0)
        cor = int(np.sum(side[el] == act[el]))
        n = int(np.sum(el))
        out["forward"][f"{h}ms"] = {
            "eligible": n,
            "correct": cor,
            "accuracy": (float(cor / n) if n else None),
        }
    return out


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
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw", "ask_volume", "bid_volume"],
        dtype={
            "timestamp_ms_utc": np.int64,
            "ask_raw": np.int64,
            "bid_raw": np.int64,
            "ask_volume": np.float64,
            "bid_volume": np.float64,
        },
    )
    df = df[df.timestamp_ms_utc < STAGE_A_END_MS]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t) != 4_205_709:
        raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:] < t[:-1]):
        raise SystemExit("Stage-A chronology mismatch")

    ask_raw = df.ask_raw.to_numpy(np.int64)
    bid_raw = df.bid_raw.to_numpy(np.int64)
    ask_vol = df.ask_volume.to_numpy(np.float64)
    bid_vol = df.bid_volume.to_numpy(np.float64)
    den = bid_vol + ask_vol
    imbalance = np.zeros(len(t), dtype=np.float64)
    valid = np.isfinite(den) & np.isfinite(bid_vol) & np.isfinite(ask_vol) & (den > 0)
    imbalance[valid] = (bid_vol[valid] - ask_vol[valid]) / den[valid]
    imbalance = np.clip(imbalance, -1.0, 1.0)

    source_mid2 = ask_raw + bid_raw
    ask, bid = p75(t, ask_raw, bid_raw)

    q = np.quantile(imbalance[valid], [0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99])
    diag = {
        "valid_volume_ticks": int(np.sum(valid)),
        "invalid_or_zero_volume_ticks": int(np.sum(~valid)),
        "imbalance_quantiles": {
            "p01": float(q[0]), "p10": float(q[1]), "p25": float(q[2]),
            "p50": float(q[3]), "p75": float(q[4]), "p90": float(q[5]), "p99": float(q[6]),
        },
        "exact_zero_imbalance_ticks": int(np.sum(valid & (imbalance == 0.0))),
        "positive_imbalance_ticks": int(np.sum(valid & (imbalance > 0))),
        "negative_imbalance_ticks": int(np.sum(valid & (imbalance < 0))),
    }

    configs = {}
    ordinary = []
    strong = []
    for name, threshold in PROFILES:
        idx, side = event_indices(imbalance, threshold)
        pred = prediction_metrics(idx, side, t, source_mid2)
        ev = evaluate_events(idx, side, t, ask, bid)
        (
            trades, busy_skips, spread_rejects, distinct_days, longs, shorts,
            wins, gp, gl, net, stop_count, hold_count, end_count,
        ) = ev
        metrics = {
            "proposals": int(idx.size),
            "busy_skips": int(busy_skips),
            "spread_rejects": int(spread_rejects),
            "trades": int(trades),
            "distinct_days": int(distinct_days),
            "long": int(longs),
            "short": int(shorts),
            "official_wins": int(wins),
            "gross_profit": round(float(gp), 2),
            "gross_loss": round(float(gl), 2),
            "direct_net_usd": round(float(net), 2),
            "exit_reasons": {"STOP": int(stop_count), "MAX_HOLD": int(hold_count), "END": int(end_count)},
        }
        nma = pred["next_nonzero_mid_move"]["accuracy"]
        gate = {
            "minimum_trades_50": metrics["trades"] >= 50,
            "minimum_distinct_days_6": metrics["distinct_days"] >= 6,
            "direct_net_min_minus_1": metrics["direct_net_usd"] >= -1.0,
            "predictive_next_move_accuracy_min_0_5": nma is not None and nma >= 0.5,
        }
        gate["screen_pass"] = all(gate.values())
        gate["strong_pass"] = gate["screen_pass"] and metrics["direct_net_usd"] >= 0.0
        configs[name] = {
            "threshold": threshold,
            "prediction": pred,
            "metrics": metrics,
            "gate": gate,
        }
        if gate["screen_pass"]:
            ordinary.append(name)
        if gate["strong_pass"]:
            strong.append(name)

    def rk(name: str):
        x = configs[name]
        return (x["metrics"]["direct_net_usd"], x["prediction"]["next_nonzero_mid_move"]["accuracy"] or 0.0, x["metrics"]["trades"])

    ordinary.sort(key=rk, reverse=True)
    strong.sort(key=rk, reverse=True)

    if strong:
        leader = strong[0]
        decision = "ADVANCE_STRONG_QIM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt = "R037_QIM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader = ordinary[0]
        decision = "ADVANCE_ORDINARY_QIM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt = "R037_QIM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader = None
        decision = "RETIRE_QIM_STAGE_A_NO_EXECUTABLE_SURVIVOR"
        nxt = "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    out = {
        "schema": "delta-r037-qim-stage-a-screen-17at-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_QUEUE_IMBALANCE_MICROPRICE_STAGE_A_SCREEN",
        "family": "R037-QIM-v1",
        "parent_checkpoint": "R037_OFM_STAGE_A_SCREEN_CHECKPOINT_17AS",
        "prereg_commit": PREREG_COMMIT,
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "queue_imbalance": "(bid_volume-ask_volume)/(bid_volume+ask_volume)",
        "feature_diagnostics": diag,
        "numeric_retuning": False,
        "august_accessed": False,
        "configs": configs,
        "finding": {
            "leading_config": leader,
            "ordinary_survivors": ordinary,
            "strong_survivors": strong,
            "decision": decision,
            "next": nxt,
        },
        "mql5_authorized": False,
    }
    atomic_write_json(args.output, out)
    print(json.dumps({
        "finding": out["finding"],
        "feature_diagnostics": diag,
        "configs": {
            k: {
                "threshold": v["threshold"],
                "next_move_accuracy": v["prediction"]["next_nonzero_mid_move"]["accuracy"],
                "trades": v["metrics"]["trades"],
                "days": v["metrics"]["distinct_days"],
                "wins": v["metrics"]["official_wins"],
                "net": v["metrics"]["direct_net_usd"],
            } for k, v in configs.items()
        },
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
