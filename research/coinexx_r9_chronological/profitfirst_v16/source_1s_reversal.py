"""V16 research-only: source-exact one-second reclaims and verified quote cascades.
Completed 1s event observed at first quote of NEXT second. Fill one source
quote later, never prior seconds' revised/future prices. All targets / stops
in source quote-side prices, not passive limit orders or actual broker fills.
"""
from __future__ import annotations
import hashlib,sys,time,json,argparse,os
from pathlib import Path
import numpy as np,pandas as pd
BASE=Path(os.environ.get('COINEXX_DATA_ROOT','/mnt/data'))
LEDGERS=Path(os.environ.get('V12_EVENT_LEDGER_ROOT',str(BASE/'r9_micro180_v12_results')))
OUT=Path(os.environ.get('V16_RESEARCH_OUT',str(BASE/'v16_profitfirst')))
CONFIGS={
 'FADE_1S_BREAKOUT_15S_TARGET035':('CR',15,30,0,0.35,40,5000),
 'FADE_1S_BREAKOUT_30S_TARGET035':('CR',30,30,0,0.35,40,5000),
 'FOLLOW_1S_FAILED_RECLAIM_15S_TARGET035':('RR',15,20,10,0.35,40,5000),
 'FADE_1S_BREAKOUT_15S_TARGET075':('CR',15,30,0,0.75,60,10000),
}

def event_candidates(ms,bid,ask,cfg):
    typ,lookback,sweep_c,reclaim_c,target,stop,hold=cfg
    mid=(bid.astype(float)+ask)/2
    bucket=ms//1000
    start=np.r_[0,np.flatnonzero(np.diff(bucket)!=0)+1]
    end=np.r_[start[1:]-1,len(ms)-1]
    high=np.maximum.reduceat(mid,start);low=np.minimum.reduceat(mid,start);close=mid[end]
    seconds=bucket[start];maxgap=np.maximum.reduceat(np.diff(ms,prepend=ms[0]),start)
    prev_hi=pd.Series(high).shift(1).rolling(lookback,min_periods=lookback//2).max().to_numpy()
    prev_lo=pd.Series(low).shift(1).rolling(lookback,min_periods=lookback//2).min().to_numpy()
    val=(np.arange(len(start))>=lookback)&np.isfinite(prev_hi)&np.isfinite(prev_lo)
    # Confirm previous seconds span close to real elapsed time. No bars across
    # invisible gaps; prior extremes are defined from actually observed ticks.
    prior_seq=np.maximum(0,np.arange(len(start))-lookback)
    val &= (seconds-seconds[prior_seq] <= lookback+3)
    val &= (maxgap<=2500)
    if typ in ('R','RR'):
        up=(low<=prev_lo-sweep_c)&(close>=prev_lo+reclaim_c)
        down=(high>=prev_hi+sweep_c)&(close<=prev_hi-reclaim_c)
        side=np.where(up&~down,1,np.where(down&~up,-1,0))
    else:
        # Last completed second broke a known (not current) prior range
        # and the close remains close to its observed extreme.
        up=(close>=prev_hi+sweep_c)&((high-close)<=(high-low)*.25)
        down=(close<=prev_lo-sweep_c)&((close-low)<=(high-low)*.25)
        side=np.where(up&~down,1,np.where(down&~up,-1,0))
    val &= (side!=0)&((prev_hi-prev_lo)>=60)&((prev_hi-prev_lo)<=2000)
    if typ in ('CR','RR'):
        # Observed completed-bar directional breakout/reclaim failed as a
        # continuation hypothesis; test the *opposite* side prospectively.
        side=-side
    val &= (end-start>=2)
    # Next second first quote sees completed prior second. New order can only
    # execute on a quote AFTER that availability quote.
    fill=start[1:]+1;idx=np.flatnonzero(val[:-1])
    if len(idx)==0:return np.empty(0,dtype=np.int64),np.empty(0,dtype=np.int8),{'eligible':0}
    fill=fill[idx];sd=side[idx].astype(np.int8)
    valid=(fill<len(ms))&(ms[fill]-ms[start[idx+1]]<=500)&(ms[start[idx+1]]-ms[end[idx]]<=2500)
    valid&=(ask[fill]-bid[fill]<=25)&(ask[fill]>=bid[fill])
    # Avoid book-unknown speed chases, but do not demand too much confirmation.
    return fill[valid],sd[valid],{'raw':len(idx),'eligible':int(valid.sum())}

def exit_trade(ms,bid,ask,entry,side,config):
    _,_,_,_,target,stop,hold=config
    t=int(ms[entry]);finish=int(np.searchsorted(ms,t+hold,side='right'))
    if finish<=entry+1:return None
    ex=int(ask[entry] if side>0 else bid[entry]);initial=int(bid[entry] if side>0 else ask[entry])
    liq=(bid[entry+1:finish] if side>0 else ask[entry+1:finish]).astype(np.int32)
    cash=side*(liq-ex)/100.-.2
    drift=side*(liq-initial)
    gaps=np.diff(ms[entry:finish])>2500
    events=(cash>=target)|(drift<=-stop)|gaps
    hits=np.flatnonzero(events)
    k=int(hits[0]) if len(hits) else len(liq)-1
    j=entry+1+k
    reason='GAP' if gaps[k] else ('STOP' if drift[k]<=-stop else ('TARGET' if cash[k]>=target else 'TIME'))
    return (j,float(round(float(cash[k]),4)),reason)

def run_month(mon):
    src=BASE/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
    expected=pd.read_csv(LEDGERS/'V12_MONTHLY_SOURCE_PROOF.csv',dtype={'month':str}).set_index('month').loc[mon,'source_sha256']
    with src.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    if sha!=expected:raise AssertionError('Original source SHA mismatch')
    t0=time.monotonic();df=pd.read_csv(src,usecols=['time_msc','bid','ask'])
    ms=df.time_msc.to_numpy(dtype='int64');bid=np.rint(df.bid.to_numpy()*100).astype('int32');ask=np.rint(df.ask.to_numpy()*100).astype('int32');del df
    result={'month':mon,'quote_records':len(ms),'sha256':sha,'models':{}}
    for name,cfg in CONFIGS.items():
        fill,side,counts=event_candidates(ms,bid,ask,cfg)
        minute_counts={};last_exit_idx=-1;last_exit_ms=-10000000
        cash=[];reasons=[];events=[]
        for idx,di in zip(fill,side):
            idx=int(idx); now=int(ms[idx]);minute=now//60000
            if idx<=last_exit_idx or now-last_exit_ms<1500 or minute_counts.get(minute,0)>=4:continue
            trade=exit_trade(ms,bid,ask,idx,int(di),cfg)
            if trade is None:continue
            j,net,why=trade
            last_exit_idx=j;last_exit_ms=int(ms[j]);minute_counts[minute]=minute_counts.get(minute,0)+1
            cash.append(net);reasons.append(why);events.append((int(idx+1),int(j+1),int(di),net,why))
        arr=np.asarray(cash,dtype=float)
        equity=np.r_[0,np.cumsum(arr)];mdd=np.max(np.maximum.accumulate(equity)-equity)
        result['models'][name]={'raw_signals':counts['raw'],'eligible_signals':counts['eligible'],
             'trades':len(arr),'positive':int((arr>0).sum()),'win_rate':float((arr>0).mean()) if len(arr) else None,
             'net_cash':round(float(arr.sum()),2),'mean_net':round(float(arr.mean()),5) if len(arr) else None,
             'max_closed_trade_drawdown':round(float(mdd),2),'target_n':reasons.count('TARGET'),
             'stop_n':reasons.count('STOP'),'gap_n':reasons.count('GAP'),'timeout_n':reasons.count('TIME'),
             'past_only':True,'first_available_quote':True,'demo_trades':False,'cost_per_trade':0.20}
        print(mon,name,'raw',counts['raw'],'trades',len(arr),'positive',int((arr>0).sum()),'net',round(float(arr.sum()),2),flush=True)
    OUT.mkdir(parents=True,exist_ok=True);(OUT/f'V16_{mon}_FADE_1S.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SECS',mon,round(time.monotonic()-t0,1),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('months',nargs='*');z=p.parse_args()
    for m in z.months or ('01','05','09'):run_month(m)
