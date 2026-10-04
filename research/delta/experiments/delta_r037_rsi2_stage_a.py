"""DELTA R037 RSI2 trend-aligned mean-reversion Stage-A screen.

Frozen source-grounded variants:
- M1/M5 Connors-style classic RSI(2) exhaustion: <5 long above SMA200,
  >95 short below SMA200.
- M1/M5 persistent pullback: three consecutive RSI(2) <10 or >90
  with the same SMA200 trend alignment.

All decisions use completed Bid bars. No threshold/period/MA/timeframe tuning,
session slicing, previous-day logic, volatility-compression prerequisite,
Donchian breakout, August access, or MQL5 work is allowed in this unit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import delta_r037_vce_stage_a as vce

val = vce.val
STAGE_A_START_MS = vce.STAGE_A_START_MS
STAGE_A_END_MS = vce.STAGE_A_END_MS

CONFIGS = (
    "R037-RSI2-C01_M1_CLASSIC_TREND200",
    "R037-RSI2-C02_M1_PULLBACK3_TREND200",
    "R037-RSI2-C03_M5_CLASSIC_TREND200",
    "R037-RSI2-C04_M5_PULLBACK3_TREND200",
)


def sma(x: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(x), np.nan, np.float64)
    if len(x) < period:
        return out
    xf = x.astype(np.float64)
    cs = np.r_[0.0, np.cumsum(xf)]
    out[period - 1:] = (cs[period:] - cs[:-period]) / period
    return out


def rsi_wilder(x: np.ndarray, period: int = 2) -> np.ndarray:
    """Causal Wilder-smoothed RSI from completed closes."""
    xf = x.astype(np.float64)
    out = np.full(len(xf), np.nan, np.float64)
    if len(xf) <= period:
        return out
    d = np.diff(xf)
    gain = np.maximum(d, 0.0)
    loss = np.maximum(-d, 0.0)
    ag = float(np.mean(gain[:period]))
    al = float(np.mean(loss[:period]))

    def to_rsi(g: float, l: float) -> float:
        if l == 0.0:
            return 100.0 if g > 0.0 else 50.0
        if g == 0.0:
            return 0.0
        rs = g / l
        return 100.0 - 100.0 / (1.0 + rs)

    out[period] = to_rsi(ag, al)
    for i in range(period + 1, len(xf)):
        ag = ((period - 1) * ag + gain[i - 1]) / period
        al = ((period - 1) * al + loss[i - 1]) / period
        out[i] = to_rsi(ag, al)
    return out


def rsi2_proposals(t, ask, bid, tf_ms: int, persistent: bool):
    b = vce.bars(t, bid, tf_ms)
    close = b["close"].astype(np.float64)
    r2 = rsi_wilder(b["close"], 2)
    ma200 = sma(b["close"], 200)
    props = []

    for k in range(200, len(close)):
        edge = int(b["end_ms"][k])
        if edge > STAGE_A_END_MS:
            break
        if np.isnan(r2[k]) or np.isnan(ma200[k]):
            continue

        side = 0
        if persistent:
            if k >= 2 and np.all(r2[k - 2:k + 1] < 10.0) and close[k] > ma200[k]:
                side = 1
            elif k >= 2 and np.all(r2[k - 2:k + 1] > 90.0) and close[k] < ma200[k]:
                side = -1
        else:
            if r2[k] < 5.0 and close[k] > ma200[k]:
                side = 1
            elif r2[k] > 95.0 and close[k] < ma200[k]:
                side = -1

        if side:
            kind = ("RSI2_PULLBACK3_" if persistent else "RSI2_CLASSIC_") + f"{tf_ms // 60000}M_TREND200"
            props.append(vce.finalize_proposal(t, ask, bid, edge, side, kind, k))

    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return rsi2_proposals(t, ask, bid, 60_000, False)
    if cid == CONFIGS[1]:
        return rsi2_proposals(t, ask, bid, 60_000, True)
    if cid == CONFIGS[2]:
        return rsi2_proposals(t, ask, bid, 300_000, False)
    if cid == CONFIGS[3]:
        return rsi2_proposals(t, ask, bid, 300_000, True)
    raise ValueError(cid)


def supply(props, t):
    return {
        "proposals": len(props),
        "source_eligible": sum(p.eligible for p in props),
        "distinct_days": len({int(t[p.decision_index] // 86_400_000) for p in props if 0 <= p.decision_index < len(t)}),
        "proposal_long": sum(p.side > 0 for p in props),
        "proposal_short": sum(p.side < 0 for p in props),
        "source_rejections": {
            "SPREAD_GATE": sum(p.reason == "SPREAD_GATE" for p in props),
            "NO_EXECUTABLE_TICK": sum(p.reason == "NO_EXECUTABLE_TICK" for p in props),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    sha = val.base.sha256_file(a.source)
    if sha != val.base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: " + sha)

    df = pd.read_csv(
        a.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    df = df[(df.timestamp_ms_utc >= STAGE_A_START_MS) & (df.timestamp_ms_utc < STAGE_A_END_MS)]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit(f"Stage-A chronology mismatch: {t.size}")

    ask, bid = val.base.p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    feat = val.parent.build_parent_features(t, ask, bid)
    streams = val.generate_streams(t, ask, bid)
    d3t, d3s = streams["DH03_S06"]
    d5t, d5s = streams["DH05_S06"]
    s11t, s11s = streams["DH02_S11"]
    s08t, s08s = streams["DH02_S08"]
    zi = np.empty(0, np.int64)
    zs = np.empty(0, np.int8)

    parent = val.pack_sorb(val.run_integrated_sorb(
        t, ask, bid, feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
        d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
        zi, zs, zs, 1, 1, 1, 1, 1,
    ))
    val.parent_gate(parent)

    results = {}
    ranking = []
    for cid in CONFIGS:
        props = generate(t, ask, bid, cid)
        sp = supply(props, t)
        ep = [p for p in props if p.eligible]
        ii = np.asarray([p.decision_index for p in ep], np.int64)
        ss = np.asarray([p.side for p in ep], np.int8)
        sk = np.ones(len(ep), np.int8)

        combined = val.pack_sorb(val.run_integrated_sorb(
            t, ask, bid, feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
            d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
            ii, ss, sk, 1, 1, 1, 1, 1,
        ))
        dec = val.decision(parent, combined, sp)
        lane = combined.pop("sorb_session_contribution")
        combined["rsi2_entries"] = combined.pop("sorb_entries")
        combined["rsi2_net"] = combined.pop("sorb_net")
        combined["rsi2_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_rsi2_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply": sp, "combined": combined, "decision": dec}
        ranking.append((
            int(dec["strong_screen_pass"]),
            int(dec["screen_pass"]),
            float(dec["net_delta"]),
            int(dec["official_win_delta"]),
            int(combined["rsi2_entries"]),
            cid,
        ))

    ranking.sort(reverse=True)
    leaders = [{
        "config_id": x[-1],
        "strong_screen_pass": results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass": results[x[-1]]["decision"]["screen_pass"],
        "net_delta": results[x[-1]]["decision"]["net_delta"],
        "trade_delta": results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta": results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries": results[x[-1]]["combined"]["rsi2_entries"],
        "direct_rsi2_net": results[x[-1]]["combined"]["rsi2_net"],
    } for x in ranking]
    strong = [x for x in leaders if x["strong_screen_pass"]]

    out = {
        "schema": "delta-r037-rsi2-stage-a-screen-17c-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family": "R037-RSI2-v1",
        "parent_checkpoint": "R037_DCB_STAGE_A_SCREEN_CHECKPOINT_17B",
        "surrogate_parent": "14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable": False,
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "indicator_semantics": "Wilder RSI2 and SMA200 on completed Bid closes",
        "numeric_retuning": False,
        "post_result_retuning": False,
        "august_accessed": False,
        "parent_control": parent,
        "configs": results,
        "ranking": leaders,
        "finding": {
            "strong_screen_survivors": [x["config_id"] for x in strong],
            "leading_config": leaders[0]["config_id"],
            "next": "R037_RSI2_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        },
        "mql5_authorized": False,
    }
    val.base.atomic_write_json(a.output, out)
    print(json.dumps({"ranking": leaders, "finding": out["finding"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
