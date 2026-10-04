"""DELTA R037 engulfing-structure failure Stage-A screen — Checkpoint 17G.

Frozen preregistration:
- Completed Bid bars only.
- Regular BUY commitment: red Base, immediately following green Confirm closes > Base high.
- Regular SELL mirror.
- Type-1 additionally sweeps the opposite Base edge on Confirm.
- Each confirmed commitment remains active without retrospective expiry.
- BUY commitment fails on first later red close strictly < Base low -> SELL proposal.
- SELL commitment fails on first later green close strictly > Base high -> BUY proposal.
- Wick-only breaches do not fail.
- Multiple same-direction failures on one completed bar collapse to the most recently
  confirmed failed commitment. Opposite-direction collision emits no proposal.
- M1/M5 x REGULAR/TYPE1 are the only frozen configs.
- No retuning, session/side slicing, candidate merge, exit tuning, August, or MQL5.
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
    "R037-EGF-C01_M1_REGULAR_FAILURE",
    "R037-EGF-C02_M1_TYPE1_FAILURE",
    "R037-EGF-C03_M5_REGULAR_FAILURE",
    "R037-EGF-C04_M5_TYPE1_FAILURE",
)


def engulf_failure_proposals(t, ask, bid, tf_ms: int, type1: bool):
    b = vce.bars(t, bid, tf_ms)
    o, h, l, c, e = b["open"], b["high"], b["low"], b["close"], b["end_ms"]

    # Each active tuple: (confirm_index, far_edge).
    # For BUY commitments the far edge is Base low; for SELL commitments Base high.
    active_buy: list[tuple[int, int]] = []
    active_sell: list[tuple[int, int]] = []
    props = []

    for i in range(1, len(c)):
        edge = int(e[i])
        if edge > STAGE_A_END_MS:
            break

        oi, ci = int(o[i]), int(c[i])
        red = ci < oi
        green = ci > oi

        # Failure evaluation occurs before registering a commitment confirmed by this
        # same bar. Therefore only previously completed/confirmed structures can fail.
        failed_buy = []
        failed_sell = []
        if red and active_buy:
            failed_buy = [(k, x) for k, x in active_buy if ci < x]
        if green and active_sell:
            failed_sell = [(k, x) for k, x in active_sell if ci > x]

        # Consume every pattern whose first qualifying failure is this bar.
        if failed_buy:
            failed_ids = {k for k, _ in failed_buy}
            active_buy = [(k, x) for k, x in active_buy if k not in failed_ids]
        if failed_sell:
            failed_ids = {k for k, _ in failed_sell}
            active_sell = [(k, x) for k, x in active_sell if k not in failed_ids]

        # Collision rule retained even though opposite candle colours make a true
        # two-direction collision impossible under the frozen grammar.
        if failed_buy and failed_sell:
            pass
        elif failed_buy:
            newest = max(failed_buy, key=lambda z: z[0])[0]
            kind = f"EGF_{'TYPE1' if type1 else 'REGULAR'}_{tf_ms // 60000}M"
            props.append(vce.finalize_proposal(t, ask, bid, edge, -1, kind, newest))
        elif failed_sell:
            newest = max(failed_sell, key=lambda z: z[0])[0]
            kind = f"EGF_{'TYPE1' if type1 else 'REGULAR'}_{tf_ms // 60000}M"
            props.append(vce.finalize_proposal(t, ask, bid, edge, 1, kind, newest))

        # Confirm new two-candle commitments using Base=i-1 and Confirm=i.
        bo, bc = int(o[i - 1]), int(c[i - 1])
        base_red = bc < bo
        base_green = bc > bo

        buy = base_red and green and ci > int(h[i - 1])
        sell = base_green and red and ci < int(l[i - 1])

        if type1:
            buy = buy and int(l[i]) <= int(l[i - 1])
            sell = sell and int(h[i]) >= int(h[i - 1])

        if buy:
            active_buy.append((i, int(l[i - 1])))
        if sell:
            active_sell.append((i, int(h[i - 1])))

    return props


def generate(t, ask, bid, cid):
    if cid == CONFIGS[0]:
        return engulf_failure_proposals(t, ask, bid, 60_000, False)
    if cid == CONFIGS[1]:
        return engulf_failure_proposals(t, ask, bid, 60_000, True)
    if cid == CONFIGS[2]:
        return engulf_failure_proposals(t, ask, bid, 300_000, False)
    if cid == CONFIGS[3]:
        return engulf_failure_proposals(t, ask, bid, 300_000, True)
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
        combined["egf_entries"] = combined.pop("sorb_entries")
        combined["egf_net"] = combined.pop("sorb_net")
        combined["egf_source_contribution"] = lane["LONDON"]
        dec["incremental_net_per_egf_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply": sp, "combined": combined, "decision": dec}
        ranking.append((
            int(dec["strong_screen_pass"]),
            int(dec["screen_pass"]),
            float(dec["net_delta"]),
            int(dec["official_win_delta"]),
            int(combined["egf_entries"]),
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
        "accepted_entries": results[x[-1]]["combined"]["egf_entries"],
        "direct_egf_net": results[x[-1]]["combined"]["egf_net"],
    } for x in ranking]
    strong = [x for x in leaders if x["strong_screen_pass"]]

    out = {
        "schema": "delta-r037-egf-stage-a-screen-17g-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family": "R037-EGF-v1",
        "parent_checkpoint": "R037_SFP_STAGE_A_SCREEN_CHECKPOINT_17F",
        "surrogate_parent": "14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable": False,
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "pattern_semantics": "confirmed engulf commitment retained until first opposite-colour close through Base far edge; failure follows newly controlling side",
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
                "R037_EGF_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
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
