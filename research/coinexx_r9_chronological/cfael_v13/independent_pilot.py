"""Independent, closed-loop, source-chronological M15/M5 lattice PILOT.

Separate research hypothesis: M15 closed EMA20 determines direction,
M5 closed 12-bar range sets retracement grid, completed M1 restores rail,
then next live source quote executes; never relies on V9 signal membership.
No passive fills, no averaging, max one position. Development months ONLY.
"""
from __future__ import annotations
import json, sys, time
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import pandas as pd
from research import Tape,ROOT,SHA_2026
import hashlib

@dataclass(frozen=True)
class Rules:
    name:str
    fib:float=.382
    m15_trend_c:float=4.0
    reclaim_c:float=10.
    max_dist_c:float=80.
    stop_c:float=100.
    target_cash:float=2.0
    hold_ms:int=600000
    micro_ema:bool=False
    anchor:bool=False
    reverse_trend:bool=False

RULES=(Rules('M15_Fib382_reclaim'),
       Rules('M15_Fib618_reclaim',fib=.618),
       Rules('M15_EqualMid_reclaim',fib=.5),
       Rules('M15_Fib382_EMA9_confirm',micro_ema=True),
       Rules('M15_Fib382_anchor_discount',anchor=True),
       Rules('M15_Fib382_countertrend_rejection',reverse_trend=True))

def quote_exit(tape,fill,side,rule):
    ts=tape.ms;bid=tape.bid;ask=tape.ask
    exe=int(ask[fill] if side>0 else bid[fill]);liq0=int(bid[fill] if side>0 else ask[fill]);start=int(ts[fill])
    end=min(len(ts),int(np.searchsorted(ts,start+rule.hold_ms,side='right')))
    if end<=fill+1:return None,None,None
    s=bid[fill+1:end] if side>0 else ask[fill+1:end]
    net=side*(s.astype(np.int32)-exe)/100.-.20
    stop=side*(s.astype(np.int32)-liq0)<=-rule.stop_c
    target=net>=rule.target_cash
    gap=np.diff(ts[fill:end])>2500
    # Stop/target/gap evaluated chronologically at their first source event.
    where=np.flatnonzero(stop|target|gap)
    if len(where):
        hit=int(where[0]);j=fill+1+hit
        # An unobserved interval takes precedence over apparently favorable
        # first quotes after the gap; mark uncertainty, not an earned target.
        kind='quote_gap' if gap[hit] else ('stop' if stop[hit] else 'target')
    else:
        j=end-1;kind='time_limit'
    return j, float(round(net[j-fill-1],6)),kind


def month_run(month:str,rules=RULES):
    p=ROOT/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
    with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    if sha!=SHA_2026[month]:raise ValueError('Source SHA mismatch')
    print('read original',month,flush=True)
    tape=Tape(p);tape._bar(900000,'M15')
    m1=tape.bars['M1'];m5=tape.bars['M5'];m15=tape.bars['M15'];
    M15EMA=pd.Series(m15['close']).ewm(span=20,adjust=False).mean().to_numpy()
    # M1 potential evaluation starts only once ALL three frames have mature closed bars
    fill_candidates=m1['starts'][1:]
    times=tape.ms[fill_candidates]
    M5idx=np.searchsorted(m5['available'],times,side='right')-1
    M15idx=np.searchsorted(m15['available'],times,side='right')-1
    out={}
    for rule in rules:
        completed=[];last_exit=-1;cap={};signal_n=0;reason={}
        for i,signal_tick_idx in enumerate(fill_candidates):
            if i<40:continue
            ts=int(times[i]);a=int(M5idx[i]);b=int(M15idx[i]);
            if a<21 or b<25:continue
            # The first quote in a new minute reveals that the prior bar
            # closed. An immediate fill at that same quote is too optimistic;
            # wait for a subsequent source row to model the processing path.
            fill=int(signal_tick_idx)+1
            if fill>=len(tape.ms):continue
            if int(tape.ms[fill])-int(tape.ms[signal_tick_idx])>2500:continue
            if fill<=last_exit:continue
            # Require the last closed bars were *recently* actually witnessed.
            if ts-int(m15['available'][b])>1200000 or ts-int(m5['available'][a])>600000:continue
            if any(m5['bucket'][a-q]!=m5['bucket'][a]-q for q in range(12)):continue
            if any(m15['bucket'][b-q]!=m15['bucket'][b]-q for q in range(3)):continue
            slope=float(M15EMA[b]-M15EMA[b-2]);trend_side=1 if slope>rule.m15_trend_c else (-1 if slope<-rule.m15_trend_c else 0)
            if not trend_side:continue
            if trend_side*(float(m5['SMA20'][a]-m5['SMA20'][a-2]))<=0:continue
            side=-trend_side if rule.reverse_trend else trend_side
            high=float(np.max(m5['high'][a-11:a+1]));low=float(np.min(m5['low'][a-11:a+1]));span=high-low
            if span<150 or span>2500:continue
            rail=high-rule.fib*span if side>0 else low+rule.fib*span
            cl=float(m1['close'][i]);prev=float(m1['close'][i-1])
            if side*(cl-rail)<rule.reclaim_c or side*(prev-rail)>0:continue
            if side*(cl-rail)>rule.max_dist_c:continue
            if side>0:
                if min(m1['low'][i-3:i+1])>rail:continue
            else:
                if max(m1['high'][i-3:i+1])<rail:continue
            if rule.micro_ema:
                if side*(m1['EMA9'][i]-m1['EMA20'][i])<=0:continue
            if rule.anchor:
                tw=tape.twap[signal_tick_idx]
                if not np.isfinite(tw) or side*(rail-tw)>-10:continue
            spread=int(tape.ask[fill]-tape.bid[fill])
            if spread>25:continue
            minute=ts//60000
            if cap.get(minute,0)>=4:continue
            signal_n+=1
            j,net,kind=quote_exit(tape,fill,side,rule)
            if j is None:continue
            cap[minute]=cap.get(minute,0)+1
            last_exit=j
            completed.append((ts,int(tape.ms[j]),side,net,kind,spread,rail))
        n=len(completed)
        nets=np.asarray([x[3] for x in completed],dtype=float)
        total=float(nets.sum()) if n else 0.
        maxdd=None
        if n:
            equity=np.r_[0,np.cumsum(nets)];maxdd=float(np.max(np.maximum.accumulate(equity)-equity))
        kinds={k:sum(x[4]==k for x in completed) for k in ('target','stop','quote_gap','time_limit')}
        out[rule.name]={
          'rule':asdict(rule),'signals_before_capacity':signal_n,'trades':n,
          'wins':int(np.sum(nets>0)),'win_rate':round(float(np.mean(nets>0)),5) if n else None,
          'modeled_net':round(total,2),'mean_net':round(float(nets.mean()),5) if n else None,
          'max_closed_trade_equity_drawdown':round(maxdd,2) if maxdd is not None else None,
          'outcomes':kinds,'source_verified':sha,
          'not_broker_certified':True,'development_only':True}
        print(month,rule.name,'N',n,'NET',round(total,2),'WIN%',round(100*out[rule.name]['win_rate'],1) if n else 'na',flush=True)
    return out

if __name__=='__main__':
    months=sys.argv[1:] or ['01','05','09']
    res={}
    for m in months:
        start=time.monotonic();res[m]=month_run(m);print('elapsed',m,round(time.monotonic()-start,1),flush=True)
        Path('/mnt/data/cfael_v13/independent_pilot_'+m+'.json').write_text(json.dumps(res[m],indent=2))
    print(json.dumps({m:{name:[v['trades'],v['modeled_net'],v['win_rate']] for name,v in x.items()} for m,x in res.items()},indent=2))
