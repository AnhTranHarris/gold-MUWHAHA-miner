"""DELTA R037 DH02-S08 parent-context placement parity diagnostic — 12B.

Uses the committed 12A producer as a verified helper for frozen feature/execution
semantics. Changes only where the already-frozen raw DH01 parent-direction
requirement is applied: break, rebreak, or continuously while the event is active.

No numeric retuning. No August. No SORB. No MQL5.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

BASE_SHA256 = "b5675413a094c36a619485fe299f59aa7840fc34f8c12b437fbcf0af71a26e26"
CANONICAL_JAN_SHA256 = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
STAGE_A_END_MS = 1_768_737_600_000

BREAKNORM_MIN = 0.2233
ACCEPT_DWELL_MS = 1_000
MAX_EVENT_MS = int(round(62.9664 * 1000))
MAX_RETEST_MS = int(round(40.7704 * 1000))
PENETRATION_BUFFER_ATR = 0.1271
REBREAK_DISP_ATR = 0.153
REBREAK_EFF_MIN = 0.6977
RETEST_HALFWIDTH_ATR = 0.0675

TARGET = {
    "trades": 75,
    "raw_positive_wins": 42,
    "gross_profit": 9.93,
    "gross_loss": -18.82,
    "net_profit": -8.89,
    "max_balance_drawdown": 9.66,
}

PROFILES = (
    "CONTROL_BREAK_AND_REBREAK",
    "BREAK_ONLY",
    "REBREAK_ONLY",
    "CONTINUOUS_ACTIVE_CONTEXT",
)

CONTROL_SIGNAL_SHA = "0f64c1f727c9fef6f9ee3676b1aa8d8a3df874b5a1c381d4a3bd6e6fe8657841"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            prefix=f".{path.name}.", suffix=".tmp",
            dir=path.parent, delete=False,
        ) as tmp:
            tmp_name = tmp.name
            json.dump(payload, tmp, indent=2)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def load_base(path: Path):
    if sha256_file(path) != BASE_SHA256:
        raise SystemExit("12A base-producer SHA mismatch")
    spec = importlib.util.spec_from_file_location("delta_s08_12a_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load 12A base producer")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@njit(cache=True)
def bidx(end, tm):
    return np.searchsorted(end, tm, side="right") - 1


@njit(cache=True)
def raw_parent_matches(tm, side, pe, praw):
    j = bidx(pe, tm)
    return j >= 0 and praw[j] == side


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
    si = 0
    last_s1 = -1
    last_s5 = -1

    sig_t = np.empty(50000, np.int64)
    sig_side = np.empty(50000, np.int8)
    sig_boundary = np.empty(50000, np.int64)
    nsig = 0

    # break, accepted, retest, failed, expired, signal,
    # break_context_veto, rebreak_context_veto, active_context_invalidation,
    # dwell_reset, failure_pending_start, failure_pending_reset, failure_pending_confirm
    cnt = np.zeros(13, np.int64)

    for i in range(t.size):
        tm = int(t[i])
        px = int(mid2[i])

        while si < swing_t.size and swing_t[si] <= tm:
            idx = 0 if swing_side[si] > 0 else 1
            latest_level[idx] = swing_level[si]
            latest_id[idx] = swing_id[si]
            si += 1

        j15 = bidx(s15e, tm)
        if j15 < 13:
            continue
        j1 = bidx(s1e, tm)
        j5 = bidx(s5e, tm)

        if j5 >= 0 and j5 != last_s5:
            last_s5 = j5
            close5 = int(s5c[j5])
            for idx in range(2):
                side = 1 if idx == 0 else -1
                if state[idx] != 0:
                    continue
                lid = latest_id[idx]
                L = latest_level[idx]
                if lid == 0 or lid == used_id[idx]:
                    continue
                ae = float(s15atr[j15])
                if ae <= 0:
                    continue
                disp = side * (close5 - L)
                if disp <= 0 or disp / ae < BREAKNORM_MIN:
                    continue

                require_break_context = profile in (0, 1, 3)
                if require_break_context and not raw_parent_matches(tm, side, pe, praw):
                    cnt[6] += 1
                    continue

                state[idx] = 1
                level[idx] = L
                evatr[idx] = ae
                event_start[idx] = tm
                accept_start[idx] = tm
                retest_start[idx] = 0
                boundary_id[idx] = lid
                fail_pending_tick[idx] = -1
                cnt[0] += 1

        for idx in range(2):
            st = state[idx]
            if st == 0:
                continue
            side = 1 if idx == 0 else -1
            L = level[idx]
            ae = evatr[idx]
            pos = side * (px - L)

            if profile == 3 and not raw_parent_matches(tm, side, pe, praw):
                cnt[8] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1
                continue

            if tm - event_start[idx] > MAX_EVENT_MS:
                cnt[4] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1
                continue

            if st == 1:
                if pos < -PENETRATION_BUFFER_ATR * ae:
                    cnt[3] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1
                    continue
                if pos > 0:
                    if accept_start[idx] == 0:
                        accept_start[idx] = tm
                    if tm - accept_start[idx] >= ACCEPT_DWELL_MS:
                        state[idx] = 2
                        cnt[1] += 1
                        st = 2
                else:
                    if accept_start[idx] != 0:
                        cnt[9] += 1
                    accept_start[idx] = 0

            if st == 2:
                if abs(px - L) <= RETEST_HALFWIDTH_ATR * ae:
                    state[idx] = 3
                    retest_start[idx] = tm
                    fail_pending_tick[idx] = -1
                    cnt[2] += 1
                    st = 3

            if st == 3:
                if tm - retest_start[idx] > MAX_RETEST_MS:
                    cnt[4] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1
                    continue

                adverse = pos < -PENETRATION_BUFFER_ATR * ae
                if adverse:
                    if fail_pending_tick[idx] >= 0 and i > fail_pending_tick[idx]:
                        cnt[3] += 1
                        cnt[12] += 1
                        used_id[idx] = boundary_id[idx]
                        state[idx] = 0
                        fail_pending_tick[idx] = -1
                        continue
                    elif fail_pending_tick[idx] < 0:
                        fail_pending_tick[idx] = i
                        cnt[10] += 1
                elif fail_pending_tick[idx] >= 0:
                    fail_pending_tick[idx] = -1
                    cnt[11] += 1

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
                leaves_zone = disp > RETEST_HALFWIDTH_ATR * ae
                quality = side * eff1 >= REBREAK_EFF_MIN
                if not (leaves_zone and disp / ae >= REBREAK_DISP_ATR and quality):
                    continue

                require_rebreak_context = profile in (0, 2, 3)
                if require_rebreak_context and not raw_parent_matches(tm, side, pe, praw):
                    cnt[7] += 1
                    continue

                if nsig < sig_t.size:
                    sig_t[nsig] = tm
                    sig_side[nsig] = side
                    sig_boundary[nsig] = boundary_id[idx]
                    nsig += 1
                    cnt[5] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1

    return sig_t[:nsig], sig_side[:nsig], sig_boundary[:nsig], cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-producer", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    base = load_base(args.base_producer)
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if evidence.get("schema") != "delta-r037-dh02-s08-context-placement-evidence-12b-v1":
        raise SystemExit("unexpected evidence schema")
    if evidence.get("vector_fingerprint") != "7c70b5304ff7":
        raise SystemExit("unexpected S08 vector fingerprint")

    source_sha = sha256_file(args.source)
    if source_sha != CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df = pd.read_csv(
        args.source, compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"], dtype=np.int64,
    )
    df = df[df.timestamp_ms_utc < STAGE_A_END_MS]
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
            pe, praw, pi,
        )
        exe = base.execute_r9_lifecycle(t, ask, bid, st, ss)
        actual = {
            "signals": int(len(st)),
            "signal_sha256": base.signal_sha(st, ss, sb),
            "breaks": int(cnt[0]),
            "accepted": int(cnt[1]),
            "retests": int(cnt[2]),
            "failed": int(cnt[3]),
            "expired": int(cnt[4]),
            "break_context_vetoes": int(cnt[6]),
            "rebreak_context_vetoes": int(cnt[7]),
            "active_context_invalidations": int(cnt[8]),
            "dwell_resets": int(cnt[9]),
            "failure_pending_starts": int(cnt[10]),
            "failure_pending_resets": int(cnt[11]),
            "failure_pending_confirms": int(cnt[12]),
            "trades": int(exe[0]),
            "raw_positive_wins": int(exe[1]),
            "official_wins": int(exe[2]),
            "gross_profit": float(exe[3]),
            "gross_loss": float(exe[4]),
            "net_profit": float(exe[5]),
            "max_balance_drawdown": float(exe[6]),
        }
        err = {
            "trades": abs(actual["trades"] - TARGET["trades"]),
            "raw_positive_wins": abs(actual["raw_positive_wins"] - TARGET["raw_positive_wins"]),
            "gross_profit": abs(actual["gross_profit"] - TARGET["gross_profit"]),
            "gross_loss": abs(actual["gross_loss"] - TARGET["gross_loss"]),
            "net_profit": abs(actual["net_profit"] - TARGET["net_profit"]),
            "max_balance_drawdown": abs(actual["max_balance_drawdown"] - TARGET["max_balance_drawdown"]),
        }
        score = (
            100.0 * err["trades"]
            + 25.0 * err["raw_positive_wins"]
            + err["gross_profit"] + err["gross_loss"]
            + err["net_profit"] + err["max_balance_drawdown"]
        )
        profiles[pname] = {"actual": actual, "abs_error": err, "parity_score": float(score)}

    control = profiles["CONTROL_BREAK_AND_REBREAK"]["actual"]
    if (
        control["signal_sha256"] != CONTROL_SIGNAL_SHA
        or control["trades"] != 105
        or control["raw_positive_wins"] != 37
        or abs(control["gross_profit"] - 8.75) > 0.011
        or abs(control["gross_loss"] + 37.73) > 0.011
        or abs(control["net_profit"] + 28.98) > 0.011
    ):
        raise SystemExit("12A control fingerprint mismatch")

    order = sorted(PROFILES, key=lambda p: profiles[p]["parity_score"])
    lead = order[0]
    a = profiles[lead]["actual"]
    exact = (
        a["trades"] == TARGET["trades"]
        and a["raw_positive_wins"] == TARGET["raw_positive_wins"]
        and abs(a["gross_profit"] - TARGET["gross_profit"]) < 0.011
        and abs(a["gross_loss"] - TARGET["gross_loss"]) < 0.011
        and abs(a["net_profit"] - TARGET["net_profit"]) < 0.011
        and abs(a["max_balance_drawdown"] - TARGET["max_balance_drawdown"]) < 0.011
    )

    out = {
        "schema": "delta-r037-dh02-s08-context-placement-12b-v1",
        "status": "COMPLETE_EXACT_PARITY" if exact else "COMPLETE_CONTEXT_PLACEMENT_LOCALIZATION",
        "unit": evidence["unit"],
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint": evidence["vector_fingerprint"],
        "numeric_vector_retune": False,
        "august_accessed": False,
        "control_12a_reproduced": True,
        "profiles": profiles,
        "ranking": order,
        "finding": {
            "leading_profile": lead,
            "exact_historical_parity": exact,
            "target": TARGET,
            "historical_r032_incremental_owned_entries": 71,
            "next": (
                "R037_DH03_S06_CLEANROOM_PARITY_RECONSTRUCTION"
                if exact
                else evidence["next_if_no_candidate"]
            ),
        },
        "mql5_authorized": False,
    }
    atomic_write_json(args.output, out)
    print(json.dumps(out["finding"], separators=(",", ":")))


if __name__ == "__main__":
    main()
