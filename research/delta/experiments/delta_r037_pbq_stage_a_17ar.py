"""DELTA R037 Part-8/Part-9 microtrend pullback-quality Stage-A screen - 17AR.

Source-grounded reconstruction:
- MetaQuotes/MQL5 Market Microstructure Part 8 fixed M1 microtrend score:
  EMA 5/8/13, ATR14, 5-bar slope, tick-volume boost, contradiction penalty,
  fixed strong binary threshold +/-0.70, persistent direction over 3 bars.
- Part 9 pullback quality:
  20-bar swing anchor, EMA5-vs-EMA13 alignment / ATR14 >= 0.05,
  PBQ_STRONG < 0.236 and PBQ_HEALTHY 0.236..0.382.
- Part 9 explicitly says entry is strategy-specific and the composite score should
  be treated as a quality/sizing scalar rather than invented as a new binary gate.

Profiles are preregistered source conditions only. No parameter sweep, regime rescue,
session/side filter, exit tuning, August access, or MQL5 build.
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

DAY_MS=86_400_000
TICK_RAW=10
SCALE=1000
TF_MS=60_000
STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000
UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="50970048c0c6bcc448f9f95b8c02daaff26bd581"

EMA_FAST=5
EMA_MED=8
EMA_SLOW=13
ATR_PERIOD=14
SLOPE_LOOKBACK=5
VOL_WINDOW=20
THRESH_HIGH=0.70
PERSIST_N=3
SWING_BARS=20
ALIGN_MIN=0.05
FIB_236=0.236
FIB_382=0.382
H1_PROXY_BARS=60
AUTOCORR_WIN=20

MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30

PROFILES=(
    "C01_BINARY_HEALTHY",
    "C02_PERSISTENT_HEALTHY",
    "C03_PERSISTENT_SHALLOW",
)

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def atomic_write_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temp_name=None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",encoding="utf-8",newline="\n",
            prefix=f".{path.name}.",suffix=".tmp",dir=path.parent,delete=False
        ) as f:
            temp_name=f.name
            json.dump(payload,f,indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name,path)
        temp_name=None
    finally:
        if temp_name is not None:
            try: os.unlink(temp_name)
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
    s=session_code(t)
    spread=P75_POINTS[s]*TICK_RAW
    mid2=ask_raw.astype(np.int64)+bid_raw.astype(np.int64)
    bid=((mid2-spread+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    ask=bid+spread
    return ask.astype(np.int64),bid.astype(np.int64)

def q_tick(x:int)->int:
    return ((int(x)+TICK_RAW//2)//TICK_RAW)*TICK_RAW

def bars(t,price):
    bucket=t//TF_MS
    st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    en=np.r_[st[1:],len(t)]
    return {
        "end_ms":((bucket[st]+1)*TF_MS).astype(np.int64),
        "open":price[st].astype(np.float64),
        "high":np.maximum.reduceat(price,st).astype(np.float64),
        "low":np.minimum.reduceat(price,st).astype(np.float64),
        "close":price[en-1].astype(np.float64),
        "tick_volume":(en-st).astype(np.float64),
    }

def ema(arr,period):
    out=np.full(len(arr),np.nan,dtype=np.float64)
    if len(arr)<period:
        return out
    out[period-1]=float(np.mean(arr[:period]))
    alpha=2.0/(period+1.0)
    for i in range(period,len(arr)):
        out[i]=alpha*arr[i]+(1.0-alpha)*out[i-1]
    return out

def atr_wilder(h,l,c,period=14):
    tr=np.asarray(h-l,dtype=np.float64)
    if len(tr)>1:
        prev=c[:-1]
        tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-prev),np.abs(l[1:]-prev)))
    out=np.full(len(tr),np.nan,dtype=np.float64)
    if len(tr)<period:
        return out
    out[period-1]=float(np.mean(tr[:period]))
    for i in range(period,len(tr)):
        out[i]=(out[i-1]*(period-1)+tr[i])/period
    return out

def lag1_autocorr(close,j,window=20):
    if j < window:
        return 0.0
    # Match Part 9: 20 returns -> 19 adjacent lag pairs.
    x=close[j-window:j+1]
    ret=np.diff(x)/x[:-1]
    ret=np.where(np.abs(ret)>0.05,0.0,ret)
    if len(ret)<3:
        return 0.0
    a=ret[1:]; b=ret[:-1]
    da=a-a.mean(); db=b-b.mean()
    den=float(np.sqrt(np.sum(da*da)*np.sum(db*db)))
    if den<=1e-15:
        return 0.0
    return float(np.clip(np.sum(da*db)/den,-1.0,1.0))

def build_features(b):
    h,l,c,v=(b[k] for k in ("high","low","close","tick_volume"))
    ef=ema(c,EMA_FAST); em=ema(c,EMA_MED); es=ema(c,EMA_SLOW)
    atr=atr_wilder(h,l,c,ATR_PERIOD)
    n=len(c)
    strength=np.zeros(n,dtype=np.float64)
    binary=np.zeros(n,dtype=np.int8)
    persistent=np.zeros(n,dtype=np.int8)
    quality=np.zeros(n,dtype=np.int8)
    depth=np.full(n,-1.0,dtype=np.float64)
    h1pos=np.full(n,0.5,dtype=np.float64)
    ac=np.zeros(n,dtype=np.float64)
    composite=np.zeros(n,dtype=np.float64)

    start=max(H1_PROXY_BARS-1,VOL_WINDOW-1,SWING_BARS-1,ATR_PERIOD-1,EMA_SLOW-1+SLOPE_LOOKBACK,AUTOCORR_WIN)
    counts={"bars":n,"usable_bars":0,"binary_bars":0,"healthy_bars":0,"shallow_bars":0,"persistent_binary_bars":0}
    for j in range(start,n):
        if not (np.isfinite(ef[j]) and np.isfinite(em[j]) and np.isfinite(es[j]) and np.isfinite(atr[j]) and atr[j]>0):
            continue
        counts["usable_bars"]+=1
        align=(0.33 if ef[j]>em[j] else -0.33)+(0.33 if em[j]>es[j] else -0.33)+(0.34 if ef[j]>es[j] else -0.34)
        price_pos=(np.tanh((c[j]-ef[j])/atr[j])*0.40
                  +np.tanh((c[j]-em[j])/atr[j])*0.30
                  +np.tanh((c[j]-es[j])/atr[j])*0.30)
        sf=ef[j]-ef[j-SLOPE_LOOKBACK]; sm=em[j]-em[j-SLOPE_LOOKBACK]; ss=es[j]-es[j-SLOPE_LOOKBACK]
        slope=0.0
        if sf>0 and sm>0 and ss>0:
            slope=min(1.0,(sf+sm+ss)/(3.0*atr[j]))
        elif sf<0 and sm<0 and ss<0:
            slope=max(-1.0,(sf+sm+ss)/(3.0*atr[j]))
        avg_vol=float(np.mean(v[j-VOL_WINDOW+1:j+1]))
        ratio=(v[j]/avg_vol) if avg_vol>0 else 0.5
        vol_boost=min(1.5,max(0.5,0.5+ratio))
        s=(align*0.4+price_pos*0.4+slope*0.2)*vol_boost
        if align>0 and c[j]<ef[j]:
            s*=0.3
        elif align<0 and c[j]>ef[j]:
            s*=0.3
        s=float(np.clip(s,-1.0,1.0))
        strength[j]=s
        if s>THRESH_HIGH:
            binary[j]=1
        elif s<-THRESH_HIGH:
            binary[j]=-1
        if binary[j]!=0:
            counts["binary_bars"]+=1

        align_norm=(ef[j]-es[j])/atr[j]
        if abs(align_norm)>=ALIGN_MIN:
            sh=float(np.max(h[j-SWING_BARS+1:j+1]))
            sl=float(np.min(l[j-SWING_BARS+1:j+1]))
            rg=sh-sl
            if rg>0:
                d=(sh-c[j])/rg if align_norm>0 else (c[j]-sl)/rg
                d=max(0.0,float(d))
                depth[j]=d
                if d<FIB_236:
                    quality[j]=1
                    counts["shallow_bars"]+=1
                elif d<FIB_382:
                    quality[j]=2
                    counts["healthy_bars"]+=1
                    counts["shallow_bars"]+=1
                elif d<0.618:
                    quality[j]=3
                elif d<=1.0:
                    quality[j]=4
                else:
                    quality[j]=5

        if j>=PERSIST_N-1 and binary[j]!=0:
            w=binary[j-PERSIST_N+1:j+1]
            if np.all(w==binary[j]):
                persistent[j]=binary[j]
                counts["persistent_binary_bars"]+=1

        rh=float(np.max(h[j-H1_PROXY_BARS+1:j+1]))
        rl=float(np.min(l[j-H1_PROXY_BARS+1:j+1]))
        h1pos[j]=0.5 if rh<=rl else float(np.clip((c[j]-rl)/(rh-rl),0.0,1.0))
        ac[j]=lag1_autocorr(c,j,AUTOCORR_WIN)
        fibq=0.0 if depth[j]<0 or depth[j]>1 else float(np.clip(1.0-depth[j],0.0,1.0))
        composite[j]=float(np.clip(0.50*fibq+0.30*h1pos[j]+0.20*max(0.0,ac[j]),0.0,1.0))
    return {"strength":strength,"binary":binary,"persistent":persistent,"quality":quality,"depth":depth,"h1pos":h1pos,"autocorr":ac,"composite":composite},counts

def simulate_trade(i,side,t,ask,bid):
    entry=int(ask[i]) if side>0 else int(bid[i])
    stop=q_tick(int(bid[i])-STOP_RAW if side>0 else int(ask[i])+STOP_RAW)
    entry_sec=int(t[i])//1000
    net=-0.01; gp=0.0; gl=-0.01; official=0
    last=i; reason="END"; raw=0.0
    for k in range(i+1,len(t)):
        aa=int(ask[k]); bb=int(bid[k]); sec=int(t[k])//1000
        last=k
        if side>0 and bb<=stop:
            raw=(bb-entry)/SCALE; reason="STOP"; break
        if side<0 and aa>=stop:
            raw=(entry-aa)/SCALE; reason="STOP"; break
        if sec-entry_sec>=MAX_HOLD_SECONDS:
            raw=((bb-entry) if side>0 else (entry-aa))/SCALE
            reason="MAX_HOLD"; break
        favorable=(bb-entry) if side>0 else (entry-aa)
        if favorable>=TRAIL_ACTIVATION_RAW:
            ns=q_tick(bb-TRAIL_DISTANCE_RAW if side>0 else aa+TRAIL_DISTANCE_RAW)
            if (side>0 and ns>stop) or (side<0 and ns<stop):
                stop=ns
    else:
        aa=int(ask[last]); bb=int(bid[last])
        raw=((bb-entry) if side>0 else (entry-aa))/SCALE
    exit_deal=raw-0.01
    net+=exit_deal
    if exit_deal>1e-12: official=1
    if raw>0: gp+=exit_deal
    else: gl+=exit_deal
    return {"net":net,"gp":gp,"gl":gl,"official":official,"reason":reason,"exit_index":last}

def proposals_for_profile(name,b,feat,t,ask,bid):
    E=b["end_ms"]; binary=feat["binary"]; persistent=feat["persistent"]; quality=feat["quality"]
    out=[]; stage={"condition_bars":0,"no_exec":0,"spread_rejects":0,"eligible":0}
    for j in range(len(E)):
        if E[j]>=STAGE_A_END_MS:
            break
        side=int(binary[j])
        if side==0:
            continue
        q=int(quality[j])
        ok=False
        if name=="C01_BINARY_HEALTHY":
            ok=(q==2)
        elif name=="C02_PERSISTENT_HEALTHY":
            ok=(q==2 and int(persistent[j])==side)
        elif name=="C03_PERSISTENT_SHALLOW":
            ok=(q in (1,2) and int(persistent[j])==side)
        if not ok:
            continue
        stage["condition_bars"]+=1
        edge=int(E[j])
        i=int(np.searchsorted(t,edge,side="left"))
        if i>=len(t) or int(t[i])>=STAGE_A_END_MS:
            stage["no_exec"]+=1; continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            stage["spread_rejects"]+=1; continue
        stage["eligible"]+=1
        out.append({"decision_index":i,"side":side,"day":int(t[i]//DAY_MS),"bar_index":j})
    return out,stage

def evaluate(props,t,ask,bid):
    rows=[]; accepted=[]; busy=-1; busy_skips=0
    for ev in props:
        i=int(ev["decision_index"])
        if i<=busy:
            busy_skips+=1; continue
        tr=simulate_trade(i,int(ev["side"]),t,ask,bid)
        rows.append(tr); accepted.append(ev); busy=int(tr["exit_index"])
    return {
        "proposals":len(props),"busy_skips":busy_skips,"trades":len(rows),
        "distinct_days":len({x["day"] for x in accepted}),
        "long":sum(x["side"]>0 for x in accepted),"short":sum(x["side"]<0 for x in accepted),
        "official_wins":sum(x["official"] for x in rows),
        "gross_profit":round(float(sum(x["gp"] for x in rows)),2),
        "gross_loss":round(float(sum(x["gl"] for x in rows)),2),
        "direct_net_usd":round(float(sum(x["net"] for x in rows)),2),
        "exit_reasons":{name:sum(x["reason"]==name for x in rows) for name in ("STOP","MAX_HOLD","END")},
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")
    df=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709: raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]): raise SystemExit("Stage-A chronology mismatch")
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    b=bars(t,bid)
    feat,feature_counts=build_features(b)

    configs={}; ordinary=[]; strong=[]
    for name in PROFILES:
        props,stage=proposals_for_profile(name,b,feat,t,ask,bid)
        metrics=evaluate(props,t,ask,bid)
        gate={
            "minimum_trades_6":metrics["trades"]>=6,
            "minimum_distinct_days_4":metrics["distinct_days"]>=4,
            "direct_net_min_minus_1":metrics["direct_net_usd"]>=-1.0,
        }
        gate["screen_pass"]=all(gate.values())
        gate["strong_pass"]=gate["screen_pass"] and metrics["direct_net_usd"]>=0.0
        configs[name]={"stage_counts":stage,"metrics":metrics,"gate":gate}
        if gate["screen_pass"]: ordinary.append(name)
        if gate["strong_pass"]: strong.append(name)

    def rk(name):
        m=configs[name]["metrics"]
        return (m["direct_net_usd"],m["official_wins"],m["trades"])
    ordinary.sort(key=rk,reverse=True); strong.sort(key=rk,reverse=True)
    if strong:
        leader=strong[0]; decision="ADVANCE_STRONG_PBQ_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_PBQ_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader=ordinary[0]; decision="ADVANCE_ORDINARY_PBQ_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_PBQ_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader=None; decision="RETIRE_PBQ_STAGE_A_NO_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    out={
        "schema":"delta-r037-pbq-stage-a-screen-17ar-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_MICROTREND_PULLBACK_QUALITY_STAGE_A_SCREEN",
        "family":"R037-PBQ-v1",
        "parent_checkpoint":"R037_ITDC_STAGE_A_SCREEN_CHECKPOINT_17AQ",
        "prereg_commit":PREREG_COMMIT,
        "source_sha256":source_sha,
        "stage_a_ticks":len(t),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "signal_timeframe_seconds":60,
        "feature_counts":feature_counts,
        "numeric_retuning":False,
        "composite_used_as_binary_gate":False,
        "august_accessed":False,
        "configs":configs,
        "finding":{"leading_config":leader,"ordinary_survivors":ordinary,"strong_survivors":strong,"decision":decision,"next":nxt},
        "mql5_authorized":False,
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"feature_counts":feature_counts,"finding":out["finding"],"metrics":{k:v["metrics"] for k,v in configs.items()}},separators=(",",":")))

if __name__=="__main__":
    main()
