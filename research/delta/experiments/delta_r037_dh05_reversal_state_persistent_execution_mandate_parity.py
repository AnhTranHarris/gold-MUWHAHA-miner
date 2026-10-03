"""DELTA R037 DH05 reversal-state persistent execution-mandate parity — Checkpoint 09N.

Bounded research diagnostic. Uses the exact Checkpoint-09F POST_QUAL one-shot generator from
committed 09L dependency and keeps generator counts frozen. Tests only whether a downstream
execution mandate can re-enter after a prior trade closes when a NEW completed reversal-timeframe
bar causally reconfirms the thesis. No automatic tick-by-tick re-entry and no numeric retuning.
"""
from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_post_signal_intrabar_rearm_edge_parity import (
    CANONICAL_JAN_SHA256, STAGE_A_END_MS, VECTORS, admit_r9_lifecycle,
    atomic_write_json, atr14, bars, bidx, detect_signal_multiplicity,
    p75, sha256_file, symmetric_swings,
)

HIST_TRADES={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
EXPECTED_SIGNALS={"A03":192,"S05":9,"S06":651,"S09":11,"S10":227,"S16":7}

# name, state_mode, cap_mode
# state_mode 0: completed reversal bar body remains in mandate direction (>0)
# state_mode 1: completed reversal bar body meets frozen revdisp_atr using causal current M5 ATR
# cap_mode 0: state transition only; first state failure invalidates
# cap_mode 1: same, plus existing vector max_failure_age from signal time
PROFILES=(
    ("BODY_SIGN_CHAIN",0,0),
    ("BODY_SIGN_CHAIN_MAXFAIL",0,1),
    ("REV_DISP_CHAIN",1,0),
    ("REV_DISP_CHAIN_MAXFAIL",1,1),
)

@njit(cache=True)
def admit_state_mandate(t,ask,bid,sig_i,sig_side,m5e,m5a,reve,revo,revc,revdisp,maxfail,state_mode,cap_mode):
    STOP=300; TRAIL_ACT=100; TRAIL_DIST=30
    n=sig_i.size; k=0
    admitted=0; closed=0; wins=0; reentries=0; invalidations=0; pending_signals=0
    gp=0.0; gl=0.0; balance=100000.0; peak=balance; maxdd=0.0; hold_sum=0.0
    pos=0; entry=0; stop=0; entrysec=0
    active=False; mside=0; mend=0; lastrev=-1; signal_tick=-1
    last_i=t.size-1

    for i in range(t.size):
        tm=int(t[i]); sec=tm//1000; exited=False
        if pos!=0:
            ex=0; do_exit=False
            if pos>0:
                if int(bid[i])<=stop: ex=int(bid[i]); do_exit=True
            else:
                if int(ask[i])>=stop: ex=int(ask[i]); do_exit=True
            if (not do_exit) and sec-entrysec>=30:
                ex=int(bid[i]) if pos>0 else int(ask[i]); do_exit=True
            if do_exit:
                raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)
                exit_deal=raw-0.01
                if exit_deal>1e-12: wins+=1
                if raw>0: gp+=exit_deal
                else: gl+=exit_deal
                balance+=exit_deal; closed+=1; hold_sum+=sec-entrysec
                if balance>peak: peak=balance
                dd=peak-balance
                if dd>maxdd: maxdd=dd
                pos=0; entry=0; stop=0; exited=True
            else:
                if pos>0 and int(bid[i])-entry>=TRAIL_ACT:
                    ns=int(bid[i])-TRAIL_DIST
                    if ns>stop: stop=ns
                elif pos<0 and entry-int(ask[i])>=TRAIL_ACT:
                    ns=int(ask[i])+TRAIL_DIST
                    if ns<stop: stop=ns

        # New generator signal creates/replaces downstream mandate and is immediately
        # executable when flat, preserving the one-shot admission control.
        while k<n and int(sig_i[k])==i:
            active=True; mside=int(sig_side[k]); signal_tick=i
            mend=tm+maxfail if cap_mode==1 else 0
            lastrev=bidx(reve,tm)
            if pos==0:
                pos=mside; entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec; admitted+=1
                balance-=0.01; gl-=0.01
                if balance>peak: peak=balance
                dd=peak-balance
                if dd>maxdd: maxdd=dd
            else:
                pending_signals+=1
            k+=1

        if active and cap_mode==1 and tm>mend:
            active=False; invalidations+=1

        if not active:
            continue

        jrev=bidx(reve,tm)
        if jrev<0 or jrev==lastrev:
            continue
        lastrev=jrev

        body=mside*(int(revc[jrev])-int(revo[jrev]))
        if state_mode==0:
            state_ok=body>0
        else:
            jm=bidx(m5e,tm)
            ae=float(m5a[jm]) if jm>=0 else 0.0
            state_ok=(ae>0.0 and body>=revdisp*ae)

        if not state_ok:
            active=False; invalidations+=1
            continue

        # Re-entry is only allowed on a NEW completed confirming reversal bar.
        if pos==0 and i!=signal_tick:
            pos=mside; entry=int(ask[i]) if pos>0 else int(bid[i])
            stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
            entrysec=sec; admitted+=1; reentries+=1
            balance-=0.01; gl-=0.01
            if balance>peak: peak=balance
            dd=peak-balance
            if dd>maxdd: maxdd=dd

    if pos!=0:
        ex=int(bid[last_i]) if pos>0 else int(ask[last_i])
        raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)
        exit_deal=raw-0.01
        if exit_deal>1e-12: wins+=1
        if raw>0: gp+=exit_deal
        else: gl+=exit_deal
        balance+=exit_deal; closed+=1
        hold_sum+=(int(t[last_i])//1000)-entrysec
        if balance>peak: peak=balance
        dd=peak-balance
        if dd>maxdd: maxdd=dd

    return admitted,closed,wins,gp,gl,gp+gl,maxdd,(hold_sum/closed if closed else 0.0),reentries,invalidations,pending_signals


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    sha=sha256_file(args.source)
    if sha!=CANONICAL_JAN_SHA256: raise SystemExit('canonical January SHA mismatch: '+sha)
    df=pd.read_csv(args.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]; t=df.timestamp_ms_utc.to_numpy(np.int64)
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a300=atr14(b300); st,ss,sl=symmetric_swings(b300,2)

    control={}; profiles={n:{} for n,_,_ in PROFILES}; agg={n:0 for n,_,_ in PROFILES}
    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        funnel,si,ssig,se,ov=detect_signal_multiplicity(
            t,mid,st,ss,sl,b300['end_ms'],a300,
            b1['end_ms'],b1['open'],b1['close'],b5['end_ms'],b5['open'],b5['close'],b15['end_ms'],b15['open'],b15['close'],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,0)
        if ov!=0: raise SystemExit('signal overflow '+n)
        if int(si.size)!=EXPECTED_SIGNALS[n]: raise SystemExit(f'generator drift {n}: {si.size}')
        adm,ro,rl,tr,w,gp,gl,net,dd,avgh=admit_r9_lifecycle(t,ask,bid,si,ssig,False)
        control[n]={'signals':int(si.size),'trades':int(tr),'wins':int(w),'net_usd':float(net),'historical_trades':HIST_TRADES[n]}
        reve,revo,revc=(b1['end_ms'],b1['open'],b1['close']) if rt==1 else (b5['end_ms'],b5['open'],b5['close'])
        for pname,smode,cmode in PROFILES:
            vals=admit_state_mandate(t,ask,bid,si,ssig,b300['end_ms'],a300,reve,revo,revc,rd,int(mf*1000),smode,cmode)
            adm2,tr2,w2,gp2,gl2,net2,dd2,avgh2,reent,inv,pending=vals
            agg[pname]+=abs(int(tr2)-HIST_TRADES[n])
            profiles[pname][n]={
                'generator_signals':int(si.size),'admitted_entries':int(adm2),'closed_trades':int(tr2),'historical_trades':HIST_TRADES[n],
                'official_wins':int(w2),'net_usd':float(net2),'max_balance_dd_usd':float(dd2),'average_hold_seconds':float(avgh2),
                'execution_reentries':int(reent),'mandate_invalidations':int(inv),'signals_while_occupied':int(pending),
            }
    control_error=sum(abs(control[n]['trades']-HIST_TRADES[n]) for n in HIST_TRADES)
    if control_error!=336 or control['S06']['trades']!=649 or control['S06']['wins']!=274 or abs(control['S06']['net_usd']+150.35)>1e-6:
        raise SystemExit('one-shot control drift')
    ranking=[]
    for pname,_,_ in PROFILES:
        s6=profiles[pname]['S06']
        ranking.append({'profile':pname,'aggregate_trade_count_abs_error':int(agg[pname]),'s06_trade_abs_error':abs(s6['closed_trades']-615),'s06_win_abs_error':abs(s6['official_wins']-307),'s06_net_abs_error':float(abs(s6['net_usd']+101.08)),'s06_reentries':s6['execution_reentries']})
    ranking.sort(key=lambda x:(x['aggregate_trade_count_abs_error'],x['s06_trade_abs_error'],x['s06_win_abs_error'],x['s06_net_abs_error']))
    out={
      'schema':'delta-r037-dh05-reversal-state-persistent-execution-mandate-parity-v1','status':'BOUNDED_QA_COMPLETE',
      'source_sha256':sha,'stage_a_ticks':int(len(t)),'surface':'DUKAS_COINEXX_LIKE_P75','august_accessed':False,'numeric_vector_retune':False,
      'generator_semantics':'exact 09F POST_QUAL one-shot stream; generator counts frozen',
      'profiles':profiles,'control':{'aggregate_trade_count_abs_error':int(control_error),'vectors':control},'ranking':ranking,
      'finding':{'selection_rule':'candidate may carry forward only if state-conditioned execution reentry beats aggregate trade-count error 304 and does not materially worsen S06 trade/win/net parity','leading_profile':ranking[0]['profile'] if ranking else None,'parity_complete':False,'next':'freeze only a causal state-persistent mandate that improves sparse vectors without dense-vector overproduction'}
    }
    atomic_write_json(args.output,out); print(json.dumps({'control_error':control_error,'ranking':ranking},separators=(',',':')))

if __name__=='__main__': main()
