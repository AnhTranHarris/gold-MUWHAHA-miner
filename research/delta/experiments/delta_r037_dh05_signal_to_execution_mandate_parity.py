"""DELTA R037 DH05 signal-to-execution mandate persistence parity diagnostic — Checkpoint 09M.

Research-only bounded diagnostic. It imports the committed Checkpoint-09L producer as the
frozen causal generator/execution dependency, uses the exact POST_QUAL one-shot signal stream,
and tests only whether a single generator signal can authorize multiple executable admissions.

No generator thresholds are retuned. No new signal is manufactured. Candidate mandate clocks
reuse only already-frozen time quantities: the vector's max_failure_age or the R9 30-second
execution horizon. One-position-at-a-time R9/Coinexx execution remains frozen.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from delta_r037_dh05_post_signal_intrabar_rearm_edge_parity import (
    CANONICAL_JAN_SHA256,
    STAGE_A_END_MS,
    VECTORS,
    admit_r9_lifecycle,
    atomic_write_json,
    atr14,
    bars,
    detect_signal_multiplicity,
    p75,
    sha256_file,
    symmetric_swings,
)

HIST_TRADES = {"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
EXPECTED_SIGNALS = {"A03":192,"S05":9,"S06":651,"S09":11,"S10":227,"S16":7}

# profile, duration_mode, max_entries_per_mandate
# duration_mode 0 -> vector max_failure_age from signal time
# duration_mode 1 -> frozen R9 30-second execution horizon from signal time
# max_entries -1 means unlimited while the mandate remains causally valid.
MANDATE_PROFILES = (
    ("MAXFAIL_ONE_REENTRY", 0, 2),
    ("MAXFAIL_UNLIMITED", 0, -1),
    ("EXEC30_ONE_REENTRY", 1, 2),
    ("EXEC30_UNLIMITED", 1, -1),
)


@njit(cache=True)
def admit_signal_mandate(t, ask, bid, sig_i, sig_side, duration_ms, max_entries, block_exit_tick):
    """Replay frozen R9 execution under a downstream signal mandate.

    A generator signal opens/replaces a causal execution mandate. While flat and while the
    mandate remains alive, the same directional mandate may admit another trade after a prior
    trade exits. This does not emit a new DH05 generator signal.
    """
    STOP=300; TRAIL_ACT=100; TRAIL_DIST=30
    n=sig_i.size
    k=0
    admitted=0; closed_trades=0; wins=0
    rejected_latch=0; signal_refreshes=0; reentries=0
    gp=0.0; gl=0.0; balance=100000.0; peak=balance; maxdd=0.0; hold_sum=0.0
    pos=0; entry=0; stop=0; entrysec=0
    active=False; mside=0; mend=0; entries_used=0
    last_i=t.size-1

    for i in range(t.size):
        tm=int(t[i]); sec=tm//1000
        exited=False

        if pos!=0:
            ex=0; do_exit=False
            if pos>0:
                if int(bid[i])<=stop:
                    ex=int(bid[i]); do_exit=True
            else:
                if int(ask[i])>=stop:
                    ex=int(ask[i]); do_exit=True
            if (not do_exit) and sec-entrysec>=30:
                ex=int(bid[i]) if pos>0 else int(ask[i]); do_exit=True
            if do_exit:
                raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)
                exit_deal=raw-0.01
                if exit_deal>1e-12: wins+=1
                if raw>0: gp+=exit_deal
                else: gl+=exit_deal
                balance+=exit_deal; closed_trades+=1; hold_sum+=sec-entrysec
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

        # New causal generator signal creates/replaces the downstream mandate.
        while k<n and int(sig_i[k])==i:
            active=True
            mside=int(sig_side[k])
            mend=tm+duration_ms
            entries_used=0
            signal_refreshes+=1
            k+=1

        if active and tm>mend:
            active=False

        if pos==0 and active and (max_entries<0 or entries_used<max_entries):
            if exited and block_exit_tick:
                rejected_latch+=1
            else:
                pos=mside
                entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec
                admitted+=1
                if entries_used>0: reentries+=1
                entries_used+=1
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
        balance+=exit_deal; closed_trades+=1
        hold_sum+=(int(t[last_i])//1000)-entrysec
        if balance>peak: peak=balance
        dd=peak-balance
        if dd>maxdd: maxdd=dd

    return admitted,closed_trades,wins,gp,gl,gp+gl,maxdd,(hold_sum/closed_trades if closed_trades else 0.0),reentries,rejected_latch,signal_refreshes


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()

    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_JAN_SHA256:
        raise SystemExit(f'canonical January SHA mismatch: {source_sha}')

    df=pd.read_csv(args.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    mid=ask+bid
    b1=bars(t,mid,1000); b5=bars(t,mid,5000); b15=bars(t,mid,15000); b300=bars(t,mid,300000)
    a300=atr14(b300); st,ss,sl=symmetric_swings(b300,2)

    controls={}; profiles={name:{} for name,_,_ in MANDATE_PROFILES}
    aggregate={name:0 for name,_,_ in MANDATE_PROFILES}

    for v in VECTORS:
        n,ad,at,mf,mp,pe,rb,rd,em,rt=v
        funnel,si,ssig,se,ov=detect_signal_multiplicity(
            t,mid,st,ss,sl,b300['end_ms'],a300,
            b1['end_ms'],b1['open'],b1['close'],
            b5['end_ms'],b5['open'],b5['close'],
            b15['end_ms'],b15['open'],b15['close'],
            ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt,0,
        )
        if ov!=0: raise SystemExit('signal buffer overflow '+n)
        if int(si.size)!=EXPECTED_SIGNALS[n]:
            raise SystemExit(f'POST_QUAL generator drift {n}: {si.size}')

        adm,rej_occ,rej_latch,tr,w,gp,gl,net,dd,avgh=admit_r9_lifecycle(t,ask,bid,si,ssig,False)
        controls[n]={
            'generator_signals':int(si.size),'admitted_entries':int(adm),'closed_trades':int(tr),
            'official_wins':int(w),'net_usd':float(net),'historical_trades':HIST_TRADES[n],
            'average_hold_seconds':float(avgh),
        }

        for pname,dmode,max_entries in MANDATE_PROFILES:
            duration_ms=int(mf*1000) if dmode==0 else 30000
            vals=admit_signal_mandate(t,ask,bid,si,ssig,duration_ms,max_entries,False)
            adm2,tr2,w2,gp2,gl2,net2,dd2,avgh2,reentries,latchrej,refreshes=vals
            aggregate[pname]+=abs(int(tr2)-HIST_TRADES[n])
            profiles[pname][n]={
                'generator_signals':int(si.size),'mandate_duration_ms':duration_ms,
                'max_entries_per_mandate':int(max_entries),'admitted_entries':int(adm2),
                'closed_trades':int(tr2),'historical_trades':HIST_TRADES[n],
                'official_wins':int(w2),'gross_profit_usd':float(gp2),'gross_loss_usd':float(gl2),
                'net_usd':float(net2),'max_balance_dd_usd':float(dd2),
                'average_hold_seconds':float(avgh2),'execution_reentries':int(reentries),
                'signal_refreshes':int(refreshes),'rejected_by_exit_tick_latch':int(latchrej),
            }

    # Exact one-shot control inherited from 09J/09K.
    if not (controls['S06']['closed_trades']==649 and controls['S06']['official_wins']==274 and abs(controls['S06']['net_usd']+150.35)<1e-6):
        raise SystemExit('S06 one-shot execution control drift')
    control_error=sum(abs(controls[n]['closed_trades']-HIST_TRADES[n]) for n in HIST_TRADES)
    if control_error!=336:
        raise SystemExit('aggregate one-shot control drift: '+str(control_error))

    ranking=[]
    for pname,_,_ in MANDATE_PROFILES:
        s6=profiles[pname]['S06']
        ranking.append({
            'profile':pname,
            'aggregate_trade_count_abs_error':int(aggregate[pname]),
            's06_trade_abs_error':abs(s6['closed_trades']-615),
            's06_win_abs_error':abs(s6['official_wins']-307),
            's06_net_abs_error':float(abs(s6['net_usd']+101.08)),
            's06_execution_reentries':s6['execution_reentries'],
        })
    ranking.sort(key=lambda x:(x['aggregate_trade_count_abs_error'],x['s06_trade_abs_error'],x['s06_win_abs_error'],x['s06_net_abs_error']))

    out={
        'schema':'delta-r037-dh05-signal-to-execution-mandate-persistence-parity-v1',
        'status':'BOUNDED_QA_COMPLETE',
        'source_sha256':source_sha,'stage_a_ticks':int(len(t)),'surface':'DUKAS_COINEXX_LIKE_P75',
        'august_accessed':False,'numeric_vector_retune':False,
        'generator_semantics':'exact 09F POST_QUAL one-shot signal stream; no repeated generator signals',
        'execution_semantics':'frozen R9/Coinexx one-position lifecycle; downstream mandate may re-admit while alive',
        'control':{'aggregate_trade_count_abs_error':int(control_error),'vectors':controls},
        'profiles':profiles,'ranking':ranking,
        'finding':{
            'selection_rule':'candidate may carry forward only if execution-side mandate multiplicity materially beats aggregate trade-count error 304 (best 09L clue) while improving or preserving S06 trade/win/net parity without changing generator counts',
            'leading_profile':ranking[0]['profile'] if ranking else None,
            'parity_complete':False,
            'next':'freeze only a downstream execution-mandate rule that explains trades>signal-stage counts without generator inflation or broad overproduction',
        },
    }
    atomic_write_json(args.output,out)
    print(json.dumps({'control_error':control_error,'ranking':ranking},separators=(',',':')))

if __name__=='__main__':
    main()
