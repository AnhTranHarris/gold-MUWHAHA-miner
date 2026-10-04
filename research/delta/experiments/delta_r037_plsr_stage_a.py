"""DELTA R037 PLSR Stage-A screen — Checkpoint 16A.

Frozen family: previous active UTC day high/low -> strict sweep -> causal completed-bar reclaim.
Three preregistered confirmation anchors only. No numeric retuning.
Uses the verified 14A/15A surrogate-parent integration engine.
"""
from __future__ import annotations
import argparse, json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

import delta_r037_sorb_surrogate_parent_stage_a as integ

DAY_MS=86_400_000
STAGE_A_START_MS=1_767_225_600_000
STAGE_A_END_MS=1_768_737_600_000
MAX_SPREAD_RAW=25*10
CONFIGS=(
    "R037-PLSR-C01_PDH_PDL_S5_RECLAIM",
    "R037-PLSR-C02_PDH_PDL_S5_RECLAIM_CONFIRM1",
    "R037-PLSR-C03_PDH_PDL_S15_RECLAIM",
)

@dataclass(frozen=True)
class Proposal:
    decision_index:int
    side:int
    level_kind:str
    utc_day_ms:int
    eligible:bool
    reason:str

def _bars(t,bid,tf):
    bucket=t//tf
    st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    en=np.r_[st[1:],len(t)]
    return {
        "end_ms":((bucket[st]+1)*tf).astype(np.int64),
        "open":bid[st].astype(np.int64),
        "close":bid[en-1].astype(np.int64),
        "high":np.maximum.reduceat(bid,st).astype(np.int64),
        "low":np.minimum.reduceat(bid,st).astype(np.int64),
    }

def _prior_active_day_levels(t,bid):
    day=t//DAY_MS
    st=np.r_[0,np.flatnonzero(day[1:]!=day[:-1])+1]
    en=np.r_[st[1:],len(t)]
    out={}
    prev_hi=prev_lo=None
    for s,e in zip(st,en):
        d=int(day[s])
        if prev_hi is not None:
            out[d]=(int(prev_hi),int(prev_lo))
        prev_hi=int(np.max(bid[s:e])); prev_lo=int(np.min(bid[s:e]))
    return out

def _bar_idx_for_time(end_ms,tm):
    # First bar whose right edge is strictly after the sweep tick. This includes
    # the sweep's own bar and makes wick-through / close-back-inside causal.
    return int(np.searchsorted(end_ms,tm,side="right"))

def _decision_idx(t,edge):
    return int(np.searchsorted(t,edge,side="left"))

def generate_proposals(t,ask,bid,config_id):
    if config_id not in CONFIGS: raise ValueError(config_id)
    levels=_prior_active_day_levels(t,bid)
    b5=_bars(t,bid,5000); b15=_bars(t,bid,15000)
    day=t//DAY_MS
    dst=np.r_[0,np.flatnonzero(day[1:]!=day[:-1])+1]
    den=np.r_[dst[1:],len(t)]
    props=[]
    for s,e in zip(dst,den):
        d=int(day[s])
        if d not in levels: continue
        pdh,pdl=levels[d]
        for kind,L,side in (("PDH",pdh,-1),("PDL",pdl,1)):
            seg=bid[s:e]
            rel=np.flatnonzero(seg>L) if kind=="PDH" else np.flatnonzero(seg<L)
            if rel.size==0: continue
            sweep_i=s+int(rel[0]); sweep_tm=int(t[sweep_i])
            bars=b15 if config_id.endswith("S15_RECLAIM") else b5
            j=_bar_idx_for_time(bars["end_ms"],sweep_tm)
            # Search only within the current UTC day and use the first completed
            # bar that causally closes back inside the swept prior-day level.
            reclaim_j=-1
            while j<len(bars["end_ms"]) and int(bars["end_ms"][j])<= (d+1)*DAY_MS:
                c=int(bars["close"][j])
                if (kind=="PDH" and c<L) or (kind=="PDL" and c>L):
                    reclaim_j=j; break
                j+=1
            if reclaim_j<0: continue
            dec_j=reclaim_j
            if config_id=="R037-PLSR-C02_PDH_PDL_S5_RECLAIM_CONFIRM1":
                k=reclaim_j+1
                if k>=len(b5["end_ms"]) or int(b5["end_ms"][k])>(d+1)*DAY_MS:
                    props.append(Proposal(_decision_idx(t,int(b5["end_ms"][reclaim_j])),side,kind,d*DAY_MS,False,"NO_IMMEDIATE_CONFIRM_BAR"))
                    continue
                rc=int(b5["close"][reclaim_j]); o=int(b5["open"][k]); c=int(b5["close"][k])
                ok=(c<rc and c<o and c<L) if kind=="PDH" else (c>rc and c>o and c>L)
                if not ok:
                    props.append(Proposal(_decision_idx(t,int(b5["end_ms"][k])),side,kind,d*DAY_MS,False,"CONFIRM_FAIL"))
                    continue
                dec_j=k
            edge=int(bars["end_ms"][dec_j] if config_id!="R037-PLSR-C02_PDH_PDL_S5_RECLAIM_CONFIRM1" else b5["end_ms"][dec_j])
            ii=_decision_idx(t,edge)
            if ii>=len(t) or int(t[ii])>=(d+1)*DAY_MS:
                props.append(Proposal(min(ii,len(t)-1),side,kind,d*DAY_MS,False,"NO_EXECUTABLE_TICK"))
                continue
            px=int(bid[ii])
            still_inside=(px<L) if kind=="PDH" else (px>L)
            if not still_inside:
                props.append(Proposal(ii,side,kind,d*DAY_MS,False,"RELOST_RECLAIM"))
                continue
            if int(ask[ii]-bid[ii])>MAX_SPREAD_RAW:
                props.append(Proposal(ii,side,kind,d*DAY_MS,False,"SPREAD_GATE"))
                continue
            props.append(Proposal(ii,side,kind,d*DAY_MS,True,"ELIGIBLE"))
    props.sort(key=lambda x:(x.decision_index,x.level_kind))
    return props

def supply(props):
    return {
        "proposals":len(props),
        "source_eligible":sum(p.eligible for p in props),
        "distinct_days":len({p.utc_day_ms for p in props}),
        "proposal_long":sum(p.side>0 for p in props),
        "proposal_short":sum(p.side<0 for p in props),
        "levels":{"PDH":sum(p.level_kind=="PDH" for p in props),"PDL":sum(p.level_kind=="PDL" for p in props)},
        "source_rejections":{r:sum(p.reason==r for p in props) for r in ("CONFIRM_FAIL","NO_IMMEDIATE_CONFIRM_BAR","RELOST_RECLAIM","SPREAD_GATE","NO_EXECUTABLE_TICK")},
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    sha=integ.base.sha256_file(a.source)
    if sha!=integ.base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: "+sha)
    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[(df.timestamp_ms_utc>=STAGE_A_START_MS)&(df.timestamp_ms_utc<STAGE_A_END_MS)]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size!=4205709 or np.any(t[1:]<t[:-1]):
        raise SystemExit(f"Stage-A chronology mismatch: {t.size}")
    ask,bid=integ.base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    feat=integ.parent.build_parent_features(t,ask,bid)
    streams=integ.generate_streams(t,ask,bid)
    d3t,d3s=streams["DH03_S06"]; d5t,d5s=streams["DH05_S06"]
    s11t,s11s=streams["DH02_S11"]; s08t,s08s=streams["DH02_S08"]
    zi=np.empty(0,np.int64); zs=np.empty(0,np.int8)
    p=integ.pack_sorb(integ.run_integrated_sorb(
        t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
        d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,zi,zs,zs,1,1,1,1,1))
    integ.parent_gate(p)
    results={}; ranking=[]
    for cid in CONFIGS:
        props=generate_proposals(t,ask,bid,cid); sp=supply(props)
        ep=[x for x in props if x.eligible]
        ii=np.asarray([x.decision_index for x in ep],np.int64)
        ss=np.asarray([x.side for x in ep],np.int8)
        # Reuse the verified generic sixth-source integration lane. Session code
        # 1=PDH and 2=PDL only for contribution accounting.
        sk=np.asarray([1 if x.level_kind=="PDH" else 2 for x in ep],np.int8)
        c=integ.pack_sorb(integ.run_integrated_sorb(
            t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
            d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,ii,ss,sk,1,1,1,1,1))
        d=integ.decision(p,c,sp)
        contrib=c.pop("sorb_session_contribution")
        c["plsr_entries"]=c.pop("sorb_entries"); c["plsr_net"]=c.pop("sorb_net")
        c["plsr_level_contribution"]={"PDH":contrib["LONDON"],"PDL":contrib["COMEX_GOLD"]}
        d["incremental_net_per_plsr_entry"]=d.pop("incremental_net_per_sorb_entry")
        results[cid]={"supply":sp,"combined":c,"decision":d}
        ranking.append((int(d["strong_screen_pass"]),int(d["screen_pass"]),d["net_delta"],c["plsr_entries"],cid))
    ranking.sort(reverse=True)
    leaders=[{"config_id":x[-1],"strong_screen_pass":results[x[-1]]["decision"]["strong_screen_pass"],"screen_pass":results[x[-1]]["decision"]["screen_pass"],"net_delta":results[x[-1]]["decision"]["net_delta"],"trade_delta":results[x[-1]]["decision"]["trade_delta"],"official_win_delta":results[x[-1]]["decision"]["official_win_delta"],"accepted_entries":results[x[-1]]["combined"]["plsr_entries"]} for x in ranking]
    anystrong=any(results[c]["decision"]["strong_screen_pass"] for c in CONFIGS)
    out={
      "schema":"delta-r037-plsr-stage-a-screen-16a-v1",
      "status":"COMPLETE_STAGE_A_SCREEN",
      "unit":"R037_PREVIOUS_LIQUIDITY_SWEEP_RECLAIM_STAGE_A_SCREEN",
      "family":"R037-PLSR-v1",
      "parent_checkpoint":"R037_SORB_C04_DUAL30_INDEPENDENT_VALIDATION_CHECKPOINT_15B",
      "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
      "promotable":False,
      "source_sha256":sha,
      "stage_a_ticks":int(t.size),
      "surface":"DUKAS_COINEXX_LIKE_P75",
      "numeric_retuning":False,
      "august_accessed":False,
      "parent_control":p,
      "configs":results,
      "ranking":leaders,
      "finding":{"leading_config":leaders[0]["config_id"],"any_strong_screen_pass":anystrong,"next":"R037_PLSR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if anystrong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
      "mql5_authorized":False
    }
    integ.base.atomic_write_json(a.output,out)
    print(json.dumps({"ranking":leaders,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
