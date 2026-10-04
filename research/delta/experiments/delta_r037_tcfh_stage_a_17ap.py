"""DELTA R037 tick-count flow hysteresis Stage-A screen - 17AP.

Public-source reconstruction basis:
- MetaQuotes/MQL5 article Part 38: trailing 30-second tick-count flow
  (upticks-downticks)/(upticks+downticks), default trigger +/-0.30,
  hysteresis factor 0.80, and 2-second aggregation cadence.
- This producer reconstructs only the transparent tick-count flow proxy.
  It does NOT claim true exchange order-flow imbalance or DOM access.

Frozen DELTA execution semantics:
- canonical January Dukascopy XAUUSD source;
- Coinexx-like P75 synthetic quote surface;
- first executable tick at/after a causal completed decision boundary;
- max spread 25 points, 0.01 lot accounting, $0.30 stop,
  +$0.10 trail arm, $0.03 trail distance, 30-second max hold;
- no threshold sweep, rescue filter, August access, or MQL5 build.
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
PREREG_COMMIT = "3e61506898ca72ebc537e99029176f238187aaa0"

FLOW_WINDOW_MS = 30_000
FLOW_THRESHOLD = 0.30
HYSTERESIS_FACTOR = 0.80
RESET_THRESHOLD = FLOW_THRESHOLD * HYSTERESIS_FACTOR
CADENCE_MS = 2_000
MAX_SPREAD_RAW = 25 * TICK_RAW
STOP_RAW = 300
TRAIL_ACTIVATION_RAW = 100
TRAIL_DISTANCE_RAW = 30
MAX_HOLD_SECONDS = 30


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


def q_tick(x: int) -> int:
    return ((int(x) + TICK_RAW // 2) // TICK_RAW) * TICK_RAW


def build_flow_proposals(t: np.ndarray, ask: np.ndarray, bid: np.ndarray) -> tuple[list[dict], dict]:
    mid2 = ask.astype(np.int64) + bid.astype(np.int64)
    delta = np.sign(np.diff(mid2, prepend=mid2[0])).astype(np.int8)
    up = (delta > 0).astype(np.int64)
    dn = (delta < 0).astype(np.int64)
    cup = np.r_[0, np.cumsum(up, dtype=np.int64)]
    cdn = np.r_[0, np.cumsum(dn, dtype=np.int64)]

    first_edge = ((int(t[0]) + FLOW_WINDOW_MS + CADENCE_MS - 1) // CADENCE_MS) * CADENCE_MS
    last_edge = ((STAGE_A_END_MS - 1) // CADENCE_MS) * CADENCE_MS
    edges = np.arange(first_edge, last_edge + 1, CADENCE_MS, dtype=np.int64)

    end_idx = np.searchsorted(t, edges, side="left")
    start_idx = np.searchsorted(t, edges - FLOW_WINDOW_MS, side="left")
    ups = cup[end_idx] - cup[start_idx]
    dns = cdn[end_idx] - cdn[start_idx]
    tot = ups + dns
    flow = np.zeros(len(edges), dtype=np.float64)
    nz = tot > 0
    flow[nz] = (ups[nz] - dns[nz]) / tot[nz]

    proposals: list[dict] = []
    buy_latched = False
    sell_latched = False
    counts = {
        "decision_edges": int(len(edges)),
        "nonzero_flow_edges": int(np.sum(nz)),
        "buy_threshold_crossings": 0,
        "sell_threshold_crossings": 0,
        "spread_rejects": 0,
        "no_exec_rejects": 0,
        "eligible_proposals": 0,
    }

    for k, edge in enumerate(edges):
        f = float(flow[k])

        if buy_latched and f < RESET_THRESHOLD:
            buy_latched = False
        if sell_latched and f > -RESET_THRESHOLD:
            sell_latched = False

        side = 0
        if f >= FLOW_THRESHOLD and not buy_latched:
            side = 1
            buy_latched = True
            sell_latched = False
            counts["buy_threshold_crossings"] += 1
        elif f <= -FLOW_THRESHOLD and not sell_latched:
            side = -1
            sell_latched = True
            buy_latched = False
            counts["sell_threshold_crossings"] += 1
        else:
            continue

        i = int(end_idx[k])
        if i >= len(t) or int(t[i]) >= STAGE_A_END_MS:
            counts["no_exec_rejects"] += 1
            continue
        if int(ask[i] - bid[i]) > MAX_SPREAD_RAW:
            counts["spread_rejects"] += 1
            continue

        counts["eligible_proposals"] += 1
        proposals.append(
            {
                "eligible": True,
                "decision_index": i,
                "side": side,
                "day": int(t[i] // DAY_MS),
                "edge_ms": int(edge),
                "flow": f,
                "up_ticks": int(ups[k]),
                "down_ticks": int(dns[k]),
            }
        )

    return proposals, counts


def simulate_trade(ev: dict, t: np.ndarray, ask: np.ndarray, bid: np.ndarray) -> dict:
    i = int(ev["decision_index"])
    side = int(ev["side"])
    entry = int(ask[i]) if side > 0 else int(bid[i])
    stop = q_tick(int(bid[i]) - STOP_RAW if side > 0 else int(ask[i]) + STOP_RAW)
    entry_sec = int(t[i]) // 1000

    net = -0.01
    gp = 0.0
    gl = -0.01
    official = 0
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
            ns = q_tick(bb - TRAIL_DISTANCE_RAW if side > 0 else aa + TRAIL_DISTANCE_RAW)
            if (side > 0 and ns > stop) or (side < 0 and ns < stop):
                stop = ns
    else:
        aa = int(ask[last])
        bb = int(bid[last])
        raw = ((bb - entry) if side > 0 else (entry - aa)) / SCALE

    exit_deal = raw - 0.01
    net += exit_deal
    if exit_deal > 1e-12:
        official = 1
    if raw > 0:
        gp += exit_deal
    else:
        gl += exit_deal

    return {
        "net": net,
        "gp": gp,
        "gl": gl,
        "official": official,
        "reason": reason,
        "exit_index": last,
    }


def evaluate(proposals: list[dict], t: np.ndarray, ask: np.ndarray, bid: np.ndarray) -> dict:
    rows = []
    accepted = []
    busy = -1
    for ev in proposals:
        i = int(ev["decision_index"])
        if i <= busy:
            continue
        tr = simulate_trade(ev, t, ask, bid)
        rows.append(tr)
        accepted.append(ev)
        busy = int(tr["exit_index"])

    return {
        "proposals": int(len(proposals)),
        "trades": int(len(rows)),
        "distinct_days": int(len({x["day"] for x in accepted})),
        "long": int(sum(x["side"] > 0 for x in accepted)),
        "short": int(sum(x["side"] < 0 for x in accepted)),
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

    ask, bid = p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    proposals, stage = build_flow_proposals(t, ask, bid)
    metrics = evaluate(proposals, t, ask, bid)
    gate = {
        "minimum_trades_6": metrics["trades"] >= 6,
        "minimum_distinct_days_4": metrics["distinct_days"] >= 4,
        "direct_net_min_minus_1": metrics["direct_net_usd"] >= -1.0,
    }
    gate["screen_pass"] = all(gate.values())
    gate["strong_pass"] = gate["screen_pass"] and metrics["direct_net_usd"] >= 0.0

    if gate["screen_pass"]:
        decision = "ADVANCE_TCFH_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt = "R037_TCFH_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        leader = "C01_DEFAULT_30S"
    else:
        decision = "RETIRE_TCFH_STAGE_A_NO_SURVIVOR"
        nxt = "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
        leader = None

    out = {
        "schema": "delta-r037-tcfh-stage-a-screen-17ap-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_TICK_COUNT_FLOW_HYSTERESIS_STAGE_A_SCREEN",
        "family": "R037-TCFH-v1",
        "parent_checkpoint": "R037_RLSFG_STAGE_A_SCREEN_CHECKPOINT_17AO",
        "prereg_commit": PREREG_COMMIT,
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "public_defaults": {
            "flow_window_seconds": 30,
            "flow_threshold": 0.30,
            "hysteresis_factor": 0.80,
            "cadence_seconds": 2,
        },
        "numeric_retuning": False,
        "august_accessed": False,
        "config": {
            "C01_DEFAULT_30S": {
                "stage_counts": stage,
                "metrics": metrics,
                "gate": gate,
            }
        },
        "finding": {
            "leading_config": leader,
            "ordinary_survivors": [leader] if leader else [],
            "strong_survivors": [leader] if gate["strong_pass"] and leader else [],
            "decision": decision,
            "next": nxt,
        },
        "mql5_authorized": False,
    }
    atomic_write_json(args.output, out)
    print(json.dumps({"finding": out["finding"], "metrics": metrics, "stage_counts": stage}, separators=(",", ":")))


if __name__ == "__main__":
    main()
