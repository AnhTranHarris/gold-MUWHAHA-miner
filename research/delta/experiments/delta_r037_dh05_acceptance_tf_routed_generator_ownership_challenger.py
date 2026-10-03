"""DELTA R037 DH05 acceptance-timeframe routed generator ownership challenger — Checkpoint 09W.

NON-PROMOTING causal challenger.

Predeclared categorical architecture from durable 09H + 09S evidence:
- acceptance_tf == S5: retain exact serial POST_QUAL ownership control.
- acceptance_tf == S15: release the upstream generator at FAILURE_CANDIDATE
  while the failed-break episode continues independently toward
  reentry/reclaim/reversal (the 09H decoupled POST_QUAL architecture).

No numeric threshold is changed. The routing key is an existing frozen vector field,
not a fitted price/time threshold. S06 economics are a mandatory veto. A material
Stage-A improvement is only a harvested candidate and requires anti-overfit /
provenance validation before any semantic promotion.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_runtime_primitives import (
    CANONICAL_JAN_SHA256, STAGE_A_END_MS, VECTORS, atomic_write_json,
    atr14, bars, bidx, p75, sha256_file, symmetric_swings, admit_r9_lifecycle,
)
from delta_r037_dh05_conditional_failure_clock_challenger_replay import (
    detect_clock_router, EXPECTED_POSTQUAL, HIST_TRADES, S06_HIST, STAGES,
)

TARGET={
"A03":[6731,1009,207,797,432,266,187,187],
"S05":[7875,318,28,290,51,15,9,9],
"S06":[3470,1606,245,1358,1211,683,617,617],
"S09":[7748,208,40,168,61,40,9,9],
"S10":[6496,1316,202,1106,623,294,206,206],
"S16":[7870,135,43,92,37,18,8,8]}

@njit(cache=True)
def detect_decoupled_postqual_signals(
    t,mid2,st,ss,sl,m5e,m5a,
    s1e,s1o,s1c,s5e,s5o,s5c,s15e,s15o,s15c,
    accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf,
):
    stage=0; oside=0; L=0; evatr=0.; attempt_start=0; qualified_start=0
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True
    lastacc=-1; attempt_open=False; attempt_qualified=False
    cnt=np.zeros(8,np.int64)

    MAX_EP=64
    active=np.zeros(MAX_EP,np.int8); estage=np.zeros(MAX_EP,np.int8)
    eoside=np.zeros(MAX_EP,np.int8); eL=np.zeros(MAX_EP,np.int64)
    eatr=np.zeros(MAX_EP,np.float64); efstart=np.zeros(MAX_EP,np.int64)
    elastrev=np.full(MAX_EP,-1,np.int64)
    max_active=0; ep_overflow=0

    MAX_SIG=30000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8)
    nsig=0; sig_overflow=0

    for i in range(t.size):
        tm=int(t[i]); px=int(mid2[i])
        while si<st.size and st[si]<=tm:
            if ss[si]>0: latest_hi=int(sl[si])
            else: latest_lo=int(sl[si])
            si+=1

        jm=bidx(m5e,tm)
        if jm<13: continue
        ae=float(m5a[jm])
        if ae<=0: continue

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)
        acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)

        # Independent upstream generator: exact 09H immediate release architecture.
        if stage==0:
            if latest_hi and px<latest_hi: hiel=True
            if latest_lo and px>latest_lo: loel=True
            if latest_hi and hiel and px>=latest_hi:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False
            elif latest_lo and loel and px<=latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False

        if stage>0:
            inside=oside*(px-L)<0
            if inside:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                attempt_open=True; attempt_qualified=False; qualified_start=0
                attempt_start=tm; cnt[0]+=1
            if attempt_open and (not attempt_qualified) and oside*(px-L)>=probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1
            if stage==1:
                if oside*(px-L)>=probeexc*evatr:
                    stage=2
                    if qualified_start==0: qualified_start=tm
                elif tm-attempt_start>maxprobe:
                    stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0

        accepted_now=False
        if stage==2 and jacc>=0 and jacc!=lastacc:
            lastacc=jacc
            q=(qualified_start>0 and acc_end>qualified_start and
               oside*(ac-ao)>=accdisp*evatr and oside*(ac-L)>0)
            if q:
                cnt[2]+=1; stage=0; oside=0
                attempt_open=False; attempt_qualified=False; qualified_start=0
                accepted_now=True

        if (not accepted_now) and stage==2:
            recross=oside*(px-L)<0
            if tm-attempt_start>=maxprobe or recross:
                cnt[3]+=1
                slot=-1
                for qslot in range(MAX_EP):
                    if active[qslot]==0:
                        slot=qslot; break
                if slot<0:
                    ep_overflow+=1
                else:
                    active[slot]=1; estage[slot]=3; eoside[slot]=oside; eL[slot]=L
                    eatr[slot]=evatr; efstart[slot]=tm; elastrev[slot]=-1
                # Critical 09H ownership release.
                stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0

        alive=0
        jrev=j1 if revtf==1 else j5
        rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
        ro=s1o[j1] if revtf==1 and j1>=0 else (s5o[j5] if j5>=0 else 0)
        for e in range(MAX_EP):
            if active[e]==0: continue
            eo=int(eoside[e]); er=eo*(px-int(eL[e]))<0
            if estage[e]==3:
                if er:
                    cnt[4]+=1; estage[e]=4
                elif tm-int(efstart[e])>maxfail:
                    active[e]=0; continue
            elif tm-int(efstart[e])>maxfail:
                active[e]=0; continue

            if estage[e]>=4 and jrev>=0 and jrev!=elastrev[e]:
                if estage[e]==4 and (-eo)*(rc-int(eL[e]))>=reclaim*float(eatr[e]):
                    cnt[5]+=1; estage[e]=5
                if estage[e]>=5:
                    disp=(-eo)*(rc-ro)
                    eff=1.0 if abs(rc-ro)>0 else 0.0
                    if disp>=revdisp*float(eatr[e]) and eff>=effmin:
                        cnt[6]+=1; cnt[7]+=1
                        if nsig<MAX_SIG:
                            sig_i[nsig]=i; sig_side[nsig]=-eo; nsig+=1
                        else:
                            sig_overflow+=1
                        active[e]=0; continue
                elastrev[e]=jrev
            if active[e]!=0: alive+=1
        if alive>max_active: max_active=alive

    return cnt,sig_i[:nsig],sig_side[:nsig],max_active,ep_overflow,sig_overflow


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    sha=sha256_file(args.source)
    if sha!=CANONICAL_JAN_SHA256: raise SystemExit("canonical January SHA mismatch: "+sha)
    df=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size and np.any(t[1:]<t[:-1]): raise SystemExit("non-monotonic Stage-A ticks")
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a1=atr14(b1); a5=atr14(b5); a300=atr14(b300)
    st,ss,sl=symmetric_swings(b300,2)

    control_vectors={}; control_stage_abs=np.zeros(8,np.int64); control_trade_error=0
    routed_vectors={}; routed_stage_abs=np.zeros(8,np.int64); routed_trade_error=0
    max_active=0; ep_over=0; sig_over=0

    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v

        cc,csi,cssig,cov=detect_clock_router(
            t,mid,st,ss,sl,b300["end_ms"],a300,
            b1["end_ms"],b1["open"],b1["close"],a1,
            b5["end_ms"],b5["open"],b5["close"],a5,
            b15["end_ms"],b15["open"],b15["close"],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,0)
        got=list(map(int,cc))
        if cov: raise SystemExit("control signal overflow "+n)
        if got!=EXPECTED_POSTQUAL[n]: raise SystemExit("serial POST_QUAL control drift "+n+": "+json.dumps(got))
        trg=np.asarray(TARGET[n],np.int64); control_stage_abs+=np.abs(cc-trg)
        cadm=admit_r9_lifecycle(t,ask,bid,csi,cssig,True)
        control_trade_error+=abs(int(cadm[3])-HIST_TRADES[n])
        control_vectors[n]={"funnel":dict(zip(STAGES,got)),"signals":int(csi.size),"trades":int(cadm[3]),"wins":int(cadm[4]),"net_usd":float(cadm[7])}

        if at==5:
            rc,ri,rsig=cc,csi,cssig
            ma=0; eo=0; so=0; ownership="SERIAL_POST_QUAL"
        else:
            rc,ri,rsig,ma,eo,so=detect_decoupled_postqual_signals(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],
                b5["end_ms"],b5["open"],b5["close"],
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt)
            ownership="FAILURE_CANDIDATE_DECOUPLED_POST_QUAL"
        if so: raise SystemExit("routed signal overflow "+n)
        routed_stage_abs+=np.abs(rc-trg)
        radm=admit_r9_lifecycle(t,ask,bid,ri,rsig,True)
        routed_trade_error+=abs(int(radm[3])-HIST_TRADES[n])
        max_active=max(max_active,int(ma)); ep_over+=int(eo); sig_over+=int(so)
        routed_vectors[n]={
            "ownership":ownership,"target":dict(zip(STAGES,map(int,trg))),
            "funnel":dict(zip(STAGES,map(int,rc))),"signals":int(ri.size),
            "historical_trades":HIST_TRADES[n],"trades":int(radm[3]),
            "wins":int(radm[4]),"net_usd":float(radm[7]),
            "max_concurrent_failure_episodes":int(ma),"episode_overflow":int(eo)
        }

    control={"vectors":control_vectors,"stage_abs_error":dict(zip(STAGES,map(int,control_stage_abs))),
             "total_abs_error":int(control_stage_abs.sum()),"aggregate_trade_count_abs_error":int(control_trade_error)}
    routed={"vectors":routed_vectors,"stage_abs_error":dict(zip(STAGES,map(int,routed_stage_abs))),
            "total_abs_error":int(routed_stage_abs.sum()),"aggregate_trade_count_abs_error":int(routed_trade_error),
            "max_concurrent_failure_episodes":int(max_active),"episode_overflow":int(ep_over),"signal_overflow":int(sig_over)}
    s6=routed_vectors["S06"]
    routed["s06"]={
        "signals":s6["signals"],"trades":s6["trades"],"wins":s6["wins"],"net_usd":s6["net_usd"],
        "signal_abs_error":abs(s6["signals"]-S06_HIST["signals"]),
        "trade_abs_error":abs(s6["trades"]-S06_HIST["trades"]),
        "win_abs_error":abs(s6["wins"]-S06_HIST["wins"]),
        "net_abs_error":abs(s6["net_usd"]-S06_HIST["net_usd"])
    }

    out={
      "schema":"delta-r037-dh05-acceptance-tf-routed-generator-ownership-09w-v1",
      "status":"BOUNDED_CAUSAL_CHALLENGER_COMPLETE_NON_PROMOTING",
      "source_sha256":sha,"stage_a_ticks":int(t.size),"surface":"DUKAS_COINEXX_LIKE_P75",
      "august_accessed":False,"numeric_vector_retune":False,
      "router":{"acceptance_tf_S5":"SERIAL_POST_QUAL","acceptance_tf_S15":"FAILURE_CANDIDATE_DECOUPLED_POST_QUAL"},
      "control_serial_postqual":control,"routed_candidate":routed,
      "finding":{
        "stage_error_improvement":int(control["total_abs_error"]-routed["total_abs_error"]),
        "trade_error_improvement":int(control["aggregate_trade_count_abs_error"]-routed["aggregate_trade_count_abs_error"]),
        "s06_economic_veto_triggered":bool(
            routed["s06"]["trade_abs_error"]>abs(control_vectors["S06"]["trades"]-S06_HIST["trades"]) or
            routed["s06"]["win_abs_error"]>abs(control_vectors["S06"]["wins"]-S06_HIST["wins"]) or
            routed["s06"]["net_abs_error"]>abs(control_vectors["S06"]["net_usd"]-S06_HIST["net_usd"])
        ),
        "promoted":False,
        "anti_overfit_required_if_material":True,
        "selection_rule":"Material Stage-A improvement may be harvested only as a challenger; no semantic promotion until anti-overfit/provenance validation."
      },
      "next":"R037_DH05_ACCEPTANCE_TF_ROUTED_OWNERSHIP_ANTI_OVERFIT_IF_MATERIAL_ELSE_GENERATOR_PROVENANCE_CONTINUE"
    }
    atomic_write_json(args.output,out)
    print(json.dumps({
      "control_total_abs_error":control["total_abs_error"],
      "routed_total_abs_error":routed["total_abs_error"],
      "control_trade_error":control["aggregate_trade_count_abs_error"],
      "routed_trade_error":routed["aggregate_trade_count_abs_error"],
      "routed_stage_abs_error":routed["stage_abs_error"],
      "routed_signals":{n:routed_vectors[n]["signals"] for n in routed_vectors},
      "routed_trades":{n:routed_vectors[n]["trades"] for n in routed_vectors},
      "s06":routed["s06"],"max_active":max_active
    },separators=(",",":")))

if __name__=="__main__": main()
