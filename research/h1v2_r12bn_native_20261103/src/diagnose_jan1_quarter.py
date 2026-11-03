import sys,json,datetime
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r12_native/source')
from r12b_month_native import read_day,source_days,asof_quote_clocks,_rolling_extrema,earliest_finish_schedule,quote_tp_first
row=source_days('01')[0];t,b,a,rec=read_day(row,'01')
ix,flags=asof_quote_clocks(t,b,a)
q=int(datetime.datetime(2026,1,1,23,30,tzinfo=datetime.timezone.utc).timestamp()*1000)
z=(t[ix]>=q)&(t[ix]<q+900000)
print('DAY',row['date_utc'],'TICKS',len(t),'CANDIDATES Q',z.sum(),'SPAN',int(t[0]),int(t[-1]));print('MEDIAN SPREAD',float(np.median(a[(t>=q)&(t<q+900000)]-b[(t>=q)&(t<q+900000)]))/1000)
mb,xb,ma,xa,_,_,c15=_rolling_extrema(t,b,a,ix,15000)
mb30,xb30,ma30,xa30,_,_,c30=_rolling_extrema(t,b,a,ix,30000)
B=(xb.astype(np.int64)>=a[ix].astype(np.int64)+120)&(mb30.astype(np.int64)>b[ix].astype(np.int64)-100)&c15&c30
S=(ma.astype(np.int64)<=b[ix].astype(np.int64)-120)&(xa30.astype(np.int64)<a[ix].astype(np.int64)+100)&c15&c30
V=np.flatnonzero(z & (B|S));print('GOOD Q',len(V),'BUY',int(B[V].sum()),'SELL',int(S[V].sum()))
if len(V):
 vi=ix[V];side=np.where(B[V],1,-1).astype('int8');ei,et=quote_tp_first(t,b,a,vi,a[vi],b[vi],side);s=earliest_finish_schedule(t[vi],et)
 print('ISOLATED Q MAX',len(s),'first eligible',t[vi[0]],'last eligible',t[vi[-1]],'hold max',int(np.max(et-t[vi])))
 print('FIRST 10',[(int(t[vi[k]]),int(et[k]),int(side[k])) for k in s[:10]])
