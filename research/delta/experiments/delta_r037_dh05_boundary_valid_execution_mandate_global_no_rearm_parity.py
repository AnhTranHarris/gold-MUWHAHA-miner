"""DELTA R037 DH05 boundary-valid execution mandate + GLOBAL NO_REARM — Checkpoint 09Q.

Bounded parity reconstruction. Reproduce the exact 09F POST_QUAL singular generator and attach
its original breakout boundary metadata. The downstream mandate may outlive the pre-signal failure
clock, but only while price remains on the reversal/failure side of the original boundary.
GLOBAL NO_REARM forbids downstream re-entry in the same UTC minute as the prior exit.

Profiles differ only by which prior exit type may authorize a later-minute re-entry:
ANY_EXIT, STOP_ONLY, LOSING_EXIT, MAXHOLD_ONLY. No generator multiplication, numeric retuning,
August access, SORB integration, mature-exit optimization, or MQL5 work.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_post_signal_intrabar_rearm_edge_parity import (
    CANONICAL_JAN_SHA256, STAGE_A_END_MS, VECTORS, STAGES,
    atomic_write_json, atr14, bars, bidx, p75, sha256_file, symmetric_swings,
)

HIST_TRADES={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
EXPECTED_POSTQUAL_FUNNEL={
    "A03":[6686,998,212,786,441,268,192,192],
    "S05":[7727,309,32,277,54,19,9,9],
    "S06":[3561,1599,248,1351,1210,695,651,651],
    "S09":[7632,201,40,161,63,39,11,11],
    "S10":[6440,1300,205,1095,637,309,227,227],
    "S16":[7684,130,52,78,32,18,7,7],
}
PROFILES=(("ANY_EXIT",0),("STOP_ONLY",1),("LOSING_EXIT",2),("MAXHOLD_ONLY",3))

@njit(cache=True)
def detect_signal_metadata(
    t,mid2,st,ss,sl,m5e,m5a,s1e,s1o,s1c,s5e,s5o,s5c,s15e,s15o,s15c,
    accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf,
):
    stage=0; oside=0; L=0; evatr=0.0; attempt_start=0; qualified_start=0
    fstart=0; reent=False; latest_hi=0; latest_lo=0; si=0; hiel=True; loel=True
    lastacc=-1; lastrev=-1; attempt_open=False; attempt_qualified=False; event_id=0
    cnt=np.zeros(8,np.int64); MAX_SIG=100000
    sig_i=np.empty(MAX_SIG,np.int64); sig_side=np.empty(MAX_SIG,np.int8)
    sig_event=np.empty(MAX_SIG,np.int64); sig_L=np.empty(MAX_SIG,np.int64)
    sig_oside=np.empty(MAX_SIG,np.int8); nsig=0; overflow=0

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
            q=oside*(ac-ao)>=accdisp*evatr and oside*(ac-L)>0 and qualified_start>0 and acc_end>qualified_start
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
        if stage==4 and jrev>=0 and jrev!=lastrev:
            if (-oside)*(rc-L)>=reclaim*evatr:
                cnt[5]+=1; stage=5
        if stage<5 or jrev<0 or jrev==lastrev: continue
        ro=s1o[j1] if revtf==1 else s5o[j5]
        disp=(-oside)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0
        if disp>=revdisp*evatr and eff>=effmin:
            cnt[6]+=1; cnt[7]+=1
            if nsig<MAX_SIG:
                sig_i[nsig]=i; sig_side[nsig]=-oside; sig_event[nsig]=event_id
                sig_L[nsig]=L; sig_oside[nsig]=oside; nsig+=1
            else: overflow+=1
            stage=0; oside=0; reent=False
        lastrev=jrev
    return cnt,sig_i[:nsig],sig_side[:nsig],sig_event[:nsig],sig_L[:nsig],sig_oside[:nsig],overflow

@njit(cache=True)
def admit_boundary_mandate(t,ask,bid,mid2,sig_i,sig_side,sig_L,sig_oside,mode):
    STOP=300; TRAIL_ACT=100; TRAIL_DIST=30
    n=sig_i.size; k=0; admitted=0; closed=0; wins=0; reentries=0
    boundary_invalidations=0; pending_signals=0; blocked_same_minute=0
    gp=0.0; gl=0.0; balance=100000.0; peak=balance; maxdd=0.0; hold_sum=0.0
    pos=0; entry=0; stop=0; entrysec=0; last_i=t.size-1
    active=False; mside=0; mL=0; moside=0; last_exit_minute=-1
    rearm_authorized=False

    for i in range(t.size):
        tm=int(t[i]); sec=tm//1000; minute=tm//60000; px=int(mid2[i])
        if active and moside*(px-mL)>=0:
            active=False; rearm_authorized=False; boundary_invalidations+=1
        if pos!=0:
            ex=0; do_exit=False; exit_reason=0
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
                pos=0; entry=0; stop=0; last_exit_minute=minute
                if mode==0: rearm_authorized=True
                elif mode==1: rearm_authorized=(exit_reason==1)
                elif mode==2: rearm_authorized=(raw<=0.0)
                else: rearm_authorized=(exit_reason==2)
            else:
                if pos>0 and int(bid[i])-entry>=TRAIL_ACT:
                    ns=int(bid[i])-TRAIL_DIST
                    if ns>stop: stop=ns
                elif pos<0 and entry-int(ask[i])>=TRAIL_ACT:
                    ns=int(ask[i])+TRAIL_DIST
                    if ns<stop: stop=ns

        while k<n and int(sig_i[k])==i:
            active=True; mside=int(sig_side[k]); mL=int(sig_L[k]); moside=int(sig_oside[k]); rearm_authorized=False
            if pos==0 and moside*(px-mL)<0:
                pos=mside; entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec; admitted+=1; balance-=0.01; gl-=0.01
                dd=peak-balance
                if dd>maxdd: maxdd=dd
            else: pending_signals+=1
            k+=1

        if active and pos==0 and rearm_authorized and minute!=last_exit_minute and moside*(px-mL)<0:
            pos=mside; entry=int(ask[i]) if pos>0 else int(bid[i])
            stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
            entrysec=sec; admitted+=1; reentries+=1; rearm_authorized=False
            balance-=0.01; gl-=0.01
            dd=peak-balance
            if dd>maxdd: maxdd=dd
        elif active and pos==0 and rearm_authorized and minute==last_exit_minute:
            blocked_same_minute+=1

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
    return admitted,closed,wins,gp,gl,gp+gl,maxdd,(hold_sum/closed if closed else 0.0),reentries,boundary_invalidations,pending_signals,blocked_same_minute

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True); ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    sha=sha256_file(args.source)
    if sha!=CANONICAL_JAN_SHA256: raise SystemExit("canonical January SHA mismatch: "+sha)
    df=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]; t=df.timestamp_ms_utc.to_numpy(np.int64)
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a300=atr14(b300); st,ss,sl=symmetric_swings(b300,2)
    profiles={name:{} for name,_ in PROFILES}; agg={name:0 for name,_ in PROFILES}
    control_error=0; control={}
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c,si,ssig,se,sL,sos,ov=detect_signal_metadata(
            t,mid,st,ss,sl,b300["end_ms"],a300,
            b1["end_ms"],b1["open"],b1["close"],b5["end_ms"],b5["open"],b5["close"],b15["end_ms"],b15["open"],b15["close"],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt)
        if ov!=0: raise SystemExit("signal overflow "+n)
        got=list(map(int,c))
        if got!=EXPECTED_POSTQUAL_FUNNEL[n]: raise SystemExit("POST_QUAL generator drift "+n+": "+json.dumps(got))
        base=int(si.size); control_error+=abs(base-HIST_TRADES[n]); control[n]={"signals":base,"trades":base,"historical_trades":HIST_TRADES[n]}
        for pname,mode in PROFILES:
            vals=admit_boundary_mandate(t,ask,bid,mid,si,ssig,sL,sos,mode)
            adm,tr,w,gp,gl,net,dd,avgh,reent,binv,pending,blocked=vals
            agg[pname]+=abs(int(tr)-HIST_TRADES[n])
            profiles[pname][n]={
              "generator_signals":base,"admitted_entries":int(adm),"closed_trades":int(tr),"historical_trades":HIST_TRADES[n],
              "official_wins":int(w),"net_usd":float(net),"max_balance_dd_usd":float(dd),"average_hold_seconds":float(avgh),
              "execution_reentries":int(reent),"boundary_invalidations":int(binv),"signals_while_occupied":int(pending),"blocked_same_minute":int(blocked)
            }
    if control_error!=338:
        # Raw signals as trades omit the two occupied-signal suppressions in the frozen one-position control.
        # This is only a generator-count arithmetic assertion, not the executable control.
        raise SystemExit("generator arithmetic drift: "+str(control_error))
    ranking=[]
    for pname,_ in PROFILES:
        s6=profiles[pname]["S06"]
        ranking.append({"profile":pname,"aggregate_trade_count_abs_error":int(agg[pname]),
          "s06_trade_abs_error":abs(s6["closed_trades"]-615),"s06_win_abs_error":abs(s6["official_wins"]-307),
          "s06_net_abs_error":float(abs(s6["net_usd"]+101.08)),"s06_reentries":s6["execution_reentries"]})
    ranking.sort(key=lambda x:(x["aggregate_trade_count_abs_error"],x["s06_trade_abs_error"],x["s06_win_abs_error"],x["s06_net_abs_error"]))
    out={"schema":"delta-r037-dh05-boundary-valid-execution-mandate-global-no-rearm-v1","status":"BOUNDED_QA_COMPLETE",
      "source_sha256":sha,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","august_accessed":False,"numeric_vector_retune":False,
      "generator_semantics":"exact 09F POST_QUAL singular generator with original boundary metadata",
      "mandate_validity":"persists while price remains on reversal side of original breakout boundary; invalidates on original-boundary retake",
      "global_no_rearm":"same UTC minute repeat execution prohibited",
      "profiles":profiles,"ranking":ranking,
      "finding":{"selection_rule":"carry only if boundary-valid mandate materially beats 09L aggregate error 304 while avoiding dense S06/S10 overproduction and improving sparse vectors","leading_profile":ranking[0]["profile"] if ranking else None,"parity_complete":False}}
    atomic_write_json(args.output,out); print(json.dumps({"ranking":ranking},separators=(",",":")))

if __name__=="__main__": main()
