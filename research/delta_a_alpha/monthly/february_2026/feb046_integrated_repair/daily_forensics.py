"""Independently reconstruct equity per quote and realized P&L by UTC close day, all original Feb045 accepted positions.
Month is evaluation partition, not runtime trigger.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import numpy as np
ROOT=Path('/mnt/data/feb046');T=np.load('/mnt/data/feb044_work/quotes_t.npy',mmap_mode='r');A=np.load('/mnt/data/feb044_work/quotes_a.npy',mmap_mode='r');B=np.load('/mnt/data/feb044_work/quotes_b.npy',mmap_mode='r');N=len(T)
result=[]
for case,file in [('profit','pocket_09_no_heat_ledger.npz'),('prevention','state_cut8_c22512_c25512_ledger.npz')]:
 z=np.load('/mnt/data/feb045/'+file); E,X,R,D,P=[z[k] for k in 'EXRDP'];long=D>0;sho=~long
 nl=np.cumsum(np.bincount(E[long],minlength=N)-np.bincount(X[long],minlength=N))
 ns=np.cumsum(np.bincount(E[sho],minlength=N)-np.bincount(X[sho],minlength=N))
 lr=np.cumsum(np.bincount(E[long],weights=R[long],minlength=N)-np.bincount(X[long],weights=R[long],minlength=N))
 sr=np.cumsum(np.bincount(E[sho],weights=R[sho],minlength=N)-np.bincount(X[sho],weights=R[sho],minlength=N))
 real=np.cumsum(np.bincount(X,weights=P,minlength=N))
 eq=real+(nl*B-lr+sr-ns*A)/1000-.02*(nl+ns)
 days=T//86400000;unique,st=np.unique(days,return_index=True);ex=np.r_[st[1:],len(T)]
 report=[]
 for day,x,y in zip(unique,st,ex):
  if day<np.datetime64('2026-02-01').astype('datetime64[D]').astype(int)+0:continue
  segment=eq[x:y];dd=np.max(np.maximum.accumulate(segment)-segment); exit_prices=P[(T[X]//86400000)==day]
  report.append(dict(date=datetime.fromtimestamp(int(day)*86400,timezone.utc).date().isoformat(),ticks=int(y-x),completed=len(exit_prices),realized_net=round(float(exit_prices.sum()),2),realized_gross_loss=round(float(exit_prices[exit_prices<0].sum()),2),intraday_exact_eq_dd=round(float(dd),2),peakopen=int(np.max(nl[x:y]+ns[x:y]))))
 worst=sorted(report,key=lambda r:r['intraday_exact_eq_dd'],reverse=True)[:5]
 result.append(dict(case=case,report=report,worst=worst))
 print('DAILY',case,'worst',json.dumps(worst),flush=True)
(ROOT/'DAILY_FORENSICS.json').write_text(json.dumps(result,indent=2))