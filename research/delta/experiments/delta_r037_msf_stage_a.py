"""DELTA R037 market-structure + fair-value-gap retest Stage-A screen.

Frozen before compute:
- Completed Bid bars only.
- Symmetric two-bar confirmed swing highs/lows (five-bar fractal).
- Close-confirmed break of the latest revealed swing.
- Structure classification: CHOCH when break side opposes the previous confirmed
  structure-break side; BOS when it agrees. Initial unclassified breaks establish
  state but do not generate proposals.
- Standard three-candle fair-value gap on the same completed break bar:
    bullish: high[i-2] < low[i]
    bearish: low[i-2] > high[i]
- First later completed-bar retest of the gap must close back through the gap's
  consequent-encroachment midpoint in the structural direction.
- The gap event remains armed until confirmed, fully invalidated through its far
  boundary, superseded by a newer same-side qualifying structure/FVG event, or an
  opposite confirmed structure break.
- M1/M5 x CHOCH/BOS form the four preregistered configurations.
- No numeric threshold retuning, session filter, oscillator, Donchian, volatility-
  compression, previous-day level, August access, or MQL5 work.
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
    "R037-MSF-C01_M1_CHOCH_FVG_RETEST",
    "R037-MSF-C02_M1_BOS_FVG_RETEST",
    "R037-MSF-C03_M5_CHOCH_FVG_RETEST",
    "R037-MSF-C04_M5_BOS_FVG_RETEST",
)


def is_swing_high(h: np.ndarray, k: int, w: int = 2) -> bool:
    if k < w or k + w >= len(h):
        return False
    x = h[k]
    for j in range(1, w + 1):
        if not (x > h[k-j] and x > h[k+j]):
            return False
    return True


def is_swing_low(l: np.ndarray, k: int, w: int = 2) -> bool:
    if k < w or k + w >= len(l):
        return False
    x = l[k]
    for j in range(1, w + 1):
        if not (x < l[k-j] and x < l[k+j]):
            return False
    return True


def structure_fvg_proposals(t, ask, bid, tf_ms: int, wanted_kind: str):
    b = vce.bars(t, bid, tf_ms)
    h = b["high"]
    l = b["low"]
    c = b["close"]
    e = b["end_ms"]

    latest_hi = 0
    latest_lo = 0
    latest_hi_id = -1
    latest_lo_id = -1
    broken_hi_id = -1
    broken_lo_id = -1
    last_break_side = 0

    active_long = None
    active_short = None
    props = []

    for i in range(len(c)):
        edge = int(e[i])
        if edge > STAGE_A_END_MS:
            break

        p = i - 2
        if p >= 2:
            if is_swing_high(h, p, 2):
                latest_hi = int(h[p])
                latest_hi_id = p
            if is_swing_low(l, p, 2):
                latest_lo = int(l[p])
                latest_lo_id = p

        if active_long is not None:
            eb, lower, upper, skind = active_long
            if i > eb:
                mid = (lower + upper) / 2.0
                if int(c[i]) < lower:
                    active_long = None
                elif int(l[i]) <= upper and int(h[i]) >= lower and float(c[i]) >= mid:
                    if skind == wanted_kind:
                        kind = f"MSF_{wanted_kind}_FVG_RETEST_{tf_ms // 60000}M"
                        props.append(vce.finalize_proposal(t, ask, bid, edge, 1, kind, i))
                    active_long = None

        if active_short is not None:
            eb, lower, upper, skind = active_short
            if i > eb:
                mid = (lower + upper) / 2.0
                if int(c[i]) > upper:
                    active_short = None
                elif int(h[i]) >= lower and int(l[i]) <= upper and float(c[i]) <= mid:
                    if skind == wanted_kind:
                        kind = f"MSF_{wanted_kind}_FVG_RETEST_{tf_ms // 60000}M"
                        props.append(vce.finalize_proposal(t, ask, bid, edge, -1, kind, i))
                    active_short = None

        side = 0
        if latest_hi_id >= 0 and latest_hi_id != broken_hi_id and int(c[i]) > latest_hi:
            side = 1
            broken_hi_id = latest_hi_id
        elif latest_lo_id >= 0 and latest_lo_id != broken_lo_id and int(c[i]) < latest_lo:
            side = -1
            broken_lo_id = latest_lo_id

        if side == 0:
            continue

        if last_break_side == 0:
            skind = "INIT"
        elif side == last_break_side:
            skind = "BOS"
        else:
            skind = "CHOCH"

        if side > 0:
            active_short = None
        else:
            active_long = None

        if i >= 2 and skind != "INIT":
            if side > 0 and int(h[i-2]) < int(l[i]):
                lower = int(h[i-2])
                upper = int(l[i])
                active_long = (i, lower, upper, skind)
            elif side < 0 and int(l[i-2]) > int(h[i]):
                lower = int(h[i])
                upper = int(l[i-2])
                active_short = (i, lower, upper, skind)

        last_break_side = side

    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return structure_fvg_proposals(t, ask, bid, 60_000, "CHOCH")
    if cid == CONFIGS[1]:
        return structure_fvg_proposals(t, ask, bid, 60_000, "BOS")
    if cid == CONFIGS[2]:
        return structure_fvg_proposals(t, ask, bid, 300_000, "CHOCH")
    if cid == CONFIGS[3]:
        return structure_fvg_proposals(t, ask, bid, 300_000, "BOS")
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

    df = pd.read_csv(a.source, compression="gzip", usecols=["timestamp_ms_utc","ask_raw","bid_raw"], dtype=np.int64)
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
        t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
        d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,zi,zs,zs,1,1,1,1,1,
    ))
    val.parent_gate(parent)

    results = {}
    ranking = []
    for cid in CONFIGS:
        props = generate(t,ask,bid,cid)
        sp = supply(props,t)
        ep = [p for p in props if p.eligible]
        ii = np.asarray([p.decision_index for p in ep],np.int64)
        ss = np.asarray([p.side for p in ep],np.int8)
        sk = np.ones(len(ep),np.int8)
        combined = val.pack_sorb(val.run_integrated_sorb(
            t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
            d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,ii,ss,sk,1,1,1,1,1,
        ))
        dec = val.decision(parent,combined,sp)
        lane = combined.pop("sorb_session_contribution")
        combined["msf_entries"] = combined.pop("sorb_entries")
        combined["msf_net"] = combined.pop("sorb_net")
        combined["msf_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_msf_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply":sp,"combined":combined,"decision":dec}
        ranking.append((int(dec["strong_screen_pass"]),int(dec["screen_pass"]),float(dec["net_delta"]),int(dec["official_win_delta"]),int(combined["msf_entries"]),cid))

    ranking.sort(reverse=True)
    leaders=[{
        "config_id":x[-1],
        "strong_screen_pass":results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass":results[x[-1]]["decision"]["screen_pass"],
        "net_delta":results[x[-1]]["decision"]["net_delta"],
        "trade_delta":results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta":results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries":results[x[-1]]["combined"]["msf_entries"],
        "direct_msf_net":results[x[-1]]["combined"]["msf_net"],
    } for x in ranking]
    strong=[x for x in leaders if x["strong_screen_pass"]]

    out={
        "schema":"delta-r037-msf-stage-a-screen-17e-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family":"R037-MSF-v1",
        "parent_checkpoint":"R037_STX_STAGE_A_SCREEN_CHECKPOINT_17D",
        "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable":False,
        "source_sha256":sha,
        "stage_a_ticks":int(t.size),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "structure_semantics":"two-bar confirmed fractal swing; close-confirmed CHOCH/BOS; same-break-bar 3-candle FVG; first later midpoint-confirmed retest",
        "numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,
        "parent_control":parent,
        "configs":results,
        "ranking":leaders,
        "finding":{"strong_screen_survivors":[x["config_id"] for x in strong],"leading_config":leaders[0]["config_id"],"next":"R037_MSF_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
        "mql5_authorized":False,
    }
    val.base.atomic_write_json(a.output,out)
    print(json.dumps({"ranking":leaders,"finding":out["finding"]},separators=(",",":")))


if __name__=="__main__":
    main()
