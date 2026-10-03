"""DELTA R037 DH05 generator ownership via new-boundary release — Checkpoint 09U.

Bounded causal parity reconstruction. This unit tests a middle ground between:
- serial POST_QUAL ownership, which under-produces historically sparse vectors; and
- Checkpoint 09H immediate FAILURE_CANDIDATE decoupling, which massively over-produced.

A downstream failed-break episode may continue independently, but the probe generator is
released only after a NEW causally confirmed width-2 M5 swing boundary identity appears.
No release occurs merely because FAILURE_CANDIDATE, REENTRY, or RECLAIM occurred.

Profiles:
- NEW_ANY_BOUNDARY: any newly confirmed high/low swing releases the generator onto that identity.
- NEW_SAME_SIDE_BOUNDARY: only a new boundary on the original breakout side releases it.
- NEW_OPPOSITE_SIDE_BOUNDARY: only a new boundary on the opposite side releases it.

Frozen: 09C width-2 boundary, 09E per-attempt probe clock, 09F post-qualification
acceptance chronology, 09D body-displacement acceptance, FAILURE_CANDIDATE failure clock,
all numeric vectors, P75 surface, Stage-A window. August sealed.
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
from delta_r037_dh05_conditional_failure_clock_challenger_replay import detect_clock_router

STAGES=("probe","qualified","accepted","failure","reentry","reclaim","reversal","signal")
TARGET={
"A03":[6731,1009,207,797,432,266,187,187],
"S05":[7875,318,28,290,51,15,9,9],
"S06":[3470,1606,245,1358,1211,683,617,617],
"S09":[7748,208,40,168,61,40,9,9],
"S10":[6496,1316,202,1106,623,294,206,206],
"S16":[7870,135,43,92,37,18,8,8]}
HIST_TRADES={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
EXPECTED_POSTQUAL={
"A03":[6686,998,212,786,441,268,192,192],
"S05":[7727,309,32,277,54,19,9,9],
"S06":[3561,1599,248,1351,1210,695,651,651],
"S09":[7632,201,40,161,63,39,11,11],
"S10":[6440,1300,205,1095,637,309,227,227],
"S16":[7684,130,52,78,32,18,7,7]}

PROFILE_NAMES=("NEW_ANY_BOUNDARY","NEW_SAME_SIDE_BOUNDARY","NEW_OPPOSITE_SIDE_BOUNDARY")

@njit(cache=True)
def detect_new_boundary_release(
    t,mid2,st,ss,sl,m5e,m5a,
    s1e,s1o,s1c,s5e,s5o,s5c,s15e,s15o,s15c,
    accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf,profile,
):
    # Generator state: 0 idle, 1 probe, 2 qualified. Once it creates a failure episode
    # it becomes locked until a qualifying newly revealed M5 swing identity releases it.
    stage=0; locked=False; locked_side=0
    oside=0; L=0; evatr=0.; attempt_start=0; qualified_start=0
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True
    lastacc=-1; attempt_open=False; attempt_qualified=False
    cnt=np.zeros(8,np.int64)

    MAX_EP=64
    active=np.zeros(MAX_EP,np.int8)
    estage=np.zeros(MAX_EP,np.int8)
    eoside=np.zeros(MAX_EP,np.int8)
    eL=np.zeros(MAX_EP,np.int64)
    eatr=np.zeros(MAX_EP,np.float64)
    efstart=np.zeros(MAX_EP,np.int64)
    elastrev=np.full(MAX_EP,-1,np.int64)
    max_active=0; overflow=0; releases=0

    MAX_SIG=30000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8); nsig=0; sig_overflow=0

    for i in range(t.size):
        tm=int(t[i]); px=int(mid2[i])

        # New swing identities are processed causally. When locked, only a qualifying
        # NEW identity can release the generator; the released identity is the sole
        # immediately eligible boundary, preventing an old consumed boundary from firing.
        while si<st.size and st[si]<=tm:
            new_side=int(ss[si]); new_level=int(sl[si])
            qualifies=False
            if locked:
                if profile==0:
                    qualifies=True
                elif profile==1:
                    qualifies=(new_side==locked_side)
                else:
                    qualifies=(new_side!=locked_side)
            if new_side>0:
                latest_hi=new_level
            else:
                latest_lo=new_level
            if locked and qualifies:
                locked=False; stage=0; oside=0; L=0; evatr=0.; attempt_start=0; qualified_start=0
                attempt_open=False; attempt_qualified=False; releases+=1
                if new_side>0:
                    hiel=True; loel=False
                else:
                    loel=True; hiel=False
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

        if not locked and stage==0:
            if latest_hi and px<latest_hi: hiel=True
            if latest_lo and px>latest_lo: loel=True
            if latest_hi and hiel and px>=latest_hi:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False
            elif latest_lo and loel and px<=latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False

        if not locked and stage>0:
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
        if (not locked) and stage==2 and jacc>=0 and jacc!=lastacc:
            lastacc=jacc
            q=(qualified_start>0 and acc_end>qualified_start and
               oside*(ac-ao)>=accdisp*evatr and oside*(ac-L)>0)
            if q:
                cnt[2]+=1; stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                accepted_now=True

        if (not locked) and (not accepted_now) and stage==2:
            recross=oside*(px-L)<0
            if tm-attempt_start>=maxprobe or recross:
                cnt[3]+=1
                slot=-1
                for qslot in range(MAX_EP):
                    if active[qslot]==0:
                        slot=qslot; break
                if slot<0:
                    overflow+=1
                else:
                    active[slot]=1; estage[slot]=3; eoside[slot]=oside; eL[slot]=L
                    eatr[slot]=evatr; efstart[slot]=tm; elastrev[slot]=-1
                # Unlike 09H, generator stays locked until a NEW boundary identity reveals.
                locked=True; locked_side=oside
                stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0

        # Downstream failed-break episodes continue independently.
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

    return cnt,sig_i[:nsig],sig_side[:nsig],max_active,overflow,sig_overflow,releases


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

    # Exact current serial POST_QUAL control from the already-durable 09T detector.
    control_vectors={}; control_stage_abs=np.zeros(8,np.int64)
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c,si,ssig,ov=detect_clock_router(
            t,mid,st,ss,sl,b300["end_ms"],a300,
            b1["end_ms"],b1["open"],b1["close"],a1,
            b5["end_ms"],b5["open"],b5["close"],a5,
            b15["end_ms"],b15["open"],b15["close"],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,0)
        got=list(map(int,c))
        if got!=EXPECTED_POSTQUAL[n]: raise SystemExit("serial POST_QUAL control drift "+n+": "+json.dumps(got))
        trg=np.asarray(TARGET[n],np.int64); control_stage_abs+=np.abs(c-trg)
        adm=admit_r9_lifecycle(t,ask,bid,si,ssig,True)
        control_vectors[n]={"funnel":dict(zip(STAGES,got)),"signals":int(si.size),"trades":int(adm[3]),"wins":int(adm[4]),"net_usd":float(adm[7])}
    control={"vectors":control_vectors,"stage_abs_error":dict(zip(STAGES,map(int,control_stage_abs))),"total_abs_error":int(control_stage_abs.sum())}

    results={}; ranking=[]
    for pi,pname in enumerate(PROFILE_NAMES):
        vectors={}; stage_abs=np.zeros(8,np.int64); trade_error=0; max_active=0; ep_over=0; sig_over=0; release_total=0
        for v in VECTORS:
            n,ad,at,mf,mp,pe,rb,rd,em,rt=v
            c,si,ssig,ma,eo,so,rel=detect_new_boundary_release(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],
                b5["end_ms"],b5["open"],b5["close"],
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,pi)
            if eo or so: pass
            trg=np.asarray(TARGET[n],np.int64); stage_abs+=np.abs(c-trg)
            adm=admit_r9_lifecycle(t,ask,bid,si,ssig,True)
            trade_error+=abs(int(adm[3])-HIST_TRADES[n])
            max_active=max(max_active,int(ma)); ep_over+=int(eo); sig_over+=int(so); release_total+=int(rel)
            vectors[n]={
              "target":dict(zip(STAGES,map(int,trg))),"funnel":dict(zip(STAGES,map(int,c))),
              "signals":int(si.size),"historical_trades":HIST_TRADES[n],
              "trades":int(adm[3]),"wins":int(adm[4]),"net_usd":float(adm[7]),
              "max_concurrent_failure_episodes":int(ma),"episode_overflow":int(eo),"signal_overflow":int(so),"generator_releases":int(rel)
            }
        r={"vectors":vectors,"stage_abs_error":dict(zip(STAGES,map(int,stage_abs))),"total_abs_error":int(stage_abs.sum()),
           "aggregate_trade_count_abs_error":int(trade_error),"max_concurrent_failure_episodes":max_active,
           "episode_overflow":ep_over,"signal_overflow":sig_over,"generator_releases":release_total}
        results[pname]=r
        s6=vectors["S06"]
        ranking.append({"profile":pname,"total_abs_error":r["total_abs_error"],"trade_count_abs_error":r["aggregate_trade_count_abs_error"],
                        "s06_signal_abs_error":abs(s6["signals"]-672),"s06_trade_abs_error":abs(s6["trades"]-615),
                        "s06_win_abs_error":abs(s6["wins"]-307),"s06_net_abs_error":abs(s6["net_usd"]+101.08),
                        "max_concurrent_failure_episodes":max_active,"episode_overflow":ep_over,"signal_overflow":sig_over})
    ranking.sort(key=lambda x:(x["total_abs_error"],x["trade_count_abs_error"],x["s06_trade_abs_error"],x["s06_win_abs_error"],x["s06_net_abs_error"]))

    out={
      "schema":"delta-r037-dh05-generator-ownership-new-boundary-release-09u-v1",
      "status":"BOUNDED_QA_COMPLETE",
      "source_sha256":sha,"stage_a_ticks":int(t.size),"surface":"DUKAS_COINEXX_LIKE_P75",
      "august_accessed":False,"numeric_vector_retune":False,
      "control_serial_postqual":control,"profiles":results,"ranking":ranking,
      "finding":{
        "selection_rule":"candidate may carry forward only if new-boundary release materially improves six-vector total funnel parity and trade-density parity without episode/signal overflow or material S06 economic deterioration",
        "leading_profile":ranking[0]["profile"] if ranking else None,
        "parity_complete":False
      },
      "next":"R037_DH05_GENERATOR_OWNERSHIP_REFINE_OR_PROVENANCE_CONTINUE"
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"control_total_abs_error":control["total_abs_error"],"ranking":ranking},separators=(",",":")))

if __name__=="__main__": main()
