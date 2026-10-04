"""DELTA R037 intrinsic-time directional-change Stage-A screen - 17AQ.

Public-source reconstruction:
- MetaQuotes/MQL5 "Intrinsic Time: From the Directional-Change Scaling Laws to
  the source article's online directional-change operator.
- Fixed delta = 0.02%, the finest threshold in the article's verified
  0.02%-2% real-tick scaling-law grid.
- C01 enters in the newly confirmed direction to test the overshoot premise.
- C02 enters the opposite direction to test the source article's first-unit
  contrarian premise under DELTA's one-position lifecycle.

No threshold sweep, cascade, rescue filters, August access, or MQL5 build.
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
PREREG_COMMIT="adccb54efa49aa4f91b9701ec5c393d51be25fa4"

DELTA=0.0002
MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30
PROFILES=(("C01_OVERSHOOT_CONTINUATION",1),("C02_ALPHA_FIRST_UNIT_CONTRARIAN",-1))

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def atomic_write_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",
            prefix=f".{path.name}.",suffix=".tmp",dir=path.parent,delete=False) as f:
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

def directional_change_events(t,ask,bid):
    mid2=ask.astype(np.int64)+bid.astype(np.int64)
    if len(mid2)==0:
        return [],{"events":0,"up":0,"down":0}
    # Source algorithm starts in up mode and tracks the running high.
    mode=1
    extreme=int(mid2[0])
    out=[]
    up=0; down=0
    for i in range(1,len(mid2)):
        px=int(mid2[i])
        if mode==1:
            if px>extreme:
                extreme=px
            elif (px-extreme)/extreme <= -DELTA:
                out.append({"decision_index":i,"dc_side":-1,"day":int(t[i]//DAY_MS)})
                down+=1
                mode=-1
                extreme=px
        else:
            if px<extreme:
                extreme=px
            elif (px-extreme)/extreme >= DELTA:
                out.append({"decision_index":i,"dc_side":1,"day":int(t[i]//DAY_MS)})
                up+=1
                mode=1
                extreme=px
    return out,{"events":len(out),"up":up,"down":down}

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

def evaluate(events,polarity,t,ask,bid):
    rows=[]; accepted=[]; busy=-1; spread_rejects=0; busy_skips=0
    for ev in events:
        i=int(ev["decision_index"])
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            spread_rejects+=1; continue
        if i<=busy:
            busy_skips+=1; continue
        side=int(ev["dc_side"])*polarity
        tr=simulate_trade(i,side,t,ask,bid)
        rows.append(tr); accepted.append((ev,side)); busy=int(tr["exit_index"])
    return {
        "events":int(len(events)),
        "spread_rejects":spread_rejects,
        "busy_skips":busy_skips,
        "trades":len(rows),
        "distinct_days":len({ev["day"] for ev,_ in accepted}),
        "long":sum(side>0 for _,side in accepted),
        "short":sum(side<0 for _,side in accepted),
        "official_wins":sum(x["official"] for x in rows),
        "gross_profit":round(float(sum(x["gp"] for x in rows)),2),
        "gross_loss":round(float(sum(x["gl"] for x in rows)),2),
        "direct_net_usd":round(float(sum(x["net"] for x in rows)),2),
        "exit_reasons":{name:sum(x["reason"]==name for x in rows) for name in ("STOP","MAX_HOLD","END")}
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

    events,stage=directional_change_events(t,ask,bid)
    configs={}; ordinary=[]; strong=[]
    for name,polarity in PROFILES:
        metrics=evaluate(events,polarity,t,ask,bid)
        gate={
            "minimum_trades_6":metrics["trades"]>=6,
            "minimum_distinct_days_4":metrics["distinct_days"]>=4,
            "direct_net_min_minus_1":metrics["direct_net_usd"]>=-1.0,
        }
        gate["screen_pass"]=all(gate.values())
        gate["strong_pass"]=gate["screen_pass"] and metrics["direct_net_usd"]>=0.0
        configs[name]={"polarity":polarity,"metrics":metrics,"gate":gate}
        if gate["screen_pass"]: ordinary.append(name)
        if gate["strong_pass"]: strong.append(name)
    def rk(name):
        m=configs[name]["metrics"]; return (m["direct_net_usd"],m["official_wins"],m["trades"])
    ordinary.sort(key=rk,reverse=True); strong.sort(key=rk,reverse=True)
    if strong:
        leader=strong[0]; decision="ADVANCE_STRONG_ITDC_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_ITDC_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader=ordinary[0]; decision="ADVANCE_ORDINARY_ITDC_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_ITDC_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader=None; decision="RETIRE_ITDC_STAGE_A_NO_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
    out={
        "schema":"delta-r037-itdc-stage-a-screen-17aq-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_INTRINSIC_TIME_DIRECTIONAL_CHANGE_STAGE_A_SCREEN",
        "family":"R037-ITDC-v1",
        "parent_checkpoint":"R037_TCFH_STAGE_A_SCREEN_CHECKPOINT_17AP",
        "prereg_commit":PREREG_COMMIT,
        "source_sha256":source_sha,
        "stage_a_ticks":len(t),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "delta_fraction":DELTA,
        "stage_counts":stage,
        "numeric_retuning":False,
        "august_accessed":False,
        "configs":configs,
        "finding":{"leading_config":leader,"ordinary_survivors":ordinary,"strong_survivors":strong,"decision":decision,"next":nxt},
        "mql5_authorized":False
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"stage_counts":stage,"finding":out["finding"],"metrics":{k:v["metrics"] for k,v in configs.items()}},separators=(",",":")))

if __name__=="__main__":
    main()
