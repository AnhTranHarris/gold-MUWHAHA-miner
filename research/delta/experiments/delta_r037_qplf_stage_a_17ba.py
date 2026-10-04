"""DELTA R037 quote-propagation leader/follower Stage-A screen — Checkpoint 17BA.

Single preregistered source family:
- work on native Dukascopy BBO price-changing events;
- ignore volume-only revisions for event adjacency;
- bullish event: ask-up-only leader, then the next BBO price-changing event is
  bid-up-only follower;
- bearish event: bid-down-only leader, then the next BBO price-changing event is
  ask-down-only follower;
- follower spread must be <= spread immediately before the leader;
- enter on the first strictly subsequent raw tick after the follower;
- frozen P75 execution and 30-second lifecycle.

No threshold/window sweep, no session/side rescue, no QIM/OFI overlay,
no exit retuning, no August access, no MQL5.
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

DAY_MS=86_400_000
TICK_RAW=10
SCALE=1000
STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000
UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="ee771014b206b3e1a9f77777bfaf46b662168461"

MAX_SPREAD_RAW=250
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30

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
        with tempfile.NamedTemporaryFile(
            mode="w",encoding="utf-8",newline="\n",
            prefix=f".{path.name}.",suffix=".tmp",
            dir=path.parent,delete=False
        ) as f:
            tmp_name=f.name
            json.dump(payload,f,indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name,path)
        tmp_name=None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass

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
def detect_events(t,ask,bid):
    n=t.size
    pc=np.empty(n,np.int64)
    m=0
    for i in range(1,n):
        if ask[i]!=ask[i-1] or bid[i]!=bid[i-1]:
            pc[m]=i
            m+=1
    pc=pc[:m]

    idx=np.empty(m,np.int64)
    side=np.empty(m,np.int8)
    latency=np.empty(m,np.int64)
    pre_spread=np.empty(m,np.int64)
    peak_spread=np.empty(m,np.int64)
    post_spread=np.empty(m,np.int64)
    lead_move=np.empty(m,np.int64)
    follow_move=np.empty(m,np.int64)

    bull_leaders=0
    bear_leaders=0
    completed=0
    out=0
    k=0
    while k+1<m:
        i=int(pc[k])
        j=int(pc[k+1])

        ai0=int(ask[i-1]); bi0=int(bid[i-1])
        ai=int(ask[i]); bi=int(bid[i])
        aj0=int(ask[j-1]); bj0=int(bid[j-1])
        aj=int(ask[j]); bj=int(bid[j])

        bull_leader=(ai>ai0 and bi==bi0)
        bear_leader=(bi<bi0 and ai==ai0)

        if bull_leader:
            bull_leaders+=1
            bull_follower=(bj>bj0 and aj==aj0)
            if bull_follower:
                completed+=1
                s0=ai0-bi0
                sp=ai-bi
                s1=aj-bj
                if s1<=s0 and j+1<n:
                    idx[out]=j+1
                    side[out]=1
                    latency[out]=int(t[j]-t[i])
                    pre_spread[out]=s0
                    peak_spread[out]=sp
                    post_spread[out]=s1
                    lead_move[out]=ai-ai0
                    follow_move[out]=bj-bj0
                    out+=1
                    k+=2
                    continue

        elif bear_leader:
            bear_leaders+=1
            bear_follower=(aj<aj0 and bj==bj0)
            if bear_follower:
                completed+=1
                s0=ai0-bi0
                sp=ai-bi
                s1=aj-bj
                if s1<=s0 and j+1<n:
                    idx[out]=j+1
                    side[out]=-1
                    latency[out]=int(t[j]-t[i])
                    pre_spread[out]=s0
                    peak_spread[out]=sp
                    post_spread[out]=s1
                    lead_move[out]=bi0-bi
                    follow_move[out]=aj0-aj
                    out+=1
                    k+=2
                    continue
        k+=1

    return (
        idx[:out],side[:out],latency[:out],pre_spread[:out],peak_spread[:out],
        post_spread[:out],lead_move[:out],follow_move[:out],
        m,bull_leaders,bear_leaders,completed
    )

@njit(cache=True)
def evaluate(event_idx,event_side,t,ask,bid):
    busy=-1
    trades=busy_skips=spread_rejects=wins=longs=shorts=0
    gp=gl=net=0.0
    stop_count=hold_count=end_count=0
    days=np.empty(event_idx.size,np.int64)
    dn=0

    for z in range(event_idx.size):
        i=int(event_idx[z])
        s=int(event_side[z])
        if i<=busy:
            busy_skips+=1
            continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            spread_rejects+=1
            continue

        trades+=1
        if s>0: longs+=1
        else: shorts+=1
        days[dn]=int(t[i]//DAY_MS)
        dn+=1

        entry=int(ask[i]) if s>0 else int(bid[i])
        stop=q_tick(int(bid[i])-STOP_RAW if s>0 else int(ask[i])+STOP_RAW)
        entry_sec=int(t[i])//1000
        raw=0.0
        reason=2
        last=i

        for k in range(i+1,t.size):
            aa=int(ask[k]); bb=int(bid[k]); sec=int(t[k])//1000
            last=k
            if s>0 and bb<=stop:
                raw=(bb-entry)/SCALE
                reason=0
                break
            if s<0 and aa>=stop:
                raw=(entry-aa)/SCALE
                reason=0
                break
            if sec-entry_sec>=MAX_HOLD_SECONDS:
                raw=((bb-entry) if s>0 else (entry-aa))/SCALE
                reason=1
                break
            fav=(bb-entry) if s>0 else (entry-aa)
            if fav>=TRAIL_ACTIVATION_RAW:
                ns=q_tick(bb-TRAIL_DISTANCE_RAW if s>0 else aa+TRAIL_DISTANCE_RAW)
                if (s>0 and ns>stop) or (s<0 and ns<stop):
                    stop=ns
        else:
            aa=int(ask[last]); bb=int(bid[last])
            raw=((bb-entry) if s>0 else (entry-aa))/SCALE

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

    return (
        trades,busy_skips,spread_rejects,distinct,longs,shorts,wins,
        gp,gl,net,stop_count,hold_count,end_count
    )

def quantiles(x):
    if len(x)==0:
        return {}
    q=np.quantile(x,[.1,.25,.5,.75,.9,.99])
    return {
        "p10":float(q[0]),"p25":float(q[1]),"p50":float(q[2]),
        "p75":float(q[3]),"p90":float(q[4]),"p99":float(q[5])
    }

def predictive(event_idx,event_side,t,ask,bid):
    if len(event_idx)==0:
        return {}
    mid=ask.astype(np.int64)+bid.astype(np.int64)
    horizons=(250,1000,5000)
    out={}

    # next nonzero mid move after executable entry tick
    eligible=correct=0
    for z in range(len(event_idx)):
        i=int(event_idx[z]); s=int(event_side[z]); base=int(mid[i])
        k=i+1
        while k<len(mid) and int(mid[k])==base:
            k+=1
        if k<len(mid):
            eligible+=1
            if s*(int(mid[k])-base)>0:
                correct+=1
    out["next_nonzero_mid_move"]={
        "eligible":eligible,
        "correct":correct,
        "accuracy":float(correct/eligible) if eligible else None
    }

    fwd={}
    for h in horizons:
        eligible=correct=0
        for z in range(len(event_idx)):
            i=int(event_idx[z]); s=int(event_side[z]); tm=int(t[i])+h
            k=int(np.searchsorted(t,tm,side="left"))
            if k>=len(t):
                continue
            move=int(mid[k])-int(mid[i])
            if move==0:
                continue
            eligible+=1
            if s*move>0:
                correct+=1
        fwd[f"{h}ms"]={
            "eligible":eligible,
            "correct":correct,
            "accuracy":float(correct/eligible) if eligible else None
        }
    out["forward"]=fwd
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df=pd.read_csv(
        args.source,
        compression="gzip",
        usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
        dtype=np.int64
    )
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709:
        raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]):
        raise SystemExit("Stage-A chronology mismatch")

    ar=df.ask_raw.to_numpy(np.int64)
    br=df.bid_raw.to_numpy(np.int64)
    ea,eb=p75(t,ar,br)

    (
        idx,side,latency,pre_spread,peak_spread,post_spread,lead_move,follow_move,
        price_change_events,bull_leaders,bear_leaders,completed_pairs
    )=detect_events(t,ar,br)

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
        leader="C01_OUTWARD_LEADER_FOLLOWER_CONTINUATION"
        decision="ADVANCE_QPLF_C01_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_QPLF_C01_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader=None
        decision="RETIRE_QPLF_STAGE_A_NO_EXECUTABLE_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    diag={
        "native_price_change_events":int(price_change_events),
        "bullish_ask_up_only_leaders":int(bull_leaders),
        "bearish_bid_down_only_leaders":int(bear_leaders),
        "same_direction_follower_pairs_before_restore_gate":int(completed_pairs),
        "restored_spread_signals":int(idx.size),
        "signals_per_day":float(idx.size/14.0),
        "leader_to_follower_latency_ms_quantiles":quantiles(latency),
        "pre_leader_spread_raw_quantiles":quantiles(pre_spread),
        "leader_peak_spread_raw_quantiles":quantiles(peak_spread),
        "post_follower_spread_raw_quantiles":quantiles(post_spread),
        "leader_move_raw_quantiles":quantiles(lead_move),
        "follower_move_raw_quantiles":quantiles(follow_move)
    }

    out={
        "schema":"delta-r037-qplf-stage-a-screen-17ba-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_QUOTE_PROPAGATION_LEADER_FOLLOWER_STAGE_A_SCREEN",
        "family":"R037-QPLF-v1",
        "parent_checkpoint":"R037_TSO_STAGE_A_SCREEN_CHECKPOINT_17AZ",
        "prereg_commit":PREREG_COMMIT,
        "source_sha256":source_sha,
        "stage_a_ticks":int(len(t)),
        "signal_surface":"NATIVE_DUKASCOPY_BBO",
        "execution_surface":"DUKAS_COINEXX_LIKE_P75",
        "event_definition":{
            "bullish":"ask-up-only leader -> next price-changing event bid-up-only follower",
            "bearish":"bid-down-only leader -> next price-changing event ask-down-only follower",
            "spread_restoration":"post-follower spread <= pre-leader spread",
            "entry":"first strictly subsequent raw tick after follower"
        },
        "numeric_retuning":False,
        "august_accessed":False,
        "diagnostics":diag,
        "prediction":predictive(idx,side,t,ar,br),
        "configs":{
            "C01_OUTWARD_LEADER_FOLLOWER_CONTINUATION":{
                "metrics":metrics,
                "gate":gate
            }
        },
        "finding":{
            "leading_config":leader,
            "decision":decision,
            "next":nxt
        },
        "mql5_authorized":False
    }

    atomic_write_json(args.output,out)
    print(json.dumps({
        "diagnostics":diag,
        "prediction":out["prediction"],
        "metrics":metrics,
        "gate":gate,
        "finding":out["finding"]
    },separators=(",",":")))

if __name__=="__main__":
    main()
