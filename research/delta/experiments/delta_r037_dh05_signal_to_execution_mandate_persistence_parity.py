"""DELTA R037 DH05 signal-to-execution mandate persistence parity — Checkpoint 09M.

Bounded clean-room parity diagnostic. The generator is frozen to the durable 09F POST_QUAL
one-shot signal chronology embedded in the committed 09L parent producer. This unit tests only
whether one causal generator signal may remain an execution-side authorization for later
admissions while the original frozen failure episode remains valid.

No generator signal is manufactured, max_failure_age is never refreshed/extended, no frozen
DH05 numeric vector is retuned, August remains sealed, and no MQL5 work is authorized.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from numba import njit

PARENT_PATH = Path(__file__).with_name("delta_r037_dh05_post_signal_intrabar_rearm_edge_parity.py")
_spec = importlib.util.spec_from_file_location("delta_r037_09l_parent", PARENT_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load 09L parent: {PARENT_PATH}")
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

CANONICAL_JAN_SHA256 = P.CANONICAL_JAN_SHA256
STAGE_A_END_MS = P.STAGE_A_END_MS
VECTORS = P.VECTORS
STAGES = P.STAGES
bidx = P.bidx

HIST_TRADES = {"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
EXPECTED_POSTQUAL_FUNNEL = {
    "A03":[6686,998,212,786,441,268,192,192],
    "S05":[7727,309,32,277,54,19,9,9],
    "S06":[3561,1599,248,1351,1210,695,651,651],
    "S09":[7632,201,40,161,63,39,11,11],
    "S10":[6440,1300,205,1095,637,309,227,227],
    "S16":[7684,130,52,78,32,18,7,7],
}
MODES = {
    "IMMEDIATE_TO_FAILURE_EXPIRY":0,
    "IMMEDIATE_UNTIL_BOUNDARY_RETAKE":1,
    "REVERSAL_BAR_RECONFIRM":2,
    "STOP_ONLY_REVERSAL_RECONFIRM":3,
    "ORIGINAL_BOUNDARY_RECYCLE":4,
    "STOP_ONLY_IMMEDIATE":5,
}


@njit(cache=True)
def detect_execution_mandates(
    t, mid2, st, ss, sl, m5e, m5a, s1e, s1o, s1c, s5e, s5o, s5c,
    s15e, s15o, s15c, accdisp, acctf, maxfail, maxprobe, probeexc,
    reclaim, revdisp, effmin, revtf,
):
    """Reproduce 09F POST_QUAL one-shot signals and attach original failure metadata."""
    stage=0; oside=0; L=0; evatr=0.0; attempt_start=0; qualified_start=0
    fstart=0; reent=False
    latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True; lastacc=-1; lastrev=-1
    attempt_open=False; attempt_qualified=False; event_id=0
    cnt=np.zeros(8,np.int64)
    MAX_SIG=100000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8)
    sig_event=np.empty(MAX_SIG,np.int64); sig_expiry=np.empty(MAX_SIG,np.int64)
    sig_L=np.empty(MAX_SIG,np.int64); sig_oside=np.empty(MAX_SIG,np.int8)
    sig_atr=np.empty(MAX_SIG,np.float64)
    nsig=0; overflow=0

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
                hiel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; event_id+=1
            elif latest_lo and loel and px<=latest_lo:
                stage=1; oside=-1; L=latest_lo; evatr=ae; attempt_start=tm; qualified_start=0
                loel=False; cnt[0]+=1; attempt_open=True; attempt_qualified=False; event_id+=1
        if stage==0: continue

        if stage<=2:
            inside=oside*(px-L)<0
            if inside:
                attempt_open=False; attempt_qualified=False; qualified_start=0
            elif not attempt_open:
                attempt_open=True; attempt_qualified=False; qualified_start=0; cnt[0]+=1; attempt_start=tm
            if attempt_open and (not attempt_qualified) and oside*(px-L)>=probeexc*evatr:
                attempt_qualified=True; qualified_start=tm; cnt[1]+=1

        j1=bidx(s1e,tm); j5=bidx(s5e,tm); j15=bidx(s15e,tm)
        jacc=j5 if acctf==5 else j15
        ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
        ao=s5o[j5] if acctf==5 and j5>=0 else (s15o[j15] if j15>=0 else 0)

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
            acc_end=s5e[j5] if acctf==5 and j5>=0 else (s15e[j15] if j15>=0 else 0)
            post_qual_bar=acc_end>qualified_start if qualified_start>0 else False
            q=oside*(ac-ao)>=accdisp*evatr and oside*(ac-L)>0 and post_qual_bar
            if q:
                cnt[2]+=1; stage=0; oside=0; attempt_open=False; attempt_qualified=False; qualified_start=0
                continue

        recross=oside*(px-L)<0
        if stage==2 and (tm-attempt_start>=maxprobe or recross):
            stage=3; cnt[3]+=1; fstart=tm; attempt_open=False; attempt_qualified=False; qualified_start=0

        if stage==3:
            if recross and not reent:
                reent=True; cnt[4]+=1; stage=4
            elif fstart and tm-fstart>maxfail:
                stage=0; oside=0; reent=False; continue
        elif stage>=4 and fstart and tm-fstart>maxfail:
            stage=0; oside=0; reent=False; continue
        if stage<4: continue

        jrev=j1 if revtf==1 else j5
        rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
        if stage==4 and jrev>=0 and jrev!=lastrev and (-oside)*(rc-L)>=reclaim*evatr:
            cnt[5]+=1; stage=5
        if stage<5 or jrev<0 or jrev==lastrev: continue

        ro=s1o[j1] if revtf==1 else s5o[j5]
        disp=(-oside)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0
        if disp>=revdisp*evatr and eff>=effmin:
            cnt[6]+=1; cnt[7]+=1
            if nsig<MAX_SIG:
                sig_i[nsig]=i; sig_side[nsig]=-oside; sig_event[nsig]=event_id
                sig_expiry[nsig]=fstart+maxfail; sig_L[nsig]=L; sig_oside[nsig]=oside; sig_atr[nsig]=evatr
                nsig+=1
            else:
                overflow+=1
            stage=0; oside=0; reent=False
        lastrev=jrev

    return (cnt,sig_i[:nsig],sig_side[:nsig],sig_event[:nsig],sig_expiry[:nsig],
            sig_L[:nsig],sig_oside[:nsig],sig_atr[:nsig],overflow)


@njit(cache=True)
def admit_r9_execution_mandate(
    t, ask, bid, mid2, s1e, s1o, s1c, s5e, s5o, s5c,
    sig_i, sig_side, sig_event, sig_expiry, sig_L, sig_oside, sig_atr,
    revtf, revdisp, effmin, mode,
):
    """Frozen R9 lifecycle plus one active latest-signal mandate and observation latch."""
    STOP=300; TRAIL_ACT=100; TRAIL_DIST=30
    n=sig_i.size; k=0
    admitted=0; closed=0; wins=0; gp=0.0; gl=0.0
    occupied_signals=0; queued_signals=0; reentries=0; expired=0; boundary_cancel=0; maxhold_cancel=0
    balance=100000.0; peak=balance; maxdd=0.0; hold_sum=0.0
    pos=0; entry=0; stop=0; entrysec=0; last_i=t.size-1

    m_active=False; m_consumed=False; m_side=0; m_expiry=0; mL=0; moside=0; matr=0.0
    rearm_ready=False; wait_reversal=False; wait_boundary=False; boundary_seen=False; rearm_anchor=-1
    trades_this_mandate=0; max_trades_per_mandate=0

    for i in range(t.size):
        tm=int(t[i]); sec=tm//1000; px=int(mid2[i]); exited=False; exit_reason=0
        j1=bidx(s1e,tm); j5=bidx(s5e,tm); jrev=j1 if revtf==1 else j5
        rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
        ro=s1o[j1] if revtf==1 and j1>=0 else (s5o[j5] if j5>=0 else 0)

        if pos!=0:
            ex=0; do_exit=False
            if pos>0 and int(bid[i])<=stop:
                ex=int(bid[i]); do_exit=True; exit_reason=1
            elif pos<0 and int(ask[i])>=stop:
                ex=int(ask[i]); do_exit=True; exit_reason=1
            if (not do_exit) and sec-entrysec>=30:
                ex=int(bid[i]) if pos>0 else int(ask[i]); do_exit=True; exit_reason=2
            if do_exit:
                raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0); exit_deal=raw-0.01
                if exit_deal>1e-12: wins+=1
                if raw>0: gp+=exit_deal
                else: gl+=exit_deal
                balance+=exit_deal; closed+=1; hold_sum+=sec-entrysec
                if balance>peak: peak=balance
                dd=peak-balance
                if dd>maxdd: maxdd=dd
                pos=0; entry=0; stop=0; exited=True
                if m_active and m_consumed:
                    rearm_ready=False; wait_reversal=False; wait_boundary=False; boundary_seen=False
                    if mode in (0,1): rearm_ready=True
                    elif mode==2: wait_reversal=True; rearm_anchor=jrev
                    elif mode==3:
                        if exit_reason==1: wait_reversal=True; rearm_anchor=jrev
                        else: m_active=False; maxhold_cancel+=1
                    elif mode==4: wait_boundary=True
                    elif mode==5:
                        if exit_reason==1: rearm_ready=True
                        else: m_active=False; maxhold_cancel+=1
            else:
                if pos>0 and int(bid[i])-entry>=TRAIL_ACT:
                    ns=int(bid[i])-TRAIL_DIST
                    if ns>stop: stop=ns
                elif pos<0 and entry-int(ask[i])>=TRAIL_ACT:
                    ns=int(ask[i])+TRAIL_DIST
                    if ns<stop: stop=ns

        if m_active and tm>m_expiry:
            m_active=False; rearm_ready=False; wait_reversal=False; wait_boundary=False; expired+=1
        if m_active and mode==1 and moside*(px-mL)>=0:
            m_active=False; rearm_ready=False; wait_reversal=False; wait_boundary=False; boundary_cancel+=1

        # Every generator signal becomes the newest causal mandate. If occupied it is queued,
        # rather than discarded; latest-signal ownership avoids retrospective multi-mandate selection.
        while k<n and int(sig_i[k])==i:
            if pos!=0: occupied_signals+=1; queued_signals+=1
            m_active=True; m_consumed=False; m_side=int(sig_side[k]); m_expiry=int(sig_expiry[k])
            mL=int(sig_L[k]); moside=int(sig_oside[k]); matr=float(sig_atr[k])
            rearm_ready=True; wait_reversal=False; wait_boundary=False; boundary_seen=False
            rearm_anchor=jrev; trades_this_mandate=0; k+=1

        if m_active and tm<=m_expiry and pos==0 and not exited:
            if wait_reversal and jrev>=0 and jrev!=rearm_anchor:
                disp=(-moside)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0; rearm_anchor=jrev
                if disp>=revdisp*matr and eff>=effmin:
                    rearm_ready=True; wait_reversal=False
            elif wait_boundary:
                if moside*(px-mL)>=0: boundary_seen=True
                elif boundary_seen:
                    rearm_ready=True; wait_boundary=False; boundary_seen=False

            if rearm_ready:
                pos=m_side; entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec; admitted+=1; balance-=0.01; gl-=0.01
                if m_consumed: reentries+=1
                m_consumed=True; rearm_ready=False; trades_this_mandate+=1
                if trades_this_mandate>max_trades_per_mandate: max_trades_per_mandate=trades_this_mandate
                dd=peak-balance
                if dd>maxdd: maxdd=dd

    if pos!=0:
        ex=int(bid[last_i]) if pos>0 else int(ask[last_i])
        raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0); exit_deal=raw-0.01
        if exit_deal>1e-12: wins+=1
        if raw>0: gp+=exit_deal
        else: gl+=exit_deal
        balance+=exit_deal; closed+=1; hold_sum+=(int(t[last_i])//1000)-entrysec
        if balance>peak: peak=balance
        dd=peak-balance
        if dd>maxdd: maxdd=dd

    return (admitted,closed,wins,gp,gl,gp+gl,maxdd,(hold_sum/closed if closed else 0.0),
            occupied_signals,queued_signals,reentries,expired,boundary_cancel,maxhold_cancel,max_trades_per_mandate)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    source_sha=P.sha256_file(args.source)
    if source_sha!=CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    import pandas as pd
    df=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    ask,bid=P.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b1=P.bars(t,mid,1000); b5=P.bars(t,mid,5000); b15=P.bars(t,mid,15000); b300=P.bars(t,mid,300000)
    a300=P.atr14(b300); st,ss,sl=P.symmetric_swings(b300,2)

    results={name:{"vectors":{},"aggregate_trade_count_abs_error":0} for name in MODES}
    overflow_total=0
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c,si,ssig,se,sexp,sL,sos,satr,ov=detect_execution_mandates(
            t,mid,st,ss,sl,b300["end_ms"],a300,
            b1["end_ms"],b1["open"],b1["close"],b5["end_ms"],b5["open"],b5["close"],
            b15["end_ms"],b15["open"],b15["close"],ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt)
        overflow_total+=int(ov)
        got=list(map(int,c))
        if got!=EXPECTED_POSTQUAL_FUNNEL[n]:
            raise SystemExit("09F POST_QUAL generator drift "+n+": "+json.dumps(got))
        for pname,mode in MODES.items():
            vals=admit_r9_execution_mandate(
                t,ask,bid,mid,b1["end_ms"],b1["open"],b1["close"],b5["end_ms"],b5["open"],b5["close"],
                si,ssig,se,sexp,sL,sos,satr,rt,rd,em,mode)
            adm,trades,w,gp,gl,net,dd,avgh,occ,queued,reentries,expired,bcancel,mhcancel,maxpm=vals
            target=HIST_TRADES[n]; results[pname]["aggregate_trade_count_abs_error"]+=abs(int(trades)-target)
            results[pname]["vectors"][n]={
                "generator_signals":int(si.size),"historical_trades":int(target),
                "admitted_entries":int(adm),"closed_trades":int(trades),"official_wins":int(w),
                "gross_profit_usd":float(gp),"gross_loss_usd":float(gl),"net_usd":float(net),
                "max_balance_dd_usd":float(dd),"average_hold_seconds":float(avgh),
                "signals_arriving_occupied":int(occ),"queued_occupied_signals":int(queued),
                "mandate_reentries":int(reentries),"mandate_expirations":int(expired),
                "mandate_boundary_cancels":int(bcancel),"mandate_maxhold_cancels":int(mhcancel),
                "max_trades_per_mandate":int(maxpm),
            }
    if overflow_total!=0: raise SystemExit("mandate signal buffer overflow")

    ranking=[]
    for pname,r in results.items():
        s6=r["vectors"]["S06"]
        ranking.append({
            "profile":pname,"aggregate_trade_count_abs_error":int(r["aggregate_trade_count_abs_error"]),
            "s06_generator_signals":int(s6["generator_signals"]),
            "s06_trade_abs_error":abs(int(s6["closed_trades"])-615),
            "s06_win_abs_error":abs(int(s6["official_wins"])-307),
            "s06_net_abs_error":float(abs(float(s6["net_usd"])+101.08)),
            "total_mandate_reentries":int(sum(x["mandate_reentries"] for x in r["vectors"].values())),
        })
    ranking.sort(key=lambda x:(x["aggregate_trade_count_abs_error"],x["s06_trade_abs_error"],x["s06_win_abs_error"],x["s06_net_abs_error"]))

    out={
        "schema":"delta-r037-dh05-signal-to-execution-mandate-persistence-parity-v1",
        "status":"BOUNDED_QA_COMPLETE","source_sha256":source_sha,"stage_a_ticks":int(len(t)),
        "surface":"DUKAS_COINEXX_LIKE_P75","august_accessed":False,"numeric_vector_retune":False,
        "generator":"09F POST_QUAL one-shot generator frozen exactly; generator counts unchanged",
        "failure_clock":"original FAILURE_CANDIDATE start + frozen max_failure_age; never refreshed",
        "ownership":"latest causal generator signal owns one execution mandate; occupied signals queue as newest mandate",
        "observation_latch":"same-tick post-exit admission prohibited",
        "profiles":results,"ranking":ranking,"signal_overflow_total":int(overflow_total),
        "finding":{
            "selection_rule":"carry forward only if six-vector trade-count error materially improves with fixed generator counts/failure expiry and without compensating S06 trade-win-economic collapse",
            "leading_profile":ranking[0]["profile"] if ranking else None,
            "parity_complete":False,
            "next":"use result to either refine the execution-mandate invalidation/rearm edge or reject persistent mandate mapping",
        },
    }
    P.atomic_write_json(args.output,out)
    print(json.dumps({"ranking":ranking},separators=(",",":")))


if __name__=="__main__":
    main()
