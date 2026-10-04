"""DELTA R037 Directional-Change / Overshoot Stage-A screen — 17AW.

Single preregistered source family:
- native Dukascopy BBO midquote is processed tick-by-tick in intrinsic time;
- one fixed directional-change threshold: 0.05% (5 bps), source-backed and
  preregistered before compute;
- a directional-change confirmation occurs causally when price reverses by the
  fixed threshold from the running local extreme;
- candidate direction is the new directional-change direction, seeking the
  source-documented overshoot continuation;
- executable entry is the first strictly subsequent P75 tick.

No threshold/profile sweep, no session/side rescue, no QIM/OFI/burst overlay,
no exit retuning, no August access, and no MQL5 translation.
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
PREREG_COMMIT="fdc3ec8d81d9183ebd9f8985e513ac128797ec99"

# 0.05% = 1 / 2000. Use integer comparisons to avoid float threshold drift.
DC_DEN=2000

MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30

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
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name,path)
        tmp_name=None
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
    il=(tod>=ls)&(tod<le)
    iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75(t,ask_raw,bid_raw):
    s=session_code(t)
    spread=P75_POINTS[s]*TICK_RAW
    mid2=ask_raw.astype(np.int64)+bid_raw.astype(np.int64)
    bid=((mid2-spread+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    return (bid+spread).astype(np.int64),bid.astype(np.int64)

@njit(cache=True)
def q_tick(x):
    return ((int(x)+TICK_RAW//2)//TICK_RAW)*TICK_RAW

@njit(cache=True)
def dc_events(t,ask_native,bid_native):
    n=t.size
    idx=np.empty(n,np.int64)
    side=np.empty(n,np.int8)
    extreme_move=np.empty(n,np.int64)
    m=0
    if n<3:
        return idx[:0],side[:0],extreme_move[:0]

    mid0=int(ask_native[0])+int(bid_native[0])
    hi=mid0
    lo=mid0
    state=0  # 0 unknown, +1 upward mode, -1 downward mode

    for i in range(1,n-1):
        px=int(ask_native[i])+int(bid_native[i])

        if state==0:
            if px>hi:
                hi=px
            if px<lo:
                lo=px

            # Upward directional-change confirmation from running low.
            if (px-lo)*DC_DEN>=lo:
                state=1
                hi=px
                move=px-lo
                idx[m]=i+1
                side[m]=1
                extreme_move[m]=move
                m+=1
            # Downward directional-change confirmation from running high.
            elif (hi-px)*DC_DEN>=hi:
                state=-1
                lo=px
                move=hi-px
                idx[m]=i+1
                side[m]=-1
                extreme_move[m]=move
                m+=1
            continue

        if state>0:
            if px>hi:
                hi=px
            # Reverse downward by >=0.05% from the running high.
            elif (hi-px)*DC_DEN>=hi:
                move=hi-px
                state=-1
                lo=px
                idx[m]=i+1
                side[m]=-1
                extreme_move[m]=move
                m+=1
        else:
            if px<lo:
                lo=px
            # Reverse upward by >=0.05% from the running low.
            elif (px-lo)*DC_DEN>=lo:
                move=px-lo
                state=1
                hi=px
                idx[m]=i+1
                side[m]=1
                extreme_move[m]=move
                m+=1

    return idx[:m],side[:m],extreme_move[:m]

@njit(cache=True)
def evaluate(event_idx,event_side,t,ask,bid):
    busy=-1
    trades=0
    busy_skips=0
    spread_rejects=0
    wins=0
    longs=0
    shorts=0
    gp=0.
    gl=0.
    net=0.
    stop_count=0
    hold_count=0
    end_count=0
    days=np.empty(event_idx.size,np.int64)
    dn=0

    for z in range(event_idx.size):
        i=int(event_idx[z])
        side=int(event_side[z])
        if i<=busy:
            busy_skips+=1
            continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            spread_rejects+=1
            continue

        trades+=1
        if side>0: longs+=1
        else: shorts+=1
        days[dn]=int(t[i]//DAY_MS)
        dn+=1

        entry=int(ask[i]) if side>0 else int(bid[i])
        stop=q_tick(int(bid[i])-STOP_RAW if side>0 else int(ask[i])+STOP_RAW)
        entry_sec=int(t[i])//1000
        raw=0.
        reason=2
        last=i

        for k in range(i+1,t.size):
            aa=int(ask[k])
            bb=int(bid[k])
            sec=int(t[k])//1000
            last=k

            if side>0 and bb<=stop:
                raw=(bb-entry)/SCALE
                reason=0
                break
            if side<0 and aa>=stop:
                raw=(entry-aa)/SCALE
                reason=0
                break
            if sec-entry_sec>=MAX_HOLD_SECONDS:
                raw=((bb-entry) if side>0 else (entry-aa))/SCALE
                reason=1
                break

            fav=(bb-entry) if side>0 else (entry-aa)
            if fav>=TRAIL_ACTIVATION_RAW:
                ns=q_tick(bb-TRAIL_DISTANCE_RAW if side>0 else aa+TRAIL_DISTANCE_RAW)
                if (side>0 and ns>stop) or (side<0 and ns<stop):
                    stop=ns
        else:
            aa=int(ask[last])
            bb=int(bid[last])
            raw=((bb-entry) if side>0 else (entry-aa))/SCALE

        exit_deal=raw-0.01
        trade_net=-0.01+exit_deal
        net+=trade_net

        if exit_deal>1e-12:
            wins+=1
        if raw>0:
            gp+=exit_deal
        else:
            gl+=exit_deal

        if reason==0: stop_count+=1
        elif reason==1: hold_count+=1
        else: end_count+=1
        busy=last

    distinct=0
    if dn>0:
        d=np.sort(days[:dn])
        distinct=1
        for k in range(1,d.size):
            if d[k]!=d[k-1]:
                distinct+=1

    return trades,busy_skips,spread_rejects,distinct,longs,shorts,wins,gp,gl,net,stop_count,hold_count,end_count

def qs(x):
    if len(x)==0:
        return {}
    q=np.quantile(x,[.1,.25,.5,.75,.9,.99])
    return {"p10":float(q[0]),"p25":float(q[1]),"p50":float(q[2]),
            "p75":float(q[3]),"p90":float(q[4]),"p99":float(q[5])}

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
    if len(t)!=4_205_709:
        raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]):
        raise SystemExit("Stage-A chronology mismatch")

    ar=df.ask_raw.to_numpy(np.int64)
    br=df.bid_raw.to_numpy(np.int64)
    ea,eb=p75(t,ar,br)

    idx,side,move=dc_events(t,ar,br)
    vals=evaluate(idx,side,t,ea,eb)
    trades,busy,sprej,days,longs,shorts,wins,gp,gl,net,stops,holds,ends=vals

    metrics={
      "signals":int(idx.size),
      "busy_skips":int(busy),
      "spread_rejects":int(sprej),
      "trades":int(trades),
      "distinct_days":int(days),
      "long":int(longs),
      "short":int(shorts),
      "official_wins":int(wins),
      "gross_profit":round(float(gp),2),
      "gross_loss":round(float(gl),2),
      "direct_net_usd":round(float(net),2),
      "exit_reasons":{"STOP":int(stops),"MAX_HOLD":int(holds),"END":int(ends)}
    }
    gate={
      "minimum_trades_50":metrics["trades"]>=50,
      "minimum_distinct_days_6":metrics["distinct_days"]>=6,
      "direct_net_min_minus_1":metrics["direct_net_usd"]>=-1.0
    }
    gate["screen_pass"]=all(gate.values())
    gate["strong_pass"]=gate["screen_pass"] and metrics["direct_net_usd"]>=0.0

    if gate["screen_pass"]:
        decision="ADVANCE_DCOS_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_DCOS_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        leader="C01_DC_005_OVERSHOOT_CONTINUATION"
    else:
        decision="RETIRE_DCOS_STAGE_A_NO_EXECUTABLE_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
        leader=None

    event_t=t[idx] if idx.size else np.empty(0,np.int64)
    gaps=np.diff(event_t).astype(np.float64)/1000.0 if event_t.size>1 else np.empty(0)
    diag={
      "directional_change_signals":int(idx.size),
      "signals_per_day":float(idx.size/14.0),
      "threshold_fraction":0.0005,
      "confirmation_move_mid2_quantiles":qs(move),
      "inter_event_seconds_quantiles":qs(gaps)
    }

    out={
      "schema":"delta-r037-dcos-stage-a-screen-17aw-v1",
      "status":"COMPLETE_STAGE_A_SCREEN",
      "unit":"R037_DIRECTIONAL_CHANGE_OVERSHOOT_STAGE_A_SCREEN",
      "family":"R037-DCOS-v1",
      "parent_checkpoint":"R037_QRBM_STAGE_A_SCREEN_CHECKPOINT_17AV",
      "prereg_commit":PREREG_COMMIT,
      "source_sha256":source_sha,
      "stage_a_ticks":int(len(t)),
      "signal_surface":"NATIVE_DUKASCOPY_BBO",
      "execution_surface":"DUKAS_COINEXX_LIKE_P75",
      "event_definition":{
        "directional_change_threshold_fraction":0.0005,
        "threshold_pct":0.05,
        "direction":"new directional-change trend / overshoot continuation",
        "entry":"first strictly subsequent tick after causal confirmation"
      },
      "numeric_retuning":False,
      "august_accessed":False,
      "diagnostics":diag,
      "configs":{"C01_DC_005_OVERSHOOT_CONTINUATION":{"metrics":metrics,"gate":gate}},
      "finding":{"leading_config":leader,"decision":decision,"next":nxt},
      "mql5_authorized":False
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"diagnostics":diag,"metrics":metrics,"gate":gate,
                      "finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":
    main()
