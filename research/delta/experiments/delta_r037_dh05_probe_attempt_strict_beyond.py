"""DELTA R037 DH05 causal probe-attempt identity parity — Checkpoint 10D.

Preregistered after durable 10C.  This unit tests one provenance-backed semantic only:
the original DH-05 white paper defines PROBE as midpoint trading *beyond* L, while
the current clean-room attempt ledger counts a boundary touch as a new probe attempt.

Profiles
--------
STRICT_REATTEMPT_BEYOND:
    Initial event seeding is unchanged.  After causal rearm, a new same-boundary
    probe attempt opens/counts only when signed price displacement is strictly > 0.

STRICT_ALL_BEYOND:
    Same repeated-attempt rule, and initial event seeding also requires price to
    move strictly beyond the eligible boundary rather than merely touch it.

All 09Z ownership, clocks, acceptance, failure, reclaim, reversal and execution
semantics are unchanged. No numeric vector, boundary source, or width is retuned.
The producer fails closed unless the exact durable 09Z control is reproduced first.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_runtime_primitives import (
    CANONICAL_JAN_SHA256,
    STAGE_A_END_MS,
    VECTORS,
    admit_r9_lifecycle,
    atr14,
    atomic_write_json,
    bars,
    bidx,
    p75,
    sha256_file,
    symmetric_swings,
)
from delta_r037_dh05_conditional_failure_clock_challenger_replay import (
    HIST_TRADES,
    S06_HIST,
    STAGES,
    detect_clock_router,
)
from delta_r037_dh05_short_probe_relative_acceptance_bar_ownership_challenger import (
    detect_decoupled_postqual_signals,
)

TARGET={
"A03":[6731,1009,207,797,432,266,187,187],
"S05":[7875,318,28,290,51,15,9,9],
"S06":[3470,1606,245,1358,1211,683,617,617],
"S09":[7748,208,40,168,61,40,9,9],
"S10":[6496,1316,202,1106,623,294,206,206],
"S16":[7870,135,43,92,37,18,8,8]}

EXPECTED_09Z={
"A03":[6686,998,212,786,441,268,192,192],
"S05":[7818,315,34,281,56,20,9,9],
"S06":[3561,1599,248,1351,1210,695,651,651],
"S09":[7856,219,44,175,65,41,11,11],
"S10":[6440,1300,205,1095,637,309,227,227],
"S16":[7778,134,53,81,33,19,8,8]}


@njit(cache=True)
def detect_serial_strict(
    t,mid2,st,ss,sl,m5e,m5a,
    s1e,s1o,s1c,s5e,s5o,s5c,s15e,s15o,s15c,
    accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf,
    strict_initial,strict_reattempt,
):
    stage=0; oside=0; L=0; evatr=0.; attempt_start=0; qualified_start=0; fstart=0
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True
    lastacc=-1; lastrev=-1; attempt_open=False; attempt_qualified=False; reent=False
    cnt=np.zeros(8,np.int64)
    MAX_SIG=20000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8); nsig=0; overflow=0

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

        if stage==0:
            if latest_hi and px<latest_hi: hiel=True
            if latest_lo and px>latest_lo: loel=True
            hi_cross = latest_hi and hiel and (px>latest_hi if strict_initial else px>=latest_hi)
            lo_cross = latest_lo and loel and (px<latest_lo if strict_initial else px<=latest_lo)
            if hi_cross:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; reent=False; fstart=0
            elif lo_cross:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; reent=False; fstart=0
        if stage==0: continue

        if stage<=2:
            signed=oside*(px-L)
            if signed<0:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                can_open = signed>0 if strict_reattempt else signed>=0
                if can_open:
                    attempt_open=True; attempt_qualified=False; qualified_start=0
                    attempt_start=tm; cnt[0]+=1
            if attempt_open and (not attempt_qualified) and signed>=probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)
        acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)

        if stage==1:
            signed=oside*(px-L)
            if signed>=probeexc*evatr:
                stage=2
                if qualified_start==0: qualified_start=tm
            elif tm-attempt_start>maxprobe:
                stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                continue
        if stage<2: continue

        if stage==2 and jacc>=0 and jacc!=lastacc:
            lastacc=jacc
            q=(qualified_start>0 and acc_end>qualified_start and
               oside*(ac-ao)>=accdisp*evatr and oside*(ac-L)>0)
            if q:
                cnt[2]+=1; stage=0; oside=0; attempt_open=False; attempt_qualified=False
                qualified_start=0; fstart=0; reent=False
                continue

        recross=oside*(px-L)<0
        if stage==2:
            if tm-attempt_start>=maxprobe or recross:
                stage=3; cnt[3]+=1; attempt_open=False; attempt_qualified=False; qualified_start=0
                fstart=tm

        if stage==3:
            if recross and not reent:
                reent=True; cnt[4]+=1; stage=4
            elif fstart and tm-fstart>maxfail:
                stage=0; oside=0; reent=False; fstart=0
                continue
        elif stage>=4 and fstart and tm-fstart>maxfail:
            stage=0; oside=0; reent=False; fstart=0
            continue

        if stage<4: continue
        jrev=j1 if revtf==1 else j5
        rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
        if stage==4 and jrev>=0 and jrev!=lastrev:
            if (-oside)*(rc-L)>=reclaim*evatr:
                cnt[5]+=1; stage=5
        if stage<5 or jrev<0 or jrev==lastrev: continue

        ro=s1o[j1] if revtf==1 else s5o[j5]
        disp=(-oside)*(rc-ro)
        eff=1.0 if abs(rc-ro)>0 else 0.0
        if disp>=revdisp*evatr and eff>=effmin:
            cnt[6]+=1; cnt[7]+=1
            if nsig<MAX_SIG:
                sig_i[nsig]=i; sig_side[nsig]=-oside; nsig+=1
            else: overflow+=1
            stage=0; oside=0; reent=False; fstart=0
        lastrev=jrev

    return cnt,sig_i[:nsig],sig_side[:nsig],overflow


@njit(cache=True)
def detect_decoupled_strict(
    t,mid2,st,ss,sl,m5e,m5a,
    s1e,s1o,s1c,s5e,s5o,s5c,s15e,s15o,s15c,
    accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf,
    strict_initial,strict_reattempt,
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

        if stage==0:
            if latest_hi and px<latest_hi: hiel=True
            if latest_lo and px>latest_lo: loel=True
            hi_cross = latest_hi and hiel and (px>latest_hi if strict_initial else px>=latest_hi)
            lo_cross = latest_lo and loel and (px<latest_lo if strict_initial else px<=latest_lo)
            if hi_cross:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False
            elif lo_cross:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False

        if stage>0:
            signed=oside*(px-L)
            if signed<0:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                can_open=signed>0 if strict_reattempt else signed>=0
                if can_open:
                    attempt_open=True; attempt_qualified=False; qualified_start=0
                    attempt_start=tm; cnt[0]+=1
            if attempt_open and (not attempt_qualified) and signed>=probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1
            if stage==1:
                if signed>=probeexc*evatr:
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
                if slot<0: ep_overflow+=1
                else:
                    active[slot]=1; estage[slot]=3; eoside[slot]=oside; eL[slot]=L
                    eatr[slot]=evatr; efstart[slot]=tm; elastrev[slot]=-1
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
                        else: sig_overflow+=1
                        active[e]=0; continue
                elastrev[e]=jrev
            if active[e]!=0: alive+=1
        if alive>max_active: max_active=alive

    return cnt,sig_i[:nsig],sig_side[:nsig],max_active,ep_overflow,sig_overflow


def run_profile(t,mid,ask,bid,st,ss,sl,b1,a1,b5,a5,b15,b300,a300,strict_initial,strict_reattempt):
    vectors={}; stage_abs=np.zeros(8,np.int64); signed=np.zeros(8,np.int64); trade_error=0
    max_active=0; ep_over=0
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        if mp>=at:
            cnt,si,sd,ov=detect_serial_strict(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],
                b5["end_ms"],b5["open"],b5["close"],
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,
                strict_initial,strict_reattempt)
            if ov: raise SystemExit("serial signal overflow "+n)
            ma=0; eo=0
        else:
            cnt,si,sd,ma,eo,ov=detect_decoupled_strict(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],
                b5["end_ms"],b5["open"],b5["close"],
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,
                strict_initial,strict_reattempt)
            if ov: raise SystemExit("decoupled signal overflow "+n)
        trg=np.asarray(TARGET[n],np.int64); err=np.abs(cnt-trg)
        stage_abs+=err; signed+=cnt-trg
        adm=admit_r9_lifecycle(t,ask,bid,si,sd,True)
        trades=int(adm[3]); wins=int(adm[4]); net=float(adm[7])
        trade_error+=abs(trades-HIST_TRADES[n])
        max_active=max(max_active,int(ma)); ep_over+=int(eo)
        vectors[n]={
          "target":dict(zip(STAGES,map(int,trg))),
          "actual":dict(zip(STAGES,map(int,cnt))),
          "signed_error_actual_minus_target":dict(zip(STAGES,map(int,cnt-trg))),
          "abs_error":dict(zip(STAGES,map(int,err))),
          "signals":int(si.size),"trades":trades,"wins":wins,"net_usd":net}
    return {
      "vectors":vectors,
      "stage_abs_error":dict(zip(STAGES,map(int,stage_abs))),
      "stage_signed_error_actual_minus_target":dict(zip(STAGES,map(int,signed))),
      "total_abs_error":int(stage_abs.sum()),
      "aggregate_trade_count_abs_error":int(trade_error),
      "max_concurrent_failure_episodes":int(max_active),
      "episode_overflow":int(ep_over)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    sha=sha256_file(args.source)
    if sha!=CANONICAL_JAN_SHA256: raise SystemExit("canonical January SHA mismatch: "+sha)
    df=pd.read_csv(args.source,compression="gzip",
                   usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size and np.any(t[1:]<t[:-1]): raise SystemExit("non-monotonic Stage-A ticks")
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a1=atr14(b1); a5=atr14(b5); a300=atr14(b300)
    st,ss,sl=symmetric_swings(b300,2)

    # Exact 09Z control uses the already-durable implementations.
    control_vectors={}; control_stage_abs=np.zeros(8,np.int64); control_trade_error=0
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        if mp>=at:
            cnt,si,sd,ov=detect_clock_router(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],a1,
                b5["end_ms"],b5["open"],b5["close"],a5,
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,0)
            if ov: raise SystemExit("control signal overflow "+n)
        else:
            cnt,si,sd,ma,eo,ov=detect_decoupled_postqual_signals(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],
                b5["end_ms"],b5["open"],b5["close"],
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt)
            if ov: raise SystemExit("control signal overflow "+n)
        got=list(map(int,cnt))
        if got!=EXPECTED_09Z[n]:
            raise SystemExit("09Z control drift "+n+": "+json.dumps({"got":got,"expected":EXPECTED_09Z[n]}))
        trg=np.asarray(TARGET[n],np.int64); control_stage_abs+=np.abs(cnt-trg)
        adm=admit_r9_lifecycle(t,ask,bid,si,sd,True)
        control_trade_error+=abs(int(adm[3])-HIST_TRADES[n])
        control_vectors[n]={"actual":dict(zip(STAGES,got)),"trades":int(adm[3]),"wins":int(adm[4]),"net_usd":float(adm[7])}

    control={"vectors":control_vectors,
      "stage_abs_error":dict(zip(STAGES,map(int,control_stage_abs))),
      "total_abs_error":int(control_stage_abs.sum()),
      "aggregate_trade_count_abs_error":int(control_trade_error)}
    if control["stage_abs_error"]["probe"]!=449 or control["total_abs_error"]!=782:
        raise SystemExit("09Z aggregate control drift: "+json.dumps(control["stage_abs_error"]))

    profiles={
      "STRICT_REATTEMPT_BEYOND":run_profile(t,mid,ask,bid,st,ss,sl,b1,a1,b5,a5,b15,b300,a300,False,True),
      "STRICT_ALL_BEYOND":run_profile(t,mid,ask,bid,st,ss,sl,b1,a1,b5,a5,b15,b300,a300,True,True),
    }

    ranking=[]
    cprobe=control["stage_abs_error"]["probe"]; ctotal=control["total_abs_error"]
    s6c=control["vectors"]["S06"]
    c_s6_err=(abs(s6c["trades"]-S06_HIST["trades"]),
              abs(s6c["wins"]-S06_HIST["wins"]),
              abs(s6c["net_usd"]-S06_HIST["net_usd"]))
    for name,p in profiles.items():
        s6=p["vectors"]["S06"]
        n_s6_err=(abs(s6["trades"]-S06_HIST["trades"]),
                  abs(s6["wins"]-S06_HIST["wins"]),
                  abs(s6["net_usd"]-S06_HIST["net_usd"]))
        veto=(n_s6_err[0]>c_s6_err[0] or n_s6_err[1]>c_s6_err[1] or n_s6_err[2]>c_s6_err[2])
        p["s06_economic_veto"]=bool(veto)
        ranking.append({
          "profile":name,
          "probe_abs_error_improvement":int(cprobe-p["stage_abs_error"]["probe"]),
          "total_abs_error_improvement":int(ctotal-p["total_abs_error"]),
          "trade_count_abs_error_improvement":int(control["aggregate_trade_count_abs_error"]-p["aggregate_trade_count_abs_error"]),
          "s06_economic_veto":bool(veto),
          "carry_forward_eligible":bool(p["stage_abs_error"]["probe"]<cprobe and p["total_abs_error"]<ctotal and not veto)})
    ranking.sort(key=lambda x:(not x["carry_forward_eligible"],-x["probe_abs_error_improvement"],-x["total_abs_error_improvement"]))

    out={
      "schema":"delta-r037-dh05-probe-attempt-strict-beyond-10d-v1",
      "status":"BOUNDED_CAUSAL_ATTEMPT_IDENTITY_RECONCILIATION_COMPLETE",
      "parent":"R037_DH05_PROBE_RESIDUAL_BOUNDARY_EPOCH_CHECKPOINT_10C",
      "source_sha256":sha,"stage_a_ticks":int(t.size),"surface":"DUKAS_COINEXX_LIKE_P75",
      "august_accessed":False,"numeric_vector_retune":False,"boundary_source_retune":False,"width_retune":False,
      "provenance":{"source":"original DH-05 white paper","definition":"PROBE = midpoint trades beyond L in direction d","current_mismatch":"clean-room attempt creation permits equality touch at L"},
      "control_09z":control,"profiles":profiles,"ranking":ranking,
      "finding":{"leading_profile":ranking[0]["profile"],"carry_forward_eligible":ranking[0]["carry_forward_eligible"],
                 "selection_rule":"carry only if probe and total funnel error both improve with no S06 economic veto"},
      "next_if_positive":"R037_DH05_STRICT_BEYOND_ATTEMPT_IDENTITY_ANTI_OVERFIT_VALIDATION",
      "next_if_negative":"R037_DH05_PROBE_RESIDUAL_ATTEMPT_REARM_COMPLETION_PROVENANCE_RECONCILIATION"}
    atomic_write_json(args.output,out)
    print(json.dumps({
      "control_probe_error":cprobe,"control_total_error":ctotal,
      "profiles":{k:{"probe_error":v["stage_abs_error"]["probe"],"total_error":v["total_abs_error"],
                       "trade_error":v["aggregate_trade_count_abs_error"],"s06_veto":v["s06_economic_veto"],
                       "probe_counts":{n:v["vectors"][n]["actual"]["probe"] for n in v["vectors"]}}
                  for k,v in profiles.items()},
      "ranking":ranking},separators=(",",":")))


if __name__=="__main__":
    main()
