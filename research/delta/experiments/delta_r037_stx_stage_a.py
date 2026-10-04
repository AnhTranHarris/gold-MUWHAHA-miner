"""DELTA R037 stochastic transition-confirmation Stage-A screen.

Frozen before compute:
- Slow stochastic 14/3/3 from completed Bid bars.
- M1/M5 %D exit from 20/80.
- M1/M5 %K/%D crossover while %D remains in the 20/80 extreme zone.
- No parameter retuning, trend/session filter, prior-day level, compression,
  Donchian logic, RSI entry state, August access, or MQL5 work.
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
    "R037-STX-C01_M1_D_EXIT20_80",
    "R037-STX-C02_M1_KD_CROSS_EXTREME",
    "R037-STX-C03_M5_D_EXIT20_80",
    "R037-STX-C04_M5_KD_CROSS_EXTREME",
)


def sma_nan(x: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(x), np.nan, np.float64)
    for i in range(period - 1, len(x)):
        w = x[i - period + 1:i + 1]
        if not np.any(np.isnan(w)):
            out[i] = float(np.mean(w))
    return out


def stochastic_slow(b, k_period=14, d_period=3, slowing=3):
    h = b["high"].astype(np.float64)
    l = b["low"].astype(np.float64)
    c = b["close"].astype(np.float64)
    raw = np.full(len(c), np.nan, np.float64)
    for i in range(k_period - 1, len(c)):
        hh = float(np.max(h[i - k_period + 1:i + 1]))
        ll = float(np.min(l[i - k_period + 1:i + 1]))
        den = hh - ll
        raw[i] = 50.0 if den <= 0.0 else 100.0 * (c[i] - ll) / den
    slow_k = sma_nan(raw, slowing)
    d = sma_nan(slow_k, d_period)
    return slow_k, d


def transition_proposals(t, ask, bid, tf_ms: int, cross_mode: bool):
    b = vce.bars(t, bid, tf_ms)
    k, d = stochastic_slow(b)
    props = []
    for i in range(1, len(d)):
        edge = int(b["end_ms"][i])
        if edge > STAGE_A_END_MS:
            break
        if np.isnan(k[i]) or np.isnan(k[i - 1]) or np.isnan(d[i]) or np.isnan(d[i - 1]):
            continue
        side = 0
        if cross_mode:
            if k[i - 1] <= d[i - 1] and k[i] > d[i] and d[i] < 20.0:
                side = 1
            elif k[i - 1] >= d[i - 1] and k[i] < d[i] and d[i] > 80.0:
                side = -1
            kind = f"STX_KD_CROSS_EXTREME_{tf_ms // 60000}M"
        else:
            if d[i - 1] < 20.0 and d[i] >= 20.0:
                side = 1
            elif d[i - 1] > 80.0 and d[i] <= 80.0:
                side = -1
            kind = f"STX_D_EXIT20_80_{tf_ms // 60000}M"
        if side:
            props.append(vce.finalize_proposal(t, ask, bid, edge, side, kind, i))
    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return transition_proposals(t, ask, bid, 60_000, False)
    if cid == CONFIGS[1]:
        return transition_proposals(t, ask, bid, 60_000, True)
    if cid == CONFIGS[2]:
        return transition_proposals(t, ask, bid, 300_000, False)
    if cid == CONFIGS[3]:
        return transition_proposals(t, ask, bid, 300_000, True)
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
    d3t, d3s = streams["DH03_S06"]; d5t, d5s = streams["DH05_S06"]
    s11t, s11s = streams["DH02_S11"]; s08t, s08s = streams["DH02_S08"]
    zi = np.empty(0, np.int64); zs = np.empty(0, np.int8)

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
        combined["stx_entries"] = combined.pop("sorb_entries")
        combined["stx_net"] = combined.pop("sorb_net")
        combined["stx_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_stx_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply":sp,"combined":combined,"decision":dec}
        ranking.append((int(dec["strong_screen_pass"]),int(dec["screen_pass"]),float(dec["net_delta"]),int(dec["official_win_delta"]),int(combined["stx_entries"]),cid))

    ranking.sort(reverse=True)
    leaders=[{
        "config_id":x[-1],
        "strong_screen_pass":results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass":results[x[-1]]["decision"]["screen_pass"],
        "net_delta":results[x[-1]]["decision"]["net_delta"],
        "trade_delta":results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta":results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries":results[x[-1]]["combined"]["stx_entries"],
        "direct_stx_net":results[x[-1]]["combined"]["stx_net"],
    } for x in ranking]
    strong=[x for x in leaders if x["strong_screen_pass"]]

    out={
        "schema":"delta-r037-stx-stage-a-screen-17d-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family":"R037-STX-v1",
        "parent_checkpoint":"R037_RSI2_STAGE_A_SCREEN_CHECKPOINT_17C",
        "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable":False,
        "source_sha256":sha,
        "stage_a_ticks":int(t.size),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "indicator_semantics":"slow stochastic 14/3/3 on completed Bid bars",
        "numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,
        "parent_control":parent,
        "configs":results,
        "ranking":leaders,
        "finding":{"strong_screen_survivors":[x["config_id"] for x in strong],"leading_config":leaders[0]["config_id"],"next":"R037_STX_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
        "mql5_authorized":False,
    }
    val.base.atomic_write_json(a.output,out)
    print(json.dumps({"ranking":leaders,"finding":out["finding"]},separators=(",",":")))


if __name__=="__main__":
    main()
