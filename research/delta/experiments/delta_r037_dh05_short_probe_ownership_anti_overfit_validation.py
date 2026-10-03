"""DELTA R037 DH05 short-probe ownership anti-overfit validation — Checkpoint 10A.

Independent late-January holdout validation of the non-promoting 09Z challenger.

Frozen before compute:
- Router: max_probe_age_s < acceptance_tf_seconds -> decouple the upstream generator
  at FAILURE_CANDIDATE; otherwise retain SERIAL_POST_QUAL ownership.
- Frozen DH05 vectors and 09C/09D/09E/09F chronology.
- Validation window: [2026-01-18T12:00:00Z, final January tick].
- Warmup: [2026-01-14T00:00:00Z, holdout boundary), indicator/boundary state only;
  strategy/event state begins cold at the holdout boundary.
- Surfaces: frozen Coinexx-like P50/P75/P90.
- No numeric retuning, no same-holdout recuts, August sealed.

Anti-overfit gate is deliberately threshold-free:
- For every P50/P75/P90 holdout surface, the routed candidate's aggregate net over the
  six frozen vectors must be >= serial control aggregate net.
- This gate is robustness evidence only; it does not itself prove historical DH05
  parity or authorize promotion/MQL5/SORB.

Crash safety:
- canonical source SHA gate;
- monotonic-tick gate;
- fresh external Numba cache expected by the launcher;
- Python faulthandler watchdog;
- bounded episode/signal buffers with overflow hard-fail;
- atomic result write.
"""
from __future__ import annotations

import argparse
import faulthandler
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
WARMUP_START_MS = 1_768_348_800_000  # 2026-01-14T00:00:00Z
HOLDOUT_START_MS = 1_768_737_600_000  # 2026-01-18T12:00:00Z
US_DST_START_2026_MS = 1_772_953_200_000
UK_DST_START_2026_MS = 1_774_746_000_000
CANONICAL_JAN_SHA256 = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"

SURFACES = {
    "P50": np.asarray([19, 19, 19, 19], dtype=np.int64),
    "P75": np.asarray([20, 20, 21, 21], dtype=np.int64),
    "P90": np.asarray([35, 34, 23, 37], dtype=np.int64),
}

VECTORS = (
    ("A03", .3, 15, 40, 20, .15, .08, .12, .5, 5),
    ("S05", .374062, 15, 9.099416, 6.468982, .244588, .093793, .217011, .062661, 5),
    ("S06", .217738, 5, 59.699117, 23.47226, .029179, .145085, .041213, .673017, 1),
    ("S09", .329294, 15, 41.910749, 10.844137, .335024, .12735, .272984, .126644, 1),
    ("S10", .26416, 5, 20.537168, 19.210606, .108825, .077129, .088265, .644213, 5),
    ("S16", .18608, 5, 31.219954, 3.711492, .279091, .121753, .206212, .746067, 5),
)

SELECTED = ("S05", "S09", "S16")
STAGES = ("probe", "qualified", "accepted", "failure", "reentry", "reclaim", "reversal", "signal")


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
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
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


def surface_quotes(t, a, b, spread_points):
    s = session_code(t)
    sp = spread_points[s] * TICK_RAW
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
            rev.append(reveal); side.append(1); lev.append(int(h))
        if isl:
            rev.append(reveal); side.append(-1); lev.append(int(l))
    arr = np.asarray(rev, np.int64)
    order = np.argsort(arr, kind="stable")
    return arr[order], np.asarray(side, np.int8)[order], np.asarray(lev, np.int64)[order]


@njit(cache=True)
def bidx(end, tm):
    return np.searchsorted(end, tm, side="right") - 1


@njit(cache=True)
def admit_r9_lifecycle(t, ask, bid, sig_i, sig_side):
    STOP = 300
    TRAIL_ACT = 100
    TRAIL_DIST = 30
    n = sig_i.size
    admitted = rejected_occupied = rejected_latch = wins = 0
    gp = gl = 0.0
    balance = 100000.0
    peak = balance
    maxdd = 0.0
    pos = entry = stop = entrysec = k = 0
    hold_sum = 0.0
    closed_trades = 0
    last_i = t.size - 1
    for i in range(t.size):
        sec = int(t[i]) // 1000
        exited = False
        if pos != 0:
            ex = 0
            do_exit = False
            if pos > 0:
                if int(bid[i]) <= stop:
                    ex = int(bid[i]); do_exit = True
            else:
                if int(ask[i]) >= stop:
                    ex = int(ask[i]); do_exit = True
            if (not do_exit) and sec - entrysec >= 30:
                ex = int(bid[i]) if pos > 0 else int(ask[i]); do_exit = True
            if do_exit:
                raw = ((ex - entry) / 1000.0 if pos > 0 else (entry - ex) / 1000.0)
                exit_deal = raw - 0.01
                if exit_deal > 1e-12:
                    wins += 1
                if raw > 0:
                    gp += exit_deal
                else:
                    gl += exit_deal
                balance += exit_deal
                closed_trades += 1
                hold_sum += sec - entrysec
                if balance > peak:
                    peak = balance
                dd = peak - balance
                if dd > maxdd:
                    maxdd = dd
                pos = entry = stop = 0
                exited = True
            else:
                if pos > 0 and int(bid[i]) - entry >= TRAIL_ACT:
                    ns = int(bid[i]) - TRAIL_DIST
                    if ns > stop:
                        stop = ns
                elif pos < 0 and entry - int(ask[i]) >= TRAIL_ACT:
                    ns = int(ask[i]) + TRAIL_DIST
                    if ns < stop:
                        stop = ns
        while k < n and int(sig_i[k]) == i:
            if pos != 0:
                rejected_occupied += 1
            elif exited:
                rejected_latch += 1
            else:
                pos = int(sig_side[k])
                entry = int(ask[i]) if pos > 0 else int(bid[i])
                stop = int(bid[i]) - STOP if pos > 0 else int(ask[i]) + STOP
                entrysec = sec
                admitted += 1
                balance -= 0.01
                gl -= 0.01
                dd = peak - balance
                if dd > maxdd:
                    maxdd = dd
            k += 1
    if pos != 0:
        ex = int(bid[last_i]) if pos > 0 else int(ask[last_i])
        raw = ((ex - entry) / 1000.0 if pos > 0 else (entry - ex) / 1000.0)
        exit_deal = raw - 0.01
        if exit_deal > 1e-12:
            wins += 1
        if raw > 0:
            gp += exit_deal
        else:
            gl += exit_deal
        balance += exit_deal
        closed_trades += 1
        hold_sum += (int(t[last_i]) // 1000) - entrysec
        if balance > peak:
            peak = balance
        dd = peak - balance
        if dd > maxdd:
            maxdd = dd
    return admitted, rejected_occupied, rejected_latch, closed_trades, wins, gp, gl, gp + gl, maxdd, (hold_sum / closed_trades if closed_trades else 0.0)


@njit(cache=True)
def detect_serial_holdout(
    t, mid2, st, ss, sl, m5e, m5a,
    s1e, s1o, s1c, s5e, s5o, s5c, s15e, s15o, s15c,
    accdisp, acctf, maxfail, maxprobe, probeexc, reclaim, revdisp, effmin, revtf, score_start,
):
    stage = 0; oside = 0; L = 0; evatr = 0.0; attempt_start = 0; qualified_start = 0; fstart = 0
    latest_hi = 0; latest_lo = 0; si = 0; hiel = True; loel = True
    lastacc = -1; lastrev = -1; attempt_open = False; attempt_qualified = False; reent = False
    cnt = np.zeros(8, np.int64)
    MAX_SIG = 30000
    sig_i = np.empty(MAX_SIG, np.int64); sig_side = np.empty(MAX_SIG, np.int8); nsig = 0; overflow = 0
    for i in range(t.size):
        tm = int(t[i]); px = int(mid2[i])
        while si < st.size and st[si] <= tm:
            if ss[si] > 0:
                latest_hi = int(sl[si])
            else:
                latest_lo = int(sl[si])
            si += 1
        if tm < score_start:
            continue
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
                stage = 1; oside = 1; L = latest_hi; evatr = ae; attempt_start = tm; qualified_start = 0
                hiel = False; cnt[0] += 1; attempt_open = True; attempt_qualified = False; reent = False; fstart = 0
            elif latest_lo and loel and px <= latest_lo:
                stage = 1; oside = -1; L = latest_lo; evatr = ae; attempt_start = tm; qualified_start = 0
                loel = False; cnt[0] += 1; attempt_open = True; attempt_qualified = False; reent = False; fstart = 0
        if stage == 0:
            continue
        if stage <= 2:
            inside = oside * (px - L) < 0
            if inside:
                attempt_open = False; attempt_qualified = False; qualified_start = 0
            elif not attempt_open:
                attempt_open = True; attempt_qualified = False; qualified_start = 0; attempt_start = tm; cnt[0] += 1
            if attempt_open and (not attempt_qualified) and oside * (px - L) >= probeexc * evatr:
                attempt_qualified = True; qualified_start = tm; cnt[1] += 1
        j1 = bidx(s1e, tm); j5 = bidx(s5e, tm); j15 = bidx(s15e, tm)
        jacc = j5 if acctf == 5 else j15
        ac = s5c[j5] if acctf == 5 and j5 >= 0 else (s15c[j15] if j15 >= 0 else 0)
        ao = s5o[j5] if acctf == 5 and j5 >= 0 else (s15o[j15] if j15 >= 0 else 0)
        acc_end = s5e[j5] if acctf == 5 and j5 >= 0 else (s15e[j15] if j15 >= 0 else 0)
        if stage == 1:
            if oside * (px - L) >= probeexc * evatr:
                stage = 2
                if qualified_start == 0:
                    qualified_start = tm
            elif tm - attempt_start > maxprobe:
                stage = 0; oside = 0; attempt_open = False; attempt_qualified = False; qualified_start = 0
                continue
        if stage < 2:
            continue
        if stage == 2 and jacc >= 0 and jacc != lastacc:
            lastacc = jacc
            q = (qualified_start > 0 and acc_end > qualified_start and
                 oside * (ac - ao) >= accdisp * evatr and oside * (ac - L) > 0)
            if q:
                cnt[2] += 1; stage = 0; oside = 0; attempt_open = False; attempt_qualified = False
                qualified_start = 0; fstart = 0; reent = False
                continue
        recross = oside * (px - L) < 0
        if stage == 2:
            if tm - attempt_start >= maxprobe or recross:
                stage = 3; cnt[3] += 1; attempt_open = False; attempt_qualified = False; qualified_start = 0; fstart = tm
        if stage == 3:
            if recross and not reent:
                reent = True; cnt[4] += 1; stage = 4
            elif fstart and tm - fstart > maxfail:
                stage = 0; oside = 0; reent = False; fstart = 0
                continue
        elif stage >= 4 and fstart and tm - fstart > maxfail:
            stage = 0; oside = 0; reent = False; fstart = 0
            continue
        if stage < 4:
            continue
        jrev = j1 if revtf == 1 else j5
        rc = s1c[j1] if revtf == 1 and j1 >= 0 else (s5c[j5] if j5 >= 0 else 0)
        if stage == 4 and jrev >= 0 and jrev != lastrev:
            if (-oside) * (rc - L) >= reclaim * evatr:
                cnt[5] += 1; stage = 5
        if stage < 5 or jrev < 0 or jrev == lastrev:
            continue
        ro = s1o[j1] if revtf == 1 else s5o[j5]
        rside = -oside
        disp = rside * (rc - ro)
        eff = 1.0 if abs(rc - ro) > 0 else 0.0
        if disp >= revdisp * evatr and eff >= effmin:
            cnt[6] += 1; cnt[7] += 1
            if nsig < MAX_SIG:
                sig_i[nsig] = i; sig_side[nsig] = rside; nsig += 1
            else:
                overflow += 1
            stage = 0; oside = 0; reent = False; fstart = 0
        lastrev = jrev
    return cnt, sig_i[:nsig], sig_side[:nsig], overflow


@njit(cache=True)
def detect_decoupled_holdout(
    t, mid2, st, ss, sl, m5e, m5a,
    s1e, s1o, s1c, s5e, s5o, s5c, s15e, s15o, s15c,
    accdisp, acctf, maxfail, maxprobe, probeexc, reclaim, revdisp, effmin, revtf, score_start,
):
    stage = 0; oside = 0; L = 0; evatr = 0.0; attempt_start = 0; qualified_start = 0
    latest_hi = 0; latest_lo = 0; si = 0; hiel = True; loel = True
    lastacc = -1; attempt_open = False; attempt_qualified = False
    cnt = np.zeros(8, np.int64)
    MAX_EP = 64
    active = np.zeros(MAX_EP, np.int8); estage = np.zeros(MAX_EP, np.int8); eoside = np.zeros(MAX_EP, np.int8)
    eL = np.zeros(MAX_EP, np.int64); eatr = np.zeros(MAX_EP, np.float64); efstart = np.zeros(MAX_EP, np.int64)
    elastrev = np.full(MAX_EP, -1, np.int64)
    max_active = 0; ep_overflow = 0
    MAX_SIG = 30000
    sig_i = np.empty(MAX_SIG, np.int64); sig_side = np.empty(MAX_SIG, np.int8); nsig = 0; sig_overflow = 0
    for i in range(t.size):
        tm = int(t[i]); px = int(mid2[i])
        while si < st.size and st[si] <= tm:
            if ss[si] > 0:
                latest_hi = int(sl[si])
            else:
                latest_lo = int(sl[si])
            si += 1
        if tm < score_start:
            continue
        jm = bidx(m5e, tm)
        if jm < 13:
            continue
        ae = float(m5a[jm])
        if ae <= 0:
            continue
        j1 = bidx(s1e, tm); j5 = bidx(s5e, tm); j15 = bidx(s15e, tm)
        jacc = j5 if acctf == 5 else j15
        ac = s5c[j5] if acctf == 5 and j5 >= 0 else (s15c[j15] if j15 >= 0 else 0)
        ao = s5o[j5] if acctf == 5 and j5 >= 0 else (s15o[j15] if j15 >= 0 else 0)
        acc_end = s5e[j5] if acctf == 5 and j5 >= 0 else (s15e[j15] if j15 >= 0 else 0)
        if stage == 0:
            if latest_hi and px < latest_hi:
                hiel = True
            if latest_lo and px > latest_lo:
                loel = True
            if latest_hi and hiel and px >= latest_hi:
                stage = 1; oside = 1; L = latest_hi; evatr = ae; attempt_start = tm; qualified_start = 0
                hiel = False; cnt[0] += 1; attempt_open = True; attempt_qualified = False
            elif latest_lo and loel and px <= latest_lo:
                stage = 1; oside = -1; L = latest_lo; evatr = ae; attempt_start = tm; qualified_start = 0
                loel = False; cnt[0] += 1; attempt_open = True; attempt_qualified = False
        if stage > 0:
            inside = oside * (px - L) < 0
            if inside:
                attempt_open = False; attempt_qualified = False; qualified_start = 0
            elif not attempt_open:
                attempt_open = True; attempt_qualified = False; qualified_start = 0; attempt_start = tm; cnt[0] += 1
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
            q = (qualified_start > 0 and acc_end > qualified_start and
                 oside * (ac - ao) >= accdisp * evatr and oside * (ac - L) > 0)
            if q:
                cnt[2] += 1; stage = 0; oside = 0; attempt_open = False; attempt_qualified = False
                qualified_start = 0; accepted_now = True
        if (not accepted_now) and stage == 2:
            recross = oside * (px - L) < 0
            if tm - attempt_start >= maxprobe or recross:
                cnt[3] += 1
                slot = -1
                for qslot in range(MAX_EP):
                    if active[qslot] == 0:
                        slot = qslot; break
                if slot < 0:
                    ep_overflow += 1
                else:
                    active[slot] = 1; estage[slot] = 3; eoside[slot] = oside; eL[slot] = L
                    eatr[slot] = evatr; efstart[slot] = tm; elastrev[slot] = -1
                stage = 0; oside = 0; attempt_open = False; attempt_qualified = False; qualified_start = 0
        alive = 0
        jrev = j1 if revtf == 1 else j5
        rc = s1c[j1] if revtf == 1 and j1 >= 0 else (s5c[j5] if j5 >= 0 else 0)
        ro = s1o[j1] if revtf == 1 and j1 >= 0 else (s5o[j5] if j5 >= 0 else 0)
        for e in range(MAX_EP):
            if active[e] == 0:
                continue
            eo = int(eoside[e]); er = eo * (px - int(eL[e])) < 0
            if estage[e] == 3:
                if er:
                    cnt[4] += 1; estage[e] = 4
                elif tm - int(efstart[e]) > maxfail:
                    active[e] = 0; continue
            elif tm - int(efstart[e]) > maxfail:
                active[e] = 0; continue
            if estage[e] >= 4 and jrev >= 0 and jrev != elastrev[e]:
                if estage[e] == 4 and (-eo) * (rc - int(eL[e])) >= reclaim * float(eatr[e]):
                    cnt[5] += 1; estage[e] = 5
                if estage[e] >= 5:
                    disp = (-eo) * (rc - ro)
                    eff = 1.0 if abs(rc - ro) > 0 else 0.0
                    if disp >= revdisp * float(eatr[e]) and eff >= effmin:
                        cnt[6] += 1; cnt[7] += 1
                        if nsig < MAX_SIG:
                            sig_i[nsig] = i; sig_side[nsig] = -eo; nsig += 1
                        else:
                            sig_overflow += 1
                        active[e] = 0; continue
                elastrev[e] = jrev
            if active[e] != 0:
                alive += 1
        if alive > max_active:
            max_active = alive
    return cnt, sig_i[:nsig], sig_side[:nsig], max_active, ep_overflow, sig_overflow


def metrics_tuple(x):
    return {
        "admitted": int(x[0]), "rejected_occupied": int(x[1]), "rejected_latch": int(x[2]),
        "trades": int(x[3]), "wins": int(x[4]), "gross_profit_usd": float(x[5]),
        "gross_loss_usd": float(x[6]), "net_usd": float(x[7]), "max_drawdown_usd": float(x[8]),
        "average_hold_seconds": float(x[9]),
    }


def main():
    faulthandler.enable(all_threads=True)
    faulthandler.dump_traceback_later(90, repeat=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    sha = sha256_file(args.source)
    if sha != CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: " + sha)
    df = pd.read_csv(args.source, compression="gzip", usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"], dtype=np.int64)
    df = df[df.timestamp_ms_utc >= WARMUP_START_MS]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size == 0 or int(t[-1]) < HOLDOUT_START_MS:
        raise SystemExit("January holdout missing")
    if np.any(t[1:] < t[:-1]):
        raise SystemExit("non-monotonic January ticks")
    raw_ask = df.ask_raw.to_numpy(np.int64)
    raw_bid = df.bid_raw.to_numpy(np.int64)
    results = {}
    all_surface_pass = True
    for surface, points in SURFACES.items():
        ask, bid = surface_quotes(t, raw_ask, raw_bid, points)
        mid = ask + bid
        b1 = bars(t, mid, 1000); b5 = bars(t, mid, 5000); b15 = bars(t, mid, 15000); b300 = bars(t, mid, 300000)
        a300 = atr14(b300)
        st, ss, sl = symmetric_swings(b300, 2)
        control_vectors = {}; candidate_vectors = {}
        control_net = candidate_net = 0.0
        control_trades = candidate_trades = 0
        control_wins = candidate_wins = 0
        control_dd_sum = candidate_dd_sum = 0.0
        selected_control_net = selected_candidate_net = 0.0
        max_active = ep_over = sig_over = 0
        for v in VECTORS:
            n, ad, at, mf, mp, pe, rb, rd, em, rt = v
            cc, csi, cssig, cov = detect_serial_holdout(
                t, mid, st, ss, sl, b300["end_ms"], a300,
                b1["end_ms"], b1["open"], b1["close"],
                b5["end_ms"], b5["open"], b5["close"],
                b15["end_ms"], b15["open"], b15["close"],
                ad, at, int(mf * 1000), int(mp * 1000), pe, rb, rd, em, rt, HOLDOUT_START_MS,
            )
            if cov:
                raise SystemExit(f"control signal overflow {surface} {n}")
            cm = admit_r9_lifecycle(t, ask, bid, csi, cssig)
            if mp < at:
                rc, rsi, rssig, ma, eo, so = detect_decoupled_holdout(
                    t, mid, st, ss, sl, b300["end_ms"], a300,
                    b1["end_ms"], b1["open"], b1["close"],
                    b5["end_ms"], b5["open"], b5["close"],
                    b15["end_ms"], b15["open"], b15["close"],
                    ad, at, int(mf * 1000), int(mp * 1000), pe, rb, rd, em, rt, HOLDOUT_START_MS,
                )
                ownership = "FAILURE_CANDIDATE_DECOUPLED_SHORT_PROBE_WINDOW"
            else:
                rc, rsi, rssig = cc, csi, cssig
                ma = eo = so = 0
                ownership = "SERIAL_POST_QUAL_LONG_OR_EQUAL_PROBE_WINDOW"
            if so:
                raise SystemExit(f"candidate signal overflow {surface} {n}")
            rm = admit_r9_lifecycle(t, ask, bid, rsi, rssig)
            cmet = metrics_tuple(cm); rmet = metrics_tuple(rm)
            control_vectors[n] = {"funnel": dict(zip(STAGES, map(int, cc))), "signals": int(csi.size), "execution": cmet}
            candidate_vectors[n] = {"ownership": ownership, "funnel": dict(zip(STAGES, map(int, rc))), "signals": int(rsi.size), "execution": rmet}
            control_net += cmet["net_usd"]; candidate_net += rmet["net_usd"]
            control_trades += cmet["trades"]; candidate_trades += rmet["trades"]
            control_wins += cmet["wins"]; candidate_wins += rmet["wins"]
            control_dd_sum += cmet["max_drawdown_usd"]; candidate_dd_sum += rmet["max_drawdown_usd"]
            if n in SELECTED:
                selected_control_net += cmet["net_usd"]; selected_candidate_net += rmet["net_usd"]
            max_active = max(max_active, int(ma)); ep_over += int(eo); sig_over += int(so)
        if ep_over or sig_over:
            raise SystemExit(f"capacity overflow {surface}: episodes={ep_over} signals={sig_over}")
        net_delta = candidate_net - control_net
        selected_net_delta = selected_candidate_net - selected_control_net
        surface_pass = bool(net_delta >= -1e-12 and selected_net_delta >= -1e-12)
        all_surface_pass = all_surface_pass and surface_pass
        results[surface] = {
            "control": {"trades": control_trades, "wins": control_wins, "net_usd": control_net, "sum_vector_max_drawdown_usd": control_dd_sum, "vectors": control_vectors},
            "candidate": {"trades": candidate_trades, "wins": candidate_wins, "net_usd": candidate_net, "sum_vector_max_drawdown_usd": candidate_dd_sum, "vectors": candidate_vectors},
            "delta": {"trades": candidate_trades - control_trades, "wins": candidate_wins - control_wins, "net_usd": net_delta, "sum_vector_max_drawdown_usd": candidate_dd_sum - control_dd_sum, "selected_vector_net_usd": selected_net_delta},
            "surface_gate_pass": surface_pass,
            "max_concurrent_failure_episodes": max_active,
            "episode_overflow": ep_over,
            "signal_overflow": sig_over,
        }
    out = {
        "schema": "delta-r037-dh05-short-probe-ownership-anti-overfit-validation-10a-v1",
        "status": "BOUNDED_LATE_JAN_CROSS_SURFACE_ANTI_OVERFIT_VALIDATION_COMPLETE",
        "source_sha256": sha,
        "warmup_start_ms": WARMUP_START_MS,
        "holdout_start_ms": HOLDOUT_START_MS,
        "holdout_last_tick_ms": int(t[-1]),
        "loaded_ticks_from_warmup": int(t.size),
        "surfaces": results,
        "router_rule": "max_probe_age_s < acceptance_tf_seconds -> FAILURE_CANDIDATE_DECOUPLED_POST_QUAL; otherwise SERIAL_POST_QUAL",
        "numeric_vector_retune": False,
        "same_holdout_recuts": False,
        "august_accessed": False,
        "finding": {
            "all_three_surfaces_no_worse_net": all_surface_pass,
            "promotion_eligible_from_this_gate_alone": False,
            "interpretation": "Independent late-January cross-surface robustness evidence only. Passing permits a separate semantic-promotion/provenance decision; failing rejects 09Z as a promotable ownership rule.",
        },
        "next": "R037_DH05_SHORT_PROBE_OWNERSHIP_PROVENANCE_PROMOTION_DECISION_IF_PASS_ELSE_GENERATOR_PROVENANCE_CLOSE",
    }
    atomic_write_json(args.output, out)
    faulthandler.cancel_dump_traceback_later()
    print(json.dumps({
        "all_three_surfaces_no_worse_net": all_surface_pass,
        "surface_summary": {s: {"control_net": results[s]["control"]["net_usd"], "candidate_net": results[s]["candidate"]["net_usd"], "delta_net": results[s]["delta"]["net_usd"], "delta_trades": results[s]["delta"]["trades"], "delta_wins": results[s]["delta"]["wins"], "delta_dd_sum": results[s]["delta"]["sum_vector_max_drawdown_usd"], "selected_net_delta": results[s]["delta"]["selected_vector_net_usd"], "pass": results[s]["surface_gate_pass"]} for s in results}
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
