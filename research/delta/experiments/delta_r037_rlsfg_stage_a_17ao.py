"""DELTA R037 rolling liquidity sweep follow-through guard Stage-A screen - 17AO.

Reconstructible open-source logic:
- prior 20 completed bars define rolling liquidity high/low;
- sweep pierces the frozen level by >= 0.10 previous-bar ATR20;
- sweep bar closes back inside and rejection wick is >= 35% of range;
- only one episode is active at a time; a dual sweep is resolved by candle direction;
- next two completed closes must hold the reclaimed side;
- second close must extend >= 0.30 frozen ATR from sweep close;
- directional progress / cumulative close-to-close path must be >= 45%;
- first executable P75 tick after the second follow-through bar is the entry.

Two frozen signal timeframes are screened: M1 and M5. No parameter sweep,
rescue filters, August access, or MQL5.
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
STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000
UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="b13e98eccf79d4394a6e47f7c79a073ec0b66727"

LOOKBACK=20
SWEEP_ATR=0.10
REJECTION_FRAC=0.35
EXTENSION_ATR=0.30
PATH_EFF=0.45
MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30
PROFILES=(("C01_M1",60_000),("C02_M5",300_000))

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
    il=(tod>=ls)&(tod<le)
    iny=(tod>=ns)&(tod<ne)
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

def bars(t,price,tf_ms):
    bucket=t//tf_ms
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:],len(t)]
    return {
        "end_ms":((bucket[starts]+1)*tf_ms).astype(np.int64),
        "open":price[starts].astype(np.int64),
        "high":np.maximum.reduceat(price,starts).astype(np.int64),
        "low":np.minimum.reduceat(price,starts).astype(np.int64),
        "close":price[ends-1].astype(np.int64),
    }

def atr20(b):
    h=b["high"].astype(np.float64)
    l=b["low"].astype(np.float64)
    c=b["close"].astype(np.float64)
    prev=np.r_[np.nan,c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)))
    tr[0]=h[0]-l[0]
    return pd.Series(tr).rolling(LOOKBACK,min_periods=LOOKBACK).mean().to_numpy(np.float64)

def generate_proposals(t,ask,bid,tf_ms):
    b=bars(t,bid,tf_ms)
    E,O,H,L,C=(b[k] for k in ("end_ms","open","high","low","close"))
    ATR=atr20(b)
    out=[]
    stage={
        "bars":int(len(E)),
        "sweep_candidates":0,
        "reclaim_hold_2":0,
        "extension_pass":0,
        "path_efficiency_pass":0,
        "confirmations":0,
        "dual_sweeps":0,
    }
    next_free=LOOKBACK

    for j in range(LOOKBACK,len(E)-2):
        if j<next_free:
            continue
        if E[j+2]>=STAGE_A_END_MS:
            break

        atr_prev=float(ATR[j-1])
        if not np.isfinite(atr_prev) or atr_prev<=0:
            continue

        rh=int(np.max(H[j-LOOKBACK:j]))
        rl=int(np.min(L[j-LOOKBACK:j]))
        rng=float(H[j]-L[j])
        if rng<=0:
            continue

        upper_wick=float(H[j]-max(O[j],C[j]))/rng
        lower_wick=float(min(O[j],C[j])-L[j])/rng

        bear=(
            float(H[j])>=rh+SWEEP_ATR*atr_prev
            and int(C[j])<rh
            and upper_wick>=REJECTION_FRAC
        )
        bull=(
            float(L[j])<=rl-SWEEP_ATR*atr_prev
            and int(C[j])>rl
            and lower_wick>=REJECTION_FRAC
        )
        if not bear and not bull:
            continue

        if bear and bull:
            stage["dual_sweeps"]+=1
            if C[j]>O[j]:
                bear=False
            elif C[j]<O[j]:
                bull=False
            else:
                continue

        stage["sweep_candidates"]+=1
        side=1 if bull else -1
        level=rl if bull else rh
        frozen_atr=atr_prev
        sweep_close=int(C[j])

        # One active episode at a time through the two-bar follow-through decision.
        next_free=j+3

        c1=int(C[j+1]); c2=int(C[j+2])
        hold=(c1>level and c2>level) if side>0 else (c1<level and c2<level)
        if not hold:
            continue
        stage["reclaim_hold_2"]+=1

        progress=float(side*(c2-sweep_close))
        if progress<EXTENSION_ATR*frozen_atr:
            continue
        stage["extension_pass"]+=1

        path=float(abs(c1-sweep_close)+abs(c2-c1))
        efficiency=(progress/path) if path>0 else 0.0
        if efficiency<PATH_EFF:
            continue
        stage["path_efficiency_pass"]+=1
        stage["confirmations"]+=1

        edge=int(E[j+2])
        i=int(np.searchsorted(t,edge,side="left"))
        if i>=len(t) or int(t[i])>=STAGE_A_END_MS:
            out.append({"eligible":False,"reason":"NO_EXEC","edge_ms":edge})
            continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            out.append({"eligible":False,"reason":"SPREAD","edge_ms":edge})
            continue

        out.append({
            "eligible":True,
            "decision_index":i,
            "side":side,
            "day":int(t[i]//DAY_MS),
            "edge_ms":edge,
            "reference_level":int(level),
        })

    return out,stage

def simulate_trade(ev,t,ask,bid):
    i=int(ev["decision_index"])
    side=int(ev["side"])
    entry=int(ask[i]) if side>0 else int(bid[i])
    stop=q_tick(int(bid[i])-STOP_RAW if side>0 else int(ask[i])+STOP_RAW)
    entry_sec=int(t[i])//1000

    net=-0.01
    gp=0.0
    gl=-0.01
    official=0
    last=i
    reason="END"
    raw=0.0

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
    if exit_deal>1e-12:
        official=1
    if raw>0:
        gp+=exit_deal
    else:
        gl+=exit_deal

    return {"net":net,"gp":gp,"gl":gl,"official":official,"reason":reason,"exit_index":last}

def evaluate(proposals,t,ask,bid):
    eligible=[x for x in proposals if x.get("eligible")]
    rows=[]; accepted=[]; busy=-1
    for ev in eligible:
        i=int(ev["decision_index"])
        if i<=busy:
            continue
        tr=simulate_trade(ev,t,ask,bid)
        rows.append(tr); accepted.append(ev); busy=int(tr["exit_index"])

    rej={}
    for ev in proposals:
        if not ev.get("eligible"):
            r=ev.get("reason","UNKNOWN")
            rej[r]=rej.get(r,0)+1

    return {
        "proposals":int(len(proposals)),
        "eligible":int(len(eligible)),
        "trades":int(len(rows)),
        "distinct_days":int(len({x["day"] for x in accepted})),
        "long":int(sum(x["side"]>0 for x in accepted)),
        "short":int(sum(x["side"]<0 for x in accepted)),
        "rejections":rej,
        "official_wins":int(sum(x["official"] for x in rows)),
        "gross_profit":round(float(sum(x["gp"] for x in rows)),2),
        "gross_loss":round(float(sum(x["gl"] for x in rows)),2),
        "direct_net_usd":round(float(sum(x["net"] for x in rows)),2),
        "exit_reasons":{name:int(sum(x["reason"]==name for x in rows)) for name in ("STOP","MAX_HOLD","END")},
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
    if len(t)!=4_205_709:
        raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]):
        raise SystemExit("Stage-A chronology mismatch")

    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))

    configs={}
    ordinary=[]
    strong=[]
    for name,tf_ms in PROFILES:
        props,stage=generate_proposals(t,ask,bid,tf_ms)
        metrics=evaluate(props,t,ask,bid)
        gate={
            "minimum_trades_6":metrics["trades"]>=6,
            "minimum_distinct_days_4":metrics["distinct_days"]>=4,
            "direct_net_min_minus_1":metrics["direct_net_usd"]>=-1.0,
        }
        gate["screen_pass"]=all(gate.values())
        gate["strong_pass"]=gate["screen_pass"] and metrics["direct_net_usd"]>=0.0
        configs[name]={"timeframe_seconds":int(tf_ms//1000),"stage_counts":stage,"metrics":metrics,"gate":gate}
        if gate["screen_pass"]: ordinary.append(name)
        if gate["strong_pass"]: strong.append(name)

    def rk(name):
        m=configs[name]["metrics"]
        return (m["direct_net_usd"],m["official_wins"],m["trades"])
    ordinary.sort(key=rk,reverse=True)
    strong.sort(key=rk,reverse=True)

    if strong:
        leader=strong[0]
        decision="ADVANCE_STRONG_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_RLSFG_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader=ordinary[0]
        decision="ADVANCE_ORDINARY_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_RLSFG_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader=None
        decision="RETIRE_RLSFG_STAGE_A_NO_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    out={
        "schema":"delta-r037-rlsfg-stage-a-screen-17ao-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_ROLLING_LIQUIDITY_SWEEP_FOLLOW_THROUGH_GUARD_STAGE_A_SCREEN",
        "family":"R037-RLSFG-v1",
        "parent_checkpoint":"R037_VSBR_STAGE_A_SCREEN_CHECKPOINT_17AN",
        "prereg_commit":PREREG_COMMIT,
        "source_sha256":source_sha,
        "stage_a_ticks":int(len(t)),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning":False,
        "august_accessed":False,
        "configs":configs,
        "ranking":ordinary,
        "finding":{
            "leading_config":leader,
            "ordinary_survivors":ordinary,
            "strong_survivors":strong,
            "decision":decision,
            "next":nxt,
        },
        "mql5_authorized":False,
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"finding":out["finding"],"metrics":{k:v["metrics"] for k,v in configs.items()}},separators=(",",":")))

if __name__=="__main__":
    main()
