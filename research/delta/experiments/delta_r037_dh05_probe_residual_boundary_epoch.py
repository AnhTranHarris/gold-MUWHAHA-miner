"""DELTA R037 DH05 probe-count residual / boundary-epoch reconciliation — Checkpoint 10C.

Bounded causal replay derived from independent DH-05 provenance after durable 10B.

Question
--------
Does the dominant remaining 09Z probe-count residual come from stale opposite-side
boundary eligibility?  The frozen historical vector says boundary_source=M5 swing,
so this unit does NOT change source or width.  It changes only lifecycle identity:

LATEST_GLOBAL_SWING_EPOCH:
    For opening a NEW upstream probe, only swing boundaries revealed in the most
    recent causal width-2 M5 reveal epoch are eligible.  A newer high-only epoch
    retires the older low from future probe seeding; a newer low-only epoch retires
    the older high.  If both sides reveal at the same timestamp, both remain current.

Already-active upstream events retain their captured boundary L.  Existing downstream
failed-break episodes remain untouched.  Therefore this is not a generator release,
rearm, acceptance-clock, or threshold change.

The exact 09Z ownership architecture remains frozen:
    max_probe_age_s < acceptance_tf_seconds -> FAILURE_CANDIDATE decoupled generator;
    otherwise -> serial POST_QUAL ownership.

The producer fails closed unless the exact 09Z control funnel is reproduced first.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from delta_r037_dh05_runtime_primitives import (
    CANONICAL_JAN_SHA256,
    STAGE_A_END_MS,
    VECTORS,
    admit_r9_lifecycle,
    atr14,
    atomic_write_json,
    bars,
    p75,
    sha256_file,
    symmetric_swings,
)
from delta_r037_dh05_conditional_failure_clock_challenger_replay import (
    EXPECTED_POSTQUAL,
    HIST_TRADES,
    S06_HIST,
    STAGES,
    detect_clock_router,
)
from delta_r037_dh05_short_probe_relative_acceptance_bar_ownership_challenger import (
    detect_decoupled_postqual_signals,
)

TARGET = {
    "A03": [6731, 1009, 207, 797, 432, 266, 187, 187],
    "S05": [7875, 318, 28, 290, 51, 15, 9, 9],
    "S06": [3470, 1606, 245, 1358, 1211, 683, 617, 617],
    "S09": [7748, 208, 40, 168, 61, 40, 9, 9],
    "S10": [6496, 1316, 202, 1106, 623, 294, 206, 206],
    "S16": [7870, 135, 43, 92, 37, 18, 8, 8],
}

EXPECTED_09Z = {
    "A03": [6686, 998, 212, 786, 441, 268, 192, 192],
    "S05": [7818, 315, 34, 281, 56, 20, 9, 9],
    "S06": [3561, 1599, 248, 1351, 1210, 695, 651, 651],
    "S09": [7856, 219, 44, 175, 65, 41, 11, 11],
    "S10": [6440, 1300, 205, 1095, 637, 309, 227, 227],
    "S16": [7778, 134, 53, 81, 33, 19, 8, 8],
}

# Sentinels are outside any plausible XAUUSD raw midpoint2 range and are used only
# to make an older opposite-side boundary unreachable by the existing exact detector.
DISABLED_HIGH = np.int64(4_000_000_000_000_000_000)
DISABLED_LOW = np.int64(-4_000_000_000_000_000_000)


def latest_global_epoch_stream(st: np.ndarray, ss: np.ndarray, sl: np.ndarray):
    """Return a causal stream where only the latest reveal epoch can seed new probes.

    The exact detector retains separate latest-high/latest-low memories.  We preserve
    its code and chronology, but at each NEW reveal timestamp explicitly retire any
    side absent from that epoch by updating it to an unreachable sentinel.  If both
    high and low are confirmed at the same reveal timestamp, both real levels survive.

    This affects NEW event seeding only because active detector events snapshot L.
    """
    out_t = []
    out_s = []
    out_l = []
    i = 0
    n = int(st.size)
    while i < n:
        tm = int(st[i])
        j = i
        hi = None
        lo = None
        while j < n and int(st[j]) == tm:
            if int(ss[j]) > 0:
                hi = int(sl[j])
            else:
                lo = int(sl[j])
            j += 1

        if hi is None:
            out_t.append(tm)
            out_s.append(1)
            out_l.append(int(DISABLED_HIGH))
        else:
            out_t.append(tm)
            out_s.append(1)
            out_l.append(hi)

        if lo is None:
            out_t.append(tm)
            out_s.append(-1)
            out_l.append(int(DISABLED_LOW))
        else:
            out_t.append(tm)
            out_s.append(-1)
            out_l.append(lo)

        i = j

    return (
        np.asarray(out_t, dtype=np.int64),
        np.asarray(out_s, dtype=np.int8),
        np.asarray(out_l, dtype=np.int64),
    )


def run_router(
    t,
    mid,
    ask,
    bid,
    st,
    ss,
    sl,
    b1,
    a1,
    b5,
    a5,
    b15,
    b300,
    a300,
):
    vectors = {}
    stage_abs = np.zeros(8, np.int64)
    signed = np.zeros(8, np.int64)
    trade_error = 0
    max_active = 0
    episode_overflow = 0
    signal_overflow = 0

    for v in VECTORS:
        n, ad, at, mf, mp, pe, rb, rd, em, rt = v
        if mp >= at:
            cnt, sig_i, sig_side, overflow = detect_clock_router(
                t,
                mid,
                st,
                ss,
                sl,
                b300["end_ms"],
                a300,
                b1["end_ms"],
                b1["open"],
                b1["close"],
                a1,
                b5["end_ms"],
                b5["open"],
                b5["close"],
                a5,
                b15["end_ms"],
                b15["open"],
                b15["close"],
                ad,
                at,
                int(mf * 1000),
                int(mp * 1000),
                pe,
                rb,
                rd,
                em,
                rt,
                0,
            )
            ownership = "SERIAL_POST_QUAL_LONG_OR_EQUAL_PROBE_WINDOW"
            ma = 0
            eo = 0
            so = int(overflow)
        else:
            cnt, sig_i, sig_side, ma, eo, so = detect_decoupled_postqual_signals(
                t,
                mid,
                st,
                ss,
                sl,
                b300["end_ms"],
                a300,
                b1["end_ms"],
                b1["open"],
                b1["close"],
                b5["end_ms"],
                b5["open"],
                b5["close"],
                b15["end_ms"],
                b15["open"],
                b15["close"],
                ad,
                at,
                int(mf * 1000),
                int(mp * 1000),
                pe,
                rb,
                rd,
                em,
                rt,
            )
            ownership = "FAILURE_CANDIDATE_DECOUPLED_SHORT_PROBE_WINDOW"

        if int(so):
            raise SystemExit(f"signal overflow {n}: {int(so)}")

        trg = np.asarray(TARGET[n], dtype=np.int64)
        err = np.abs(cnt - trg)
        stage_abs += err
        signed += cnt - trg

        adm = admit_r9_lifecycle(t, ask, bid, sig_i, sig_side, True)
        trades = int(adm[3])
        wins = int(adm[4])
        net = float(adm[7])
        trade_error += abs(trades - HIST_TRADES[n])

        max_active = max(max_active, int(ma))
        episode_overflow += int(eo)
        signal_overflow += int(so)

        vectors[n] = {
            "ownership": ownership,
            "target": dict(zip(STAGES, map(int, trg))),
            "actual": dict(zip(STAGES, map(int, cnt))),
            "signed_error_actual_minus_target": dict(zip(STAGES, map(int, cnt - trg))),
            "abs_error": dict(zip(STAGES, map(int, err))),
            "signals": int(sig_i.size),
            "historical_trades": int(HIST_TRADES[n]),
            "trades": trades,
            "wins": wins,
            "net_usd": net,
        }

    return {
        "vectors": vectors,
        "stage_abs_error": dict(zip(STAGES, map(int, stage_abs))),
        "stage_signed_error_actual_minus_target": dict(zip(STAGES, map(int, signed))),
        "total_abs_error": int(stage_abs.sum()),
        "aggregate_trade_count_abs_error": int(trade_error),
        "max_concurrent_failure_episodes": int(max_active),
        "episode_overflow": int(episode_overflow),
        "signal_overflow": int(signal_overflow),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source_sha = sha256_file(args.source)
    if source_sha != CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: " + source_sha)

    df = pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    df = df[df.timestamp_ms_utc < STAGE_A_END_MS]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size and np.any(t[1:] < t[:-1]):
        raise SystemExit("non-monotonic Stage-A ticks")

    ask, bid = p75(
        t,
        df.ask_raw.to_numpy(np.int64),
        df.bid_raw.to_numpy(np.int64),
    )
    mid = ask + bid
    b1 = bars(t, mid, 1000)
    b5 = bars(t, mid, 5000)
    b15 = bars(t, mid, 15000)
    b300 = bars(t, mid, 300000)
    a1 = atr14(b1)
    a5 = atr14(b5)
    a300 = atr14(b300)
    st, ss, sl = symmetric_swings(b300, 2)

    control = run_router(
        t, mid, ask, bid, st, ss, sl, b1, a1, b5, a5, b15, b300, a300
    )

    # Fail closed unless the exact durable 09Z funnel is reproduced.
    for n in EXPECTED_09Z:
        got = [control["vectors"][n]["actual"][stage] for stage in STAGES]
        if got != EXPECTED_09Z[n]:
            raise SystemExit(
                "09Z control drift " + n + ": " + json.dumps({"got": got, "expected": EXPECTED_09Z[n]})
            )

    if control["total_abs_error"] != 782:
        raise SystemExit("09Z control total drift: " + str(control["total_abs_error"]))
    if control["stage_abs_error"]["probe"] != 449:
        raise SystemExit("09Z control probe drift: " + str(control["stage_abs_error"]["probe"]))

    est, ess, esl = latest_global_epoch_stream(st, ss, sl)
    candidate = run_router(
        t, mid, ask, bid, est, ess, esl, b1, a1, b5, a5, b15, b300, a300
    )

    s6c = control["vectors"]["S06"]
    s6n = candidate["vectors"]["S06"]
    control_s6_err = {
        "trades": abs(int(s6c["trades"]) - int(S06_HIST["trades"])),
        "wins": abs(int(s6c["wins"]) - int(S06_HIST["wins"])),
        "net": abs(float(s6c["net_usd"]) - float(S06_HIST["net_usd"])),
    }
    candidate_s6_err = {
        "trades": abs(int(s6n["trades"]) - int(S06_HIST["trades"])),
        "wins": abs(int(s6n["wins"]) - int(S06_HIST["wins"])),
        "net": abs(float(s6n["net_usd"]) - float(S06_HIST["net_usd"])),
    }
    s6_veto = (
        candidate_s6_err["trades"] > control_s6_err["trades"]
        or candidate_s6_err["wins"] > control_s6_err["wins"]
        or candidate_s6_err["net"] > control_s6_err["net"]
    )

    probe_improvement = int(
        control["stage_abs_error"]["probe"] - candidate["stage_abs_error"]["probe"]
    )
    total_improvement = int(control["total_abs_error"] - candidate["total_abs_error"])

    out = {
        "schema": "delta-r037-dh05-probe-residual-boundary-epoch-10c-v1",
        "status": "BOUNDED_CAUSAL_BOUNDARY_EPOCH_RECONCILIATION_COMPLETE",
        "source_sha256": source_sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "august_accessed": False,
        "numeric_vector_retune": False,
        "width_retune": False,
        "parent": "R037_DH05_SHORT_PROBE_OWNERSHIP_PROVENANCE_PROMOTION_DECISION_CHECKPOINT_10B",
        "provenance": {
            "source": "original DH-05 white paper",
            "clue": "stale swing boundary can manufacture false failure events",
            "frozen_boundary_source_preserved": "M5 swing",
            "interpretation_scope": "boundary lifecycle only; no source or width change",
        },
        "candidate_semantic": {
            "name": "LATEST_GLOBAL_SWING_EPOCH",
            "definition": "Only width-2 M5 swing boundaries in the latest causal reveal timestamp may seed a NEW upstream probe. Older opposite-side boundaries are retired for future probe seeding. Active upstream event L and existing downstream failure episodes are not rewritten.",
            "same_timestamp_dual_side": "both real boundaries remain current",
            "ownership_router": "exact 09Z relative-duration router retained",
        },
        "control_09z": control,
        "candidate": candidate,
        "finding": {
            "probe_abs_error_improvement": probe_improvement,
            "probe_abs_error_improvement_pct": 100.0 * probe_improvement / control["stage_abs_error"]["probe"],
            "total_abs_error_improvement": total_improvement,
            "total_abs_error_improvement_pct": 100.0 * total_improvement / control["total_abs_error"],
            "trade_count_abs_error_improvement": int(
                control["aggregate_trade_count_abs_error"]
                - candidate["aggregate_trade_count_abs_error"]
            ),
            "s06_economic_veto_triggered": bool(s6_veto),
            "s06_control_error": control_s6_err,
            "s06_candidate_error": candidate_s6_err,
            "carry_forward_eligible": bool(
                probe_improvement > 0 and total_improvement > 0 and not s6_veto
            ),
            "selection_rule": "Carry forward only if probe error and total funnel error both improve and the S06 economic veto is false. Historical-semantic promotion still requires provenance; this unit is parity reconstruction, not economic promotion.",
        },
        "next_if_positive": "R037_DH05_BOUNDARY_EPOCH_ACTIVE_PREFailure_SUPERSESSION_REFINEMENT",
        "next_if_negative": "R037_DH05_PROBE_RESIDUAL_CAUSAL_ATTEMPT_IDENTITY_PROVENANCE_RECONCILIATION",
    }
    atomic_write_json(args.output, out)
    print(
        json.dumps(
            {
                "control_probe_error": control["stage_abs_error"]["probe"],
                "candidate_probe_error": candidate["stage_abs_error"]["probe"],
                "control_total_error": control["total_abs_error"],
                "candidate_total_error": candidate["total_abs_error"],
                "control_trade_error": control["aggregate_trade_count_abs_error"],
                "candidate_trade_error": candidate["aggregate_trade_count_abs_error"],
                "candidate_stage_abs_error": candidate["stage_abs_error"],
                "candidate_probe_counts": {
                    n: candidate["vectors"][n]["actual"]["probe"] for n in candidate["vectors"]
                },
                "s06_veto": s6_veto,
                "carry_forward_eligible": out["finding"]["carry_forward_eligible"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
