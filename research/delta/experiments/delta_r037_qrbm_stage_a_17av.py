"""DELTA R037 quote-revision burst momentum Stage-A screen — 17AV.

One preregistered source family only:
- native Dukascopy BBO quote revisions are counted in completed UTC 1-second bins;
- each completed second is compared with the previous 600 completed seconds;
- extreme if count > trailing median + 3 * 1.4826 * trailing MAD;
- only the first second of a consecutive extreme run is eligible;
- direction is the sign of native midquote displacement from first to last revision
  within that completed burst second;
- entry is the first executable P75 tick at/after the second's right edge.

No threshold/window/profile sweep, no QIM/OFI overlay, no session/side rescue,
no exit retuning, no August access, no MQL5.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

DAY_MS=86_400_000
TICK_RAW=10
SCALE=1000
STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000
UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="06e151b552adafe5fed571c45e2581e30831f10f"

MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30
BASELINE_SECONDS=600
MAD_SCALE=1.4826
ROBUST_Z=3.0

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def atomic_write_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",
                                         prefix=f".{path.name}.",suffix=".tmp",
                                         dir=path.parent,delete=False) as f:
            tmp_name=f.name
            json.dump(payload,f,indent=2)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp_name,path); tmp_name=None
    finally:
        if tmp_name is not None:
            try: os.unlink(tmp_name)
            except FileNotFoundError: pass

def session_code(t):
    tod=t%DAY_MS
    ls=np.where(t>=UK_DST_START_2026_MS,7,8)*3_600_000
    le=ls+8*3_600_000+30*60_000
    ns=np.where(t>=US_DST_START_2026_MS,12,13)*3_600_000
    ne=ns+9*3_600_000
    il=(tod>=ls)&(tod<le); iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75(t,ask_raw,bid_raw):
    s=session_code(t); spread=P75_POINTS[s]*TICK_RAW
    mid2=ask_raw.astype(np.int64)+bid_raw.astype(np.int64)
    bid=((mid2-spread+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    return (bid+spread).astype(np.int64),bid.astype(np.int64)

@njit(cache=True)
def q_tick(x):
    return ((int(x)+TICK_RAW//2)//TICK_RAW)*TICK_RAW

@njit(cache=True)
def build_second_features(t,ask,bid,sec0,nsec):
    counts=np.zeros(nsec,np.int32)
    first_mid=np.zeros(nsec,np.int64)
    last_mid=np.zeros(nsec,np.int64)
    seen=np.zeros(nsec,np.uint8)
    for i in range(1,t.size):
        if ask[i]==ask[i-1] and bid[i]==bid[i-1]:
            continue
        s=int(t[i]//1000-sec0)
        if s<0 or s>=nsec: continue
        m=int(ask[i])+int(bid[i])
        counts[s]+=1
        if seen[s]==0:
            first_mid[s]=m
            seen[s]=1
        last_mid[s]=m
    return counts,first_mid,last_mid,seen

@njit(cache=True)
def hist_lower_median(hist,n):
    k=(n-1)//2
    acc=0
    for v in range(hist.size):
        acc+=hist[v]
        if acc>k: return v
    return hist.size-1

@njit(cache=True)
def hist_mad(hist,n,med):
    k=(n-1)//2
    acc=hist[med]
    if acc>k: return 0
    maxd=max(med,hist.size-1-med)
    for d in range(1,maxd+1):
        lo=med-d; hi=med+d
        if lo>=0: acc+=hist[lo]
        if hi<hist.size: acc+=hist[hi]
        if acc>k: return d
    return maxd

@njit(cache=True)
def robust_extreme_flags(counts,window):
    n=counts.size
    maxc=int(np.max(counts))
    hist=np.zeros(maxc+1,np.int32)
    flags=np.zeros(n,np.uint8)
    medout=np.zeros(n,np.int32)
    madout=np.zeros(n,np.int32)
    if n<=window: return flags,medout,madout
    for i in range(window):
        hist[int(counts[i])]+=1
    for i in range(window,n):
        med=hist_lower_median(hist,window)
        mad=hist_mad(hist,window,med)
        medout[i]=med; madout[i]=mad
        threshold=float(med)+ROBUST_Z*MAD_SCALE*float(mad)
        if float(counts[i])>threshold:
            flags[i]=1
        hist[int(counts[i-window])]-=1
        hist[int(counts[i])]+=1
    return flags,medout,madout

@njit(cache=True)
def burst_events(counts,first_mid,last_mid,seen,flags,t,sec0):
    n=counts.size
    idx=np.empty(n,np.int64); side=np.empty(n,np.int8)
    burst_count=np.empty(n,np.int32); burst_disp=np.empty(n,np.int64)
    m=0
    for s in range(1,n):
        if flags[s]==0 or flags[s-1]!=0 or seen[s]==0:
            continue
        disp=int(last_mid[s]-first_mid[s])
        if disp==0: continue
        right_edge=(sec0+s+1)*1000
        j=np.searchsorted(t,right_edge,side="left")
        if j>=t.size: continue
        idx[m]=j
        side[m]=1 if disp>0 else -1
        burst_count[m]=counts[s]
        burst_disp[m]=abs(disp)
        m+=1
    return idx[:m],side[:m],burst_count[:m],burst_disp[:m]

@njit(cache=True)
def evaluate(event_idx,event_side,t,ask,bid):
    busy=-1;trades=0;busy_skips=0;spread_rejects=0;wins=0;longs=0;shorts=0
    gp=0.;gl=0.;net=0.;stop_count=0;hold_count=0;end_count=0
    days=np.empty(event_idx.size,np.int64);dn=0
    for z in range(event_idx.size):
        i=int(event_idx[z]); side=int(event_side[z])
        if i<=busy:
            busy_skips+=1;continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            spread_rejects+=1;continue
        trades+=1
        if side>0:longs+=1
        else:shorts+=1
        days[dn]=int(t[i]//DAY_MS);dn+=1
        entry=int(ask[i]) if side>0 else int(bid[i])
        stop=q_tick(int(bid[i])-STOP_RAW if side>0 else int(ask[i])+STOP_RAW)
        entry_sec=int(t[i])//1000
        raw=0.;reason=2;last=i
        for k in range(i+1,t.size):
            aa=int(ask[k]);bb=int(bid[k]);sec=int(t[k])//1000;last=k
            if side>0 and bb<=stop:
                raw=(bb-entry)/SCALE;reason=0;break
            if side<0 and aa>=stop:
                raw=(entry-aa)/SCALE;reason=0;break
            if sec-entry_sec>=MAX_HOLD_SECONDS:
                raw=((bb-entry) if side>0 else (entry-aa))/SCALE;reason=1;break
            fav=(bb-entry) if side>0 else (entry-aa)
            if fav>=TRAIL_ACTIVATION_RAW:
                ns=q_tick(bb-TRAIL_DISTANCE_RAW if side>0 else aa+TRAIL_DISTANCE_RAW)
                if (side>0 and ns>stop) or (side<0 and ns<stop):stop=ns
        else:
            aa=int(ask[last]);bb=int(bid[last])
            raw=((bb-entry) if side>0 else (entry-aa))/SCALE
        exit_deal=raw-0.01; trade_net=-0.01+exit_deal
        net+=trade_net
        if exit_deal>1e-12:wins+=1
        if raw>0:gp+=exit_deal
        else:gl+=exit_deal
        if reason==0:stop_count+=1
        elif reason==1:hold_count+=1
        else:end_count+=1
        busy=last
    distinct=0
    if dn>0:
        d=np.sort(days[:dn]);distinct=1
        for k in range(1,d.size):
            if d[k]!=d[k-1]:distinct+=1
    return trades,busy_skips,spread_rejects,distinct,longs,shorts,wins,gp,gl,net,stop_count,hold_count,end_count

def qs(x):
    if len(x)==0:return {}
    q=np.quantile(x,[.1,.25,.5,.75,.9,.99])
    return {"p10":float(q[0]),"p25":float(q[1]),"p50":float(q[2]),"p75":float(q[3]),"p90":float(q[4]),"p99":float(q[5])}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")
    df=pd.read_csv(args.source,compression="gzip",
                   usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709:raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology mismatch")
    ar=df.ask_raw.to_numpy(np.int64);br=df.bid_raw.to_numpy(np.int64)
    ea,eb=p75(t,ar,br)

    sec0=int(t[0]//1000)
    sec_last=int(t[-1]//1000)
    nsec=sec_last-sec0+1
    counts,first_mid,last_mid,seen=build_second_features(t,ar,br,sec0,nsec)
    flags,med,mad=robust_extreme_flags(counts,BASELINE_SECONDS)
    idx,side,burst_count,burst_disp=burst_events(counts,first_mid,last_mid,seen,flags,t,sec0)
    vals=evaluate(idx,side,t,ea,eb)
    trades,busy,sprej,days,longs,shorts,wins,gp,gl,net,stops,holds,ends=vals
    metrics={
      "signals":int(idx.size),"busy_skips":int(busy),"spread_rejects":int(sprej),
      "trades":int(trades),"distinct_days":int(days),"long":int(longs),"short":int(shorts),
      "official_wins":int(wins),"gross_profit":round(float(gp),2),
      "gross_loss":round(float(gl),2),"direct_net_usd":round(float(net),2),
      "exit_reasons":{"STOP":int(stops),"MAX_HOLD":int(holds),"END":int(ends)}
    }
    gate={"minimum_trades_50":metrics["trades"]>=50,
          "minimum_distinct_days_6":metrics["distinct_days"]>=6,
          "direct_net_min_minus_1":metrics["direct_net_usd"]>=-1.0}
    gate["screen_pass"]=all(gate.values())
    gate["strong_pass"]=gate["screen_pass"] and metrics["direct_net_usd"]>=0.0
    if gate["screen_pass"]:
        decision="ADVANCE_QRBM_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_QRBM_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        leader="C01_BURST_CONTINUATION"
    else:
        decision="RETIRE_QRBM_STAGE_A_NO_EXECUTABLE_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
        leader=None
    extreme_bins=int(np.sum(flags))
    diag={
      "completed_seconds":int(nsec),
      "extreme_seconds":extreme_bins,
      "burst_start_directional_signals":int(idx.size),
      "signals_per_day":float(idx.size/14.0),
      "revision_count_all_seconds_quantiles":qs(counts),
      "burst_revision_count_quantiles":qs(burst_count),
      "burst_abs_mid2_displacement_quantiles":qs(burst_disp),
      "baseline_median_at_signal_quantiles":qs(med[(idx*0)+0]) if False else {}
    }
    out={
      "schema":"delta-r037-qrbm-stage-a-screen-17av-v1",
      "status":"COMPLETE_STAGE_A_SCREEN",
      "unit":"R037_QUOTE_REVISION_BURST_MOMENTUM_STAGE_A_SCREEN",
      "family":"R037-QRBM-v1",
      "parent_checkpoint":"R037_OSSMR_STAGE_A_SCREEN_CHECKPOINT_17AU",
      "prereg_commit":PREREG_COMMIT,
      "source_sha256":source_sha,"stage_a_ticks":int(len(t)),
      "signal_surface":"NATIVE_DUKASCOPY_BBO",
      "execution_surface":"DUKAS_COINEXX_LIKE_P75",
      "burst_definition":{"bin_seconds":1,"baseline_seconds":BASELINE_SECONDS,
                          "threshold":"count > trailing median + 3*1.4826*MAD"},
      "numeric_retuning":False,"august_accessed":False,
      "diagnostics":diag,
      "configs":{"C01_BURST_CONTINUATION":{"metrics":metrics,"gate":gate}},
      "finding":{"leading_config":leader,"decision":decision,"next":nxt},
      "mql5_authorized":False
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"diagnostics":diag,"metrics":metrics,"gate":gate,
                      "finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":
    main()
