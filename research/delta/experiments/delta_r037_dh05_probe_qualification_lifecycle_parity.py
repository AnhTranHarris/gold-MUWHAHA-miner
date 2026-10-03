"""DELTA R037 DH05 probe-qualification clock / event-lifecycle parity diagnostic.

Checkpoint 09E candidate producer. Research-only bounded semantic diagnostic.

Frozen from 09C + 09D:
- symmetric two-bar confirmed M5 swing boundary;
- repeated causal same-boundary pre-failure probe-attempt ledger;
- BREAK_ACCEPTED only while event remains a qualified probe;
- acceptance_disp_atr = signed completed acceptance-bar body displacement / event M5 ATR;
- completed acceptance close remains beyond original boundary;
- failure-age clock starts at FAILURE_CANDIDATE;
- no frozen numeric-vector retuning.

This unit changes only the clock origin used by the pre-failure probe lifecycle.
It keeps a byte-equivalent CONTROL_09D profile and tests three deterministic,
non-numeric semantic alternatives. Outputs are written atomically.
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

# Profile semantics:
# 0 CONTROL_09D:
#   original event-start clock controls stage-1 and stage-2 max_probe_age.
# 1 ATTEMPT_STAGE1_CLOCK:
#   each causal same-boundary re-attempt gets a fresh qualification clock in stage-1;
#   once qualified, stage-2 still uses original event-start max_probe_age.
# 2 ATTEMPT_LIFECYCLE_CLOCK:
#   each causal same-boundary re-attempt gets a fresh clock and stage-2 max_probe_age
#   remains anchored to that currently qualified attempt.
# 3 QUALIFIED_LIFECYCLE_CLOCK:
#   stage-1 uses the causal attempt clock; after qualification, stage-2 max_probe_age
#   starts at the causal qualification instant. max_failure_age still starts only at
#   FAILURE_CANDIDATE exactly as frozen in 09D.
PROFILES = (
    "CONTROL_09D",
    "ATTEMPT_STAGE1_CLOCK",
    "ATTEMPT_LIFECYCLE_CLOCK",
    "QUALIFIED_LIFECYCLE_CLOCK",
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
                if profile >= 1:
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
                stage1_clock = event_start if profile == 0 else attempt_start
                if tm - stage1_clock > maxprobe:
                    stage = 0
                    oside = 0
                    attempt_open = False
                    attempt_qualified = False
                    qualified_start = 0
                    continue

        if stage < 2:
            continue

        if jacc >= 0 and jacc != lastacc:
            lastacc = jacc
            q = oside * (ac - ao) >= accdisp * evatr and oside * (ac - L) > 0
            if q:
                cnt[2] += 1
                stage = 0
                oside = 0
                attempt_open = False
                attempt_qualified = False
                qualified_start = 0
                continue

        recross = oside * (px - L) < 0

        if profile == 0:
            stage2_clock = event_start
        elif profile == 1:
            stage2_clock = event_start
        elif profile == 2:
            stage2_clock = attempt_start
        else:
            stage2_clock = qualified_start if qualified_start > 0 else attempt_start

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

    control = results["CONTROL_09D"]
    expected_control = {
        "probe": 782,
        "qualified": 343,
        "accepted": 70,
        "failure": 395,
        "reentry": 159,
        "reclaim": 75,
        "reversal": 65,
        "signal": 65,
    }
    control_parity = control["stage_abs_error"] == expected_control
    if not control_parity:
        raise SystemExit(
            "CONTROL_09D does not reproduce checkpoint 09D stage errors: "
            + json.dumps(control["stage_abs_error"], sort_keys=True)
        )

    ranking = []
    for pname in PROFILES[1:]:
        r = results[pname]
        ranking.append(
            {
                "profile": pname,
                "probe_qualified_abs_error": r["probe_qualified_abs_error"],
                "first5_abs_error": r["first5_abs_error"],
                "downstream_abs_error": r["downstream_abs_error"],
                "total_abs_error": r["total_abs_error"],
                "probe_qualified_improvement_vs_09d": control["probe_qualified_abs_error"] - r["probe_qualified_abs_error"],
                "total_improvement_vs_09d": control["total_abs_error"] - r["total_abs_error"],
            }
        )
    ranking.sort(
        key=lambda x: (
            -x["probe_qualified_improvement_vs_09d"],
            -x["total_improvement_vs_09d"],
            x["downstream_abs_error"],
        )
    )

    out = {
        "schema": "delta-r037-dh05-probe-qualification-lifecycle-parity-v1",
        "status": "BOUNDED_QA_COMPLETE",
        "source_sha256": source_sha,
        "stage_a_ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "august_accessed": False,
        "numeric_vector_retune": False,
        "boundary": "symmetric two-bar confirmed M5 swing",
        "probe_semantics": "repeated causal same-boundary pre-failure attempt ledger",
        "acceptance_semantics": "09D stage-gated signed completed acceptance-bar body displacement / event M5 ATR with close beyond boundary",
        "failure_clock": "failure-candidate start retained for max_failure_age in every profile",
        "profiles": results,
        "control_09d_reproduced_exact_stage_errors": control_parity,
        "ranking": ranking,
        "finding": {
            "selection_rule": "semantic candidate may carry forward only if probe+qualified aggregate error materially falls and total/downstream error does not show a compensating large deterioration",
            "leading_profile": ranking[0]["profile"] if ranking else None,
            "parity_complete": False,
            "next": "human/scientific review of this bounded semantic result before any downstream reclaim/reversal repair or SORB integration",
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
