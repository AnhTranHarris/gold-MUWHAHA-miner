"""DELTA R037 DH02-S08 state-funnel / parent-context placement — Checkpoint 12B.

Bounded provenance localization only. This producer imports the committed 12A
clean-room reconstruction helpers so all frozen numeric S08 semantics remain
identical, then varies only source-grounded ARMED/context placement semantics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

import delta_r037_dh02_s08_cleanroom_parity as base

PROFILES = (
    "CONTROL_12A_BREAK_AND_ENTRY_CONTEXT",
    "ARM_ON_REVEAL_LATCH_ENTRY_RECHECK",
    "ARM_WHEN_CONTEXT_FIRST_PERMITS_LATCH_ENTRY_RECHECK",
    "ARM_LATCH_CONTINUOUS_CONTEXT_CONSUME",
    "ENTRY_CONTEXT_ONLY_DIAGNOSTIC",
)

CONTROL_SIGNAL_SHA = "0f64c1f727c9fef6f9ee3676b1aa8d8a3df874b5a1c381d4a3bd6e6fe8657841"
CONTROL_FINGERPRINT = {
    "signals": 105,
    "trades": 105,
    "raw_positive_wins": 37,
    "gross_profit": 8.75,
    "gross_loss": -37.73,
    "net_profit": -28.98,
}


@njit(cache=True)
def raw_parent_match(tm, side, pe, praw):
    j = base.bidx(pe, tm)
    if j < 0:
        return False
    return praw[j] == side


@njit(cache=True)
def generate_signals(
    t, mid2,
    swing_t, swing_side, swing_level, swing_id,
    s1e, s1c, s1eff,
    s5e, s5c,
    s15e, s15atr,
    pe, praw,
    profile,
):
    state = np.zeros(2, np.int8)
    level = np.zeros(2, np.int64)
    evatr = np.zeros(2, np.float64)
    event_start = np.zeros(2, np.int64)
    accept_start = np.zeros(2, np.int64)
    retest_start = np.zeros(2, np.int64)
    boundary_id = np.zeros(2, np.int64)
    used_id = np.zeros(2, np.int64)
    fail_pending_tick = np.full(2, -1, np.int64)

    latest_level = np.zeros(2, np.int64)
    latest_id = np.zeros(2, np.int64)
    armed_level = np.zeros(2, np.int64)
    armed_id = np.zeros(2, np.int64)
    si = 0
    last_s1 = -1
    last_s5 = -1

    sig_t = np.empty(50000, np.int64)
    sig_side = np.empty(50000, np.int8)
    sig_boundary = np.empty(50000, np.int64)
    nsig = 0

    cnt = np.zeros(14, np.int64)

    for i in range(t.size):
        tm = int(t[i])
        px = int(mid2[i])

        while si < swing_t.size and swing_t[si] <= tm:
            idx = 0 if swing_side[si] > 0 else 1
            side = 1 if idx == 0 else -1
            latest_level[idx] = swing_level[si]
            latest_id[idx] = swing_id[si]
            if profile == 1 and state[idx] == 0:
                if raw_parent_match(tm, side, pe, praw):
                    armed_level[idx] = swing_level[si]
                    armed_id[idx] = swing_id[si]
                    cnt[0] += 1
                else:
                    armed_level[idx] = 0
                    armed_id[idx] = 0
            si += 1

        j15 = base.bidx(s15e, tm)
        if j15 < 13:
            continue
        j1 = base.bidx(s1e, tm)
        j5 = base.bidx(s5e, tm)

        if profile == 2 or profile == 3:
            for idx in range(2):
                if state[idx] != 0:
                    continue
                lid = latest_id[idx]
                if lid == 0 or lid == used_id[idx] or lid == armed_id[idx]:
                    continue
                side = 1 if idx == 0 else -1
                if raw_parent_match(tm, side, pe, praw):
                    armed_id[idx] = lid
                    armed_level[idx] = latest_level[idx]
                    cnt[0] += 1

        if j5 >= 0 and j5 != last_s5:
            last_s5 = j5
            close5 = int(s5c[j5])
            for idx in range(2):
                side = 1 if idx == 0 else -1
                if state[idx] != 0:
                    continue

                if profile == 0 or profile == 4:
                    lid = latest_id[idx]
                    L = latest_level[idx]
                else:
                    lid = armed_id[idx]
                    L = armed_level[idx]

                if lid == 0 or lid == used_id[idx]:
                    continue
                ae = float(s15atr[j15])
                if ae <= 0:
                    continue
                disp = side * (close5 - L)
                if disp <= 0 or disp / ae < base.BREAKNORM_MIN:
                    continue

                if profile == 0 and not raw_parent_match(tm, side, pe, praw):
                    cnt[7] += 1
                    continue

                state[idx] = 1
                level[idx] = L
                evatr[idx] = ae
                event_start[idx] = tm
                accept_start[idx] = tm
                retest_start[idx] = 0
                boundary_id[idx] = lid
                fail_pending_tick[idx] = -1
                cnt[1] += 1

        for idx in range(2):
            st = state[idx]
            if st == 0:
                continue
            side = 1 if idx == 0 else -1
            L = level[idx]
            ae = evatr[idx]
            pos = side * (px - L)

            if profile == 3 and not raw_parent_match(tm, side, pe, praw):
                cnt[9] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1
                continue

            if tm - event_start[idx] > base.MAX_EVENT_MS:
                cnt[5] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1
                continue

            if st == 1:
                if pos < -base.PENETRATION_BUFFER_ATR * ae:
                    cnt[4] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1
                    continue

                if pos > 0:
                    if accept_start[idx] == 0:
                        accept_start[idx] = tm
                    if tm - accept_start[idx] >= base.ACCEPT_DWELL_MS:
                        state[idx] = 2
                        cnt[2] += 1
                        st = 2
                else:
                    if accept_start[idx] != 0:
                        cnt[10] += 1
                    accept_start[idx] = 0

            if st == 2:
                if abs(px - L) <= base.RETEST_HALFWIDTH_ATR * ae:
                    state[idx] = 3
                    retest_start[idx] = tm
                    fail_pending_tick[idx] = -1
                    cnt[3] += 1
                    st = 3

            if st == 3:
                if tm - retest_start[idx] > base.MAX_RETEST_MS:
                    cnt[5] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1
                    continue

                adverse = pos < -base.PENETRATION_BUFFER_ATR * ae
                if adverse:
                    if fail_pending_tick[idx] >= 0 and i > fail_pending_tick[idx]:
                        cnt[4] += 1
                        cnt[13] += 1
                        used_id[idx] = boundary_id[idx]
                        state[idx] = 0
                        fail_pending_tick[idx] = -1
                        continue
                    elif fail_pending_tick[idx] < 0:
                        fail_pending_tick[idx] = i
                        cnt[11] += 1
                elif fail_pending_tick[idx] >= 0:
                    fail_pending_tick[idx] = -1
                    cnt[12] += 1

        if j1 >= 4 and j1 != last_s1:
            last_s1 = j1
            close1 = int(s1c[j1])
            eff1 = float(s1eff[j1])
            for idx in range(2):
                if state[idx] != 3:
                    continue
                side = 1 if idx == 0 else -1
                L = level[idx]
                ae = evatr[idx]
                disp = side * (close1 - L)
                if (
                    disp > base.RETEST_HALFWIDTH_ATR * ae
                    and disp / ae >= base.REBREAK_DISP_ATR
                    and side * eff1 >= base.REBREAK_EFF_MIN
                ):
                    if not raw_parent_match(tm, side, pe, praw):
                        cnt[8] += 1
                        continue
                    if nsig < sig_t.size:
                        sig_t[nsig] = tm
                        sig_side[nsig] = side
                        sig_boundary[nsig] = boundary_id[idx]
                        nsig += 1
                        cnt[6] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1

    return sig_t[:nsig], sig_side[:nsig], sig_boundary[:nsig], cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if evidence.get("schema") != "delta-r037-dh02-s08-state-funnel-provenance-evidence-12b-v1":
        raise SystemExit("unexpected evidence schema")
    if evidence.get("frozen_vector_fingerprint") != "7c70b5304ff7":
        raise SystemExit("unexpected S08 vector fingerprint")

    source_sha = base.sha256_file(args.source)
    if source_sha != base.CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df = pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    df = df[df.timestamp_ms_utc < base.STAGE_A_END_MS]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t) != 4_205_709:
        raise SystemExit(f"Stage-A tick mismatch: {len(t)}")

    ask, bid = base.p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    mid2 = ask + bid

    b1 = base.bars(t, mid2, 1_000)
    b5 = base.bars(t, mid2, 5_000)
    b15 = base.bars(t, mid2, 15_000)
    bm1 = base.bars(t, mid2, 60_000)
    bm15 = base.bars(t, mid2, 900_000)
    bm30 = base.bars(t, mid2, 1_800_000)
    bh1 = base.bars(t, mid2, 3_600_000)

    s15atr = base.atr14(b15)
    s1eff = base.signed_eff(b1, 4)
    swing_t, swing_side, swing_level, swing_id = base.symmetric_swings(bm1, 2)

    d15 = base.directional_label(bm15, 3, 0.3, 0.3)
    d30 = base.directional_label(bm30, 3, 0.3, 0.3)
    dh1 = base.directional_label(bh1, 3, 0.3, 0.3)
    pe, praw, _ = base.parent_direction_series(
        bm15["end_ms"], d15,
        bm30["end_ms"], d30,
        bh1["end_ms"], dh1,
    )

    profiles = {}
    for pi, pname in enumerate(PROFILES):
        st, ss, sb, cnt = generate_signals(
            t, mid2,
            swing_t, swing_side, swing_level, swing_id,
            b1["end_ms"], b1["close"], s1eff,
            b5["end_ms"], b5["close"],
            b15["end_ms"], s15atr,
            pe, praw,
            pi,
        )
        exe = base.execute_r9_lifecycle(t, ask, bid, st, ss)
        actual = {
            "signals": int(len(st)),
            "signal_sha256": base.signal_sha(st, ss, sb),
            "armed": int(cnt[0]),
            "breaks": int(cnt[1]),
            "accepted": int(cnt[2]),
            "retests": int(cnt[3]),
            "failed": int(cnt[4]),
            "expired": int(cnt[5]),
            "context_veto_break": int(cnt[7]),
            "context_veto_entry": int(cnt[8]),
            "context_invalidated": int(cnt[9]),
            "dwell_resets": int(cnt[10]),
            "failure_pending_starts": int(cnt[11]),
            "failure_pending_resets": int(cnt[12]),
            "failure_pending_confirms": int(cnt[13]),
            "trades": int(exe[0]),
            "raw_positive_wins": int(exe[1]),
            "official_wins": int(exe[2]),
            "gross_profit": float(exe[3]),
            "gross_loss": float(exe[4]),
            "net_profit": float(exe[5]),
            "max_balance_drawdown": float(exe[6]),
        }
        err = {
            k: abs(actual[k] - base.TARGET[k])
            for k in (
                "trades", "raw_positive_wins", "gross_profit",
                "gross_loss", "net_profit", "max_balance_drawdown"
            )
        }
        score = (
            100.0 * err["trades"]
            + 25.0 * err["raw_positive_wins"]
            + err["gross_profit"] + err["gross_loss"]
            + err["net_profit"] + err["max_balance_drawdown"]
        )
        profiles[pname] = {"actual": actual, "abs_error": err, "parity_score": float(score)}

    control = profiles[PROFILES[0]]["actual"]
    if (
        control["signal_sha256"] != CONTROL_SIGNAL_SHA
        or control["signals"] != CONTROL_FINGERPRINT["signals"]
        or control["trades"] != CONTROL_FINGERPRINT["trades"]
        or control["raw_positive_wins"] != CONTROL_FINGERPRINT["raw_positive_wins"]
        or abs(control["gross_profit"] - CONTROL_FINGERPRINT["gross_profit"]) > 0.011
        or abs(control["gross_loss"] - CONTROL_FINGERPRINT["gross_loss"]) > 0.011
        or abs(control["net_profit"] - CONTROL_FINGERPRINT["net_profit"]) > 0.011
    ):
        raise SystemExit("CONTROL_12A fingerprint mismatch; refusing result write")

    all_order = sorted(PROFILES, key=lambda p: profiles[p]["parity_score"])
    source_profiles = PROFILES[:4]
    source_order = sorted(source_profiles, key=lambda p: profiles[p]["parity_score"])
    lead = source_order[0]
    a = profiles[lead]["actual"]
    exact = (
        a["trades"] == base.TARGET["trades"]
        and a["raw_positive_wins"] == base.TARGET["raw_positive_wins"]
        and abs(a["gross_profit"] - base.TARGET["gross_profit"]) < 0.011
        and abs(a["gross_loss"] - base.TARGET["gross_loss"]) < 0.011
        and abs(a["net_profit"] - base.TARGET["net_profit"]) < 0.011
        and abs(a["max_balance_drawdown"] - base.TARGET["max_balance_drawdown"]) < 0.011
    )
    control_score = profiles[PROFILES[0]]["parity_score"]
    lead_score = profiles[lead]["parity_score"]
    improve_pct = 100.0 * (control_score - lead_score) / control_score
    material = lead != PROFILES[0] and improve_pct >= 10.0

    if exact:
        nxt = evidence["next_if_exact"]
    elif material:
        nxt = evidence["next_if_material_but_nonexact"]
    else:
        nxt = evidence["next_if_no_material_source_grounded_improvement"]

    out = {
        "schema": "delta-r037-dh02-s08-state-funnel-provenance-12b-v1",
        "status": "COMPLETE_EXACT_PARITY" if exact else "COMPLETE_STATE_FUNNEL_PROVENANCE_LOCALIZATION",
        "unit": "R037_DH02_S08_STATE_FUNNEL_AND_PROVENANCE_LOCALIZATION",
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint": "7c70b5304ff7",
        "numeric_vector_retune": False,
        "august_accessed": False,
        "control_12a_reproduced": True,
        "profiles": profiles,
        "ranking_all": all_order,
        "ranking_source_grounded": source_order,
        "finding": {
            "leading_source_grounded_profile": lead,
            "exact_historical_parity": exact,
            "material_source_grounded_improvement": material,
            "control_score": float(control_score),
            "leading_score": float(lead_score),
            "score_improvement_pct_vs_control": float(improve_pct),
            "entry_only_diagnostic_score": float(profiles[PROFILES[4]]["parity_score"]),
            "target": base.TARGET,
            "next": nxt,
        },
        "mql5_authorized": False,
    }
    base.atomic_write_json(args.output, out)
    print(json.dumps(out["finding"], separators=(",", ":")))


if __name__ == "__main__":
    main()
