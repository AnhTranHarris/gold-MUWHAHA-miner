"""DELTA R037 PLSR reclaim-quality cross-month screen — Checkpoint 17X.

Frozen preregistration:
- exact PLSR C01 previous-active-UTC-day PDH/PDL -> first strict tick sweep ->
  first completed S5 close back inside -> first executable tick at/after reclaim;
- both PDH and PDL retained; one event per level/day; no rearm;
- four fixed completed-S5 reclaim-quality gates only;
- January uses exact Stage-A; Feb-Jul use 7 UTC days of prior canonical month
  as state warmup with no economic entry before current month;
- frozen 30-second source-only execution;
- no threshold/session/side/month/exit tuning; August sealed; MQL5 unauthorized.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import delta_r037_smor_departure_swing_prescreen as base

DAY_MS=86_400_000
WARMUP_DAYS=7
SOURCE_SHA={
"2026-01":"d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5",
"2026-02":"ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d",
"2026-03":"814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177",
"2026-04":"30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f",
"2026-05":"3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d",
"2026-06":"34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2",
"2026-07":"e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7",
}
CONFIGS=("C01_DIRECTIONAL_RECLAIM","C02_REVERSAL_HALF_CLOSE","C03_ENGULFING_RECOVERY","C04_DIRECTIONAL_RANGE_EXPANSION")

def month_ms(month):
    y,m=map(int,month.split("-"))
    s=int(datetime(y,m,1,tzinfo=timezone.utc).timestamp()*1000)
    if m==12: e=int(datetime(y+1,1,1,tzinfo=timezone.utc).timestamp()*1000)
    else: e=int(datetime(y,m+1,1,tzinfo=timezone.utc).timestamp()*1000)
    return s,e

def prior_levels(t,bid):
    day=t//DAY_MS; st=np.r_[0,np.flatnonzero(day[1:]!=day[:-1])+1]; en=np.r_[st[1:],len(t)]
    out={}; ph=pl=None
    for s,e in zip(st,en):
        d=int(day[s])
        if ph is not None: out[d]=(int(ph),int(pl))
        ph=int(np.max(bid[s:e])); pl=int(np.min(bid[s:e]))
    return out

def quality_ok(cid,kind,j,b):
    o,h,l,c=b["open"],b["high"],b["low"],b["close"]
    side=-1 if kind=="PDH" else 1
    if cid=="BASE": return True
    if cid=="C01_DIRECTIONAL_RECLAIM":
        return int(c[j])<int(o[j]) if side<0 else int(c[j])>int(o[j])
    if cid=="C02_REVERSAL_HALF_CLOSE":
        mid=(int(h[j])+int(l[j]))/2.0
        return int(c[j])<=mid if side<0 else int(c[j])>=mid
    if cid=="C03_ENGULFING_RECOVERY":
        if j<=0: return False
        if side<0:
            return int(c[j])<int(o[j]) and int(c[j-1])>int(o[j-1]) and int(o[j])>=int(c[j-1]) and int(c[j])<=int(o[j-1])
        return int(c[j])>int(o[j]) and int(c[j-1])<int(o[j-1]) and int(o[j])<=int(c[j-1]) and int(c[j])>=int(o[j-1])
    if cid=="C04_DIRECTIONAL_RANGE_EXPANSION":
        if j<=0: return False
        directional=(int(c[j])<int(o[j])) if side<0 else (int(c[j])>int(o[j]))
        return directional and (int(h[j])-int(l[j]) > int(h[j-1])-int(l[j-1]))
    raise ValueError(cid)

def proposals(t,ask,bid,cid,econ_start,econ_end):
    levels=prior_levels(t,bid); b=base.bars(t,bid,5000)
    day=t//DAY_MS; st=np.r_[0,np.flatnonzero(day[1:]!=day[:-1])+1]; en=np.r_[st[1:],len(t)]
    out=[]
    for s,e in zip(st,en):
        d=int(day[s])
        if d not in levels: continue
        if (d+1)*DAY_MS<=econ_start or d*DAY_MS>=econ_end: continue
        pdh,pdl=levels[d]
        for kind,L,side in (("PDH",pdh,-1),("PDL",pdl,1)):
            seg=bid[s:e]; rel=np.flatnonzero(seg>L) if kind=="PDH" else np.flatnonzero(seg<L)
            if rel.size==0: continue
            sw=s+int(rel[0]); swtm=int(t[sw])
            j=int(np.searchsorted(b["end_ms"],swtm,side="right")); reclaim=-1
            while j<len(b["end_ms"]) and int(b["end_ms"][j])<=(d+1)*DAY_MS:
                cc=int(b["close"][j])
                if (kind=="PDH" and cc<L) or (kind=="PDL" and cc>L): reclaim=j; break
                j+=1
            if reclaim<0 or not quality_ok(cid,kind,reclaim,b): continue
            edge=int(b["end_ms"][reclaim]); ii=int(np.searchsorted(t,edge,side="left"))
            if ii>=len(t) or int(t[ii])>=econ_end or int(t[ii])<econ_start: continue
            still=(int(bid[ii])<L) if kind=="PDH" else (int(bid[ii])>L)
            if not still: continue
            if int(ask[ii]-bid[ii])>base.MAX_SPREAD_RAW: continue
            out.append(base.Proposal(ii,side,True,"ELIGIBLE",reclaim))
    out.sort(key=lambda p:(p.decision_index,p.side))
    return out

def load_window(cur,prev,month):
    if base.sha256_file(cur)!=SOURCE_SHA[month]: raise SystemExit(f"{month} SHA mismatch")
    use=["timestamp_ms_utc","ask_raw","bid_raw"]
    if month=="2026-01":
        df=pd.read_csv(cur,compression="gzip",usecols=use,dtype=np.int64)
        s,e=base.STAGE_A_START_MS,base.STAGE_A_END_MS
        df=df[(df.timestamp_ms_utc>=s)&(df.timestamp_ms_utc<e)]
        return df,s,e
    s,e=month_ms(month); pm=f"2026-{int(month[-2:])-1:02d}"
    if base.sha256_file(prev)!=SOURCE_SHA[pm]: raise SystemExit(f"{pm} SHA mismatch")
    a=pd.read_csv(prev,compression="gzip",usecols=use,dtype=np.int64)
    a=a[(a.timestamp_ms_utc>=s-WARMUP_DAYS*DAY_MS)&(a.timestamp_ms_utc<s)]
    b=pd.read_csv(cur,compression="gzip",usecols=use,dtype=np.int64)
    b=b[(b.timestamp_ms_utc>=s)&(b.timestamp_ms_utc<e)]
    return pd.concat([a,b],ignore_index=True),s,e

def one_month(cur,prev,month):
    df,s,e=load_window(cur,prev,month); t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size==0 or np.any(t[1:]<t[:-1]): raise SystemExit(f"{month} chronology mismatch")
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    res={}
    for cid in ("BASE",)+CONFIGS:
        pp=proposals(t,ask,bid,cid,s,e); ex=base.simulate_source(pp,t,ask,bid); sp=base.supply(pp,t)
        res[cid]={"supply":sp,"execution":ex}
    return {"loaded_ticks":int(t.size),"economic_ticks":int(np.sum((t>=s)&(t<e))),"results":res}

def aggregate(monthly):
    out={}
    for cid in ("BASE",)+CONFIGS:
        trades=sum(monthly[m]["results"][cid]["execution"]["trades"] for m in monthly)
        wins=sum(monthly[m]["results"][cid]["execution"]["official_wins"] for m in monthly)
        net=round(sum(monthly[m]["results"][cid]["execution"]["direct_net_usd"] for m in monthly),2)
        months_trading=sum(monthly[m]["results"][cid]["execution"]["trades"]>0 for m in monthly)
        nonneg=sum(monthly[m]["results"][cid]["execution"]["direct_net_usd"]>=0 for m in monthly)
        out[cid]={"trades":trades,"official_wins":wins,"direct_net_usd":net,"months_with_trades":months_trading,"nonnegative_months":nonneg}
    b=out["BASE"]
    for cid in CONFIGS:
        x=out[cid]; retention=x["trades"]/b["trades"] if b["trades"] else 0.0
        gate={"trade_retention_fraction":retention,"retention_ge_0_5":retention>=0.5,"months_with_trades_ge_5":x["months_with_trades"]>=5,"nonnegative_months_ge_4":x["nonnegative_months"]>=4,"aggregate_net_nonnegative":x["direct_net_usd"]>=0,"aggregate_net_improves_vs_baseline":x["direct_net_usd"]>b["direct_net_usd"]}
        gate["cross_month_pass"]=all(v for k,v in gate.items() if k!="trade_retention_fraction")
        x["gate"]=gate
    return out

def main():
    ap=argparse.ArgumentParser()
    for m in range(1,8): ap.add_argument(f"--m{m}",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    paths={f"2026-{m:02d}":getattr(a,f"m{m}") for m in range(1,8)}
    monthly={}
    for m in range(1,8):
        key=f"2026-{m:02d}"; prev=paths.get(f"2026-{m-1:02d}") if m>1 else None
        monthly["2026-01_STAGE_A" if m==1 else key]=one_month(paths[key],prev,key)
    agg=aggregate(monthly); survivors=[c for c in CONFIGS if agg[c]["gate"]["cross_month_pass"]]
    ranked=sorted(CONFIGS,key=lambda c:(agg[c]["gate"]["cross_month_pass"],agg[c]["direct_net_usd"],agg[c]["nonnegative_months"],agg[c]["trades"]),reverse=True)
    out={"schema":"delta-r037-plsr-reclaim-quality-cross-month-17x-v1","status":"COMPLETE_CROSS_MONTH_SCREEN","unit":"R037_PLSR_RECLAIM_QUALITY_CROSS_MONTH_17X","family":"R037-PLSR-RQ-v1","surface":"DUKAS_COINEXX_LIKE_P75","source_sha256":SOURCE_SHA,"warmup_days":WARMUP_DAYS,"numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,"monthly":monthly,"aggregate":agg,"ranking":ranked,"finding":{"survivors":survivors,"leader":ranked[0],"next":"R037_PLSR_RQ_LEADER_FULL_SURROGATE_PARENT_CROSS_MONTH_VALIDATION" if survivors else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False}
    base.atomic_write_json(a.output,out)
    print(json.dumps({"aggregate":agg,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
