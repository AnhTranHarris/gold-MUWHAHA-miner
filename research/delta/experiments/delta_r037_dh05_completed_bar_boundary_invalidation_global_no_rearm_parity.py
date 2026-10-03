"""DELTA R037 DH05 completed-bar boundary invalidation + GLOBAL NO_REARM — Checkpoint 09R.

Reuses the exact 09Q singular POST_QUAL generator with original boundary metadata. The only
changed semantic is downstream mandate invalidation: original-boundary retake is evaluated on a
newly completed causal bar close instead of an intrabar tick touch. Two existing clocks are tested:
the vector reversal timeframe and the frozen acceptance timeframe. Re-entry remains constrained by
GLOBAL NO_REARM and either LOSING_EXIT or MAXHOLD_ONLY eligibility. No numeric retuning.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_boundary_valid_execution_mandate_global_no_rearm_parity import (
    CANONICAL_JAN_SHA256, STAGE_A_END_MS, VECTORS, HIST_TRADES, EXPECTED_POSTQUAL_FUNNEL,
    atomic_write_json, atr14, bars, bidx, detect_signal_metadata, p75, sha256_file, symmetric_swings,
)

PROFILES=(
    ("REVTF_CLOSE__LOSING_EXIT",0,0),
    ("REVTF_CLOSE__MAXHOLD_ONLY",0,1),
    ("ACCTF_CLOSE__LOSING_EXIT",1,0),
    ("ACCTF_CLOSE__MAXHOLD_ONLY",1,1),
)

@njit(cache=True)
def admit_completed_bar_boundary(
    t,ask,bid,mid2,sig_i,sig_side,sig_L,sig_oside,inv_end,inv_close,retry_mode,
):
    STOP=300; TRAIL_ACT=100; TRAIL_DIST=30
    n=sig_i.size; k=0; admitted=0; closed=0; wins=0; reentries=0
    boundary_invalidations=0; pending_signals=0; blocked_same_minute=0
    gp=0.0; gl=0.0; balance=100000.0; peak=balance; maxdd=0.0; hold_sum=0.0
    pos=0; entry=0; stop=0; entrysec=0; last_i=t.size-1
    active=False; mside=0; mL=0; moside=0; last_exit_minute=-1
    last_inv=-1; rearm_authorized=False

    for i in range(t.size):
        tm=int(t[i]); sec=tm//1000; minute=tm//60000
        if active:
            jinv=bidx(inv_end,tm)
            if jinv>=0 and jinv!=last_inv:
                last_inv=jinv
                if moside*(int(inv_close[jinv])-mL)>=0:
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
                if retry_mode==0: rearm_authorized=(raw<=0.0)
                else: rearm_authorized=(exit_reason==2)
            else:
                if pos>0 and int(bid[i])-entry>=TRAIL_ACT:
                    ns=int(bid[i])-TRAIL_DIST
                    if ns>stop: stop=ns
                elif pos<0 and entry-int(ask[i])>=TRAIL_ACT:
                    ns=int(ask[i])+TRAIL_DIST
                    if ns<stop: stop=ns

        while k<n and int(sig_i[k])==i:
            active=True; mside=int(sig_side[k]); mL=int(sig_L[k]); moside=int(sig_oside[k])
            last_inv=bidx(inv_end,tm); rearm_authorized=False
            if pos==0:
                pos=mside; entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec; admitted+=1; balance-=0.01; gl-=0.01
                dd=peak-balance
                if dd>maxdd: maxdd=dd
            else: pending_signals+=1
            k+=1

        if active and pos==0 and rearm_authorized:
            if minute==last_exit_minute:
                blocked_same_minute+=1
            else:
                pos=mside; entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec; admitted+=1; reentries+=1; rearm_authorized=False
                balance-=0.01; gl-=0.01
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
    profiles={n:{} for n,_,_ in PROFILES}; agg={n:0 for n,_,_ in PROFILES}

    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        c,si,ssig,se,sL,sos,ov=detect_signal_metadata(
            t,mid,st,ss,sl,b300["end_ms"],a300,
            b1["end_ms"],b1["open"],b1["close"],b5["end_ms"],b5["open"],b5["close"],b15["end_ms"],b15["open"],b15["close"],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt)
        if ov!=0: raise SystemExit("signal overflow "+n)
        got=list(map(int,c))
        if got!=EXPECTED_POSTQUAL_FUNNEL[n]: raise SystemExit("POST_QUAL generator drift "+n+": "+json.dumps(got))
        for pname,clock_mode,retry_mode in PROFILES:
            if clock_mode==0:
                inv_end,inv_close=(b1["end_ms"],b1["close"]) if rt==1 else (b5["end_ms"],b5["close"])
            else:
                inv_end,inv_close=(b5["end_ms"],b5["close"]) if at==5 else (b15["end_ms"],b15["close"])
            vals=admit_completed_bar_boundary(t,ask,bid,mid,si,ssig,sL,sos,inv_end,inv_close,retry_mode)
            adm,tr,w,gp,gl,net,dd,avgh,reent,binv,pending,blocked=vals
            agg[pname]+=abs(int(tr)-HIST_TRADES[n])
            profiles[pname][n]={
              "generator_signals":int(si.size),"admitted_entries":int(adm),"closed_trades":int(tr),"historical_trades":HIST_TRADES[n],
              "official_wins":int(w),"net_usd":float(net),"max_balance_dd_usd":float(dd),"average_hold_seconds":float(avgh),
              "execution_reentries":int(reent),"completed_bar_boundary_invalidations":int(binv),"signals_while_occupied":int(pending),"blocked_same_minute":int(blocked)
            }
    ranking=[]
    for pname,_,_ in PROFILES:
        s6=profiles[pname]["S06"]
        ranking.append({"profile":pname,"aggregate_trade_count_abs_error":int(agg[pname]),
          "s06_trade_abs_error":abs(s6["closed_trades"]-615),"s06_win_abs_error":abs(s6["official_wins"]-307),
          "s06_net_abs_error":float(abs(s6["net_usd"]+101.08)),"s06_reentries":s6["execution_reentries"]})
    ranking.sort(key=lambda x:(x["aggregate_trade_count_abs_error"],x["s06_trade_abs_error"],x["s06_win_abs_error"],x["s06_net_abs_error"]))
    out={"schema":"delta-r037-dh05-completed-bar-boundary-invalidation-global-no-rearm-v1","status":"BOUNDED_QA_COMPLETE",
      "source_sha256":sha,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","august_accessed":False,"numeric_vector_retune":False,
      "generator_semantics":"exact 09F POST_QUAL singular generator with original boundary metadata",
      "global_no_rearm":"same UTC minute repeat execution prohibited",
      "profiles":profiles,"ranking":ranking,
      "finding":{"selection_rule":"carry only if completed-bar boundary invalidation beats 09L error 304 without dense-vector compensation","leading_profile":ranking[0]["profile"] if ranking else None,"parity_complete":False}}
    atomic_write_json(args.output,out); print(json.dumps({"ranking":ranking},separators=(",",":")))

if __name__=="__main__": main()
