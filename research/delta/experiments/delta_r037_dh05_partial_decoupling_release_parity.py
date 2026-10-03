"""DELTA R037 DH05 partial-decoupling release-point parity diagnostic — Checkpoint 09I.

Research-only bounded diagnostic.

Frozen causal hypotheses:
- 09C symmetric two-bar confirmed M5 swing boundary;
- 09C repeated same-boundary pre-failure attempt ledger;
- 09D stage-gated signed completed acceptance-bar body displacement / event M5 ATR;
- 09E per-attempt max_probe_age lifecycle clock;
- 09F post-qualification acceptance-bar chronology is retained as the serial comparison clue;
- max_failure_age starts at FAILURE_CANDIDATE;
- no numeric-vector retuning.

This unit changes only ownership release timing. A failed-break episode remains coupled to
and blocks the probe generator until either REENTRY or RECLAIM, then the generator is
released while that downstream episode continues independently toward reversal/expiry.
Outputs are written atomically.
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
            mode="w", encoding="utf-8", newline="\n", prefix=f".{path.name}.",
            suffix=".tmp", dir=path.parent, delete=False,
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
        h, l = hi[k], lo[k]
        ish = all(h > hi[k-j] and h > hi[k+j] for j in range(1, w+1))
        isl = all(l < lo[k-j] and l < lo[k+j] for j in range(1, w+1))
        reveal = int(end[k+w])
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
def detect_serial(
    t, mid2, st, ss, sl, m5e, m5a, s1e, s1o, s1c, s5e, s5o, s5c,
    s15e, s15o, s15c, accdisp, acctf, maxfail, maxprobe, probeexc,
    reclaim, revdisp, effmin, revtf, postqual,
):
    stage = 0; oside = 0; L = 0; evatr = 0.0; attempt_start = 0; qualified_start = 0
    fstart = 0; reent = False; latest_hi = 0; latest_lo = 0; si = 0
    hiel = True; loel = True; lastacc = -1; lastrev = -1
    attempt_open = False; attempt_qualified = False; cnt = np.zeros(8, np.int64)

    for i in range(t.size):
        tm = int(t[i]); px = int(mid2[i])
        while si < st.size and st[si] <= tm:
            if ss[si] > 0: latest_hi = int(sl[si])
            else: latest_lo = int(sl[si])
            si += 1
        jm = bidx(m5e, tm)
        if jm < 13: continue
        ae = float(m5a[jm])
        if ae <= 0: continue

        if stage == 0:
            if latest_hi and px < latest_hi: hiel = True
            if latest_lo and px > latest_lo: loel = True
            if latest_hi and hiel and px >= latest_hi:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0; hiel=False
                cnt[0]+=1; attempt_open=True; attempt_qualified=False
            elif latest_lo and loel and px <= latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0; loel=False
                cnt[0]+=1; attempt_open=True; attempt_qualified=False
        if stage == 0: continue

        if stage <= 2:
            inside = oside * (px-L) < 0
            if inside:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                attempt_open=True; attempt_qualified=False; qualified_start=0; cnt[0]+=1; attempt_start=tm
            if attempt_open and (not attempt_qualified) and oside*(px-L) >= probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)
        acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)

        if stage == 1:
            if oside*(px-L) >= probeexc*evatr:
                stage=2
                if qualified_start == 0: qualified_start=tm
            elif tm-attempt_start > maxprobe:
                stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                continue
        if stage < 2: continue

        if stage == 2 and jacc >= 0 and jacc != lastacc:
            lastacc=jacc
            q = oside*(ac-ao) >= accdisp*evatr and oside*(ac-L) > 0
            if postqual:
                q = q and qualified_start > 0 and acc_end > qualified_start
            if q:
                cnt[2]+=1; stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                continue

        recross = oside*(px-L) < 0
        if stage == 2 and (tm-attempt_start >= maxprobe or recross):
            stage=3; cnt[3]+=1; fstart=tm; attempt_open=False; attempt_qualified=False; qualified_start=0
        if stage == 3:
            if recross and not reent:
                reent=True; cnt[4]+=1; stage=4
            elif fstart and tm-fstart > maxfail:
                stage=0; oside=0; reent=False; continue
        elif stage >= 4 and fstart and tm-fstart > maxfail:
            stage=0; oside=0; reent=False; continue
        if stage < 4: continue

        jrev=j1 if revtf==1 else j5
        rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
        if stage == 4 and jrev >= 0 and jrev != lastrev:
            if (-oside)*(rc-L) >= reclaim*evatr:
                cnt[5]+=1; stage=5
        if stage < 5 or jrev < 0 or jrev == lastrev: continue
        ro=s1o[j1] if revtf==1 else s5o[j5]
        disp=(-oside)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0
        if disp >= revdisp*evatr and eff >= effmin:
            cnt[6]+=1; cnt[7]+=1; stage=0; oside=0; reent=False
        lastrev=jrev
    return cnt


@njit(cache=True)
def detect_partial(
    t, mid2, st, ss, sl, m5e, m5a, s1e, s1o, s1c, s5e, s5o, s5c,
    s15e, s15o, s15c, accdisp, acctf, maxfail, maxprobe, probeexc,
    reclaim, revdisp, effmin, revtf, release_point,
):
    stage=0; oside=0; L=0; evatr=0.0; attempt_start=0; qualified_start=0; fstart=0
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True; lastacc=-1; lastrev=-1
    attempt_open=False; attempt_qualified=False; cnt=np.zeros(8,np.int64)

    MAX_EP=64
    active=np.zeros(MAX_EP,np.int8); estage=np.zeros(MAX_EP,np.int8); eoside=np.zeros(MAX_EP,np.int8)
    eL=np.zeros(MAX_EP,np.int64); eatr=np.zeros(MAX_EP,np.float64); efstart=np.zeros(MAX_EP,np.int64)
    elastrev=np.full(MAX_EP,-1,np.int64)
    max_active=0; overflow=0

    for i in range(t.size):
        tm=int(t[i]); px=int(mid2[i])
        while si < st.size and st[si] <= tm:
            if ss[si] > 0: latest_hi=int(sl[si])
            else: latest_lo=int(sl[si])
            si += 1
        jm=bidx(m5e,tm)
        if jm < 13: continue
        ae=float(m5a[jm])
        if ae <= 0: continue

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)
        acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)
        jrev=j1 if revtf==1 else j5
        rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
        ro=s1o[j1] if revtf==1 and j1>=0 else (s5o[j5] if j5>=0 else 0)

        if stage == 0:
            if latest_hi and px < latest_hi: hiel=True
            if latest_lo and px > latest_lo: loel=True
            if latest_hi and hiel and px >= latest_hi:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0; hiel=False
                cnt[0]+=1; attempt_open=True; attempt_qualified=False
            elif latest_lo and loel and px <= latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0; loel=False
                cnt[0]+=1; attempt_open=True; attempt_qualified=False

        if stage > 0 and stage <= 2:
            inside=oside*(px-L) < 0
            if inside:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                attempt_open=True; attempt_qualified=False; qualified_start=0; cnt[0]+=1; attempt_start=tm
            if attempt_open and (not attempt_qualified) and oside*(px-L) >= probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1

            if stage == 1:
                if oside*(px-L) >= probeexc*evatr:
                    stage=2
                    if qualified_start == 0: qualified_start=tm
                elif tm-attempt_start > maxprobe:
                    stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0

        if stage == 2 and jacc >= 0 and jacc != lastacc:
            lastacc=jacc
            q=oside*(ac-ao) >= accdisp*evatr and oside*(ac-L)>0
            q=q and qualified_start>0 and acc_end>qualified_start
            if q:
                cnt[2]+=1; stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0

        if stage == 2:
            recross=oside*(px-L)<0
            if tm-attempt_start >= maxprobe or recross:
                stage=3; cnt[3]+=1; fstart=tm; attempt_open=False; attempt_qualified=False; qualified_start=0

        if stage >= 3:
            recross=oside*(px-L)<0
            if stage == 3:
                if recross:
                    cnt[4]+=1; stage=4
                    if release_point == 4:
                        slot=-1
                        for qslot in range(MAX_EP):
                            if active[qslot] == 0:
                                slot=qslot; break
                        if slot < 0:
                            overflow += 1
                        else:
                            active[slot]=1; estage[slot]=4; eoside[slot]=oside; eL[slot]=L; eatr[slot]=evatr
                            efstart[slot]=fstart; elastrev[slot]=lastrev
                        stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0; lastrev=-1
                elif fstart and tm-fstart > maxfail:
                    stage=0; oside=0; lastrev=-1
            elif stage >= 4 and fstart and tm-fstart > maxfail:
                stage=0; oside=0; lastrev=-1

        if stage == 4 and release_point == 5 and jrev >= 0 and jrev != lastrev:
            if (-oside)*(rc-L) >= reclaim*evatr:
                cnt[5]+=1
                slot=-1
                for qslot in range(MAX_EP):
                    if active[qslot] == 0:
                        slot=qslot; break
                if slot < 0:
                    overflow += 1
                else:
                    active[slot]=1; estage[slot]=5; eoside[slot]=oside; eL[slot]=L; eatr[slot]=evatr
                    efstart[slot]=fstart; elastrev[slot]=lastrev
                stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0; lastrev=-1
            else:
                lastrev=jrev

        alive=0
        for e in range(MAX_EP):
            if active[e] == 0: continue
            eo=int(eoside[e]); el=int(eL[e]); ea=float(eatr[e])
            if tm-int(efstart[e]) > maxfail:
                active[e]=0; continue
            if jrev >= 0 and jrev != elastrev[e]:
                if estage[e] == 4 and (-eo)*(rc-el) >= reclaim*ea:
                    cnt[5]+=1; estage[e]=5
                if estage[e] >= 5:
                    disp=(-eo)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0
                    if disp >= revdisp*ea and eff >= effmin:
                        cnt[6]+=1; cnt[7]+=1; active[e]=0; continue
                elastrev[e]=jrev
            if active[e] != 0: alive += 1
        if alive > max_active: max_active=alive

        if stage >= 4 and release_point == 4:
            if jrev >= 0 and jrev != lastrev:
                if stage == 4 and (-oside)*(rc-L) >= reclaim*evatr:
                    cnt[5]+=1; stage=5
                if stage >= 5:
                    disp=(-oside)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0
                    if disp >= revdisp*evatr and eff >= effmin:
                        cnt[6]+=1; cnt[7]+=1; stage=0; oside=0; lastrev=-1
                    else:
                        lastrev=jrev

    return cnt, max_active, overflow


def summarize(c, trg):
    er=np.abs(c-trg)
    return {
        "target":dict(zip(STAGES,map(int,trg))),
        "actual":dict(zip(STAGES,map(int,c))),
        "signed_error":dict(zip(STAGES,map(int,c-trg))),
        "abs_error":dict(zip(STAGES,map(int,er))),
    }, er


def evaluate_serial(postqual, t, mid, st, ss, sl, b1, b5, b15, b300, a300):
    vectors={}; stage_abs=np.zeros(8,np.int64)
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c=detect_serial(t,mid,st,ss,sl,b300["end_ms"],a300,b1["end_ms"],b1["open"],b1["close"],
                        b5["end_ms"],b5["open"],b5["close"],b15["end_ms"],b15["open"],b15["close"],
                        ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,postqual)
        trg=np.asarray(TARGET[n],np.int64); row,er=summarize(c,trg); vectors[n]=row; stage_abs+=er
    return {
        "vectors":vectors,
        "stage_abs_error":dict(zip(STAGES,map(int,stage_abs))),
        "probe_qualified_abs_error":int(stage_abs[:2].sum()),
        "first5_abs_error":int(stage_abs[:5].sum()),
        "downstream_abs_error":int(stage_abs[5:].sum()),
        "total_abs_error":int(stage_abs.sum()),
    }


def evaluate_partial(release_point, t, mid, st, ss, sl, b1, b5, b15, b300, a300):
    vectors={}; stage_abs=np.zeros(8,np.int64); max_active_all=0; overflow_all=0
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c,ma,ov=detect_partial(t,mid,st,ss,sl,b300["end_ms"],a300,b1["end_ms"],b1["open"],b1["close"],
                               b5["end_ms"],b5["open"],b5["close"],b15["end_ms"],b15["open"],b15["close"],
                               ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,release_point)
        trg=np.asarray(TARGET[n],np.int64); row,er=summarize(c,trg)
        row["max_concurrent_detached_episodes"]=int(ma); row["episode_overflow"]=int(ov)
        vectors[n]=row; stage_abs+=er; max_active_all=max(max_active_all,int(ma)); overflow_all+=int(ov)
    return {
        "vectors":vectors,
        "stage_abs_error":dict(zip(STAGES,map(int,stage_abs))),
        "probe_qualified_abs_error":int(stage_abs[:2].sum()),
        "first5_abs_error":int(stage_abs[:5].sum()),
        "downstream_abs_error":int(stage_abs[5:].sum()),
        "total_abs_error":int(stage_abs.sum()),
        "max_concurrent_detached_episodes":max_active_all,
        "episode_overflow":overflow_all,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    source_sha=sha256_file(args.source)
    if source_sha != CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")
    df=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc < STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a300=atr14(b300); st,ss,sl=symmetric_swings(b300,2)

    control09e=evaluate_serial(False,t,mid,st,ss,sl,b1,b5,b15,b300,a300)
    postqual=evaluate_serial(True,t,mid,st,ss,sl,b1,b5,b15,b300,a300)
    reentry=evaluate_partial(4,t,mid,st,ss,sl,b1,b5,b15,b300,a300)
    reclaim=evaluate_partial(5,t,mid,st,ss,sl,b1,b5,b15,b300,a300)

    exp09e={"probe":525,"qualified":29,"accepted":157,"failure":170,"reentry":39,"reclaim":38,"reversal":53,"signal":53}
    exppq={"probe":642,"qualified":55,"accepted":24,"failure":63,"reentry":34,"reclaim":34,"reversal":63,"signal":63}
    if control09e["stage_abs_error"] != exp09e:
        raise SystemExit("CONTROL_09E drift: "+json.dumps(control09e["stage_abs_error"],sort_keys=True))
    if postqual["stage_abs_error"] != exppq:
        raise SystemExit("POST_QUAL_BASE drift: "+json.dumps(postqual["stage_abs_error"],sort_keys=True))
    if reentry["episode_overflow"] != 0 or reclaim["episode_overflow"] != 0:
        raise SystemExit("detached episode overflow")

    profiles={"CONTROL_09E":control09e,"POST_QUAL_BASE":postqual,
              "RELEASE_AT_REENTRY_POST_QUAL":reentry,"RELEASE_AT_RECLAIM_POST_QUAL":reclaim}
    ranking=[]
    for name in ("RELEASE_AT_REENTRY_POST_QUAL","RELEASE_AT_RECLAIM_POST_QUAL"):
        r=profiles[name]
        ranking.append({
            "profile":name,
            "probe_qualified_abs_error":r["probe_qualified_abs_error"],
            "first5_abs_error":r["first5_abs_error"],
            "downstream_abs_error":r["downstream_abs_error"],
            "total_abs_error":r["total_abs_error"],
            "total_improvement_vs_postqual":postqual["total_abs_error"]-r["total_abs_error"],
            "probe_qualified_improvement_vs_postqual":postqual["probe_qualified_abs_error"]-r["probe_qualified_abs_error"],
        })
    ranking.sort(key=lambda x:(-x["total_improvement_vs_postqual"],-x["probe_qualified_improvement_vs_postqual"],x["downstream_abs_error"]))

    out={
        "schema":"delta-r037-dh05-partial-decoupling-release-parity-v1",
        "status":"BOUNDED_QA_COMPLETE",
        "source_sha256":source_sha,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75",
        "august_accessed":False,"numeric_vector_retune":False,
        "frozen_semantics":{
            "boundary":"09C symmetric two-bar confirmed M5 swing",
            "probe":"09C repeated same-boundary attempt ledger",
            "probe_clock":"09E per-attempt lifecycle clock",
            "acceptance":"09F post-qualification completed acceptance-bar chronology",
            "failure_clock":"starts at FAILURE_CANDIDATE",
        },
        "profiles":profiles,"ranking":ranking,
        "finding":{
            "selection_rule":"release point may carry forward only if it improves total six-vector parity versus POST_QUAL_BASE without episode overflow and without a compensating large downstream mismatch",
            "leading_profile":ranking[0]["profile"],
            "parity_complete":False,
            "next":"review release-point fingerprint; if material, freeze ownership release boundary before any signal-multiplicity/admission diagnostic",
        },
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"postqual_total":postqual["total_abs_error"],"ranking":ranking},separators=(",",":")))


if __name__ == "__main__":
    main()
