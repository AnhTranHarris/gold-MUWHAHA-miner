#!/usr/bin/env python3
"""
Portable January source-equivalence + multi-resolution cache certification.

Heavy raw input is processed in one process only. This job:
1) finds exactly one January Dukascopy gzip under R9_DATA_DIR,
2) verifies the known raw SHA-256,
3) reproduces the authoritative V2 January baseline with local-window S1 arithmetic,
4) builds the full tick-derived resolution lattice required by the Master Protocol,
5) stores compact local caches plus a small certification result.

No model fitting. No February-July access. No August access.
"""
import gc, hashlib, json, os, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

RAW_NAME = "XAUUSD_DUKAS_2026_01_ticks.csv.gz"
RAW_SHA = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
EXPECTED = {
    "trades": 33793,
    "net": -6253.808000024798,
    "gp": 4301.471499988871,
    "gl": -10555.279500013668,
    "pf": 0.407518483994981,
    "win": 0.44630544787382004,
    "avg_hold": 5.547792087118634,
    "maxdd": 6256.753000024797,
}
RESOLUTIONS_MS = {
    "S025": 250,
    "S1": 1000,
    "S5": 5000,
    "S15": 15000,
    "S30": 30000,
    "S45": 45000,
    "M1": 60000,
    "M5": 300000,
    "M7": 420000,
    "M15": 900000,
    "M30": 1800000,
    "M45": 2700000,
    "H1": 3600000,
    "H4": 14400000,
    "H12": 43200000,
    "D1": 86400000,
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as w:
        json.dump(obj, w, indent=2, sort_keys=True, allow_nan=False)
        w.flush()
        os.fsync(w.fileno())
    os.replace(tmp, path)

def find_raw(root):
    hits = list(Path(root).rglob(RAW_NAME))
    if len(hits) != 1:
        raise RuntimeError(f"expected exactly one {RAW_NAME} under {root}; found {len(hits)}: {hits}")
    return hits[0]

def load_ticks(raw):
    df = pd.read_csv(
        raw, compression="gzip",
        usecols=["timestamp_ms_utc","ask_raw","bid_raw","ask_volume","bid_volume"],
        dtype={"timestamp_ms_utc":"int64","ask_raw":"int64","bid_raw":"int64",
               "ask_volume":"float64","bid_volume":"float64"}
    )
    t = df.timestamp_ms_utc.to_numpy(np.int64, copy=False)
    ask = df.ask_raw.to_numpy(np.float64, copy=False) / 1000.0
    bid = df.bid_raw.to_numpy(np.float64, copy=False) / 1000.0
    mid = (ask + bid) * 0.5
    av = df.ask_volume.to_numpy(np.float64, copy=False)
    bv = df.bid_volume.to_numpy(np.float64, copy=False)
    return t, mid, av, bv

def aggregate_active_seconds(t, mid, av, bv):
    sec = t // 1000
    ids, idx, cnt = np.unique(sec, return_index=True, return_counts=True)
    last = idx + cnt - 1
    o = mid[idx]; c = mid[last]
    h = np.maximum.reduceat(mid, idx); l = np.minimum.reduceat(mid, idx)
    asum = np.add.reduceat(av, idx); bsum = np.add.reduceat(bv, idx)
    return ids.astype(np.int64), o, h, l, c, cnt.astype(np.int64), asum/cnt, bsum/cnt

def build_s1_exact(sec_ids, o, h, l, c, n, am, bm):
    N = len(sec_ids)
    disp = np.full(N, np.nan); eff = np.full(N, np.nan)
    rng = np.full(N, np.nan); turns = np.full(N, 99.0)
    tickratio = np.full(N, np.nan); volimb = np.full(N, np.nan)
    for i in range(10, N):
        w = c[i-9:i+1]
        d = np.diff(w)
        travel = np.abs(d).sum()
        disp[i] = w[-1] - w[0]
        eff[i] = abs(disp[i]) / (travel + 1e-12)
        rng[i] = h[i-9:i+1].max() - l[i-9:i+1].min()
        nz = np.sign(d); nz = nz[nz != 0]
        turns[i] = np.sum(nz[1:] != nz[:-1]) if len(nz) > 1 else 0
        tickratio[i] = n[i] / (np.mean(n[max(0,i-10):i]) + 1e-9)
        volimb[i] = (bm[i] - am[i]) / (bm[i] + am[i] + 1e-12)
    return disp, eff, rng, turns, tickratio, volimb

def aggregate_tf(t, mid, tf_sec):
    bucket = t // (tf_sec * 1000)
    ids, idx, cnt = np.unique(bucket, return_index=True, return_counts=True)
    last = idx + cnt - 1
    o = mid[idx]; c = mid[last]
    h = np.maximum.reduceat(mid, idx); l = np.minimum.reduceat(mid, idx)
    end = (ids + 1) * tf_sec
    prev = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h-l, np.maximum(np.abs(h-prev), np.abs(l-prev)))
    atr = np.full(len(tr), np.nan)
    e = np.nan
    for i, x in enumerate(tr):
        if not np.isfinite(x): continue
        e = x if not np.isfinite(e) else (13.0/14.0)*e + (1.0/14.0)*x
        if i >= 13: atr[i] = e
    return {"end": end.astype(np.int64), "o": o, "h": h, "l": l, "c": c,
            "count": cnt.astype(np.int32), "atr": atr}

def build_m5_atr_by_sec(sec_ids, t, mid):
    z = aggregate_tf(t, mid, 300)
    j = np.searchsorted(z["end"], sec_ids, side="right") - 1
    out = np.full(len(sec_ids), np.nan)
    ok = j >= 0
    out[ok] = z["atr"][j[ok]]
    return out

@njit
def session_for_sec(sec):
    lon_off = 60 if (sec >= 1774746000 and sec < 1792890000) else 0
    ny_off = -240 if (sec >= 1772953200 and sec < 1793512800) else -300
    lm = ((sec + lon_off*60) % 86400) // 60
    nm = ((sec + ny_off*60) % 86400) // 60
    l = (lm >= 480 and lm < 990)
    n = (nm >= 480 and nm < 1020)
    if l and n: return 2
    if l: return 1
    if n: return 3
    return 0

@njit
def r9_baseline_events(t, mid, sec_ids, s1_disp, s1_eff, s1_rng, s1_turns, atr_by_sec):
    maxtr = max(50000, len(t)//20)
    ev_i=np.empty(maxtr,np.int64); exit_t=np.empty(maxtr,np.int64)
    pnl=np.empty(maxtr,np.float64); hold=np.empty(maxtr,np.float64)
    ntr=0; sec_idx=-1; last_sec=-1; minute=-1
    buy_lvl=0.; sell_lvl=0.; pending=0; rearms=0
    pos=0; entry=0.; stop=0.; opent=0; last_pos=0; rearm_pending=0
    for i in range(len(t)):
        tt=t[i]; p=mid[i]; sec=tt//1000
        if sec != last_sec:
            while sec_idx+1 < len(sec_ids) and sec_ids[sec_idx+1] < sec:
                sec_idx += 1
            last_sec = sec
        mn=tt//60000
        if mn != minute:
            minute=mn; rearms=0; pending=2
            buy_lvl=round((p+.15)*100.)/100.; sell_lvl=round((p-.15)*100.)/100.
        bid=p-.10; ask=p+.10
        if pos != 0:
            exited=False; ex=0.
            if (pos>0 and bid<=stop) or (pos<0 and ask>=stop):
                ex=bid if pos>0 else ask; exited=True
            elif tt-opent >= 30000:
                ex=bid if pos>0 else ask; exited=True
            else:
                if pos>0 and bid-entry >= .10:
                    cand=bid-.03
                    if cand > stop+.005: stop=cand
                elif pos<0 and entry-ask >= .10:
                    cand=ask+.03
                    if cand < stop-.005: stop=cand
            if exited:
                pnl[ntr-1]=(ex-entry)*pos; hold[ntr-1]=(tt-opent)/1000.; exit_t[ntr-1]=tt
                last_pos=pos; pos=0; rearm_pending=1
            continue
        if rearm_pending:
            rearm_pending=0
            if tt//60000 == minute and rearms < 3:
                rearms += 1; pending=-last_pos
            else: pending=0
            continue
        if pending==0 or sec_idx<10: continue
        av=atr_by_sec[sec_idx]
        if not np.isfinite(av): continue
        ss=session_for_sec(sec_ids[sec_idx]); floor=2.5
        if ss==1: floor=2.0
        elif ss==2 or ss==3: floor=1.75
        if av+1e-12 < floor: continue
        side=0
        if (pending==2 or pending==1) and ask>=buy_lvl: side=1
        elif (pending==2 or pending==-1) and bid<=sell_lvl: side=-1
        if side==0: continue
        dd=s1_disp[sec_idx]; ee=s1_eff[sec_idx]; rr=s1_rng[sec_idx]; tr=s1_turns[sec_idx]
        if not (ee>=.70 and rr>=.50 and tr<=9): continue
        if side>0 and dd<.15: continue
        if side<0 and dd>-.15: continue
        if ntr>=maxtr: break
        ev_i[ntr]=i
        entry=ask if side>0 else bid
        stop=bid-.30 if side>0 else ask+.30
        pos=side; opent=tt; pending=0
        pnl[ntr]=np.nan; hold[ntr]=np.nan; exit_t[ntr]=0
        ntr += 1
    return ev_i[:ntr], exit_t[:ntr], pnl[:ntr], hold[:ntr]

def maxdd(pnl):
    eq=np.cumsum(pnl)
    peak=np.maximum.accumulate(np.r_[0.0,eq])
    dd=peak[1:]-eq
    return float(dd.max(initial=0.0))

def daily_drawdowns(exit_t, pnl):
    days = exit_t // 86400000
    out = {}
    for d in np.unique(days):
        x=pnl[days==d]
        out[str(int(d))]={"net":float(x.sum()),"maxdd":maxdd(x),"trades":int(len(x))}
    return out

def build_resolution_cache(out_dir, t, mid):
    manifest={}
    for name, ms in RESOLUTIONS_MS.items():
        bucket=t//ms
        ids, idx, cnt=np.unique(bucket,return_index=True,return_counts=True)
        last=idx+cnt-1
        o=mid[idx]; c=mid[last]
        h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
        end_ms=(ids+1)*ms
        p=out_dir/f"{name}.npz"
        np.savez_compressed(p,end_ms=end_ms,o=o,h=h,l=l,c=c,count=cnt.astype(np.int32))
        manifest[name]={"interval_ms":ms,"bars":int(len(ids)),"bytes":p.stat().st_size,"sha256":sha256(p)}
        del bucket,ids,idx,cnt,last,o,c,h,l,end_ms
        gc.collect()
    return manifest

def close_enough(a,b,tol=1e-9):
    return abs(float(a)-float(b)) <= tol

def main():
    t0=time.time()
    data_root=Path(os.environ["R9_DATA_DIR"])
    out=Path(os.environ["R9_CACHE_DIR"])
    out.mkdir(parents=True,exist_ok=True)
    result_path=out/"CERT_RESULT.json"

    raw=find_raw(data_root)
    raw_sha=sha256(raw)
    if raw_sha != RAW_SHA:
        raise RuntimeError(f"January raw SHA mismatch: {raw_sha}")

    t,mid,av,bv=load_ticks(raw)
    if len(t)!=9135062:
        raise RuntimeError(f"January row-count mismatch: {len(t)}")

    sec_ids,o,h,l,c,n,am,bm=aggregate_active_seconds(t,mid,av,bv)
    s1_disp,s1_eff,s1_rng,s1_turns,tickratio,volimb=build_s1_exact(sec_ids,o,h,l,c,n,am,bm)
    atrsec=build_m5_atr_by_sec(sec_ids,t,mid)

    ev_i,exit_t,pnl,hold=r9_baseline_events(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atrsec)
    good=np.isfinite(pnl) & (exit_t>0)
    ev_i=ev_i[good]; exit_t=exit_t[good]; pnl=pnl[good]; hold=hold[good]
    gp=float(pnl[pnl>0].sum()); gl=float(pnl[pnl<0].sum())
    summary={
        "trades":int(len(pnl)),"net":float(pnl.sum()),"gp":gp,"gl":gl,
        "pf":float(gp/(-gl)),"win":float((pnl>0).mean()),
        "avg_hold":float(hold.mean()),"maxdd":maxdd(pnl)
    }
    exact=(summary["trades"]==EXPECTED["trades"]
           and all(close_enough(summary[k],EXPECTED[k],1e-8) for k in ("net","gp","gl","pf","win","avg_hold","maxdd")))
    if not exact:
        atomic_json(result_path,{"job_id":"MM-C30-B1B-S73-RECOVERY-JAN-SERIAL","status":"BLOCKED_SOURCE_EQUIVALENCE",
                                 "raw":str(raw),"raw_sha256":raw_sha,"summary":summary,"expected":EXPECTED,
                                 "august_accessed":False,"forward_accessed":False})
        raise RuntimeError(f"Exact V2 January checksum failed: {summary}")

    bars_dir=out/"bars"
    bars_dir.mkdir(exist_ok=True)
    lattice=build_resolution_cache(bars_dir,t,mid)

    feature_cache=out/"V2_JAN_CAUSAL_STATE.npz"
    np.savez_compressed(feature_cache,sec_ids=sec_ids,o=o,h=h,l=l,c=c,tick_count=n,
                        s1_disp=s1_disp,s1_eff=s1_eff,s1_range=s1_rng,s1_turns=s1_turns,
                        s1_tickratio=tickratio,s1_volimb=volimb,m5_atr=atrsec,
                        event_tick_index=ev_i,exit_time_ms=exit_t,base_pnl=pnl,base_hold=hold)

    result={
        "job_id":"MM-C30-B1B-S73-RECOVERY-JAN-SERIAL",
        "status":"COMPLETED_LOCAL",
        "scientific_scope":"January source-equivalence + reusable full-resolution cache; no model fitting",
        "month":"2026-01",
        "raw":str(raw),"raw_sha256":raw_sha,"raw_rows":int(len(t)),
        "active_seconds":int(len(sec_ids)),
        "exact_v2_baseline_match":True,
        "baseline":summary,
        "daily_drawdown_retained_internal":True,
        "daily":daily_drawdowns(exit_t,pnl),
        "lattice":lattice,
        "feature_cache":{"path":str(feature_cache),"bytes":feature_cache.stat().st_size,"sha256":sha256(feature_cache)},
        "forward_accessed":False,"august_accessed":False,
        "elapsed_seconds":time.time()-t0
    }
    atomic_json(result_path,result)
    print(json.dumps({k:v for k,v in result.items() if k!="daily"},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
