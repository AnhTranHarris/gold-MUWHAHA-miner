"""DELTA R037 DH05 generator-ownership / new-boundary-release parity diagnostic — Checkpoint 09U.

Bounded causal reconstruction only. No numeric vector retuning. August stays sealed.
The frozen serial POST_QUAL generator is the control.

Candidate hypothesis:
- when a qualified probe becomes FAILURE_CANDIDATE, its downstream failed-break
  episode may continue independently;
- the upstream probe generator is released, BUT it may not open another event on
  the exact same causally revealed M5 swing boundary identity while that episode
  remains active;
- a later causally revealed M5 swing is a new boundary identity even if its price
  level happens to equal an older swing;
- downstream failure/reentry/reclaim/reversal semantics and max_failure_age remain
  frozen; no new threshold is introduced.

This directly tests the middle ground between fully serial ownership and the
rejected 09H immediate same-boundary full decoupling.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_runtime_primitives import (
    CANONICAL_JAN_SHA256,
    STAGE_A_END_MS,
    VECTORS,
    admit_r9_lifecycle,
    atomic_write_json,
    atr14,
    bars,
    bidx,
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

TARGET = {
    "A03": [6731, 1009, 207, 797, 432, 266, 187, 187],
    "S05": [7875, 318, 28, 290, 51, 15, 9, 9],
    "S06": [3470, 1606, 245, 1358, 1211, 683, 617, 617],
    "S09": [7748, 208, 40, 168, 61, 40, 9, 9],
    "S10": [6496, 1316, 202, 1106, 623, 294, 206, 206],
    "S16": [7870, 135, 43, 92, 37, 18, 8, 8],
}

FULL_DECOUPLED_09H_REFERENCE = {
    "total_abs_error": 14260,
    "probe_qualified_abs_error": 8437,
    "max_concurrent_failure_episodes": 8,
    "selected": {
        "S05": [7818, 315, 34, 281, 56, 20, 9, 9],
        "S06": [7373, 3117, 370, 2747, 2412, 1372, 1281, 1281],
        "S09": [7856, 219, 44, 175, 65, 41, 11, 11],
        "S10": [7778, 1536, 223, 1313, 772, 373, 283, 283],
        "S16": [7778, 134, 53, 81, 33, 19, 8, 8],
    },
}


@njit(cache=True)
def boundary_is_active(active, ebid, candidate_id):
    for e in range(active.size):
        if active[e] != 0 and ebid[e] == candidate_id:
            return True
    return False


@njit(cache=True)
def active_count(active):
    n = 0
    for e in range(active.size):
        if active[e] != 0:
            n += 1
    return n


@njit(cache=True)
def detect_new_boundary_release(
    t,
    mid2,
    st,
    ss,
    sl,
    m5e,
    m5a,
    s1e,
    s1o,
    s1c,
    s5e,
    s5o,
    s5c,
    s15e,
    s15o,
    s15c,
    accdisp,
    acctf,
    maxfail,
    maxprobe,
    probeexc,
    reclaim,
    revdisp,
    effmin,
    revtf,
):
    # One upstream generator plus independently surviving failed-break episodes.
    stage = 0
    oside = 0
    L = 0
    boundary_id = -1
    evatr = 0.0
    attempt_start = 0
    qualified_start = 0

    latest_hi = 0
    latest_lo = 0
    latest_hi_id = -1
    latest_lo_id = -1
    si = 0
    hiel = True
    loel = True
    lastacc = -1
    attempt_open = False
    attempt_qualified = False

    cnt = np.zeros(8, np.int64)

    MAX_EP = 64
    active = np.zeros(MAX_EP, np.int8)
    estage = np.zeros(MAX_EP, np.int8)
    eoside = np.zeros(MAX_EP, np.int8)
    eL = np.zeros(MAX_EP, np.int64)
    ebid = np.full(MAX_EP, -1, np.int64)
    eatr = np.zeros(MAX_EP, np.float64)
    efstart = np.zeros(MAX_EP, np.int64)
    elastrev = np.full(MAX_EP, -1, np.int64)

    MAX_SIG = 20000
    sig_i = np.empty(MAX_SIG, np.int64)
    sig_side = np.empty(MAX_SIG, np.int8)
    nsig = 0
    signal_overflow = 0
    episode_overflow = 0
    max_active = 0
    new_boundary_starts_while_failure_active = 0

    for i in range(t.size):
        tm = int(t[i])
        px = int(mid2[i])

        while si < st.size and st[si] <= tm:
            if ss[si] > 0:
                latest_hi = int(sl[si])
                latest_hi_id = si
            else:
                latest_lo = int(sl[si])
                latest_lo_id = si
            si += 1

        jm = bidx(m5e, tm)
        if jm < 13:
            continue
        ae = float(m5a[jm])
        if ae <= 0:
            continue

        j1 = bidx(s1e, tm)
        j5 = bidx(s5e, tm)
        j15 = bidx(s15e, tm)
        jacc = j5 if acctf == 5 else j15
        ac = s5c[j5] if acctf == 5 and j5 >= 0 else (s15c[j15] if j15 >= 0 else 0)
        ao = s5o[j5] if acctf == 5 and j5 >= 0 else (s15o[j15] if j15 >= 0 else 0)
        acc_end = s5e[j5] if acctf == 5 and j5 >= 0 else (s15e[j15] if j15 >= 0 else 0)

        # Upstream generator. Active downstream episodes block only their exact
        # causal boundary identity, not a later revealed M5 swing.
        if stage == 0:
            if latest_hi and px < latest_hi:
                hiel = True
            if latest_lo and px > latest_lo:
                loel = True

            if (
                latest_hi
                and hiel
                and px >= latest_hi
                and latest_hi_id >= 0
                and not boundary_is_active(active, ebid, latest_hi_id)
            ):
                if active_count(active) > 0:
                    new_boundary_starts_while_failure_active += 1
                stage = 1
                oside = 1
                L = latest_hi
                boundary_id = latest_hi_id
                evatr = ae
                attempt_start = tm
                qualified_start = 0
                hiel = False
                cnt[0] += 1
                attempt_open = True
                attempt_qualified = False
            elif (
                latest_lo
                and loel
                and px <= latest_lo
                and latest_lo_id >= 0
                and not boundary_is_active(active, ebid, latest_lo_id)
            ):
                if active_count(active) > 0:
                    new_boundary_starts_while_failure_active += 1
                stage = 1
                oside = -1
                L = latest_lo
                boundary_id = latest_lo_id
                evatr = ae
                attempt_start = tm
                qualified_start = 0
                loel = False
                cnt[0] += 1
                attempt_open = True
                attempt_qualified = False

        if stage > 0:
            inside = oside * (px - L) < 0
            if inside:
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0
            elif not attempt_open:
                attempt_open = True
                attempt_qualified = False
                qualified_start = 0
                cnt[0] += 1
                attempt_start = tm

            if attempt_open and (not attempt_qualified) and oside * (px - L) >= probeexc * evatr:
                attempt_qualified = True
                qualified_start = tm
                cnt[1] += 1

            if stage == 1:
                if oside * (px - L) >= probeexc * evatr:
                    stage = 2
                    if qualified_start == 0:
                        qualified_start = tm
                elif tm - attempt_start > maxprobe:
                    stage = 0
                    oside = 0
                    boundary_id = -1
                    attempt_open = False
                    attempt_qualified = False
                    qualified_start = 0

        accepted_now = False
        if stage == 2 and jacc >= 0 and jacc != lastacc:
            lastacc = jacc
            q = (
                qualified_start > 0
                and acc_end > qualified_start
                and oside * (ac - ao) >= accdisp * evatr
                and oside * (ac - L) > 0
            )
            if q:
                cnt[2] += 1
                stage = 0
                oside = 0
                boundary_id = -1
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0
                accepted_now = True

        if (not accepted_now) and stage == 2:
            recross = oside * (px - L) < 0
            if tm - attempt_start >= maxprobe or recross:
                cnt[3] += 1
                slot = -1
                for qslot in range(MAX_EP):
                    if active[qslot] == 0:
                        slot = qslot
                        break
                if slot < 0:
                    episode_overflow += 1
                else:
                    active[slot] = 1
                    estage[slot] = 3
                    eoside[slot] = oside
                    eL[slot] = L
                    ebid[slot] = boundary_id
                    eatr[slot] = evatr
                    efstart[slot] = tm
                    elastrev[slot] = -1

                # Release generator, but the active episode now owns this exact
                # boundary identity and blocks a duplicate concurrent episode.
                stage = 0
                oside = 0
                boundary_id = -1
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0

        # Downstream failed-break episodes.
        jrev = j1 if revtf == 1 else j5
        rc = s1c[j1] if revtf == 1 and j1 >= 0 else (s5c[j5] if j5 >= 0 else 0)
        ro = s1o[j1] if revtf == 1 and j1 >= 0 else (s5o[j5] if j5 >= 0 else 0)

        for e in range(MAX_EP):
            if active[e] == 0:
                continue
            eo = int(eoside[e])
            recross_e = eo * (px - int(eL[e])) < 0

            if estage[e] == 3:
                if recross_e:
                    cnt[4] += 1
                    estage[e] = 4
                elif tm - int(efstart[e]) > maxfail:
                    active[e] = 0
                    continue
            elif tm - int(efstart[e]) > maxfail:
                active[e] = 0
                continue

            if estage[e] >= 4 and jrev >= 0 and jrev != elastrev[e]:
                if estage[e] == 4 and (-eo) * (rc - int(eL[e])) >= reclaim * float(eatr[e]):
                    cnt[5] += 1
                    estage[e] = 5

                if estage[e] >= 5:
                    disp = (-eo) * (rc - ro)
                    eff = 1.0 if abs(rc - ro) > 0 else 0.0
                    if disp >= revdisp * float(eatr[e]) and eff >= effmin:
                        cnt[6] += 1
                        cnt[7] += 1
                        if nsig < MAX_SIG:
                            sig_i[nsig] = i
                            sig_side[nsig] = -eo
                            nsig += 1
                        else:
                            signal_overflow += 1
                        active[e] = 0
                        continue
                elastrev[e] = jrev

        alive = active_count(active)
        if alive > max_active:
            max_active = alive

    return (
        cnt,
        sig_i[:nsig],
        sig_side[:nsig],
        max_active,
        episode_overflow,
        signal_overflow,
        new_boundary_starts_while_failure_active,
    )


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

    ask, bid = p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    mid = ask + bid

    b1 = bars(t, mid, 1000)
    b5 = bars(t, mid, 5000)
    b15 = bars(t, mid, 15000)
    b300 = bars(t, mid, 300000)
    a1 = atr14(b1)
    a5 = atr14(b5)
    a300 = atr14(b300)
    st, ss, sl = symmetric_swings(b300, 2)

    candidate_vectors = {}
    control_vectors = {}
    stage_abs = np.zeros(8, np.int64)
    trade_abs = 0
    max_active_all = 0
    episode_overflow_all = 0
    signal_overflow_all = 0
    new_boundary_starts_all = 0

    for v in VECTORS:
        n, ad, at, mf, mp, pe, rb, rd, em, rt = v

        cc, csi, cssig, cov = detect_clock_router(
            t, mid, st, ss, sl, b300["end_ms"], a300,
            b1["end_ms"], b1["open"], b1["close"], a1,
            b5["end_ms"], b5["open"], b5["close"], a5,
            b15["end_ms"], b15["open"], b15["close"],
            ad, at, int(mf * 1000), int(mp * 1000), pe, rb, rd, em, rt, 0,
        )
        if cov:
            raise SystemExit("control signal overflow " + n)
        got = list(map(int, cc))
        if got != EXPECTED_POSTQUAL[n]:
            raise SystemExit("CONTROL_POSTQUAL drift " + n + ": " + json.dumps(got))
        control_latch = admit_r9_lifecycle(t, ask, bid, csi, cssig, True)
        control_vectors[n] = {
            "funnel": dict(zip(STAGES, got)),
            "generator_signals": int(csi.size),
            "latch_trades": int(control_latch[3]),
            "latch_wins": int(control_latch[4]),
            "latch_net_usd": float(control_latch[7]),
        }

        c, si2, ss2, ma, eov, sov, nbs = detect_new_boundary_release(
            t, mid, st, ss, sl, b300["end_ms"], a300,
            b1["end_ms"], b1["open"], b1["close"],
            b5["end_ms"], b5["open"], b5["close"],
            b15["end_ms"], b15["open"], b15["close"],
            ad, at, int(mf * 1000), int(mp * 1000), pe, rb, rd, em, rt,
        )
        if sov:
            raise SystemExit("candidate signal overflow " + n)
        trg = np.asarray(TARGET[n], np.int64)
        err = np.abs(c - trg)
        stage_abs += err
        latch = admit_r9_lifecycle(t, ask, bid, si2, ss2, True)
        trade_abs += abs(int(latch[3]) - HIST_TRADES[n])
        max_active_all = max(max_active_all, int(ma))
        episode_overflow_all += int(eov)
        signal_overflow_all += int(sov)
        new_boundary_starts_all += int(nbs)
        candidate_vectors[n] = {
            "target": dict(zip(STAGES, map(int, trg))),
            "funnel": dict(zip(STAGES, map(int, c))),
            "abs_error": dict(zip(STAGES, map(int, err))),
            "generator_signals": int(si2.size),
            "historical_trades": int(HIST_TRADES[n]),
            "position_observation_latch": {
                "trades": int(latch[3]),
                "wins": int(latch[4]),
                "net_usd": float(latch[7]),
                "rejected_occupied": int(latch[1]),
                "rejected_latch": int(latch[2]),
            },
            "max_concurrent_failure_episodes": int(ma),
            "episode_overflow": int(eov),
            "new_boundary_starts_while_failure_active": int(nbs),
        }

    control_signal_error = sum(
        abs(control_vectors[n]["generator_signals"] - HIST_TRADES[n])
        for n in HIST_TRADES
    )
    control_trade_error = sum(
        abs(control_vectors[n]["latch_trades"] - HIST_TRADES[n])
        for n in HIST_TRADES
    )

    s6 = candidate_vectors["S06"]
    s6_exec = s6["position_observation_latch"]

    out = {
        "schema": "delta-r037-dh05-generator-ownership-new-boundary-release-09u-v1",
        "status": "BOUNDED_CAUSAL_PARITY_REPLAY_COMPLETE_NON_PROMOTING_PENDING_REVIEW",
        "source_sha256": source_sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "august_accessed": False,
        "numeric_vector_retune": False,
        "control_postqual_reproduced": True,
        "candidate_semantics": {
            "generator_release": "FAILURE_CANDIDATE",
            "same_boundary_concurrent_duplicate": "BLOCKED_BY_CAUSAL_SWING_IDENTITY",
            "new_boundary_while_old_episode_alive": "ALLOWED",
            "boundary_identity": "causal symmetric-width-2 M5 swing reveal index, not price alone",
            "failure_clock": "starts at FAILURE_CANDIDATE",
            "acceptance": "09F post-qualification completed-bar chronology + 09D body displacement",
        },
        "control": {
            "vectors": control_vectors,
            "aggregate_signal_vs_historical_trade_abs_error": int(control_signal_error),
            "aggregate_latch_trade_abs_error": int(control_trade_error),
        },
        "candidate": {
            "vectors": candidate_vectors,
            "stage_abs_error": dict(zip(STAGES, map(int, stage_abs))),
            "total_stage_abs_error": int(stage_abs.sum()),
            "probe_qualified_abs_error": int(stage_abs[:2].sum()),
            "first5_abs_error": int(stage_abs[:5].sum()),
            "downstream_abs_error": int(stage_abs[5:].sum()),
            "aggregate_latch_trade_abs_error": int(trade_abs),
            "max_concurrent_failure_episodes": int(max_active_all),
            "episode_overflow": int(episode_overflow_all),
            "signal_overflow": int(signal_overflow_all),
            "new_boundary_starts_while_failure_active": int(new_boundary_starts_all),
            "s06": {
                "signals": int(s6["generator_signals"]),
                "trades": int(s6_exec["trades"]),
                "wins": int(s6_exec["wins"]),
                "net_usd": float(s6_exec["net_usd"]),
                "signal_abs_error": abs(int(s6["generator_signals"]) - S06_HIST["signals"]),
                "trade_abs_error": abs(int(s6_exec["trades"]) - S06_HIST["trades"]),
                "win_abs_error": abs(int(s6_exec["wins"]) - S06_HIST["wins"]),
                "net_abs_error": abs(float(s6_exec["net_usd"]) - S06_HIST["net_usd"]),
            },
        },
        "reference_09h_full_decoupling": FULL_DECOUPLED_09H_REFERENCE,
        "selection_rule": "Carry forward only if new-boundary-only ownership materially improves family funnel/trade parity versus serial control without recreating 09H dense-vector explosion; S06 economics remain a mandatory veto.",
        "promoted": False,
        "next": "R037_DH05_NEW_BOUNDARY_RELEASE_REVIEW_OR_NEXT_GENERATOR_PROVENANCE_UNIT",
    }

    atomic_write_json(args.output, out)
    print(
        json.dumps(
            {
                "control_signal_error": out["control"]["aggregate_signal_vs_historical_trade_abs_error"],
                "control_trade_error": out["control"]["aggregate_latch_trade_abs_error"],
                "candidate_stage_error": out["candidate"]["total_stage_abs_error"],
                "candidate_trade_error": out["candidate"]["aggregate_latch_trade_abs_error"],
                "candidate_s06": out["candidate"]["s06"],
                "candidate_signals": {n: candidate_vectors[n]["generator_signals"] for n in candidate_vectors},
                "candidate_trades": {n: candidate_vectors[n]["position_observation_latch"]["trades"] for n in candidate_vectors},
                "max_active": out["candidate"]["max_concurrent_failure_episodes"],
                "new_boundary_starts": out["candidate"]["new_boundary_starts_while_failure_active"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
