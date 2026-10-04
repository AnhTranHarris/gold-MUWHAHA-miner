"""DELTA R037 SMOR + FVG confluence Stage-A screen — Checkpoint 17I.

This producer preserves the exact 17H C02 M1 midpoint lifecycle and adds only the
four preregistered same-direction FVG context rules. No parameter tuning, session
filter, side split, exit change, August access, or MQL5.
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
    "R037-SFOC-C01_ANY_ACTIVE_FVG",
    "R037-SFOC-C02_MSS_OR_NEXT_FVG",
    "R037-SFOC-C03_OB_FVG_OVERLAP",
    "R037-SFOC-C04_RETEST_TOUCHES_FVG",
)


def swing_high(h, k, w=2):
    if k < w or k + w >= len(h):
        return False
    x = h[k]
    return all(x > h[k-j] and x > h[k+j] for j in range(1, w+1))


def swing_low(l, k, w=2):
    if k < w or k + w >= len(l):
        return False
    x = l[k]
    return all(x < l[k-j] and x < l[k+j] for j in range(1, w+1))


def last_opposite_bar(o, c, lo_exclusive, hi_exclusive, shift_side):
    for j in range(hi_exclusive - 1, lo_exclusive, -1):
        if shift_side > 0 and int(c[j]) < int(o[j]):
            return j
        if shift_side < 0 and int(c[j]) > int(o[j]):
            return j
    return -1


def overlap(a0, a1, b0, b1):
    return max(a0, b0) <= min(a1, b1)


def generate_proposals(t, ask, bid, mode):
    b = vce.bars(t, bid, 60_000)
    o, h, l, c, e = b["open"], b["high"], b["low"], b["close"], b["end_ms"]

    latest_hi = latest_lo = 0
    latest_hi_id = latest_lo_id = -1
    pending_bear = pending_bull = None
    # zone = (mss_idx, sweep_idx, ob_idx, zlo, zhi)
    zone_bear = zone_bull = None

    # FVG tuple = (create_idx, low_edge, high_edge), retained until fully mitigated.
    bull_fvgs = []
    bear_fvgs = []
    props = []

    for i in range(len(c)):
        edge = int(e[i])
        if edge > STAGE_A_END_MS:
            break

        # Causal swing reveal.
        p = i - 2
        if p >= 2:
            if swing_high(h, p, 2):
                latest_hi, latest_hi_id = int(h[p]), p
            if swing_low(l, p, 2):
                latest_lo, latest_lo_id = int(l[p]), p

        # Retire previously created FVGs only when a later completed bar fully fills.
        if bull_fvgs:
            bull_fvgs = [z for z in bull_fvgs if not (i > z[0] and int(l[i]) <= z[1])]
        if bear_fvgs:
            bear_fvgs = [z for z in bear_fvgs if not (i > z[0] and int(h[i]) >= z[2])]

        # Detect FVG created by the current completed bar; it is visible at this edge.
        if i >= 2:
            if int(l[i]) > int(h[i-2]):
                bull_fvgs.append((i, int(h[i-2]), int(l[i])))
            if int(h[i]) < int(l[i-2]):
                bear_fvgs.append((i, int(h[i]), int(l[i-2])))

        candidates = []

        # Preserve exact 17H C02 first-body-interaction + midpoint requirement.
        if zone_bear is not None and i > zone_bear[0]:
            mss_idx, sweep_idx, ob_idx, zlo, zhi = zone_bear
            mid = (zlo + zhi) / 2.0
            touch = int(h[i]) >= zlo and int(l[i]) <= zhi
            if touch:
                base_valid = int(l[i]) <= mid <= int(h[i]) and int(c[i]) <= mid and int(c[i]) >= zlo
                eligible_fvgs = [z for z in bear_fvgs if z[0] > sweep_idx and z[0] <= i]
                fvg_ok = False
                if mode == 0:
                    fvg_ok = bool(eligible_fvgs)
                elif mode == 1:
                    fvg_ok = any(z[0] in (mss_idx, mss_idx + 1) for z in eligible_fvgs)
                elif mode == 2:
                    fvg_ok = any(overlap(zlo, zhi, z[1], z[2]) for z in eligible_fvgs)
                else:
                    fvg_ok = any(int(h[i]) >= z[1] and int(l[i]) <= z[2] for z in eligible_fvgs)
                if base_valid and fvg_ok:
                    candidates.append((-1, ob_idx))
                zone_bear = None

        if zone_bull is not None and i > zone_bull[0]:
            mss_idx, sweep_idx, ob_idx, zlo, zhi = zone_bull
            mid = (zlo + zhi) / 2.0
            touch = int(h[i]) >= zlo and int(l[i]) <= zhi
            if touch:
                base_valid = int(l[i]) <= mid <= int(h[i]) and int(c[i]) >= mid and int(c[i]) <= zhi
                eligible_fvgs = [z for z in bull_fvgs if z[0] > sweep_idx and z[0] <= i]
                fvg_ok = False
                if mode == 0:
                    fvg_ok = bool(eligible_fvgs)
                elif mode == 1:
                    fvg_ok = any(z[0] in (mss_idx, mss_idx + 1) for z in eligible_fvgs)
                elif mode == 2:
                    fvg_ok = any(overlap(zlo, zhi, z[1], z[2]) for z in eligible_fvgs)
                else:
                    fvg_ok = any(int(h[i]) >= z[1] and int(l[i]) <= z[2] for z in eligible_fvgs)
                if base_valid and fvg_ok:
                    candidates.append((1, ob_idx))
                zone_bull = None

        # Pending sweep -> frozen-opposite-swing MSS -> OB.
        if pending_bear is not None and zone_bear is None:
            sw_idx, mss_level = pending_bear
            if i > sw_idx and int(c[i]) < mss_level:
                ob = last_opposite_bar(o, c, sw_idx, i, -1)
                if ob >= 0:
                    zlo, zhi = min(int(o[ob]), int(c[ob])), max(int(o[ob]), int(c[ob]))
                    if zhi > zlo:
                        zone_bear = (i, sw_idx, ob, zlo, zhi)
                pending_bear = None

        if pending_bull is not None and zone_bull is None:
            sw_idx, mss_level = pending_bull
            if i > sw_idx and int(c[i]) > mss_level:
                ob = last_opposite_bar(o, c, sw_idx, i, 1)
                if ob >= 0:
                    zlo, zhi = min(int(o[ob]), int(c[ob])), max(int(o[ob]), int(c[ob]))
                    if zhi > zlo:
                        zone_bull = (i, sw_idx, ob, zlo, zhi)
                pending_bull = None

        # New sweep / same-direction pending supersession.
        bear_sweep = (
            zone_bear is None and latest_hi_id >= 0 and latest_lo_id >= 0
            and int(h[i]) > latest_hi and int(c[i]) < latest_hi
        )
        bull_sweep = (
            zone_bull is None and latest_lo_id >= 0 and latest_hi_id >= 0
            and int(l[i]) < latest_lo and int(c[i]) > latest_lo
        )
        if bear_sweep and bull_sweep:
            pending_bear = pending_bull = None
        else:
            if bear_sweep:
                pending_bear = (i, latest_lo)
            if bull_sweep:
                pending_bull = (i, latest_hi)

        if len(candidates) == 1:
            side, ob_idx = candidates[0]
            props.append(vce.finalize_proposal(
                t, ask, bid, edge, side, CONFIGS[mode], ob_idx
            ))

    return props


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
        d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,zi,zs,zs,1,1,1,1,1
    ))
    val.parent_gate(parent)

    results = {}; ranking = []
    for mode, cid in enumerate(CONFIGS):
        props = generate_proposals(t, ask, bid, mode)
        sp = supply(props, t)
        ep = [p for p in props if p.eligible]
        ii = np.asarray([p.decision_index for p in ep], np.int64)
        ss = np.asarray([p.side for p in ep], np.int8)
        sk = np.ones(len(ep), np.int8)
        combined = val.pack_sorb(val.run_integrated_sorb(
            t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
            d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,ii,ss,sk,1,1,1,1,1
        ))
        dec = val.decision(parent, combined, sp)
        lane = combined.pop("sorb_session_contribution")
        combined["sfoc_entries"] = combined.pop("sorb_entries")
        combined["sfoc_net"] = combined.pop("sorb_net")
        combined["sfoc_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_sfoc_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply":sp,"combined":combined,"decision":dec}
        ranking.append((int(dec["strong_screen_pass"]),int(dec["screen_pass"]),float(dec["net_delta"]),int(dec["official_win_delta"]),int(combined["sfoc_entries"]),cid))

    ranking.sort(reverse=True)
    leaders=[{
        "config_id":x[-1],
        "strong_screen_pass":results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass":results[x[-1]]["decision"]["screen_pass"],
        "net_delta":results[x[-1]]["decision"]["net_delta"],
        "trade_delta":results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta":results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries":results[x[-1]]["combined"]["sfoc_entries"],
        "direct_sfoc_net":results[x[-1]]["combined"]["sfoc_net"],
    } for x in ranking]
    strong=[x for x in leaders if x["strong_screen_pass"]]

    out={
        "schema":"delta-r037-sfoc-stage-a-screen-17i-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family":"R037-SFOC-v1",
        "parent_checkpoint":"R037_SMOR_STAGE_A_SCREEN_CHECKPOINT_17H",
        "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable":False,
        "source_sha256":sha,"stage_a_ticks":int(t.size),"surface":"DUKAS_COINEXX_LIKE_P75",
        "base":"exact 17H C02 SMOR M1 midpoint lifecycle + preregistered same-direction FVG confluence only",
        "numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,
        "parent_control":parent,"configs":results,"ranking":leaders,
        "finding":{"strong_screen_survivors":[x["config_id"] for x in strong],"leading_config":leaders[0]["config_id"],"next":"R037_SFOC_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
        "mql5_authorized":False,
    }
    val.base.atomic_write_json(a.output,out)
    print(json.dumps({"ranking":leaders,"finding":out["finding"]},separators=(",",":")))


if __name__=="__main__":
    main()
