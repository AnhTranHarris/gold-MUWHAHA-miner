"""DELTA R037 order-flow imbalance / microstructure Stage-A screen — 17AS.

Source-grounded reconstruction from MetaQuotes/MQL5 Market Microstructure
Parts 4, 5, and 6. The official Stage-A screen uses published source
thresholds without XAUUSD calibration.

Profiles:
- C01_SOURCE_FLOW_SMI: Part-6 example confidence + signed-flow + SMI gate.
- C02_FLOW_SMI_MOMENTUM: C01 plus sign-aligned Part-6 flow momentum.
- C03_PART5_CLEAN_IMBALANCE: Part-5 clean-noise + order-imbalance example.

Completed M1 P75-bid bars only. No parameter sweep, session/side rescue,
exit tuning, August access, or MQL5 build.
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
PREREG_COMMIT="b6eb77574ac32a151c371a4b4774b5946c3a300e"

WINDOW=90
SMI_ENDS=15
FLOW_SHORT=10
FLOW_LONG=30
JUMP_SIGMA=3.0
JUMP_GATE=0.021
NOISE_CONF_P75=0.632
FLOW_CONF_MIN=0.565
FLOW_LONG_THRESHOLD=0.092
FLOW_SHORT_THRESHOLD=-0.055
PART5_NOISE_CLEAN=0.63
PART5_OI_ABS=0.09

MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30

PROFILES=(
    "C01_SOURCE_FLOW_SMI",
    "C02_FLOW_SMI_MOMENTUM",
    "C03_PART5_CLEAN_IMBALANCE",
)

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
            prefix=f".{path.name}.",suffix=".tmp",dir=path.parent,delete=False
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

def flow_imbalance(h,l,c,v)->float:
    br=h-l
    ok=br>0
    if not np.any(ok):
        return 0.0
    frac=np.clip((c[ok]-l[ok])/br[ok],0.0,1.0)
    vv=np.where(v[ok]>0,v[ok],1.0)
    den=float(np.sum(vv))
    if den<=0:
        return 0.0
    val=float(np.sum((frac-0.5)*2.0*vv)/den)
    return float(np.clip(val,-1.0,1.0))

def enhanced_noise(o,h,l,c)->float:
    br=h-l
    mid=(h+l)/2.0
    ok=(br>0)&(mid>0)
    if int(np.sum(ok))<3:
        return 0.0
    oo=o[ok]; hh=h[ok]; ll=l[ok]; cc=c[ok]
    br=hh-ll; mid=(hh+ll)/2.0
    diff=(cc-mid)/mid
    rng=br/mid
    btr=np.abs(cc-oo)/br
    oc=(cc-oo)/mid
    var_d=float(np.var(diff))
    var_r=float(np.var(rng))
    var_oc=float(np.var(oc))
    if var_r<=np.finfo(np.float64).tiny:
        c1=0.0; c3=0.0
    else:
        c1=min(1.0,var_d/(var_r+np.finfo(np.float64).tiny))
        c3=min(1.0,var_oc/(var_r+np.finfo(np.float64).tiny))
    c2=max(0.0,1.0-float(np.mean(btr)))
    return float(np.clip(0.40*c1+0.40*c2+0.20*c3,0.0,1.0))

def jump_intensity(closes)->float:
    if len(closes)<6 or np.any(closes<=0):
        return 0.0
    r=np.diff(np.log(closes))
    r=r[np.isfinite(r)]
    if len(r)<5:
        return 0.0
    bpv=(np.pi/2.0)*float(np.mean(np.abs(r[1:])*np.abs(r[:-1])))
    if bpv<=np.finfo(np.float64).tiny:
        return 0.0
    return float(np.mean((r*r)>(JUMP_SIGMA*JUMP_SIGMA*bpv)))

def smart_money(o,h,l,c)->float:
    if len(c)<2*SMI_ENDS+10:
        return 0.0
    early_r=np.log(c[:SMI_ENDS]/o[:SMI_ENDS])
    late_r=np.log(c[-SMI_ENDS:]/o[-SMI_ENDS:])
    early=float(np.sum(early_r[np.abs(early_r)<0.1]))
    late=float(np.sum(late_r[np.abs(late_r)<0.1]))
    hi=float(np.max(h)); lo=float(np.min(l))
    mid=(hi+lo)/2.0
    if mid<=np.finfo(np.float64).tiny:
        return 0.0
    nr=(hi-lo)/mid
    if nr<=np.finfo(np.float64).tiny:
        return 0.0
    return float(np.clip((late-early)/nr,-1.0,1.0))

def build_features(b):
    o,h,l,c,v=(b[k] for k in ("open","high","low","close","tick_volume"))
    n=len(c)
    noise=np.full(n,np.nan,dtype=np.float64)
    jumps=np.full(n,np.nan,dtype=np.float64)
    flow90=np.full(n,np.nan,dtype=np.float64)
    smi=np.full(n,np.nan,dtype=np.float64)
    momentum=np.full(n,np.nan,dtype=np.float64)
    confidence=np.full(n,np.nan,dtype=np.float64)

    for j in range(WINDOW,n):
        w0=j-WINDOW+1
        ow=o[w0:j+1]; hw=h[w0:j+1]; lw=l[w0:j+1]; cw=c[w0:j+1]; vw=v[w0:j+1]
        nn=enhanced_noise(ow,hw,lw,cw)
        ji=jump_intensity(c[j-WINDOW:j+1])
        f90=flow_imbalance(hw,lw,cw,vw)
        sm=smart_money(ow,hw,lw,cw)
        s0=j-FLOW_SHORT+1
        l0=j-FLOW_LONG+1
        fs=flow_imbalance(h[s0:j+1],l[s0:j+1],c[s0:j+1],v[s0:j+1])
        fl=flow_imbalance(h[l0:j+1],l[l0:j+1],c[l0:j+1],v[l0:j+1])
        mom=float(np.clip(fs-fl,-2.0,2.0))
        if ji>JUMP_GATE:
            conf=0.0
        elif nn>NOISE_CONF_P75:
            excess=(nn-NOISE_CONF_P75)/(1.0-NOISE_CONF_P75)
            conf=max(0.0,0.7*(1.0-excess))
        else:
            conf=float(np.clip(1.0-(nn/NOISE_CONF_P75)*0.3,0.0,1.0))
        noise[j]=nn; jumps[j]=ji; flow90[j]=f90; smi[j]=sm; momentum[j]=mom; confidence[j]=conf

    valid=np.isfinite(flow90)
    def q(arr):
        x=arr[valid & np.isfinite(arr)]
        if len(x)==0:
            return {}
        vals=np.quantile(x,[0.10,0.25,0.50,0.75,0.90])
        return {"p10":float(vals[0]),"p25":float(vals[1]),"p50":float(vals[2]),"p75":float(vals[3]),"p90":float(vals[4])}
    diag={
        "usable_feature_bars":int(np.sum(valid)),
        "noise_quantiles":q(noise),
        "jump_quantiles":q(jumps),
        "flow_imbalance_quantiles":q(flow90),
        "smart_money_quantiles":q(smi),
        "flow_momentum_quantiles":q(momentum),
        "flow_confidence_quantiles":q(confidence),
        "jump_contaminated_bars":int(np.sum(valid & (jumps>JUMP_GATE))),
        "confidence_eligible_bars":int(np.sum(valid & (confidence>=FLOW_CONF_MIN))),
        "part5_clean_noise_bars":int(np.sum(valid & (noise<PART5_NOISE_CLEAN))),
    }
    return {
        "noise":noise,"jump":jumps,"flow":flow90,"smart_money":smi,
        "momentum":momentum,"confidence":confidence
    },diag

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
    if exit_deal>1e-12:
        official=1
    if raw>0:
        gp+=exit_deal
    else:
        gl+=exit_deal
    return {"net":net,"gp":gp,"gl":gl,"official":official,"reason":reason,"exit_index":last}

def proposals_for_profile(name,b,feat,t,ask,bid):
    E=b["end_ms"]
    noise=feat["noise"]; flow=feat["flow"]; smi=feat["smart_money"]
    mom=feat["momentum"]; conf=feat["confidence"]
    out=[]
    stage={"feature_bars":0,"condition_bars":0,"no_exec":0,"spread_rejects":0,"eligible":0}
    for j in range(len(E)):
        if E[j]>=STAGE_A_END_MS:
            break
        if not np.isfinite(flow[j]):
            continue
        stage["feature_bars"]+=1
        side=0
        if name=="C01_SOURCE_FLOW_SMI" or name=="C02_FLOW_SMI_MOMENTUM":
            if conf[j]>=FLOW_CONF_MIN:
                if flow[j]>FLOW_LONG_THRESHOLD and smi[j]>0:
                    side=1
                elif flow[j]<FLOW_SHORT_THRESHOLD and smi[j]<0:
                    side=-1
            if name=="C02_FLOW_SMI_MOMENTUM" and side!=0 and side*mom[j]<=0:
                side=0
        elif name=="C03_PART5_CLEAN_IMBALANCE":
            if noise[j]<PART5_NOISE_CLEAN and abs(flow[j])>PART5_OI_ABS:
                side=1 if flow[j]>0 else -1
        if side==0:
            continue
        stage["condition_bars"]+=1
        edge=int(E[j])
        i=int(np.searchsorted(t,edge,side="left"))
        if i>=len(t) or int(t[i])>=STAGE_A_END_MS:
            stage["no_exec"]+=1
            continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            stage["spread_rejects"]+=1
            continue
        stage["eligible"]+=1
        out.append({"decision_index":i,"side":side,"day":int(t[i]//DAY_MS),"bar_index":j})
    return out,stage

def evaluate(props,t,ask,bid):
    rows=[]; accepted=[]; busy=-1; busy_skips=0
    for ev in props:
        i=int(ev["decision_index"])
        if i<=busy:
            busy_skips+=1
            continue
        tr=simulate_trade(i,int(ev["side"]),t,ask,bid)
        rows.append(tr); accepted.append(ev); busy=int(tr["exit_index"])
    return {
        "proposals":len(props),"busy_skips":busy_skips,"trades":len(rows),
        "distinct_days":len({x["day"] for x in accepted}),
        "long":sum(x["side"]>0 for x in accepted),
        "short":sum(x["side"]<0 for x in accepted),
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
    df=pd.read_csv(args.source,compression="gzip",
                   usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709:
        raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]):
        raise SystemExit("Stage-A chronology mismatch")

    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    b=bars(t,bid)
    feat,feature_diag=build_features(b)

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
        if gate["screen_pass"]:
            ordinary.append(name)
        if gate["strong_pass"]:
            strong.append(name)

    def rk(name):
        m=configs[name]["metrics"]
        return (m["direct_net_usd"],m["official_wins"],m["trades"])
    ordinary.sort(key=rk,reverse=True)
    strong.sort(key=rk,reverse=True)

    if strong:
        leader=strong[0]
        decision="ADVANCE_STRONG_OFM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_OFM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader=ordinary[0]
        decision="ADVANCE_ORDINARY_OFM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_OFM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader=None
        decision="RETIRE_OFM_PUBLISHED_THRESHOLD_STAGE_A_NO_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    out={
        "schema":"delta-r037-ofm-stage-a-screen-17as-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_ORDER_FLOW_IMBALANCE_MOMENTUM_STAGE_A_SCREEN",
        "family":"R037-OFM-v1",
        "parent_checkpoint":"R037_PBQ_STAGE_A_SCREEN_CHECKPOINT_17AR",
        "prereg_commit":PREREG_COMMIT,
        "source_sha256":source_sha,
        "stage_a_ticks":len(t),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "signal_timeframe_seconds":60,
        "feature_diagnostics":feature_diag,
        "published_threshold_screen":True,
        "xauusd_threshold_calibration":False,
        "numeric_retuning":False,
        "august_accessed":False,
        "configs":configs,
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
    print(json.dumps({
        "feature_diagnostics":feature_diag,
        "finding":out["finding"],
        "metrics":{k:v["metrics"] for k,v in configs.items()}
    },separators=(",",":")))

if __name__=="__main__":
    main()
