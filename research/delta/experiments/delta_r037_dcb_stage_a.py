"""DELTA R037 Donchian confirmed-close breakout Stage-A screen.

Four source-grounded variants are frozen before compute:
- M1 previous-20-bar channel breakout close, raw and EMA200-aligned.
- M5 previous-20-bar channel breakout close, raw and EMA200-aligned.

No session clock, prior-day level, volatility-compression prerequisite, volume input,
post-result tuning, August access, or MQL5 work is allowed in this unit.
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
MAX_SPREAD_RAW = vce.MAX_SPREAD_RAW

CONFIGS = (
    "R037-DCB-C01_M1_DONCHIAN20",
    "R037-DCB-C02_M1_DONCHIAN20_EMA200",
    "R037-DCB-C03_M5_DONCHIAN20",
    "R037-DCB-C04_M5_DONCHIAN20_EMA200",
)


def channel_proposals(t, ask, bid, tf_ms: int, use_ema: bool):
    b = vce.bars(t, bid, tf_ms)
    e200 = vce.ema(b["close"], 200)
    props = []
    for k in range(20, len(b["close"])):
        edge = int(b["end_ms"][k])
        if edge > STAGE_A_END_MS:
            break
        prev_hi = int(np.max(b["high"][k - 20:k]))
        prev_lo = int(np.min(b["low"][k - 20:k]))
        c = int(b["close"][k])
        side = 1 if c > prev_hi else (-1 if c < prev_lo else 0)
        if side == 0:
            continue
        source_ok = True
        reason = "ELIGIBLE"
        if use_ema:
            if np.isnan(e200[k]):
                source_ok = False
                reason = "EMA_NOT_READY"
            elif (side > 0 and c <= e200[k]) or (side < 0 and c >= e200[k]):
                source_ok = False
                reason = "EMA200_DIRECTION"
        props.append(vce.finalize_proposal(
            t, ask, bid, edge, side,
            f"DONCHIAN20_{tf_ms // 60000}M" + ("_EMA200" if use_ema else ""),
            k, source_ok, reason,
        ))
    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return channel_proposals(t, ask, bid, 60_000, False)
    if cid == CONFIGS[1]:
        return channel_proposals(t, ask, bid, 60_000, True)
    if cid == CONFIGS[2]:
        return channel_proposals(t, ask, bid, 300_000, False)
    if cid == CONFIGS[3]:
        return channel_proposals(t, ask, bid, 300_000, True)
    raise ValueError(cid)


def supply(props, t):
    reasons = ("EMA_NOT_READY", "EMA200_DIRECTION", "SPREAD_GATE", "NO_EXECUTABLE_TICK")
    return {
        "proposals": len(props),
        "source_eligible": sum(p.eligible for p in props),
        "distinct_days": len({int(t[p.decision_index] // 86_400_000) for p in props if 0 <= p.decision_index < len(t)}),
        "proposal_long": sum(p.side > 0 for p in props),
        "proposal_short": sum(p.side < 0 for p in props),
        "source_rejections": {r: sum(p.reason == r for p in props) for r in reasons},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    sha = val.base.sha256_file(a.source)
    if sha != val.base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: " + sha)

    df = pd.read_csv(a.source, compression="gzip", usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"], dtype=np.int64)
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
        combined["dcb_entries"] = combined.pop("sorb_entries")
        combined["dcb_net"] = combined.pop("sorb_net")
        combined["dcb_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_dcb_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply": sp, "combined": combined, "decision": dec}
        ranking.append((int(dec["strong_screen_pass"]), int(dec["screen_pass"]), float(dec["net_delta"]), int(dec["official_win_delta"]), int(combined["dcb_entries"]), cid))

    ranking.sort(reverse=True)
    leaders = [{
        "config_id": x[-1],
        "strong_screen_pass": results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass": results[x[-1]]["decision"]["screen_pass"],
        "net_delta": results[x[-1]]["decision"]["net_delta"],
        "trade_delta": results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta": results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries": results[x[-1]]["combined"]["dcb_entries"],
        "direct_dcb_net": results[x[-1]]["combined"]["dcb_net"],
    } for x in ranking]
    strong = [x for x in leaders if x["strong_screen_pass"]]
    out = {
        "schema": "delta-r037-dcb-stage-a-screen-17b-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family": "R037-DCB-v1",
        "parent_checkpoint": "R037_VCE_STAGE_A_SCREEN_CHECKPOINT_17A",
        "surrogate_parent": "14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable": False,
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning": False,
        "post_result_retuning": False,
        "august_accessed": False,
        "parent_control": parent,
        "configs": results,
        "ranking": leaders,
        "finding": {
            "strong_screen_survivors": [x["config_id"] for x in strong],
            "leading_config": leaders[0]["config_id"],
            "next": "R037_DCB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        },
        "mql5_authorized": False,
    }
    val.base.atomic_write_json(a.output, out)
    print(json.dumps({"ranking": leaders, "finding": out["finding"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
