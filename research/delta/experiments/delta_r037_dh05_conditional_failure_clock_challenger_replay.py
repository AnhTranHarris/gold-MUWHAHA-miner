"""DELTA R037 DH05 conditional failure-clock challenger replay — Checkpoint 09T.

Non-promoting causal Stage-A replay of the two categorical routers preregistered in 09S.
No numeric vector retuning. August remains sealed. The current frozen failure clock remains
the scientific control unless this challenger survives causal replay and later anti-overfit QA.

The producer reuses only committed 09L utilities for canonical Stage-A loading/execution.
All generator semantics are implemented here and are fully reconstructible:
- 09C width-2 confirmed M5 swing boundary;
- 09E repeated same-boundary attempt ledger with per-attempt max_probe_age;
- 09F completed acceptance bar must end after qualification;
- 09D signed acceptance-bar body displacement / event M5 ATR;
- conditional max_failure_age clock ownership from 09S;
- optional Checkpoint-08 stage-normalized reversal = reversal-TF ATR14 +
  signed 3-completed-close efficiency path.
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

HIST_TRADES={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
S06_HIST={"signals":672,"trades":615,"wins":307,"net_usd":-101.08}
STAGES=("probe","qualified","accepted","failure","reentry","reclaim","reversal","signal")
EXPECTED_POSTQUAL={
"A03":[6686,998,212,786,441,268,192,192],
"S05":[7727,309,32,277,54,19,9,9],
"S06":[3561,1599,248,1351,1210,695,651,651],
"S09":[7632,201,40,161,63,39,11,11],
"S10":[6440,1300,205,1095,637,309,227,227],
"S16":[7684,130,52,78,32,18,7,7],
}

# Profile semantics are categorical, not fitted.
# 0 CONTROL_CURRENT_NEUTRAL: max_failure starts at FAILURE_CANDIDATE; event M5 ATR; 1-bar efficiency.
# 1 ACCEPTANCE_CLOCK_ROUTER: acceptance_tf=5 -> control; acceptance_tf=15 -> wait until causal reentry to start max_failure.
# 2 CLOCK_TOPOLOGY_ROUTER: acceptance_tf=5 -> control; acceptance_tf=15/reversal_tf=5 -> wait-reentry neutral;
#   acceptance_tf=15/reversal_tf=1 -> wait-reentry + stage-normalized 3-bar reversal.
# 3 UNIVERSAL_WAIT_NEUTRAL: wait-reentry neutral for all vectors (diagnostic).
# 4 UNIVERSAL_CURRENT_STAGE: current clock + stage-normalized reversal for all (diagnostic).
# 5 UNIVERSAL_WAIT_STAGE: wait-reentry + stage-normalized reversal for all (diagnostic).
PROFILES=(
 "CONTROL_CURRENT_NEUTRAL",
 "ACCEPTANCE_CLOCK_ROUTER",
 "CLOCK_TOPOLOGY_ROUTER",
 "UNIVERSAL_WAIT_NEUTRAL",
 "UNIVERSAL_CURRENT_STAGE",
 "UNIVERSAL_WAIT_STAGE",
)

@njit(cache=True)
def detect_clock_router(
    t,mid2,st,ss,sl,m5e,m5a,
    s1e,s1o,s1c,s1a,s5e,s5o,s5c,s5a,s15e,s15o,s15c,
    accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf,profile,
):
    stage=0; oside=0; L=0; evatr=0.; attempt_start=0; qualified_start=0; fstart=0
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True
    lastacc=-1; lastrev=-1; attempt_open=False; attempt_qualified=False; reent=False
    cnt=np.zeros(8,np.int64)
    MAX_SIG=20000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8); nsig=0; overflow=0

    wait_reentry=False; stage_norm=False
    if profile==1:
        wait_reentry = acctf==15
    elif profile==2:
        wait_reentry = acctf==15
        stage_norm = acctf==15 and revtf==1
    elif profile==3:
        wait_reentry=True
    elif profile==4:
        stage_norm=True
    elif profile==5:
        wait_reentry=True; stage_norm=True

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
            if latest_hi and hiel and px>=latest_hi:
                stage=1; oside=1; L=latest_hi; evatr=ae; attempt_start=tm; qualified_start=0
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; reent=False; fstart=0
            elif latest_lo and loel and px<=latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; reent=False; fstart=0
        if stage==0: continue

        if stage<=2:
            inside=oside*(px-L)<0
            if inside:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                attempt_open=True; attempt_qualified=False; qualified_start=0
                attempt_start=tm; cnt[0]+=1
            if attempt_open and (not attempt_qualified) and oside*(px-L)>=probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)
        acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)

        if stage==1:
            if oside*(px-L)>=probeexc*evatr:
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
                fstart=0 if wait_reentry else tm

        if stage==3:
            if recross and not reent:
                reent=True; cnt[4]+=1; stage=4
                if wait_reentry: fstart=tm
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
        rside=-oside
        revatr=evatr
        eff=0.0
        if stage_norm:
            revatr=float(s1a[j1]) if revtf==1 else float(s5a[j5])
            starts=jrev-2
            if starts>=0:
                closes=s1c if revtf==1 else s5c
                net=rside*(closes[jrev]-closes[starts])
                travel=0
                for z in range(starts+1,jrev+1):
                    travel+=abs(closes[z]-closes[z-1])
                eff=net/travel if travel>0 else 0.0
        else:
            eff=1.0 if abs(rc-ro)>0 else 0.0

        disp=rside*(rc-ro)
        if revatr>0 and disp>=revdisp*revatr and eff>=effmin:
            cnt[6]+=1; cnt[7]+=1
            if nsig<MAX_SIG:
                sig_i[nsig]=i; sig_side[nsig]=rside; nsig+=1
            else:
                overflow+=1
            stage=0; oside=0; reent=False; fstart=0
        lastrev=jrev

    return cnt,sig_i[:nsig],sig_side[:nsig],overflow


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    sha=sha256_file(args.source)
    if sha!=CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: "+sha)

    df=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size and np.any(t[1:]<t[:-1]): raise SystemExit("non-monotonic Stage-A ticks")
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid

    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a1=atr14(b1); a5=atr14(b5); a300=atr14(b300)
    st,ss,sl=symmetric_swings(b300,2)

    results={}
    ranking=[]
    for pi,pname in enumerate(PROFILES):
        vectors={}; signal_err=0; trade_err_latch=0; trade_err_plain=0
        for v in VECTORS:
            n,ad,at,mf,mp,pe,rb,rd,em,rt=v
            c,si,ssig,ov=detect_clock_router(
                t,mid,st,ss,sl,b300["end_ms"],a300,
                b1["end_ms"],b1["open"],b1["close"],a1,
                b5["end_ms"],b5["open"],b5["close"],a5,
                b15["end_ms"],b15["open"],b15["close"],
                ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,pi)
            if ov: raise SystemExit("signal overflow "+pname+" "+n)
            if pi==0:
                exp=EXPECTED_POSTQUAL[n]
                got=list(map(int,c))
                if got!=exp:
                    raise SystemExit("CONTROL_POSTQUAL drift "+n+": "+json.dumps(got))
            plain=admit_r9_lifecycle(t,ask,bid,si,ssig,False)
            latch=admit_r9_lifecycle(t,ask,bid,si,ssig,True)
            signal_err+=abs(int(si.size)-HIST_TRADES[n])
            trade_err_plain+=abs(int(plain[3])-HIST_TRADES[n])
            trade_err_latch+=abs(int(latch[3])-HIST_TRADES[n])
            vectors[n]={
              "funnel":dict(zip(STAGES,map(int,c))),
              "generator_signals":int(si.size),"historical_trades":HIST_TRADES[n],
              "one_position_only":{"trades":int(plain[3]),"wins":int(plain[4]),"net_usd":float(plain[7]),"rejected_occupied":int(plain[1]),"rejected_latch":int(plain[2])},
              "position_observation_latch":{"trades":int(latch[3]),"wins":int(latch[4]),"net_usd":float(latch[7]),"rejected_occupied":int(latch[1]),"rejected_latch":int(latch[2])},
            }
        s6=vectors["S06"]
        results[pname]={
          "vectors":vectors,
          "aggregate_signal_vs_historical_trade_abs_error":int(signal_err),
          "aggregate_trade_abs_error_one_position_only":int(trade_err_plain),
          "aggregate_trade_abs_error_position_observation_latch":int(trade_err_latch),
          "s06":{
            "generator_signals":s6["generator_signals"],
            "plain_trades":s6["one_position_only"]["trades"],"plain_wins":s6["one_position_only"]["wins"],"plain_net_usd":s6["one_position_only"]["net_usd"],
            "latch_trades":s6["position_observation_latch"]["trades"],"latch_wins":s6["position_observation_latch"]["wins"],"latch_net_usd":s6["position_observation_latch"]["net_usd"],
            "signal_abs_error":abs(s6["generator_signals"]-S06_HIST["signals"]),
            "plain_trade_abs_error":abs(s6["one_position_only"]["trades"]-S06_HIST["trades"]),
            "latch_trade_abs_error":abs(s6["position_observation_latch"]["trades"]-S06_HIST["trades"]),
            "plain_win_abs_error":abs(s6["one_position_only"]["wins"]-S06_HIST["wins"]),
            "latch_win_abs_error":abs(s6["position_observation_latch"]["wins"]-S06_HIST["wins"]),
            "plain_net_abs_error":abs(s6["one_position_only"]["net_usd"]-S06_HIST["net_usd"]),
            "latch_net_abs_error":abs(s6["position_observation_latch"]["net_usd"]-S06_HIST["net_usd"]),
          }
        }
        ranking.append({
          "profile":pname,
          "signal_error":int(signal_err),
          "trade_error_latch":int(trade_err_latch),
          "trade_error_plain":int(trade_err_plain),
          "s06_signal_abs_error":results[pname]["s06"]["signal_abs_error"],
          "s06_latch_trade_abs_error":results[pname]["s06"]["latch_trade_abs_error"],
          "s06_latch_win_abs_error":results[pname]["s06"]["latch_win_abs_error"],
          "s06_latch_net_abs_error":results[pname]["s06"]["latch_net_abs_error"],
        })

    ranking.sort(key=lambda x:(x["signal_error"],x["trade_error_latch"],x["s06_signal_abs_error"],x["s06_latch_trade_abs_error"],x["s06_latch_win_abs_error"],x["s06_latch_net_abs_error"]))
    control=results["CONTROL_CURRENT_NEUTRAL"]
    topology=results["CLOCK_TOPOLOGY_ROUTER"]
    out={
      "schema":"delta-r037-dh05-conditional-failure-clock-challenger-replay-09t-v1",
      "status":"BOUNDED_CAUSAL_CHALLENGER_REPLAY_COMPLETE_NON_PROMOTING",
      "source_sha256":sha,"stage_a_ticks":int(t.size),"surface":"DUKAS_COINEXX_LIKE_P75",
      "august_accessed":False,"numeric_vector_retune":False,
      "control_postqual_reproduced":True,
      "profiles":results,"ranking":ranking,
      "finding":{
        "predeclared_topology_router_signal_error":topology["aggregate_signal_vs_historical_trade_abs_error"],
        "control_signal_error":control["aggregate_signal_vs_historical_trade_abs_error"],
        "predeclared_topology_router_latch_trade_error":topology["aggregate_trade_abs_error_position_observation_latch"],
        "control_latch_trade_error":control["aggregate_trade_abs_error_position_observation_latch"],
        "promoted":False,
        "selection_rule":"No semantic unfreeze from Stage-A count fit alone. Material improvement must also preserve S06 signal/trade/win/net and then survive anti-overfit validation.",
      },
      "next":"R037_DH05_CONDITIONAL_CLOCK_CHALLENGER_ANTI_OVERFIT_VALIDATION_IF_MATERIAL_ELSE_GENERATOR_PROVENANCE_CONTINUE"
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"ranking":ranking,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
