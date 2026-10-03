"""DELTA R037 DH02-S08 clean-room parity reconstruction — Checkpoint 12A.

Bounded reconstruction only. Frozen S08 thresholds are never retuned.

Reconstructible contract:
- width-2 causally confirmed M1 swing boundary inherited from fixed DH01-A02;
- completed-S5 break observation;
- ATR(14) on completed S15, frozen at break;
- one-second causal breakout acceptance dwell;
- frozen retest zone and penetration buffer from event ATR;
- tick-persistence failure represented by the same explicit two-adverse-tick
  clean-room surrogate already provenance-limited by S11/11G;
- completed-S1 rebreak with four-completed-bar SignedEfficiency;
- DH01 parent direction reconstructed from completed M15/M30/H1 directional
  labels using the fixed A02 0.30 efficiency/displacement thresholds;
- one boundary + one original break direction = one event;
- frozen R9 downstream stop/trail/max-hold execution.

Profiles are semantic diagnostics only; no numeric parameter changes are tested.
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
    "NO_CONTEXT_CONTINUOUS_DWELL_DIAGNOSTIC",
    "RAW_PARENT_DIRECTION_CONTINUOUS_DWELL",
    "HYSTERETIC_PARENT_DIRECTION_CONTINUOUS_DWELL",
    "HYSTERETIC_PARENT_DIRECTION_EVENTAGE_DWELL",
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


def parent_direction_series(e15, d15, e30, d30, eh1, dh1):
    """Causal parent-direction diagnostics on parent-bar close events.

    raw direction = 2-of-3 majority among nonzero completed M15/M30/H1 labels.
    stable direction = DH01-A02-style 2-confirmation hysteresis on raw direction.
    A zero/ambiguous raw state does not erase an already confirmed parent direction.
    """
    times = np.unique(np.concatenate((e15, e30, eh1))).astype(np.int64)
    raw = np.zeros(times.size, dtype=np.int8)
    stable = np.zeros(times.size, dtype=np.int8)
    cur = 0
    pending = 0
    pending_n = 0
    for i, tm in enumerate(times):
        labels = []
        for end, lab in ((e15, d15), (e30, d30), (eh1, dh1)):
            j = np.searchsorted(end, tm, side="right") - 1
            labels.append(int(lab[j]) if j >= 0 else 0)
        up = sum(1 for x in labels if x > 0)
        dn = sum(1 for x in labels if x < 0)
        r = 1 if up >= 2 else (-1 if dn >= 2 else 0)
        raw[i] = r
        if r == 0:
            pending = 0
            pending_n = 0
        elif r == cur:
            pending = 0
            pending_n = 0
        else:
            if pending == r:
                pending_n += 1
            else:
                pending = r
                pending_n = 1
            if pending_n >= 2:
                cur = r
                pending = 0
                pending_n = 0
        stable[i] = cur
    return times, raw, stable


@njit(cache=True)
def bidx(end, tm):
    return np.searchsorted(end, tm, side="right") - 1


@njit(cache=True)
def parent_match(tm, side, pe, praw, pstable, profile):
    if profile == 0:
        return True
    j = bidx(pe, tm)
    if j < 0:
        return False
    pd = praw[j] if profile == 1 else pstable[j]
    return pd == side


@njit(cache=True)
def generate_signals(
    t, mid2,
    swing_t, swing_side, swing_level, swing_id,
    s1e, s1c, s1eff,
    s5e, s5c,
    s15e, s15atr,
    pe, praw, pstable,
    profile,
):
    # index 0 = long/+1/high break, 1 = short/-1/low break
    # state: 0 idle, 1 broken-await-dwell, 2 accepted, 3 retesting
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

    # break, accepted, retest, failed, expired, signal, context_veto,
    # dwell_reset, failure_pending_start, failure_pending_reset, failure_pending_confirm
    cnt = np.zeros(11, np.int64)

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

        # Newly completed S5 can create a break event.
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
                if not parent_match(tm, side, pe, praw, pstable, profile):
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

        # Evolve live events on ticks.
        for idx in range(2):
            st = state[idx]
            if st == 0:
                continue
            side = 1 if idx == 0 else -1
            L = level[idx]
            ae = evatr[idx]
            pos = side * (px - L)

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

                if profile == 3:
                    # Bounded diagnostic: event-age dwell; shallow recross does not
                    # reset the original one-second clock.
                    if tm - event_start[idx] >= ACCEPT_DWELL_MS and pos > 0:
                        state[idx] = 2
                        cnt[1] += 1
                        st = 2
                else:
                    # Stronger literal white-paper reading: price must remain on the
                    # breakout side for the full dwell; shallow recross resets dwell.
                    if pos > 0:
                        if accept_start[idx] == 0:
                            accept_start[idx] = tm
                        if tm - accept_start[idx] >= ACCEPT_DWELL_MS:
                            state[idx] = 2
                            cnt[1] += 1
                            st = 2
                    else:
                        if accept_start[idx] != 0:
                            cnt[7] += 1
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
                        cnt[10] += 1
                        used_id[idx] = boundary_id[idx]
                        state[idx] = 0
                        fail_pending_tick[idx] = -1
                        continue
                    elif fail_pending_tick[idx] < 0:
                        fail_pending_tick[idx] = i
                        cnt[8] += 1
                elif fail_pending_tick[idx] >= 0:
                    fail_pending_tick[idx] = -1
                    cnt[9] += 1

        # Rebreak uses newly completed S1 only.
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
                if (
                    leaves_zone
                    and disp / ae >= REBREAK_DISP_ATR
                    and quality
                ):
                    if not parent_match(tm, side, pe, praw, pstable, profile):
                        cnt[6] += 1
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


@njit(cache=True)
def qtick(v, tick=10):
    return ((v + tick // 2) // tick) * tick


@njit(cache=True)
def execute_r9_lifecycle(t, ask, bid, sig_t, sig_side):
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
    if evidence.get("schema") != "delta-r037-dh02-s08-cleanroom-parity-evidence-12a-v1":
        raise SystemExit("unexpected evidence schema")
    if evidence["vector"]["fingerprint"] != "7c70b5304ff7":
        raise SystemExit("unexpected S08 vector fingerprint")

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
    bm1 = bars(t, mid2, 60_000)
    bm15 = bars(t, mid2, 900_000)
    bm30 = bars(t, mid2, 1_800_000)
    bh1 = bars(t, mid2, 3_600_000)

    s15atr = atr14(b15)
    s1eff = signed_eff(b1, 4)
    swing_t, swing_side, swing_level, swing_id = symmetric_swings(bm1, 2)

    d15 = directional_label(bm15, 3, 0.3, 0.3)
    d30 = directional_label(bm30, 3, 0.3, 0.3)
    dh1 = directional_label(bh1, 3, 0.3, 0.3)
    pe, praw, pstable = parent_direction_series(
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
            pe, praw, pstable,
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
            "dwell_resets": int(cnt[7]),
            "failure_pending_starts": int(cnt[8]),
            "failure_pending_resets": int(cnt[9]),
            "failure_pending_confirms": int(cnt[10]),
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
            + err["gross_profit"]
            + err["gross_loss"]
            + err["net_profit"]
            + err["max_balance_drawdown"]
        )
        profiles[pname] = {"actual": actual, "abs_error": err, "parity_score": float(score)}

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
        "schema": "delta-r037-dh02-s08-cleanroom-parity-12a-v1",
        "status": "COMPLETE_EXACT_PARITY" if exact else "COMPLETE_CLEANROOM_PARITY_FAIL_LOCALIZED",
        "unit": "R037_DH02_S08_CLEANROOM_PARITY_RECONSTRUCTION",
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint": "7c70b5304ff7",
        "numeric_vector_retune": False,
        "august_accessed": False,
        "profiles": profiles,
        "ranking": order,
        "finding": {
            "leading_profile": lead,
            "exact_historical_parity": exact,
            "target": TARGET,
            "next": (
                "R037_DH03_S06_CLEANROOM_PARITY_RECONSTRUCTION"
                if exact
                else evidence["next_if_full_parity_false"]
            ),
        },
        "mql5_authorized": False,
    }
    atomic_write_json(args.output, out)
    print(json.dumps(out["finding"], separators=(",", ":")))


if __name__ == "__main__":
    main()
