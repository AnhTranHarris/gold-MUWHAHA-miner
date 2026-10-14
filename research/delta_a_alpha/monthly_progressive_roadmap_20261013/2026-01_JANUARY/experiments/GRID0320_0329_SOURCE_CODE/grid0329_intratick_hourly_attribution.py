"""Research-only explanation of a $0.06 intraquote hourly-DD reconciliation deviation.
Stored separate from original 40-episode independent cash/equity audit.
"""
from __future__ import annotations
import numpy as np,gzip,json
import grid0328_conservative_source_slippage_stress as p

def main():
 a=None
 with gzip.open('/mnt/data/jan_continuation_20261013/grid0329_full_40_portfolios_original_quote_booked_deal_ledger.ndjson.gz','rt') as f:
  for l in f:
   x=json.loads(l)
   if x['start_day']=='2026-01-23' and x['policy']=='ADVERSE_0P30':a=x;break
 assert a
 t,bid,ask,z,k,o,g,r9,org=p.p.p.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 d=int(np.datetime64('2026-01-23T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,d,'left');hi=np.searchsorted(t,d+7*86400000,'left');t=t[lo:hi];b=bid[lo:hi];ak=ask[lo:hi]
 n=len(t);dlo=np.zeros(n+1,int);dsh=np.zeros(n+1,int);dbasis=np.zeros(n+1,float);dcash=np.zeros(n+1,float)
 en_mtm=np.zeros(n,float)
 for deal in a['booked_deals']:
  i=deal['entry_quote_idx'];j=deal['exit_quote_idx'];dr=deal['direction'];px=deal['entry_price_usd'];net=deal['modeled_net_cash']
  if dr>0:dlo[i]+=1;dlo[j]-=1
  else:dsh[i]+=1;dsh[j]-=1
  dbasis[i]+=dr*px;dbasis[j]-=dr*px;dcash[j]+=net
  en_mtm[i]+=(dr*((int(b[i] if dr>0 else ak[i])/1000.)-px)-.20)
 longs=np.cumsum(dlo[:-1]);shorts=np.cumsum(dsh[:-1]);cash=np.cumsum(dcash[:-1]);basis=np.cumsum(dbasis[:-1]);opened=longs+shorts
 q=100+cash+(longs*b-shorts*ak)/1000.-basis-.20*opened
 pre=q-en_mtm
 keys=t//3600000;idx=np.r_[0,np.flatnonzero(np.diff(keys))+1,n]
 max1=0.;max2=0.;top=None;dbg=None
 for start,end in zip(idx[:-1],idx[1:]):
  post=q[start:end];dd=np.maximum.accumulate(post)-post
  if dd.max()>max1:max1=float(dd.max());top=keys[start]
  both=np.empty(2*len(post));both[0::2]=pre[start:end];both[1::2]=post
  d2=np.maximum.accumulate(both)-both
  if d2.max()>max2:max2=float(d2.max());dbg=(keys[start],int(start+np.argmax(d2)//2),float(np.max(pre[start:end]-post)))
 print('UTC hour after-booking-only DD',max1,'two-state prior-to-fill and post-fill DD',max2,'hour',top,'debug',dbg)
 print('source original model reports',a['initial_cash'],a['final_cash'])
if __name__=='__main__':main()
