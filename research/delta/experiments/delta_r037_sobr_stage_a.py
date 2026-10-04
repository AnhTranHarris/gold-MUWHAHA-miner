"""DELTA R037 SOBR Stage-A screen — Checkpoint 17AG.

Source-grounded reconstruction of MQL5 CodeBase 77639 entry logic:
M15 5-left/5-right confirmed swing -> >=0.15 ATR14 wick sweep and close back
inside -> sweep candle body becomes order block -> within next 3 completed M15
bars a >=0.30 ATR14 range candle closes through that body. C01 requires the
published H1 EMA50 trend direction using only the most recently completed H1 bar;
C02 is the preregistered trend-filter ablation.

DELTA execution semantics remain frozen (P75, <=25-point spread, parent priority,
0.01 lot, fixed 30-second initial-hold research exit). No numeric retuning.
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
    "R037-SOBR-C01_M15_BODY_H1EMA50",
    "R037-SOBR-C02_M15_BODY_NO_TREND",
)


def swing_high(h: np.ndarray, k: int, w: int = 5) -> bool:
    if k < w or k + w >= len(h):
        return False
    x = h[k]
    for j in range(1, w + 1):
        if not (x > h[k-j] and x > h[k+j]):
            return False
    return True


def swing_low(l: np.ndarray, k: int, w: int = 5) -> bool:
    if k < w or k + w >= len(l):
        return False
    x = l[k]
    for j in range(1, w + 1):
        if not (x < l[k-j] and x < l[k+j]):
            return False
    return True


def completed_h1_trend(m15_edge: int, h1, h1ema: np.ndarray) -> int:
    # Last H1 bar whose right edge is visible at the M15 decision edge.
    j = int(np.searchsorted(h1["end_ms"], m15_edge, side="right") - 1)
    if j < 0 or j >= len(h1ema) or np.isnan(h1ema[j]):
        return 0
    c = float(h1["close"][j])
    e = float(h1ema[j])
    return 1 if c > e else (-1 if c < e else 0)


def sobr_proposals(t, ask, bid, use_trend: bool):
    b = vce.bars(t, bid, 900_000)
    h1 = vce.bars(t, bid, 3_600_000)
    a14 = vce.atr(b, 14)
    h1ema = vce.ema(h1["close"], 50)

    o, h, l, c, e = b["open"], b["high"], b["low"], b["close"], b["end_ms"]
    props = []

    latest_hi = 0
    latest_lo = 0
    hi_id = -1
    lo_id = -1
    used_hi = -1
    used_lo = -1

    # One active setup per direction. Each stores expiry M15 bar index and
    # frozen sweep-body / side. A new qualifying sweep of that side replaces
    # only that side's prior pending setup.
    pending_long = None
    pending_short = None

    for i in range(len(c)):
        edge = int(e[i])
        if edge > STAGE_A_END_MS:
            break

        # Confirm a pivot only after five completed bars on its right.
        p = i - 5
        if p >= 5:
            if swing_high(h, p, 5):
                latest_hi = int(h[p])
                hi_id = p
            if swing_low(l, p, 5):
                latest_lo = int(l[p])
                lo_id = p

        # First evaluate confirmations from earlier sweep bars; the sweep bar
        # itself may not confirm itself.
        for side in (1, -1):
            pending = pending_long if side > 0 else pending_short
            if pending is None:
                continue
            if i > pending["expiry"]:
                if side > 0:
                    pending_long = None
                else:
                    pending_short = None
                continue
            if i <= pending["sweep_i"]:
                continue
            if np.isnan(a14[i]):
                continue
            bar_range = float(int(h[i]) - int(l[i]))
            if bar_range < 0.30 * float(a14[i]):
                continue
            through = int(c[i]) > pending["body_hi"] if side > 0 else int(c[i]) < pending["body_lo"]
            if through:
                props.append(vce.finalize_proposal(
                    t, ask, bid, edge, side,
                    "SOBR_M15_BODY_H1EMA50" if use_trend else "SOBR_M15_BODY_NO_TREND",
                    i,
                ))
                if side > 0:
                    pending_long = None
                else:
                    pending_short = None

        if np.isnan(a14[i]) or float(a14[i]) <= 0:
            continue

        trend = completed_h1_trend(edge, h1, h1ema)
        body_hi = max(int(o[i]), int(c[i]))
        body_lo = min(int(o[i]), int(c[i]))

        # Bullish: sweep active swing low by >=0.15 ATR and close back above.
        if lo_id >= 0 and lo_id != used_lo:
            excursion = float(latest_lo - int(l[i]))
            if excursion >= 0.15 * float(a14[i]) and int(c[i]) > latest_lo:
                used_lo = lo_id
                trend_ok = (not use_trend) or trend > 0
                if trend_ok:
                    pending_long = {
                        "sweep_i": i,
                        "expiry": i + 3,
                        "body_hi": body_hi,
                        "body_lo": body_lo,
                    }

        # Bearish: sweep active swing high by >=0.15 ATR and close back below.
        if hi_id >= 0 and hi_id != used_hi:
            excursion = float(int(h[i]) - latest_hi)
            if excursion >= 0.15 * float(a14[i]) and int(c[i]) < latest_hi:
                used_hi = hi_id
                trend_ok = (not use_trend) or trend < 0
                if trend_ok:
                    pending_short = {
                        "sweep_i": i,
                        "expiry": i + 3,
                        "body_hi": body_hi,
                        "body_lo": body_lo,
                    }

    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return sobr_proposals(t, ask, bid, True)
    if cid == CONFIGS[1]:
        return sobr_proposals(t, ask, bid, False)
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
        combined["sobr_entries"] = combined.pop("sorb_entries")
        combined["sobr_net"] = combined.pop("sorb_net")
        combined["sobr_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_sobr_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply": sp, "combined": combined, "decision": dec}
        ranking.append((
            int(dec["strong_screen_pass"]),
            int(dec["screen_pass"]),
            float(dec["net_delta"]),
            int(dec["official_win_delta"]),
            int(combined["sobr_entries"]),
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
        "accepted_entries": results[x[-1]]["combined"]["sobr_entries"],
        "direct_sobr_net": results[x[-1]]["combined"]["sobr_net"],
    } for x in ranking]

    strong = [x for x in leaders if x["strong_screen_pass"]]
    out = {
        "schema": "delta-r037-sobr-stage-a-screen-17ag-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family": "R037-SOBR-v1",
        "parent_checkpoint": "R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION_CHECKPOINT_17AF",
        "surrogate_parent": "14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable": False,
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "source_logic": "M15 5/5 swing; >=0.15 ATR14 sweep and close back; sweep body order block; <=3 M15 bars; confirmation range >=0.30 ATR14; close through body; optional completed-H1 EMA50 trend",
        "numeric_retuning": False,
        "post_result_retuning": False,
        "august_accessed": False,
        "parent_control": parent,
        "configs": results,
        "ranking": leaders,
        "finding": {
            "strong_screen_survivors": [x["config_id"] for x in strong],
            "leading_config": leaders[0]["config_id"],
            "next": "R037_SOBR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
                    if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        },
        "mql5_authorized": False,
    }
    val.base.atomic_write_json(a.output, out)
    print(json.dumps({"ranking": leaders, "finding": out["finding"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
