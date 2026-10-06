from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

from grid001_january_event_label_lab import load, materialize

CAN_GP=3785.28
CAN_GL=-10436.90
CAN_NET=-6651.62
SPLIT_MS=1769418162219

def load_volumes(path: Path, n: int):
    av=np.empty(n,np.float32); bv=np.empty(n,np.float32); pos=0
    for d in pd.read_csv(path,compression="gzip",usecols=["ask_volume","bid_volume"],
                         dtype={"ask_volume":"f4","bid_volume":"f4"},chunksize=1_000_000):
        k=len(d); av[pos:pos+k]=d.ask_volume.to_numpy(); bv[pos:pos+k]=d.bid_volume.to_numpy(); pos+=k
    if pos!=n: raise RuntimeError(f"volume rows {pos}!={n}")
    return av,bv

def econ(df,mask):
    x=df.loc[np.asarray(mask,bool)]
    deals=np.concatenate([x.entry_deal_cashflow.to_numpy(float),x.exit_deal_cashflow.to_numpy(float)]) if len(x) else np.array([],float)
    gp=float(deals[deals>0].sum()) if len(deals) else 0.0
    gl=float(deals[deals<0].sum()) if len(deals) else 0.0
    net=float(x.net_cashflow.sum())
    ts=100*len(x)/len(df)
    ls=100*abs(gl)/abs(CAN_GL)
    ps=100*gp/CAN_GP
    return {"trades":int(len(x)),"trade_share_pct":ts,"net":net,"gross_profit":gp,"gross_loss":gl,
            "pf":gp/abs(gl) if gl<0 else None,"gross_loss_share_pct":ls,"gross_profit_share_pct":ps,
            "gross_loss_minus_trade_share_pct":ls-ts,"gross_loss_minus_gross_profit_share_pct":ls-ps,
            "hypothetical_veto_net_improvement":-net}

def nearest_indices(t,ms):
    j=np.searchsorted(t,ms); j=np.clip(j,0,len(t)-1)
    prev=np.maximum(j-1,0)
    use_prev=np.abs(t[prev]-ms)<=np.abs(t[j]-ms)
    return np.where(use_prev,prev,j)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("context_rows",type=Path)
    ap.add_argument("ticks",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    df=pd.read_csv(args.context_rows).sort_values("entry_utc_ms").reset_index(drop=True)
    t,sa,sb=load(args.ticks)
    a,b,maxe=materialize(t,sa,sb)
    av,bv=load_volumes(args.ticks,len(t))
    mid=(a.astype(np.int64)+b.astype(np.int64))/2.0
    dm=np.abs(np.diff(mid,prepend=mid[0]))
    cpath=np.cumsum(dm,dtype=np.float64)

    if "mapped_tick_utc_ms" in df.columns:
        entry_ms=df.mapped_tick_utc_ms.to_numpy(np.int64)
    else:
        entry_ms=df.entry_utc_ms.to_numpy(np.int64)
    idx=nearest_indices(t,entry_ms)
    side=df.side.to_numpy(np.int8)

    def window_features(ms):
        s=np.searchsorted(t,t[idx]-ms,side="left")
        net=mid[idx]-mid[s]
        path=cpath[idx]-cpath[s]
        eff=np.divide(np.abs(net),path,out=np.zeros(len(idx),float),where=path>0)
        aligned=side*net
        state=np.full(len(idx),"FLAT",object)
        state[aligned>0]="SUPPORT"; state[aligned<0]="OPPOSE"
        return s,aligned,eff,state

    s250,d250,e250,st250=window_features(250)
    s1,d1,e1,st1=window_features(1000)
    s5,d5,e5,st5=window_features(5000)

    price=np.full(len(df),"MIXED_FLAT",object)
    price[(st250=="SUPPORT")&(st1=="SUPPORT")&(st5=="SUPPORT")]="ALL_SUPPORT"
    price[(st250=="OPPOSE")&(st1=="OPPOSE")&(st5=="OPPOSE")]="ALL_OPPOSE"
    price[(st250=="SUPPORT")&(st5=="OPPOSE")]="FAST_SUPPORT_SLOW_OPPOSE"
    price[(st250=="OPPOSE")&(st5=="SUPPORT")]="FAST_OPPOSE_SLOW_SUPPORT"

    den=(bv+av).astype(float)
    imb=np.divide(bv.astype(float)-av.astype(float),den,out=np.zeros(len(den),float),where=den>0)
    cimb=np.r_[0.0,np.cumsum(imb)]
    cnt1=idx-s1+1
    mean1=(cimb[idx+1]-cimb[s1])/cnt1
    cur=imb[idx]
    acur=side*cur; amean=side*mean1
    l1=np.full(len(df),"MIXED_OR_ZERO",object)
    l1[(acur>0)&(amean>0)]="BOTH_SUPPORT"
    l1[(acur<0)&(amean<0)]="BOTH_OPPOSE"
    l1[(acur>0)&(amean<0)]="FLIP_TO_SUPPORT"
    l1[(acur<0)&(amean>0)]="FLIP_TO_OPPOSE"

    sask=sa[idx].astype(float); sbid=sb[idx].astype(float)
    vv=(bv[idx]+av[idx]).astype(float)
    micro=np.divide(sask*bv[idx]+sbid*av[idx],vv,out=(sask+sbid)/2.0,where=vv>0)
    source_mid=(sask+sbid)/2.0
    half=(sask-sbid)/2.0
    micro_norm=side*np.divide(micro-source_mid,half,out=np.zeros(len(df),float),where=half>0)

    s30=np.searchsorted(t,t[idx]-30000,side="left")
    cnt30=idx-s30+1
    rate_ratio=30.0*cnt1/cnt30
    intensity=np.full(len(df),"NORMAL",object)
    intensity[rate_ratio<.5]="THIN"
    intensity[rate_ratio>=2.0]="BURST"

    df["price_state"]=price
    df["l1_state"]=l1
    df["intensity_state"]=intensity
    df["segment"]=np.where(df.entry_utc_ms<SPLIT_MS,"discovery","validation")
    df["owner_rel_name"]=df.owner_relation.map({1:"ALIGNED",-1:"OPPOSED",0:"NEUTRAL",2:"CONFLICT"})
    df["owner_phase_cross"]=df.owner_phase.map({1:"EARLY",2:"MATURE",3:"EXTENDED_NONE",0:"EXTENDED_NONE"})

    groups=[]
    def add(family,key,mask):
        m=np.asarray(mask,bool)
        groups.append({"family":family,"key":key,"full":econ(df,m),
                       "discovery":econ(df,m&(df.segment=="discovery")),
                       "validation":econ(df,m&(df.segment=="validation"))})

    price_states=["ALL_SUPPORT","ALL_OPPOSE","FAST_SUPPORT_SLOW_OPPOSE","FAST_OPPOSE_SLOW_SUPPORT","MIXED_FLAT"]
    l1_states=["BOTH_SUPPORT","BOTH_OPPOSE","FLIP_TO_SUPPORT","FLIP_TO_OPPOSE","MIXED_OR_ZERO"]
    for x in price_states: add("M1_PRICE_STATE",x,df.price_state==x)
    for x in l1_states: add("M2_L1_STATE",x,df.l1_state==x)
    for x in ["THIN","NORMAL","BURST"]: add("M4_INTENSITY",x,df.intensity_state==x)
    for p in price_states:
        for l in l1_states: add("M1xM2_PRICE_L1",f"{p}__{l}",(df.price_state==p)&(df.l1_state==l))
        for r in ["ALIGNED","OPPOSED","NEUTRAL","CONFLICT"]: add("M1xOWNER_REL",f"{p}__{r}",(df.price_state==p)&(df.owner_rel_name==r))
        for ph in ["EARLY","MATURE","EXTENDED_NONE"]: add("M1xOWNER_PHASE",f"{p}__{ph}",(df.price_state==p)&(df.owner_phase_cross==ph))

    diagnostics={
      "median_efficiency_250ms":float(np.median(e250)),"median_efficiency_1s":float(np.median(e1)),
      "median_efficiency_5s":float(np.median(e5)),"median_aligned_imbalance_current":float(np.median(acur)),
      "median_aligned_imbalance_mean_1s":float(np.median(amean)),"median_microprice_bias_norm":float(np.median(micro_norm)),
      "median_intensity_ratio_1s":float(np.median(rate_ratio)),
      "price_state_counts":{k:int(v) for k,v in pd.Series(price).value_counts().items()},
      "l1_state_counts":{k:int(v) for k,v in pd.Series(l1).value_counts().items()},
      "intensity_state_counts":{k:int(v) for k,v in pd.Series(intensity).value_counts().items()},
      "timestamp_caveat":"250ms retained because preregistered; report timestamp fidelity limits independent subsecond promotion.",
      "max_midpoint_quantization_error_price":float(maxe/(2*1000))
    }
    out={"schema":"delta-a-alpha-r9-real-jan-micro-market-state-v1","unit":"DAA_GRID_001_R9_REAL_JAN_MICRO_MARKET_STATE_001",
         "status":"COMPLETE","canonical":{"net":CAN_NET,"gross_profit":CAN_GP,"gross_loss":CAN_GL},
         "diagnostics":diagnostics,"all_groups":groups}
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"diagnostics":diagnostics,"groups":len(groups)},indent=2))

if __name__=="__main__":
    main()
