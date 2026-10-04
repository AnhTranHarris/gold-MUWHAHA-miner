"""DELTA R037 sweep -> MSS -> order-block retest Stage-A screen — Checkpoint 17H.

Frozen before official compute:
- symmetric width-2 confirmed swings, revealed only after two completed right bars;
- wick sweep + close back inside active confirmed swing;
- after sweep, MSS is first later completed close through the opposite swing that
  was already visible at sweep time;
- OB = last opposite-colour completed candle strictly after sweep and before MSS;
  body zone only;
- per direction newest pending sweep supersedes older pending sweep;
- active OB owns its direction until first interaction/invalidation;
- first later body interaction consumes the OB;
- body-touch variants require directional close beyond OB midpoint;
- midpoint variants additionally require that same first interaction to reach midpoint;
- opposite-direction same-bar proposal collision emits none;
- M1/M5 x BODY_TOUCH/MIDPOINT are the only frozen configs;
- no tuning, session/side slicing, merge, exit changes, August, or MQL5.
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
    "R037-SMOR-C01_M1_BODY_TOUCH",
    "R037-SMOR-C02_M1_MIDPOINT",
    "R037-SMOR-C03_M5_BODY_TOUCH",
    "R037-SMOR-C04_M5_MIDPOINT",
)


def swing_high(h: np.ndarray, k: int, w: int = 2) -> bool:
    if k < w or k + w >= len(h):
        return False
    x = h[k]
    return all(x > h[k-j] and x > h[k+j] for j in range(1, w + 1))


def swing_low(l: np.ndarray, k: int, w: int = 2) -> bool:
    if k < w or k + w >= len(l):
        return False
    x = l[k]
    return all(x < l[k-j] and x < l[k+j] for j in range(1, w + 1))


def last_opposite_bar(o, c, lo_exclusive: int, hi_exclusive: int, shift_side: int) -> int:
    """Last opposite-colour bar strictly inside (lo_exclusive, hi_exclusive)."""
    for j in range(hi_exclusive - 1, lo_exclusive, -1):
        if shift_side > 0 and int(c[j]) < int(o[j]):   # bullish shift -> bearish OB
            return j
        if shift_side < 0 and int(c[j]) > int(o[j]):   # bearish shift -> bullish OB
            return j
    return -1


def smor_proposals(t, ask, bid, tf_ms: int, require_midpoint: bool):
    b = vce.bars(t, bid, tf_ms)
    o, h, l, c, e = b["open"], b["high"], b["low"], b["close"], b["end_ms"]

    latest_hi = 0
    latest_lo = 0
    latest_hi_id = -1
    latest_lo_id = -1

    # pending = [sweep_index, frozen opposite-swing level, frozen opposite-swing id]
    pending_bear = None
    pending_bull = None

    # active zone = [mss_index, ob_index, body_low, body_high]
    zone_bear = None
    zone_bull = None

    props = []

    for i in range(len(c)):
        edge = int(e[i])
        if edge > STAGE_A_END_MS:
            break

        # Reveal only swings that are causally confirmed at this completed-bar edge.
        p = i - 2
        if p >= 2:
            if swing_high(h, p, 2):
                latest_hi = int(h[p])
                latest_hi_id = p
            if swing_low(l, p, 2):
                latest_lo = int(l[p])
                latest_lo_id = p

        candidates = []

        # 1) Existing active zones get first ownership of this bar.
        if zone_bear is not None and i > zone_bear[0]:
            _, ob_idx, zlo, zhi = zone_bear
            mid = (zlo + zhi) / 2.0
            touch = int(h[i]) >= zlo and int(l[i]) <= zhi
            if touch:
                valid = int(c[i]) <= mid and int(c[i]) >= zlo
                if require_midpoint:
                    valid = valid and int(l[i]) <= mid <= int(h[i])
                if valid:
                    candidates.append((-1, ob_idx))
                zone_bear = None

        if zone_bull is not None and i > zone_bull[0]:
            _, ob_idx, zlo, zhi = zone_bull
            mid = (zlo + zhi) / 2.0
            touch = int(h[i]) >= zlo and int(l[i]) <= zhi
            if touch:
                valid = int(c[i]) >= mid and int(c[i]) <= zhi
                if require_midpoint:
                    valid = valid and int(l[i]) <= mid <= int(h[i])
                if valid:
                    candidates.append((1, ob_idx))
                zone_bull = None

        # 2) Pending sweeps may mature into MSS + OB, but not retest on the MSS bar.
        if pending_bear is not None and zone_bear is None:
            sw_idx, mss_level, _ = pending_bear
            if i > sw_idx and int(c[i]) < mss_level:
                ob = last_opposite_bar(o, c, sw_idx, i, -1)
                if ob >= 0:
                    zlo = min(int(o[ob]), int(c[ob]))
                    zhi = max(int(o[ob]), int(c[ob]))
                    if zhi > zlo:
                        zone_bear = (i, ob, zlo, zhi)
                pending_bear = None

        if pending_bull is not None and zone_bull is None:
            sw_idx, mss_level, _ = pending_bull
            if i > sw_idx and int(c[i]) > mss_level:
                ob = last_opposite_bar(o, c, sw_idx, i, 1)
                if ob >= 0:
                    zlo = min(int(o[ob]), int(c[ob]))
                    zhi = max(int(o[ob]), int(c[ob]))
                    if zhi > zlo:
                        zone_bull = (i, ob, zlo, zhi)
                pending_bull = None

        # 3) Register/supersede pending sweep only when that direction has no active OB.
        bear_sweep = (
            zone_bear is None
            and latest_hi_id >= 0
            and latest_lo_id >= 0
            and int(h[i]) > latest_hi
            and int(c[i]) < latest_hi
        )
        bull_sweep = (
            zone_bull is None
            and latest_lo_id >= 0
            and latest_hi_id >= 0
            and int(l[i]) < latest_lo
            and int(c[i]) > latest_lo
        )

        if bear_sweep and bull_sweep:
            pending_bear = None
            pending_bull = None
        else:
            if bear_sweep:
                pending_bear = (i, latest_lo, latest_lo_id)
            if bull_sweep:
                pending_bull = (i, latest_hi, latest_hi_id)

        # 4) Emit at most one direction on this completed bar.
        if len(candidates) == 1:
            side, ob_idx = candidates[0]
            kind = f"SMOR_{'MID' if require_midpoint else 'BODY'}_{tf_ms // 60000}M"
            props.append(vce.finalize_proposal(t, ask, bid, edge, side, kind, ob_idx))
        # If both directions are candidates, both zones were already consumed; emit none.

    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return smor_proposals(t, ask, bid, 60_000, False)
    if cid == CONFIGS[1]:
        return smor_proposals(t, ask, bid, 60_000, True)
    if cid == CONFIGS[2]:
        return smor_proposals(t, ask, bid, 300_000, False)
    if cid == CONFIGS[3]:
        return smor_proposals(t, ask, bid, 300_000, True)
    raise ValueError(cid)


def supply(props, t):
    return {
        "proposals": len(props),
        "source_eligible": sum(p.eligible for p in props),
        "distinct_days": len({
            int(t[p.decision_index] // 86_400_000)
            for p in props if 0 <= p.decision_index < len(t)
        }),
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
    df = df[
        (df.timestamp_ms_utc >= STAGE_A_START_MS)
        & (df.timestamp_ms_utc < STAGE_A_END_MS)
    ]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit(f"Stage-A chronology mismatch: {t.size}")

    ask, bid = val.base.p75(
        t,
        df.ask_raw.to_numpy(np.int64),
        df.bid_raw.to_numpy(np.int64),
    )
    feat = val.parent.build_parent_features(t, ask, bid)
    streams = val.generate_streams(t, ask, bid)
    d3t, d3s = streams["DH03_S06"]
    d5t, d5s = streams["DH05_S06"]
    s11t, s11s = streams["DH02_S11"]
    s08t, s08s = streams["DH02_S08"]
    zi = np.empty(0, np.int64)
    zs = np.empty(0, np.int8)

    parent = val.pack_sorb(val.run_integrated_sorb(
        t, ask, bid,
        feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
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
            t, ask, bid,
            feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
            d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
            ii, ss, sk, 1, 1, 1, 1, 1,
        ))
        dec = val.decision(parent, combined, sp)
        lane = combined.pop("sorb_session_contribution")
        combined["smor_entries"] = combined.pop("sorb_entries")
        combined["smor_net"] = combined.pop("sorb_net")
        combined["smor_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_smor_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply": sp, "combined": combined, "decision": dec}
        ranking.append((
            int(dec["strong_screen_pass"]),
            int(dec["screen_pass"]),
            float(dec["net_delta"]),
            int(dec["official_win_delta"]),
            int(combined["smor_entries"]),
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
        "accepted_entries": results[x[-1]]["combined"]["smor_entries"],
        "direct_smor_net": results[x[-1]]["combined"]["smor_net"],
    } for x in ranking]
    strong = [x for x in leaders if x["strong_screen_pass"]]

    out = {
        "schema": "delta-r037-smor-stage-a-screen-17h-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family": "R037-SMOR-v1",
        "parent_checkpoint": "R037_EGF_STAGE_A_SCREEN_CHECKPOINT_17G",
        "surrogate_parent": "14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable": False,
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "sequence": "confirmed swing sweep -> frozen opposite-swing MSS -> last opposite candle OB -> first later unmitigated body retest",
        "numeric_retuning": False,
        "post_result_retuning": False,
        "august_accessed": False,
        "parent_control": parent,
        "configs": results,
        "ranking": leaders,
        "finding": {
            "strong_screen_survivors": [x["config_id"] for x in strong],
            "leading_config": leaders[0]["config_id"],
            "next": (
                "R037_SMOR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
                if strong else
                "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
            ),
        },
        "mql5_authorized": False,
    }
    val.base.atomic_write_json(a.output, out)
    print(json.dumps(
        {"ranking": leaders, "finding": out["finding"]},
        separators=(",", ":"),
    ))


if __name__ == "__main__":
    main()
