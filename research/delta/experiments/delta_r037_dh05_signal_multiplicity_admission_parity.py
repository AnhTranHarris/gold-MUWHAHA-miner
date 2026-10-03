"""DELTA R037 DH05 probe-qualification clock / event-lifecycle parity diagnostic.

Checkpoint 09J candidate producer. Research-only signal-multiplicity / executable-admission parity diagnostic.

Frozen from 09C + 09D:
- symmetric two-bar confirmed M5 swing boundary;
- repeated causal same-boundary pre-failure probe-attempt ledger;
- BREAK_ACCEPTED only while event remains a qualified probe;
- acceptance_disp_atr = signed completed acceptance-bar body displacement / event M5 ATR;
- completed acceptance close remains beyond original boundary;
- failure-age clock starts at FAILURE_CANDIDATE;
- no frozen numeric-vector retuning.

This unit follows Checkpoints 09H/09I: pre-reversal generator decoupling is rejected.
It preserves serial episode ownership and tests only downstream signal multiplicity after
the first causal reversal confirmation, followed by a separate frozen R9-style one-position
executable-admission replay. Rearm is transition-based; no signal-every-bar shortcut, no
future information, and no numeric vector retuning.
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

VECTORS = (
    ("A03", .3, 15, 40, 20, .15, .08, .12, .5, 5),
    ("S05", .374062, 15, 9.099416, 6.468982, .244588, .093793, .217011, .062661, 5),
    ("S06", .217738, 5, 59.699117, 23.47226, .029179, .145085, .041213, .673017, 1),
    ("S09", .329294, 15, 41.910749, 10.844137, .335024, .12735, .272984, .126644, 1),
    ("S10", .26416, 5, 20.537168, 19.210606, .108825, .077129, .088265, .644213, 5),
    ("S16", .18608, 5, 31.219954, 3.711492, .279091, .121753, .206212, .746067, 5),
)

TARGET = {
    "A03": [6731, 1009, 207, 797, 432, 266, 187, 187],
    "S05": [7875, 318, 28, 290, 51, 15, 9, 9],
    "S06": [3470, 1606, 245, 1358, 1211, 683, 617, 617],
    "S09": [7748, 208, 40, 168, 61, 40, 9, 9],
    "S10": [6496, 1316, 202, 1106, 623, 294, 206, 206],
    "S16": [7870, 135, 43, 92, 37, 18, 8, 8],
}
STAGES = ["probe", "qualified", "accepted", "failure", "reentry", "reclaim", "reversal", "signal"]

# Serial control profiles:
# 0 CONTROL_09E: frozen 09E behavior.
# 1 POST_QUAL_BASE: 09F diagnostic chronology clue.
PROFILES = (
    "CONTROL_09E",
    "POST_QUAL_BASE",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    """Write JSON in the destination directory, fsync, then atomically replace."""
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


def bars(t, mid2, tf):
    bucket = t // tf
    st = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    en = np.r_[st[1:], len(t)]
    return {
        "end_ms": ((bucket[st] + 1) * tf).astype(np.int64),
        "open": mid2[st].astype(np.int64),
        "close": mid2[en - 1].astype(np.int64),
        "high": np.maximum.reduceat(mid2, st).astype(np.int64),
        "low": np.minimum.reduceat(mid2, st).astype(np.int64),
    }


def atr14(b):
    h, l, c = b["high"], b["low"], b["close"]
    tr = (h - l).copy()
    if len(tr) > 1:
        tr[1:] = np.maximum(tr[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    cs = np.r_[0, np.cumsum(tr, dtype=np.int64)]
    out = np.zeros(len(tr), dtype=np.float64)
    for i in range(13, len(tr)):
        out[i] = (cs[i + 1] - cs[i - 13]) / 14.0
    return out


def symmetric_swings(b, w=2):
    hi, lo, end = b["high"], b["low"], b["end_ms"]
    rev, side, lev = [], [], []
    for k in range(w, len(hi) - w):
        h = hi[k]
        l = lo[k]
        ish = all(h > hi[k - j] and h > hi[k + j] for j in range(1, w + 1))
        isl = all(l < lo[k - j] and l < lo[k + j] for j in range(1, w + 1))
        reveal = int(end[k + w])
        if ish:
            rev.append(reveal)
            side.append(1)
            lev.append(int(h))
        if isl:
            rev.append(reveal)
            side.append(-1)
            lev.append(int(l))
    arr = np.asarray(rev, np.int64)
    order = np.argsort(arr, kind="stable")
    return arr[order], np.asarray(side, np.int8)[order], np.asarray(lev, np.int64)[order]


@njit(cache=True)
def bidx(end, tm):
    return np.searchsorted(end, tm, side="right") - 1


@njit(cache=True)
def detect(
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
    profile,
):
    stage = 0
    oside = 0
    L = 0
    evatr = 0.0
    event_start = 0
    attempt_start = 0
    qualified_start = 0
    fstart = 0
    reent = False

    latest_hi = 0
    latest_lo = 0
    si = 0
    hiel = True
    loel = True
    lastacc = -1
    lastrev = -1
    attempt_open = False
    attempt_qualified = False
    cnt = np.zeros(8, np.int64)

    for i in range(t.size):
        tm = int(t[i])
        px = int(mid2[i])

        while si < st.size and st[si] <= tm:
            if ss[si] > 0:
                latest_hi = int(sl[si])
            else:
                latest_lo = int(sl[si])
            si += 1

        jm = bidx(m5e, tm)
        if jm < 13:
            continue
        ae = float(m5a[jm])
        if ae <= 0:
            continue

        if stage == 0:
            if latest_hi and px < latest_hi:
                hiel = True
            if latest_lo and px > latest_lo:
                loel = True
            if latest_hi and hiel and px >= latest_hi:
                stage = 1
                oside = 1
                L = latest_hi
                evatr = ae
                event_start = tm
                attempt_start = tm
                qualified_start = 0
                hiel = False
                cnt[0] += 1
                attempt_open = True
                attempt_qualified = False
            elif latest_lo and loel and px <= latest_lo:
                stage = 1
                oside = -1
                L = latest_lo
                evatr = ae
                event_start = tm
                attempt_start = tm
                qualified_start = 0
                loel = False
                cnt[0] += 1
                attempt_open = True
                attempt_qualified = False

        if stage == 0:
            continue

        if stage <= 2:
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

        j1 = bidx(s1e, tm)
        j5 = bidx(s5e, tm)
        j15 = bidx(s15e, tm)
        jacc = j5 if acctf == 5 else j15
        ac = s5c[j5] if acctf == 5 and j5 >= 0 else (s15c[j15] if j15 >= 0 else 0)
        ao = s5o[j5] if acctf == 5 and j5 >= 0 else (s15o[j15] if j15 >= 0 else 0)

        if stage == 1:
            if oside * (px - L) >= probeexc * evatr:
                stage = 2
                if qualified_start == 0:
                    qualified_start = tm
            else:
                stage1_clock = attempt_start
                if tm - stage1_clock > maxprobe:
                    stage = 0
                    oside = 0
                    attempt_open = False
                    attempt_qualified = False
                    qualified_start = 0
                    continue

        if stage < 2:
            continue

        if stage == 2 and jacc >= 0 and jacc != lastacc:
            lastacc = jacc
            acc_end = s5e[j5] if acctf == 5 and j5 >= 0 else (s15e[j15] if j15 >= 0 else 0)
            post_qual_bar = acc_end > qualified_start if qualified_start > 0 else False
            q = oside * (ac - ao) >= accdisp * evatr and oside * (ac - L) > 0
            if profile >= 1:
                q = q and post_qual_bar
            if q:
                cnt[2] += 1
                stage = 0
                oside = 0
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0
                continue

        recross = oside * (px - L) < 0

        stage2_clock = attempt_start

        if stage == 2:
            if tm - stage2_clock >= maxprobe or recross:
                stage = 3
                cnt[3] += 1
                fstart = tm
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0

        if stage == 3:
            if recross and not reent:
                reent = True
                cnt[4] += 1
                stage = 4
            elif fstart and tm - fstart > maxfail:
                stage = 0
                oside = 0
                reent = False
                continue
        elif stage >= 4 and fstart and tm - fstart > maxfail:
            stage = 0
            oside = 0
            reent = False
            continue

        if stage < 4:
            continue

        jrev = j1 if revtf == 1 else j5
        rc = s1c[j1] if revtf == 1 and j1 >= 0 else (s5c[j5] if j5 >= 0 else 0)
        if stage == 4 and jrev >= 0 and jrev != lastrev:
            if (-oside) * (rc - L) >= reclaim * evatr:
                cnt[5] += 1
                stage = 5

        if stage < 5 or jrev < 0 or jrev == lastrev:
            continue

        ro = s1o[j1] if revtf == 1 else s5o[j5]
        disp = (-oside) * (rc - ro)
        eff = 1.0 if abs(rc - ro) > 0 else 0.0
        if disp >= revdisp * evatr and eff >= effmin:
            cnt[6] += 1
            cnt[7] += 1
            stage = 0
            oside = 0
            reent = False
        lastrev = jrev

    return cnt



@njit(cache=True)
def detect_decoupled(
    t, mid2, st, ss, sl, m5e, m5a, s1e, s1o, s1c, s5e, s5o, s5c,
    s15e, s15o, s15c, accdisp, acctf, maxfail, maxprobe, probeexc,
    reclaim, revdisp, effmin, revtf, postqual,
):
    # Generator state (PROBE/QUALIFIED) is independent from downstream failed-break episodes.
    stage = 0
    oside = 0
    L = 0
    evatr = 0.0
    attempt_start = 0
    qualified_start = 0
    latest_hi = 0
    latest_lo = 0
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
    eatr = np.zeros(MAX_EP, np.float64)
    efstart = np.zeros(MAX_EP, np.int64)
    elastrev = np.full(MAX_EP, -1, np.int64)
    max_active = 0
    overflow = 0

    for i in range(t.size):
        tm = int(t[i])
        px = int(mid2[i])

        while si < st.size and st[si] <= tm:
            if ss[si] > 0:
                latest_hi = int(sl[si])
            else:
                latest_lo = int(sl[si])
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

        # Independent probe generator.
        if stage == 0:
            if latest_hi and px < latest_hi:
                hiel = True
            if latest_lo and px > latest_lo:
                loel = True
            if latest_hi and hiel and px >= latest_hi:
                stage = 1
                oside = 1
                L = latest_hi
                evatr = ae
                attempt_start = tm
                qualified_start = 0
                hiel = False
                cnt[0] += 1
                attempt_open = True
                attempt_qualified = False
            elif latest_lo and loel and px <= latest_lo:
                stage = 1
                oside = -1
                L = latest_lo
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
                    attempt_open = False
                    attempt_qualified = False
                    qualified_start = 0

        accepted_now = False
        if stage == 2 and jacc >= 0 and jacc != lastacc:
            lastacc = jacc
            q = oside * (ac - ao) >= accdisp * evatr and oside * (ac - L) > 0
            if postqual:
                q = q and qualified_start > 0 and acc_end > qualified_start
            if q:
                cnt[2] += 1
                stage = 0
                oside = 0
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
                    overflow += 1
                else:
                    active[slot] = 1
                    estage[slot] = 3
                    eoside[slot] = oside
                    eL[slot] = L
                    eatr[slot] = evatr
                    efstart[slot] = tm
                    elastrev[slot] = -1
                # Release generator immediately; downstream episode persists independently.
                stage = 0
                oside = 0
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0

        # Process all active failed-break episodes independently.
        alive = 0
        jrev = j1 if revtf == 1 else j5
        rc = s1c[j1] if revtf == 1 and j1 >= 0 else (s5c[j5] if j5 >= 0 else 0)
        ro = s1o[j1] if revtf == 1 and j1 >= 0 else (s5o[j5] if j5 >= 0 else 0)
        for e in range(MAX_EP):
            if active[e] == 0:
                continue
            eo = int(eoside[e])
            er = eo * (px - int(eL[e])) < 0
            if estage[e] == 3:
                if er:
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
                        active[e] = 0
                        continue
                elastrev[e] = jrev
            if active[e] != 0:
                alive += 1
        if alive > max_active:
            max_active = alive

    return cnt, max_active, overflow


def evaluate_decoupled(postqual, t, mid, st, ss, sl, b1, b5, b15, b300, a300):
    vectors = {}
    stage_abs = np.zeros(8, np.int64)
    stage_signed = np.zeros(8, np.int64)
    max_active_all = 0
    overflow_all = 0
    for v in VECTORS:
        n, ad, at, mf, mp, pe, rb, rd, em, rt = v
        c, ma, ov = detect_decoupled(
            t, mid, st, ss, sl, b300["end_ms"], a300,
            b1["end_ms"], b1["open"], b1["close"],
            b5["end_ms"], b5["open"], b5["close"],
            b15["end_ms"], b15["open"], b15["close"],
            ad, at, int(mf*1000), int(mp*1000), pe, rb, rd, em, rt, postqual,
        )
        trg = np.asarray(TARGET[n], np.int64)
        er = np.abs(c-trg)
        stage_abs += er
        stage_signed += c-trg
        if ma > max_active_all:
            max_active_all = ma
        overflow_all += ov
        vectors[n] = {
            "target": dict(zip(STAGES, map(int,trg))),
            "actual": dict(zip(STAGES, map(int,c))),
            "signed_error": dict(zip(STAGES, map(int,c-trg))),
            "abs_error": dict(zip(STAGES, map(int,er))),
            "max_concurrent_failure_episodes": int(ma),
            "episode_overflow": int(ov),
        }
    return {
        "vectors": vectors,
        "stage_abs_error": dict(zip(STAGES,map(int,stage_abs))),
        "stage_signed_error": dict(zip(STAGES,map(int,stage_signed))),
        "probe_qualified_abs_error": int(stage_abs[0:2].sum()),
        "first5_abs_error": int(stage_abs[:5].sum()),
        "downstream_abs_error": int(stage_abs[5:].sum()),
        "total_abs_error": int(stage_abs.sum()),
        "max_concurrent_failure_episodes": int(max_active_all),
        "episode_overflow": int(overflow_all),
    }


@njit(cache=True)
def detect_partial_release(
    t, mid2, st, ss, sl, m5e, m5a, s1e, s1o, s1c, s5e, s5o, s5c,
    s15e, s15o, s15c, accdisp, acctf, maxfail, maxprobe, probeexc,
    reclaim, revdisp, effmin, revtf, postqual, release_mode,
):
    # release_mode: 1 = REENTRY, 2 = RECLAIM.
    stage = 0
    blocked = False
    blocking_slot = -1
    oside = 0
    L = 0
    evatr = 0.0
    attempt_start = 0
    qualified_start = 0
    latest_hi = 0
    latest_lo = 0
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
    eatr = np.zeros(MAX_EP, np.float64)
    efstart = np.zeros(MAX_EP, np.int64)
    elastrev = np.full(MAX_EP, -1, np.int64)
    max_active = 0
    overflow = 0
    releases = 0

    for i in range(t.size):
        tm = int(t[i])
        px = int(mid2[i])
        while si < st.size and st[si] <= tm:
            if ss[si] > 0:
                latest_hi = int(sl[si])
            else:
                latest_lo = int(sl[si])
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

        if not blocked:
            if stage == 0:
                if latest_hi and px < latest_hi:
                    hiel = True
                if latest_lo and px > latest_lo:
                    loel = True
                if latest_hi and hiel and px >= latest_hi:
                    stage = 1; oside = 1; L = latest_hi; evatr = ae; attempt_start = tm
                    qualified_start = 0; hiel = False; cnt[0] += 1
                    attempt_open = True; attempt_qualified = False
                elif latest_lo and loel and px <= latest_lo:
                    stage = 1; oside = -1; L = latest_lo; evatr = ae; attempt_start = tm
                    qualified_start = 0; loel = False; cnt[0] += 1
                    attempt_open = True; attempt_qualified = False

            if stage > 0:
                inside = oside * (px - L) < 0
                if inside:
                    attempt_open = False; attempt_qualified = False; qualified_start = 0
                elif not attempt_open:
                    attempt_open = True; attempt_qualified = False; qualified_start = 0
                    cnt[0] += 1; attempt_start = tm
                if attempt_open and (not attempt_qualified) and oside * (px - L) >= probeexc * evatr:
                    attempt_qualified = True; qualified_start = tm; cnt[1] += 1
                if stage == 1:
                    if oside * (px - L) >= probeexc * evatr:
                        stage = 2
                        if qualified_start == 0:
                            qualified_start = tm
                    elif tm - attempt_start > maxprobe:
                        stage = 0; oside = 0; attempt_open = False; attempt_qualified = False; qualified_start = 0

            accepted_now = False
            if stage == 2 and jacc >= 0 and jacc != lastacc:
                lastacc = jacc
                q = oside * (ac - ao) >= accdisp * evatr and oside * (ac - L) > 0
                if postqual:
                    q = q and qualified_start > 0 and acc_end > qualified_start
                if q:
                    cnt[2] += 1
                    stage = 0; oside = 0; attempt_open = False; attempt_qualified = False; qualified_start = 0
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
                        overflow += 1
                    else:
                        active[slot] = 1; estage[slot] = 3; eoside[slot] = oside
                        eL[slot] = L; eatr[slot] = evatr; efstart[slot] = tm; elastrev[slot] = -1
                        blocked = True; blocking_slot = slot
                    stage = 0; oside = 0; attempt_open = False; attempt_qualified = False; qualified_start = 0

        alive = 0
        jrev = j1 if revtf == 1 else j5
        rc = s1c[j1] if revtf == 1 and j1 >= 0 else (s5c[j5] if j5 >= 0 else 0)
        ro = s1o[j1] if revtf == 1 and j1 >= 0 else (s5o[j5] if j5 >= 0 else 0)
        for e in range(MAX_EP):
            if active[e] == 0:
                continue
            eo = int(eoside[e])
            er = eo * (px - int(eL[e])) < 0
            if estage[e] == 3:
                if er:
                    cnt[4] += 1
                    estage[e] = 4
                    if e == blocking_slot and release_mode == 1:
                        blocked = False; blocking_slot = -1; releases += 1
                elif tm - int(efstart[e]) > maxfail:
                    active[e] = 0
                    if e == blocking_slot:
                        blocked = False; blocking_slot = -1; releases += 1
                    continue
            elif tm - int(efstart[e]) > maxfail:
                active[e] = 0
                if e == blocking_slot:
                    blocked = False; blocking_slot = -1; releases += 1
                continue

            if estage[e] >= 4 and jrev >= 0 and jrev != elastrev[e]:
                if estage[e] == 4 and (-eo) * (rc - int(eL[e])) >= reclaim * float(eatr[e]):
                    cnt[5] += 1
                    estage[e] = 5
                    if e == blocking_slot and release_mode == 2:
                        blocked = False; blocking_slot = -1; releases += 1
                if estage[e] >= 5:
                    disp = (-eo) * (rc - ro)
                    eff = 1.0 if abs(rc - ro) > 0 else 0.0
                    if disp >= revdisp * float(eatr[e]) and eff >= effmin:
                        cnt[6] += 1; cnt[7] += 1
                        active[e] = 0
                        if e == blocking_slot:
                            blocked = False; blocking_slot = -1; releases += 1
                        continue
                elastrev[e] = jrev
            if active[e] != 0:
                alive += 1
        if alive > max_active:
            max_active = alive

    return cnt, max_active, overflow, releases


def evaluate_partial(postqual, release_mode, t, mid, st, ss, sl, b1, b5, b15, b300, a300):
    vectors = {}
    stage_abs = np.zeros(8, np.int64)
    stage_signed = np.zeros(8, np.int64)
    max_active_all = 0
    overflow_all = 0
    releases_all = 0
    for v in VECTORS:
        n, ad, at, mf, mp, pe, rb, rd, em, rt = v
        c, ma, ov, rel = detect_partial_release(
            t, mid, st, ss, sl, b300["end_ms"], a300,
            b1["end_ms"], b1["open"], b1["close"],
            b5["end_ms"], b5["open"], b5["close"],
            b15["end_ms"], b15["open"], b15["close"],
            ad, at, int(mf*1000), int(mp*1000), pe, rb, rd, em, rt, postqual, release_mode,
        )
        trg = np.asarray(TARGET[n], np.int64)
        er = np.abs(c-trg)
        stage_abs += er; stage_signed += c-trg
        max_active_all = max(max_active_all, ma); overflow_all += ov; releases_all += rel
        vectors[n] = {
            "target": dict(zip(STAGES,map(int,trg))),
            "actual": dict(zip(STAGES,map(int,c))),
            "signed_error": dict(zip(STAGES,map(int,c-trg))),
            "abs_error": dict(zip(STAGES,map(int,er))),
            "max_concurrent_failure_episodes": int(ma),
            "episode_overflow": int(ov),
            "generator_releases": int(rel),
        }
    return {
        "vectors": vectors,
        "stage_abs_error": dict(zip(STAGES,map(int,stage_abs))),
        "stage_signed_error": dict(zip(STAGES,map(int,stage_signed))),
        "probe_qualified_abs_error": int(stage_abs[0:2].sum()),
        "first5_abs_error": int(stage_abs[:5].sum()),
        "downstream_abs_error": int(stage_abs[5:].sum()),
        "total_abs_error": int(stage_abs.sum()),
        "max_concurrent_failure_episodes": int(max_active_all),
        "episode_overflow": int(overflow_all),
        "generator_releases": int(releases_all),
    }


@njit(cache=True)
def detect_signal_multiplicity(
    t, mid2, st, ss, sl, m5e, m5a, s1e, s1o, s1c, s5e, s5o, s5c,
    s15e, s15o, s15c, accdisp, acctf, maxfail, maxprobe, probeexc,
    reclaim, revdisp, effmin, revtf, mode,
):
    # mode 0: one-shot post-qualification control.
    # mode 1: after first signal, rearm only after reversal condition becomes false.
    # mode 2: after first signal, rearm only after reclaim is lost; fire after reclaim+reversal recover.
    # mode 3: after first signal, rearm only after tick path revisits original-break side,
    #         then returns to failed-break side and reversal condition requalifies.
    stage=0; oside=0; L=0; evatr=0.0; attempt_start=0; qualified_start=0; fstart=0
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True; lastacc=-1; lastrev=-1
    attempt_open=False; attempt_qualified=False; event_id=0; first_signal_seen=False
    signal_armed=True; boundary_rearm_seen=False
    cnt=np.zeros(8,np.int64)
    MAX_SIG=100000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8); sig_event=np.empty(MAX_SIG,np.int64)
    nsig=0; overflow=0

    for i in range(t.size):
        tm=int(t[i]); px=int(mid2[i])
        while si<st.size and st[si]<=tm:
            if ss[si]>0: latest_hi=int(sl[si])
            else: latest_lo=int(sl[si])
            si+=1
        jm=bidx(m5e,tm)
        if jm<13: continue
        ae=float(m5a[jm])
        if ae<=0: continue

        if stage==0:
            if latest_hi and px<latest_hi: hiel=True
            if latest_lo and px>latest_lo: loel=True
            if latest_hi and hiel and px>=latest_hi:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; event_id+=1
                first_signal_seen=False; signal_armed=True; boundary_rearm_seen=False
            elif latest_lo and loel and px<=latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; event_id+=1
                first_signal_seen=False; signal_armed=True; boundary_rearm_seen=False
        if stage==0: continue

        if stage<=2:
            inside=oside*(px-L)<0
            if inside:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                attempt_open=True; attempt_qualified=False; qualified_start=0; cnt[0]+=1; attempt_start=tm
            if attempt_open and (not attempt_qualified) and oside*(px-L)>=probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)
        acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)

        if stage==1:
            if oside*(px-L)>=probeexc*evatr:
                stage=2
                if qualified_start==0: qualified_start=tm
            elif tm-attempt_start>maxprobe:
                stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                continue
        if stage<2: continue

        if stage==2 and jacc>=0 and jacc!=lastacc:
            lastacc=jacc
            q=oside*(ac-ao)>=accdisp*evatr and oside*(ac-L)>0
            q=q and qualified_start>0 and acc_end>qualified_start
            if q:
                cnt[2]+=1; stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                continue

        recross=oside*(px-L)<0
        if stage==2 and (tm-attempt_start>=maxprobe or recross):
            stage=3; cnt[3]+=1; fstart=tm; attempt_open=False; attempt_qualified=False; qualified_start=0
        if stage==3:
            if recross:
                cnt[4]+=1; stage=4
            elif tm-fstart>maxfail:
                stage=0; oside=0; continue
        elif stage>=4 and tm-fstart>maxfail:
            stage=0; oside=0; continue
        if stage<4: continue

        # Boundary-recycle rearm is tick-causal and independent of completed-bar checks.
        if mode==3 and first_signal_seen:
            if oside*(px-L)>=0:
                boundary_rearm_seen=True
            elif boundary_rearm_seen:
                signal_armed=True

        jrev=j1 if revtf==1 else j5
        if jrev<0 or jrev==lastrev: continue
        rc=s1c[j1] if revtf==1 else s5c[j5]
        ro=s1o[j1] if revtf==1 else s5o[j5]
        reclaim_ok=(-oside)*(rc-L)>=reclaim*evatr

        if stage==4:
            if reclaim_ok:
                cnt[5]+=1; stage=5
            else:
                lastrev=jrev; continue

        disp=(-oside)*(rc-ro)
        eff=1.0 if abs(rc-ro)>0 else 0.0
        reversal_ok=disp>=revdisp*evatr and eff>=effmin

        if first_signal_seen:
            if mode==1 and not reversal_ok:
                signal_armed=True
            elif mode==2 and not reclaim_ok:
                signal_armed=True
                stage=4
            elif mode==3 and not reclaim_ok:
                stage=4

        if stage>=5 and reclaim_ok and reversal_ok and signal_armed:
            if nsig<MAX_SIG:
                sig_i[nsig]=i; sig_side[nsig]=-oside; sig_event[nsig]=event_id; nsig+=1
            else:
                overflow+=1
            if not first_signal_seen:
                cnt[6]+=1; cnt[7]+=1; first_signal_seen=True
            if mode==0:
                stage=0; oside=0
            else:
                signal_armed=False
                boundary_rearm_seen=False
        lastrev=jrev

    return cnt, sig_i[:nsig], sig_side[:nsig], sig_event[:nsig], overflow


@njit(cache=True)
def admit_r9_lifecycle(t, ask, bid, sig_i, sig_side):
    STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30000
    n=sig_i.size
    admitted=0; rejected=0; wins=0; gross_pos=0.0; gross_neg=0.0; net=0.0
    balance=0.0; peak=0.0; maxdd=0.0
    pos=0; entry=0; stop=0; entry_tm=0; entry_idx=-1; k=0
    last_i=t.size-1
    for i in range(t.size):
        exited=False
        if pos!=0:
            ex=0; do_exit=False
            if pos>0:
                if int(bid[i])<=stop:
                    ex=int(bid[i]); do_exit=True
            else:
                if int(ask[i])>=stop:
                    ex=int(ask[i]); do_exit=True
            if (not do_exit) and int(t[i])-entry_tm>=MAX_HOLD:
                ex=int(bid[i]) if pos>0 else int(ask[i]); do_exit=True
            if do_exit:
                pnl=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)-0.02
                net+=pnl; balance+=pnl
                if pnl>0: wins+=1; gross_pos+=pnl
                else: gross_neg+=pnl
                if balance>peak: peak=balance
                dd=peak-balance
                if dd>maxdd: maxdd=dd
                pos=0; exited=True
            else:
                if pos>0 and int(bid[i])-entry>=TRAIL_ACT:
                    ns=int(bid[i])-TRAIL_DIST
                    if ns>stop: stop=ns
                elif pos<0 and entry-int(ask[i])>=TRAIL_ACT:
                    ns=int(ask[i])+TRAIL_DIST
                    if ns<stop: stop=ns

        while k<n and int(sig_i[k])==i:
            if pos==0 and not exited:
                pos=int(sig_side[k]); entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=entry-STOP if pos>0 else entry+STOP
                entry_tm=int(t[i]); entry_idx=i; admitted+=1
            else:
                rejected+=1
            k+=1

    if pos!=0:
        ex=int(bid[last_i]) if pos>0 else int(ask[last_i])
        pnl=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)-0.02
        net+=pnl; balance+=pnl
        if pnl>0: wins+=1; gross_pos+=pnl
        else: gross_neg+=pnl
        if balance>peak: peak=balance
        dd=peak-balance
        if dd>maxdd: maxdd=dd
    return admitted,rejected,wins,gross_pos,gross_neg,net,maxdd


def evaluate_signal_mode(mode, t, ask, bid, mid, st, ss, sl, b1, b5, b15, b300, a300):
    vectors={}; trade_abs=0; signal_s06_abs=0
    hist_trades={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c,si,ssig,se,ov=detect_signal_multiplicity(
            t,mid,st,ss,sl,b300["end_ms"],a300,
            b1["end_ms"],b1["open"],b1["close"],
            b5["end_ms"],b5["open"],b5["close"],
            b15["end_ms"],b15["open"],b15["close"],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,mode,
        )
        adm,rej,w,gp,gl,net,dd=admit_r9_lifecycle(t,ask,bid,si,ssig)
        h=hist_trades[n]; trade_abs+=abs(int(adm)-h)
        if n=="S06": signal_s06_abs=abs(int(si.size)-672)
        # episode multiplicity diagnostics
        unique_events=int(np.unique(se).size) if se.size else 0
        repeated=int(si.size-unique_events)
        vectors[n]={
            "funnel":dict(zip(STAGES,map(int,c))),
            "generator_signals":int(si.size),
            "unique_signal_episodes":unique_events,
            "repeated_signals":repeated,
            "signal_overflow":int(ov),
            "historical_trades":h,
            "admitted_trades":int(adm),
            "rejected_while_occupied":int(rej),
            "wins":int(w),"gross_profit_usd":float(gp),"gross_loss_usd":float(gl),
            "net_usd":float(net),"max_balance_dd_usd":float(dd),
        }
    s6=vectors["S06"]
    s6_econ_error=abs(s6["wins"]-307)+abs(s6["net_usd"]-(-101.08))
    return {
        "vectors":vectors,
        "aggregate_trade_count_abs_error":int(trade_abs),
        "s06_generator_signal_abs_error":int(signal_s06_abs),
        "s06_trade_abs_error":abs(s6["admitted_trades"]-615),
        "s06_win_abs_error":abs(s6["wins"]-307),
        "s06_net_abs_error":float(abs(s6["net_usd"]+101.08)),
        "s06_econ_composite_error":float(s6_econ_error),
    }

def evaluate_profile(profile_index, t, mid, st, ss, sl, b1, b5, b15, b300, a300):
    vectors = {}
    stage_abs = np.zeros(8, np.int64)
    signed_stage = np.zeros(8, np.int64)

    for v in VECTORS:
        n, ad, at, mf, mp, pe, rb, rd, em, rt = v
        c = detect(
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
            profile_index,
        )
        trg = np.asarray(TARGET[n], np.int64)
        er = np.abs(c - trg)
        stage_abs += er
        signed_stage += c - trg
        vectors[n] = {
            "target": dict(zip(STAGES, map(int, trg))),
            "actual": dict(zip(STAGES, map(int, c))),
            "signed_error": dict(zip(STAGES, map(int, c - trg))),
            "abs_error": dict(zip(STAGES, map(int, er))),
        }

    return {
        "vectors": vectors,
        "stage_abs_error": dict(zip(STAGES, map(int, stage_abs))),
        "stage_signed_error": dict(zip(STAGES, map(int, signed_stage))),
        "probe_qualified_abs_error": int(stage_abs[0:2].sum()),
        "first5_abs_error": int(stage_abs[:5].sum()),
        "downstream_abs_error": int(stage_abs[5:].sum()),
        "total_abs_error": int(stage_abs.sum()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

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

    ask, bid = p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    mid = ask + bid

    b1 = bars(t, mid, 1000)
    b5 = bars(t, mid, 5000)
    b15 = bars(t, mid, 15000)
    b300 = bars(t, mid, 300000)
    a300 = atr14(b300)
    st, ss, sl = symmetric_swings(b300, 2)

    results = {}
    for pi, pname in enumerate(PROFILES):
        results[pname] = evaluate_profile(pi, t, mid, st, ss, sl, b1, b5, b15, b300, a300)
    signal_modes={
        "ONE_SHOT_POST_QUAL":0,
        "REVERSAL_CONDITION_TOGGLE_REARM":1,
        "RECLAIM_LOSS_REGAIN_REARM":2,
        "BOUNDARY_RECYCLE_REARM":3,
    }
    signal_results={}
    for name,mode in signal_modes.items():
        signal_results[name]=evaluate_signal_mode(mode,t,ask,bid,mid,st,ss,sl,b1,b5,b15,b300,a300)

    control = results["CONTROL_09E"]
    expected_control = {
        "probe": 525,
        "qualified": 29,
        "accepted": 157,
        "failure": 170,
        "reentry": 39,
        "reclaim": 38,
        "reversal": 53,
        "signal": 53,
    }
    control_parity = control["stage_abs_error"] == expected_control
    if not control_parity:
        raise SystemExit(
            "CONTROL_09E does not reproduce checkpoint 09E stage errors: "
            + json.dumps(control["stage_abs_error"], sort_keys=True)
        )

    ranking=[]
    for pname,r in signal_results.items():
        ranking.append({
            "profile":pname,
            "aggregate_trade_count_abs_error":r["aggregate_trade_count_abs_error"],
            "s06_generator_signal_abs_error":r["s06_generator_signal_abs_error"],
            "s06_trade_abs_error":r["s06_trade_abs_error"],
            "s06_win_abs_error":r["s06_win_abs_error"],
            "s06_net_abs_error":r["s06_net_abs_error"],
        })
    ranking.sort(key=lambda x:(x["aggregate_trade_count_abs_error"],x["s06_generator_signal_abs_error"],x["s06_trade_abs_error"],x["s06_win_abs_error"],x["s06_net_abs_error"]))

    out = {
        "schema": "delta-r037-dh05-signal-multiplicity-executable-admission-parity-v1",
        "status": "BOUNDED_QA_COMPLETE",
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "august_accessed": False,
        "numeric_vector_retune": False,
        "boundary": "symmetric two-bar confirmed M5 swing",
        "probe_semantics": "09E repeated causal same-boundary attempt ledger with per-attempt lifecycle clock",
        "acceptance_semantics": "09F post-qualification chronology for signal-layer candidates; funnel CONTROL_09E retained as source QA",
        "failure_clock": "failure-candidate start retained for max_failure_age in every profile",
        "profiles": results,\n        "signal_profiles": signal_results,
        "control_09e_reproduced_exact_stage_errors": control_parity,
        "ranking": ranking,
        "finding": {
            "selection_rule": "candidate may carry forward only if transition-based multiplicity reduces aggregate historical admitted-trade count error and materially approaches S06 672 generator / 615 admitted / 307 wins / -101.08 net without signal overflow",
            "leading_profile": ranking[0]["profile"] if ranking else None,
            "parity_complete": False,
            "next": "freeze any reconstructible multiplicity/admission rule that materially approaches the authoritative ledger; otherwise isolate the remaining admission/lifecycle mismatch",
        },
    }

    atomic_write_json(args.output, out)
    print(
        json.dumps(
            {
                "control_probe_qualified_abs_error": control["probe_qualified_abs_error"],
                "control_total_abs_error": control["total_abs_error"],
                "ranking": ranking,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
