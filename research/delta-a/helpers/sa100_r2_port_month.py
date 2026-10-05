import sys, json, math, heapq, gc
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

US_DST=1772953200000
UK_DST=1774746000000
DAY_MS=86400000
P75=np.asarray([20,20,21,21],np.int64)
TICK_RAW=10

def sess_idx(ts):
    ts=np.asarray(ts,dtype=np.int64);tod=ts%DAY_MS
    ls=np.where(ts>=UK_DST,7,8)*3600000;le=ls+30600000
    ns=np.where(ts>=US_DST,12,13)*3600000;ne=ns+32400000
    il=(tod>=ls)&(tod<le);iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75_quotes(ts,ar,br):
    s=sess_idx(ts);sp=P75[s]*TICK_RAW;m=ar.astype(np.int64)+br.astype(np.int64)
    bid=((m-sp+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    return (bid+sp).astype(np.int64),bid.astype(np.int64)

def add_run_dtopp(df):
    cd=df.cross_dir.to_numpy(np.int8);tm=df.time_ms.to_numpy(np.int64)
    run=np.ones(len(df),np.int32);dto=np.full(len(df),-1,np.int64);last={1:-1,-1:-1}
    for i in range(len(df)):
        if i>0:run[i]=run[i-1]+1 if cd[i]==cd[i-1] else 1
        if run[i]>=2:
            opp=-int(cd[i])
            if last[opp]>=0:dto[i]=tm[i]-last[opp]
        last[int(cd[i])]=tm[i]
    df=df.copy();df['run_calc']=run;df['dtopp_calc']=dto
    return df

@njit(cache=True)
def sim_varhorizon_stop(t,ask,bid,ev_times,sides,horizons,stop):
    n=len(ev_times);out=np.empty(n,np.float64);ex=np.empty(n,np.int64)
    for k in range(n):
        tm=ev_times[k];i=np.searchsorted(t,tm)
        if i>=len(t):out[k]=np.nan;ex[k]=tm;continue
        side=int(sides[k]);entry=ask[i]/1000.0 if side==1 else bid[i]/1000.0
        jend=np.searchsorted(t,tm+int(horizons[k])*1000)
        if jend>=len(t):jend=len(t)-1
        p=0.0;xt=t[jend];hit=False
        for j in range(i+1,jend+1):
            p=(bid[j]/1000.0-entry-0.02) if side==1 else (entry-ask[j]/1000.0-0.02)
            if p<=-stop:
                xt=t[j];hit=True;break
        if not hit:
            p=(bid[jend]/1000.0-entry-0.02) if side==1 else (entry-ask[jend]/1000.0-0.02)
        out[k]=p;ex[k]=xt
    return out,ex

def capital(tm,p,ex,start_ms,end_ms,base_slots=3,target=500,startbal=100):
    bal=float(startbal);minb=bal;active=[];seq=0;tr=0;wins=0
    i0=np.searchsorted(tm,start_ms);i1=np.searchsorted(tm,end_ms)
    for q in range(i0,i1):
        now=tm[q]
        while active and active[0][0]<=now:
            xt,_,pv=heapq.heappop(active);bal+=pv;tr+=1;wins+=pv>0;minb=min(minb,bal)
            if bal>=target:return dict(success=True,hit_time=int(xt),min_balance=minb,end_balance=bal,trades=tr,wins=wins)
            if bal<=0:return dict(success=False,hit_time=None,min_balance=minb,end_balance=bal,trades=tr,wins=wins)
        cur=base_slots
        if bal>=200:cur=max(cur,2)
        if bal>=350:cur=max(cur,3)
        if len(active)>=cur:continue
        heapq.heappush(active,(int(ex[q]),seq,float(p[q])));seq+=1
    while active:
        xt,_,pv=heapq.heappop(active)
        if xt>end_ms:break
        bal+=pv;tr+=1;wins+=pv>0;minb=min(minb,bal)
        if bal>=target:return dict(success=True,hit_time=int(xt),min_balance=minb,end_balance=bal,trades=tr,wins=wins)
    return dict(success=bal>=target,hit_time=None,min_balance=minb,end_balance=bal,trades=tr,wins=wins)

mo=sys.argv[1]
base=Path('/mnt/data')
tickfiles={'feb':'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','mar':'XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','apr':'XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','may':'XAUUSD_DUKAS_2026_05_ticks.csv(3).gz','jun':'XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','jul':'XAUUSD_DUKAS_2026_07_ticks.csv(2).gz'}
core=pd.read_csv(base/f'delta_a_r2_{mo}_core_events.csv')
core=add_run_dtopp(core)
mask=(core.run_calc>=2)&(core.dtopp_calc>=0)&(core.dtopp_calc<=10000)
ev=core.loc[mask].sort_values('time_ms').reset_index(drop=True)
ticks=pd.read_csv(base/tickfiles[mo],usecols=['timestamp_ms_utc','ask_raw','bid_raw'])
t=ticks.timestamp_ms_utc.to_numpy(np.int64);ar=ticks.ask_raw.to_numpy(np.int64);br=ticks.bid_raw.to_numpy(np.int64)
ask,bid=p75_quotes(t,ar,br)
p,ex=sim_varhorizon_stop(t,ask,bid,ev.time_ms.to_numpy(np.int64),ev.trade_dir.to_numpy(np.int8),ev.horizon_s.to_numpy(np.int64),5.0)
ev['pnl_stop5']=p;ev['exit_ms_stop5']=ex
rows=[]
for slots in [1,2,3]:
    z=capital(ev.time_ms.to_numpy(np.int64),p,ex,int(t[0]),int(t[-1]),base_slots=slots)
    z.update(slots=slots)
    if z['hit_time']:
        z['days_to_500']=(z['hit_time']-int(t[0]))/86400000
    else:z['days_to_500']=None
    rows.append(z)
summary={
 'month':mo,'signals':int(len(ev)),'signal_net':float(np.nansum(p)),'signal_avg':float(np.nanmean(p)),'signal_win_rate':float(np.nanmean(p>0)),'signal_min':float(np.nanmin(p)),
 'capital_runs':rows
}
(base/f'sa100_r2_run_dtopp_{mo}_events.csv').write_text(ev.to_csv(index=False),encoding='utf-8')
(base/f'sa100_r2_run_dtopp_{mo}_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
