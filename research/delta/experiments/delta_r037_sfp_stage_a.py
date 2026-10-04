"""DELTA R037 local swing-failure-pattern Stage-A screen — Checkpoint 17F.

Frozen before compute:
- Completed Bid bars only.
- Symmetric two-bar confirmed swing highs/lows; swing revealed only after two
  completed right-side bars.
- Bearish SFP: completed bar high > active swing high AND close < swing high.
- Bullish SFP: completed bar low < active swing low AND close > swing low.
- Each active swing identity is consumed on the first beyond-level interaction,
  whether it becomes a rejection or a true close-through breakout.
- Strong-half variants additionally require the SFP close to finish in the
  reversal half of the sweep candle.
- If a single bar validly sweeps both active sides, both identities are consumed
  and no ambiguous proposal is emitted.
- M1/M5 x BASIC/HALF_REJECTION are the only preregistered configurations.
- No threshold retuning, FVG/BOS dependency, session filter, previous-day level,
  compression, Donchian, oscillator, August access, or MQL5 work.
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
    "R037-SFP-C01_M1_BASIC",
    "R037-SFP-C02_M1_HALF_REJECTION",
    "R037-SFP-C03_M5_BASIC",
    "R037-SFP-C04_M5_HALF_REJECTION",
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


def sfp_proposals(t, ask, bid, tf_ms: int, strong_half: bool):
    b = vce.bars(t, bid, tf_ms)
    h, l, c, e = b["high"], b["low"], b["close"], b["end_ms"]

    latest_hi = 0
    latest_lo = 0
    latest_hi_id = -1
    latest_lo_id = -1
    consumed_hi_id = -1
    consumed_lo_id = -1
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

        hi_touch = latest_hi_id >= 0 and latest_hi_id != consumed_hi_id and int(h[i]) > latest_hi
        lo_touch = latest_lo_id >= 0 and latest_lo_id != consumed_lo_id and int(l[i]) < latest_lo

        bear = hi_touch and int(c[i]) < latest_hi
        bull = lo_touch and int(c[i]) > latest_lo

        if hi_touch:
            consumed_hi_id = latest_hi_id
        if lo_touch:
            consumed_lo_id = latest_lo_id

        # Ambiguous two-sided rejection bar: consume touched identities, emit none.
        if bull and bear:
            continue

        if bear:
            if strong_half and float(c[i]) > (float(h[i]) + float(l[i])) / 2.0:
                continue
            kind = f"SFP_{'HALF' if strong_half else 'BASIC'}_{tf_ms // 60000}M"
            props.append(vce.finalize_proposal(t, ask, bid, edge, -1, kind, i))
        elif bull:
            if strong_half and float(c[i]) < (float(h[i]) + float(l[i])) / 2.0:
                continue
            kind = f"SFP_{'HALF' if strong_half else 'BASIC'}_{tf_ms // 60000}M"
            props.append(vce.finalize_proposal(t, ask, bid, edge, 1, kind, i))

    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return sfp_proposals(t, ask, bid, 60_000, False)
    if cid == CONFIGS[1]:
        return sfp_proposals(t, ask, bid, 60_000, True)
    if cid == CONFIGS[2]:
        return sfp_proposals(t, ask, bid, 300_000, False)
    if cid == CONFIGS[3]:
        return sfp_proposals(t, ask, bid, 300_000, True)
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
        combined["sfp_entries"] = combined.pop("sorb_entries")
        combined["sfp_net"] = combined.pop("sorb_net")
        combined["sfp_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_sfp_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply":sp,"combined":combined,"decision":dec}
        ranking.append((int(dec["strong_screen_pass"]),int(dec["screen_pass"]),float(dec["net_delta"]),int(dec["official_win_delta"]),int(combined["sfp_entries"]),cid))

    ranking.sort(reverse=True)
    leaders=[{
        "config_id":x[-1],
        "strong_screen_pass":results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass":results[x[-1]]["decision"]["screen_pass"],
        "net_delta":results[x[-1]]["decision"]["net_delta"],
        "trade_delta":results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta":results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries":results[x[-1]]["combined"]["sfp_entries"],
        "direct_sfp_net":results[x[-1]]["combined"]["sfp_net"],
    } for x in ranking]
    strong=[x for x in leaders if x["strong_screen_pass"]]

    out={
        "schema":"delta-r037-sfp-stage-a-screen-17f-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family":"R037-SFP-v1",
        "parent_checkpoint":"R037_MSF_STAGE_A_SCREEN_CHECKPOINT_17E",
        "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable":False,
        "source_sha256":sha,
        "stage_a_ticks":int(t.size),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "sfp_semantics":"two-bar confirmed fractal swing; wick-only beyond active swing; completed close back inside; optional reversal-half close",
        "numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,
        "parent_control":parent,
        "configs":results,
        "ranking":leaders,
        "finding":{"strong_screen_survivors":[x["config_id"] for x in strong],"leading_config":leaders[0]["config_id"],"next":"R037_SFP_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
        "mql5_authorized":False,
    }
    val.base.atomic_write_json(a.output,out)
    print(json.dumps({"ranking":leaders,"finding":out["finding"]},separators=(",",":")))


if __name__=="__main__":
    main()
