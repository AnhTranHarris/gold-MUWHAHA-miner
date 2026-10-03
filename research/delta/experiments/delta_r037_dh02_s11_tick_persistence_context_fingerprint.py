"""DELTA R037 DH02-S11 tick-persistence/context semantic fingerprint — Checkpoint 11B.

Bounded categorical-semantic reconstruction only. Frozen S11 numeric thresholds are
never retuned.

Committed 11B evidence constrains exactly six profiles:
- persistence = one, two, or three causal confirming ticks;
- context = decision-only (break + rebreak) or continuous lifecycle veto.

CONTROL_NEXT_TICK_DECISION_CONTEXT must reproduce the 11A leading signal fingerprint
and counters before any candidate result can be accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

DAY_MS = 86_400_000
TICK_RAW = 10
STAGE_A_END_MS = 1_768_737_600_000
US_DST_START_2026_MS = 1_772_953_200_000
UK_DST_START_2026_MS = 1_774_746_000_000
P75_POINTS = np.asarray([20, 20, 21, 21], dtype=np.int64)
CANONICAL_JAN_SHA256 = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"

BREAKNORM_MIN = 0.2467
MAX_EVENT_MS = int(round(107.701 * 1000))
MAX_RETEST_MS = int(round(84.8787 * 1000))
PENETRATION_BUFFER_ATR = 0.1172
REBREAK_DISP_ATR = 0.2246
REBREAK_EFF_MIN = 0.4903
RETEST_HALFWIDTH_ATR = 0.3249

TARGET = {
    "trades": 75,
    "raw_positive_wins": 41,
    "gross_profit": 9.39,
    "gross_loss": -17.60,
    "net_profit": -8.21,
}
PROFILES = (
    "CONTROL_NEXT_TICK_DECISION_CONTEXT",
    "TWO_TICK_DECISION_CONTEXT",
    "THREE_TICK_DECISION_CONTEXT",
    "NEXT_TICK_LIFECYCLE_CONTEXT",
    "TWO_TICK_LIFECYCLE_CONTEXT",
    "THREE_TICK_LIFECYCLE_CONTEXT",
)


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
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
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


def session_code(t):
    tod = t % DAY_MS
    ls = np.where(t >= UK_DST_START_2026_MS, 7, 8) * 3_600_000
    le = ls + 8 * 3_600_000 + 30 * 60_000
    ns = np.where(t >= US_DST_START_2026_MS, 12, 13) * 3_600_000
    ne = ns + 9 * 3_600_000
    il = (tod >= ls) & (tod < le)
    iny = (tod >= ns) & (tod < ne)
    return np.where(il & iny, 2, np.where(il, 1, np.where(iny, 3, 0))).astype(np.int8)


def p75(t, a, b):
    s = session_code(t)
    sp = P75_POINTS[s] * TICK_RAW
    mid2 = a.astype(np.int64) + b.astype(np.int64)
    bid = ((mid2 - sp + TICK_RAW) // (2 * TICK_RAW)) * TICK_RAW
    return (bid + sp).astype(np.int64), bid.astype(np.int64)


def bars(t, mid2, tf_ms):
    bucket = t // int(tf_ms)
    st = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    en = np.r_[st[1:], len(t)]
    return {
        "end_ms": ((bucket[st] + 1) * int(tf_ms)).astype(np.int64),
        "open": mid2[st].astype(np.int64),
        "close": mid2[en - 1].astype(np.int64),
        "high": np.maximum.reduceat(mid2, st).astype(np.int64),
        "low": np.minimum.reduceat(mid2, st).astype(np.int64),
    }


def atr14(b):
    h, l, c = b["high"], b["low"], b["close"]
    tr = (h - l).copy()
    if len(tr) > 1:
        tr[1:] = np.maximum(
            tr[1:],
            np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])),
        )
    cs = np.r_[0, np.cumsum(tr, dtype=np.int64)]
    out = np.zeros(len(tr), dtype=np.float64)
    for i in range(13, len(tr)):
        out[i] = (cs[i + 1] - cs[i - 13]) / 14.0
    return out


def signed_eff(b, n):
    c = b["close"]
    out = np.zeros(len(c), dtype=np.float64)
    for j in range(n, len(c)):
        net = c[j] - c[j - n]
        path = 0
        for k in range(j - n + 1, j + 1):
            path += abs(c[k] - c[k - 1])
        if path > 0:
            out[j] = net / float(path)
    return out


def directional_label(b, n=3, disp_min=0.3, eff_min=0.3):
    c = b["close"]
    atr = atr14(b)
    eff = signed_eff(b, n)
    out = np.zeros(len(c), dtype=np.int8)
    for j in range(max(13, n), len(c)):
        if atr[j] <= 0:
            continue
        disp = (c[j] - c[j - n]) / atr[j]
        if abs(disp) >= disp_min and abs(eff[j]) >= eff_min and disp * eff[j] > 0:
            out[j] = 1 if disp > 0 else -1
    return out


def symmetric_swings(b, width=2):
    hi, lo, end = b["high"], b["low"], b["end_ms"]
    rev, side, lev, ids = [], [], [], []
    ident = 0
    for k in range(width, len(hi) - width):
        h, l = hi[k], lo[k]
        ish = all(h > hi[k-j] and h > hi[k+j] for j in range(1, width + 1))
        isl = all(l < lo[k-j] and l < lo[k+j] for j in range(1, width + 1))
        reveal = int(end[k + width])
        if ish:
            ident += 1
            rev.append(reveal); side.append(1); lev.append(int(h)); ids.append(ident)
        if isl:
            ident += 1
            rev.append(reveal); side.append(-1); lev.append(int(l)); ids.append(ident)
    rev = np.asarray(rev, np.int64)
    order = np.argsort(rev, kind="stable")
    return (
        rev[order],
        np.asarray(side, np.int8)[order],
        np.asarray(lev, np.int64)[order],
        np.asarray(ids, np.int64)[order],
    )


@njit(cache=True)
def bidx(end, tm):
    return np.searchsorted(end, tm, side="right") - 1


@njit(cache=True)
def conflict_at(tm, e15, d15, e30, d30, eh1, dh1, eh4, dh4):
    labels = np.zeros(4, np.int8)
    j = bidx(e15, tm)
    if j >= 0: labels[0] = d15[j]
    j = bidx(e30, tm)
    if j >= 0: labels[1] = d30[j]
    j = bidx(eh1, tm)
    if j >= 0: labels[2] = dh1[j]
    j = bidx(eh4, tm)
    if j >= 0: labels[3] = dh4[j]
    up = False
    dn = False
    for k in range(4):
        if labels[k] > 0: up = True
        elif labels[k] < 0: dn = True
    return up and dn


@njit(cache=True)
def generate_signals(
    t, mid2,
    swing_t, swing_side, swing_level, swing_id,
    s1e, s1c, s5e, s5c, s5eff, s15e, s15atr,
    c15e, c15d, c30e, c30d, ch1e, ch1d, ch4e, ch4d,
    profile,
):
    persistence_ticks = (profile % 3) + 1
    continuous_context = profile >= 3

    state = np.zeros(2, np.int8)
    level = np.zeros(2, np.int64)
    evatr = np.zeros(2, np.float64)
    event_start = np.zeros(2, np.int64)
    retest_start = np.zeros(2, np.int64)
    boundary_id = np.zeros(2, np.int64)
    used_id = np.zeros(2, np.int64)
    break_tick = np.full(2, -1, np.int64)
    fail_pending_tick = np.full(2, -1, np.int64)
    accept_confirm_count = np.zeros(2, np.int16)
    fail_confirm_count = np.zeros(2, np.int16)

    latest_level = np.zeros(2, np.int64)
    latest_id = np.zeros(2, np.int64)
    si = 0
    last_s1 = -1
    last_s5 = -1

    sig_t = np.empty(20000, np.int64)
    sig_side = np.empty(20000, np.int8)
    sig_boundary = np.empty(20000, np.int64)
    nsig = 0

    # break, accepted, retest, failed, expired, signal, context_veto
    cnt = np.zeros(7, np.int64)

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

        if j1 >= 0 and j1 != last_s1:
            last_s1 = j1
            close1 = int(s1c[j1])
            conflict = conflict_at(tm, c15e, c15d, c30e, c30d, ch1e, ch1d, ch4e, ch4d)

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
                disp = side * (close1 - L)
                if disp <= 0 or disp / ae < BREAKNORM_MIN:
                    continue
                if conflict:
                    cnt[6] += 1
                    continue

                state[idx] = 1
                level[idx] = L
                evatr[idx] = ae
                event_start[idx] = tm
                retest_start[idx] = 0
                boundary_id[idx] = lid
                break_tick[idx] = i
                fail_pending_tick[idx] = -1
                accept_confirm_count[idx] = 0
                fail_confirm_count[idx] = 0
                cnt[0] += 1

        for idx in range(2):
            st = state[idx]
            if st == 0:
                continue
            side = 1 if idx == 0 else -1
            L = level[idx]
            ae = evatr[idx]

            if tm - event_start[idx] > MAX_EVENT_MS:
                cnt[4] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1
                accept_confirm_count[idx] = 0
                fail_confirm_count[idx] = 0
                continue

            if continuous_context and conflict_at(tm, c15e, c15d, c30e, c30d, ch1e, ch1d, ch4e, ch4d):
                cnt[6] += 1
                used_id[idx] = boundary_id[idx]
                state[idx] = 0
                fail_pending_tick[idx] = -1
                accept_confirm_count[idx] = 0
                fail_confirm_count[idx] = 0
                continue

            if st == 1:
                if i > break_tick[idx] and side * (px - L) > 0:
                    accept_confirm_count[idx] += 1
                    if accept_confirm_count[idx] >= persistence_ticks:
                        state[idx] = 2
                        cnt[1] += 1
                        st = 2
                elif i > break_tick[idx]:
                    accept_confirm_count[idx] = 0
                    if side * (px - L) < -PENETRATION_BUFFER_ATR * ae:
                        used_id[idx] = boundary_id[idx]
                        state[idx] = 0
                        cnt[3] += 1
                        fail_pending_tick[idx] = -1
                        fail_confirm_count[idx] = 0
                        continue

            if st == 2:
                if abs(px - L) <= RETEST_HALFWIDTH_ATR * ae:
                    state[idx] = 3
                    retest_start[idx] = tm
                    fail_pending_tick[idx] = -1
                    fail_confirm_count[idx] = 0
                    cnt[2] += 1
                    st = 3

            if st == 3:
                if tm - retest_start[idx] > MAX_RETEST_MS:
                    cnt[4] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1
                    fail_confirm_count[idx] = 0
                    continue

                adverse = side * (px - L) < -PENETRATION_BUFFER_ATR * ae
                if adverse:
                    if fail_pending_tick[idx] < 0:
                        fail_pending_tick[idx] = i
                        fail_confirm_count[idx] = 0
                    elif i > fail_pending_tick[idx]:
                        fail_confirm_count[idx] += 1
                        if fail_confirm_count[idx] >= persistence_ticks:
                            cnt[3] += 1
                            used_id[idx] = boundary_id[idx]
                            state[idx] = 0
                            fail_pending_tick[idx] = -1
                            fail_confirm_count[idx] = 0
                            continue
                else:
                    fail_pending_tick[idx] = -1
                    fail_confirm_count[idx] = 0

        if j5 >= 4 and j5 != last_s5:
            last_s5 = j5
            close5 = int(s5c[j5])
            eff5 = float(s5eff[j5])
            conflict = conflict_at(tm, c15e, c15d, c30e, c30d, ch1e, ch1d, ch4e, ch4d)

            for idx in range(2):
                if state[idx] != 3:
                    continue
                side = 1 if idx == 0 else -1
                L = level[idx]
                ae = evatr[idx]
                disp = side * (close5 - L)
                leaves_zone = disp > RETEST_HALFWIDTH_ATR * ae
                quality = side * eff5 >= REBREAK_EFF_MIN
                if (
                    leaves_zone
                    and disp / ae >= REBREAK_DISP_ATR
                    and quality
                    and not conflict
                ):
                    if nsig >= sig_t.size:
                        continue
                    sig_t[nsig] = tm
                    sig_side[nsig] = side
                    sig_boundary[nsig] = boundary_id[idx]
                    nsig += 1
                    cnt[5] += 1
                    used_id[idx] = boundary_id[idx]
                    state[idx] = 0
                    fail_pending_tick[idx] = -1
                    fail_confirm_count[idx] = 0

    return sig_t[:nsig], sig_side[:nsig], sig_boundary[:nsig], cnt


@njit(cache=True)
def qtick(v, tick=10):
    return ((v + tick // 2) // tick) * tick


@njit(cache=True)
def execute_r9_lifecycle(t, ask, bid, sig_t, sig_side):
    # frozen 0.01-lot R9 lifecycle on specialist entries
    stopd = 300
    trail_activation = 100
    trail_distance = 30

    pos = 0
    entry = 0
    stop = 0
    entrysec = 0
    sp = 0

    trades = 0
    raw_wins = 0
    official_wins = 0
    gp = 0.0
    gl = 0.0
    balance = 100000.0
    peak = balance
    maxdd = 0.0

    for i in range(t.size):
        tm = int(t[i])
        a = int(ask[i])
        b = int(bid[i])
        sec = tm // 1000

        if pos == 1 and b <= stop:
            raw = (b - entry) / 1000.0
            deal = raw - 0.01
            if raw > 0:
                raw_wins += 1
                gp += deal
            else:
                gl += deal
            if deal > 0:
                official_wins += 1
            balance += deal
            trades += 1
            pos = 0
        elif pos == -1 and a >= stop:
            raw = (entry - a) / 1000.0
            deal = raw - 0.01
            if raw > 0:
                raw_wins += 1
                gp += deal
            else:
                gl += deal
            if deal > 0:
                official_wins += 1
            balance += deal
            trades += 1
            pos = 0

        if pos != 0:
            if sec - entrysec >= 30:
                raw = ((b - entry) if pos == 1 else (entry - a)) / 1000.0
                deal = raw - 0.01
                if raw > 0:
                    raw_wins += 1
                    gp += deal
                else:
                    gl += deal
                if deal > 0:
                    official_wins += 1
                balance += deal
                trades += 1
                pos = 0
            else:
                fav = (b - entry) if pos == 1 else (entry - a)
                if fav >= trail_activation:
                    new_stop = qtick(b - trail_distance if pos == 1 else a + trail_distance)
                    if (pos == 1 and new_stop > stop) or (pos == -1 and new_stop < stop):
                        stop = new_stop

        # Consume all signals whose causal timestamp is now visible.
        while sp < sig_t.size and sig_t[sp] <= tm:
            side = int(sig_side[sp])
            if pos == 0:
                pos = side
                entrysec = sec
                if side == 1:
                    entry = a
                    stop = qtick(b - stopd)
                else:
                    entry = b
                    stop = qtick(a + stopd)
                balance -= 0.01
                gl -= 0.01
            sp += 1

        if balance > peak:
            peak = balance
        dd = peak - balance
        if dd > maxdd:
            maxdd = dd

    return trades, raw_wins, official_wins, gp, gl, gp + gl, maxdd


def signal_sha(t, side, boundary):
    h = hashlib.sha256()
    for a, b, c in zip(t.tolist(), side.tolist(), boundary.tolist()):
        h.update(f"{int(a)},{int(b)},{int(c)}\n".encode("ascii"))
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if evidence.get("schema") != "delta-r037-dh02-s11-tick-persistence-context-evidence-11b-v1":
        raise SystemExit("unexpected evidence schema")
    source_sha = sha256_file(args.source)
    if source_sha != CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df = pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype=np.int64,
    )
    df = df[df.timestamp_ms_utc < STAGE_A_END_MS]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t) != 4_205_709:
        raise SystemExit(f"Stage-A tick mismatch: {len(t)}")

    ask, bid = p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    mid2 = ask + bid

    b1 = bars(t, mid2, 1_000)
    b5 = bars(t, mid2, 5_000)
    b15 = bars(t, mid2, 15_000)
    bm5 = bars(t, mid2, 300_000)
    bm15 = bars(t, mid2, 900_000)
    bm30 = bars(t, mid2, 1_800_000)
    bh1 = bars(t, mid2, 3_600_000)
    bh4 = bars(t, mid2, 14_400_000)

    s15atr = atr14(b15)
    s5eff = signed_eff(b5, 4)
    swing_t, swing_side, swing_level, swing_id = symmetric_swings(bm5, 2)

    d15 = directional_label(bm15, 3, 0.3, 0.3)
    d30 = directional_label(bm30, 3, 0.3, 0.3)
    dh1 = directional_label(bh1, 3, 0.3, 0.3)
    dh4 = directional_label(bh4, 3, 0.3, 0.3)

    profiles = {}
    for pi, pname in enumerate(PROFILES):
        st, ss, sb, cnt = generate_signals(
            t, mid2,
            swing_t, swing_side, swing_level, swing_id,
            b1["end_ms"], b1["close"],
            b5["end_ms"], b5["close"], s5eff,
            b15["end_ms"], s15atr,
            bm15["end_ms"], d15,
            bm30["end_ms"], d30,
            bh1["end_ms"], dh1,
            bh4["end_ms"], dh4,
            pi,
        )
        exe = execute_r9_lifecycle(t, ask, bid, st, ss)
        actual = {
            "signals": int(len(st)),
            "signal_sha256": signal_sha(st, ss, sb),
            "breaks": int(cnt[0]),
            "accepted": int(cnt[1]),
            "retests": int(cnt[2]),
            "failed": int(cnt[3]),
            "expired": int(cnt[4]),
            "context_vetoes": int(cnt[6]),
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
        }
        # Trade count dominates parity choice; economics break ties.
        score = (
            100.0 * err["trades"]
            + 25.0 * err["raw_positive_wins"]
            + err["gross_profit"]
            + err["gross_loss"]
            + err["net_profit"]
        )
        profiles[pname] = {"actual": actual, "abs_error": err, "parity_score": float(score)}

    control = profiles["CONTROL_NEXT_TICK_DECISION_CONTEXT"]["actual"]
    expected_control = evidence["control_11a"]
    control_checks = {
        "signals": control["signals"] == int(expected_control["signals"]),
        "trades": control["trades"] == int(expected_control["trades"]),
        "raw_positive_wins": control["raw_positive_wins"] == int(expected_control["raw_positive_wins"]),
        "breaks": control["breaks"] == int(expected_control["breaks"]),
        "accepted": control["accepted"] == int(expected_control["accepted"]),
        "retests": control["retests"] == int(expected_control["retests"]),
        "failed": control["failed"] == int(expected_control["failed"]),
        "expired": control["expired"] == int(expected_control["expired"]),
        "context_vetoes": control["context_vetoes"] == int(expected_control["context_vetoes"]),
        "signal_sha256": control["signal_sha256"] == expected_control["signal_sha256"],
    }
    if not all(control_checks.values()):
        raise SystemExit("11A control fingerprint mismatch: " + json.dumps(control_checks, sort_keys=True))

    order = sorted(PROFILES, key=lambda p: profiles[p]["parity_score"])
    lead = order[0]
    a = profiles[lead]["actual"]
    exact = (
        a["trades"] == TARGET["trades"]
        and a["raw_positive_wins"] == TARGET["raw_positive_wins"]
        and abs(a["gross_profit"] - TARGET["gross_profit"]) < 0.011
        and abs(a["gross_loss"] - TARGET["gross_loss"]) < 0.011
        and abs(a["net_profit"] - TARGET["net_profit"]) < 0.011
    )

    out = {
        "schema": "delta-r037-dh02-s11-tick-persistence-context-fingerprint-11b-v1",
        "status": "COMPLETE_EXACT_PARITY" if exact else "COMPLETE_CLEANROOM_PARITY_FAIL_LOCALIZED",
        "unit": "R037_DH02_S11_TICK_PERSISTENCE_AND_CONTEXT_SEMANTICS_PARITY_FINGERPRINT",
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint": "50d1bb2e656e",
        "numeric_vector_retune": False,
        "august_accessed": False,
        "profiles": profiles,
        "control_11a_reproduced_exactly": True,
        "ranking": order,
        "finding": {
            "leading_profile": lead,
            "exact_historical_parity": exact,
            "target": TARGET,
            "next": (
                "R037_DH02_S08_CLEANROOM_PARITY_RECONSTRUCTION"
                if exact
                else evidence["next_if_localized"]
            ),
        },
        "mql5_authorized": False,
    }
    atomic_write_json(args.output, out)
    print(json.dumps(out["finding"], separators=(",", ":")))


if __name__ == "__main__":
    main()
