import sys,gc
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
US_DST=1772953200000;UK_DST=1774746000000;DAY_MS=86400000;P75=np.asarray([20,20,21,21],np.int64);TICK_RAW=10

def sess_idx(ts):
 ts=np.asarray(ts,dtype=np.int64);tod=ts%DAY_MS
 ls=np.where(ts>=UK_DST,7,8)*3600000;le=ls+30600000
 ns=np.where(ts>=US_DST,12,13)*3600000;ne=ns+32400000
 il=(tod>=ls)&(tod<le);iny=(tod>=ns)&(tod<ne)
 return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75_quotes(ts,ar,br):
 s=sess_idx(ts);sp=P75[s]*TICK_RAW;m=ar.astype(np.int64)+br.astype(np.int64);bid=((m-sp+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def add_run_dtopp(df):
 cd=df.cross_dir.to_numpy(np.int8);tm=df.time_ms.to_numpy(np.int64);run=np.ones(len(df),np.int32);dto=np.full(len(df),-1,np.int64);last={1:-1,-1:-1}
 for i in range(len(df)):
  if i>0:run[i]=run[i-1]+1 if cd[i]==cd[i-1] else 1
  if run[i]>=2:
   opp=-int(cd[i]);dto[i]=-1 if last[opp]<0 else tm[i]-last[opp]
  last[int(cd[i])]=tm[i]
 df=df.copy();df['run_calc']=run;df['dtopp_calc']=dto;return df

@njit(cache=True)
def sim(t,ask,bid,ev_times,sides,horizons,stop):
 n=len(ev_times);out=np.empty(n,np.float64);ex=np.empty(n,np.int64)
 for k in range(n):
  tm=ev_times[k];i=np.searchsorted(t,tm)
  if i>=len(t):out[k]=np.nan;ex[k]=tm;continue
  side=int(sides[k]);entry=ask[i]/1000.0 if side==1 else bid[i]/1000.0;jend=np.searchsorted(t,tm+int(horizons[k])*1000)
  if jend>=len(t):jend=len(t)-1
  p=0.0;xt=t[jend];hit=False
  for j in range(i+1,jend+1):
   p=(bid[j]/1000.0-entry-0.02) if side==1 else (entry-ask[j]/1000.0-0.02)
   if p<=-stop:xt=t[j];hit=True;break
  if not hit:p=(bid[jend]/1000.0-entry-0.02) if side==1 else (entry-ask[jend]/1000.0-0.02)
  out[k]=p;ex[k]=xt
 return out,ex

mo=sys.argv[1];base=Path('/mnt/data');tickfiles={'feb':'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','mar':'XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','apr':'XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','may':'XAUUSD_DUKAS_2026_05_ticks.csv(3).gz','jun':'XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','jul':'XAUUSD_DUKAS_2026_07_ticks.csv(2).gz'}
core=add_run_dtopp(pd.read_csv(base/f'delta_a_r2_{mo}_core_events.csv'))
ticks=pd.read_csv(base/tickfiles[mo],usecols=['timestamp_ms_utc','ask_raw','bid_raw']);t=ticks.timestamp_ms_utc.to_numpy(np.int64);ask,bid=p75_quotes(t,ticks.ask_raw.to_numpy(np.int64),ticks.bid_raw.to_numpy(np.int64))
for st,label in [(3.0,'3'),(5.0,'5'),(7.5,'7p5'),(10.0,'10'),(15.0,'15')]:
 p,ex=sim(t,ask,bid,core.time_ms.to_numpy(np.int64),core.trade_dir.to_numpy(np.int8),core.horizon_s.to_numpy(np.int64),st)
 core[f'pnl_stop{label}']=p;core[f'exit_stop{label}_ms']=ex
out=base/f'sa100_{mo}_core_stopvariants.csv';core.to_csv(out,index=False);print(mo,len(core),out)
