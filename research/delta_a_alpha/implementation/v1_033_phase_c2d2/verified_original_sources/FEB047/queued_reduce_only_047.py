"""Research-only repair 047: rate-limited reduce-only closes; no live broker margin or endogenous source regeneration.
One execution per observed market tick across original entries and portfolio exits; at most ten per second.
"""
import sys,json,time
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data/feb047');import profit_protect_047 as v
OUT=Path('/mnt/data/feb047')
@njit
def run(E,X,R,D,P,S,t,a,b,exit_order,monitor,retreat_usd,window_samples,min_profit,close_batch,cooldown_seconds,side_limit,source_only,require_dd,max_orders_sec):
 n=len(E);N=len(t); Ex=X.copy();PX=P.copy();active=np.zeros(n,np.uint8)
 ei=0;xi=0;mi=0;pending=0;qidx=N;p_side=0;lastaction=-1_000_000_000_000
 acct=100000.;nL=0;nS=0;pL=0.;pS=0.;peak=100000.;samples=np.zeros(96,np.float64);sm_count=0;nclose=0;actions=0
 sec_last=-1;nsent=0;entry_tick=-1;max_close_sec=0;sec_close=0;max_combined=0
 while ei<n or xi<n or mi<len(monitor) or pending>0:
  ne=E[ei] if ei<n else N
  nx=X[exit_order[xi]] if xi<n else N
  nm=monitor[mi] if mi<len(monitor) else N
  tick=min(ne,nx,nm,qidx)
  if tick>=N:break
  cursec=t[tick]//1000
  if cursec!=sec_last:
   sec_last=cursec;nsent=0;sec_close=0
  entry_tick=-1
  while xi<n and X[exit_order[xi]]<=tick:
   j=exit_order[xi];xi+=1
   if not active[j]:continue
   active[j]=0;acct+=PX[j]
   if D[j]>0:nL-=1;pL-=R[j]
   else:nS-=1;pS-=R[j]
  while ei<n and E[ei]<=tick:
   j=ei;ei+=1;active[j]=1
   if D[j]>0:nL+=1;pL+=R[j]
   else:nS+=1;pS+=R[j]
   nsent+=1;entry_tick=tick
  if nm==tick:
   mi+=1
   mid=(a[tick]+float(b[tick]))/2
   samples[sm_count%96]=mid;sm_count+=1
   mx=mid;mn=mid
   for off in range(min(sm_count,window_samples)):
    y=samples[(sm_count-1-off)%96]
    if y>mx:mx=y
    if y<mn:mn=y
   eq=acct+(nL*b[tick]-pL+pS-nS*a[tick])/1000.-.02*(nL+nS)
   if eq>peak:peak=eq
   dom=1 if nL>=nS else -1
   retreat=((mx-mid) if dom>0 else (mid-mn))/1000.
   if pending==0 and retreat>=retreat_usd and max(nL,nS)>=side_limit and t[tick]-lastaction>=cooldown_seconds*1000 and peak-eq>=require_dd:
    p_side=dom;pending=min(close_batch,int(max(nL,nS)*.25));qidx=tick;lastaction=t[tick];actions+=1
  if pending>0 and qidx==tick:
   if entry_tick!=tick and nsent<max_orders_sec:
    selected=-1
    for j in range(ei):
     if not active[j] or D[j]!=p_side:continue
     if source_only and S[j] not in (22,25):continue
     pnl=((b[tick]-R[j]) if D[j]>0 else (R[j]-a[tick]))/1000.-.02
     if pnl<min_profit:continue
     selected=j;break
    if selected>=0:
     j=selected;price=b[tick] if D[j]>0 else a[tick]
     pnl=((price-R[j]) if D[j]>0 else (R[j]-price))/1000.-.02
     active[j]=0;Ex[j]=tick;PX[j]=pnl;acct+=pnl
     if D[j]>0:nL-=1;pL-=R[j]
     else:nS-=1;pS-=R[j]
     pending-=1;nclose+=1;nsent+=1;sec_close+=1
     if sec_close>max_close_sec:max_close_sec=sec_close
     if nsent>max_combined:max_combined=nsent
    else:pending=0
   qidx=tick+1 if pending>0 else N
 return Ex,PX,nclose,actions,max_close_sec,max_combined

if __name__=='__main__':
 cases=[('focused_best',json.load(open(OUT/'FEB047_FOCUSED_BEST.json'))['params'], 'pocket_09_no_heat_ledger.npz'),('reversal_best',json.load(open(OUT/'FEB047_REVERSAL_BEST.json'))['params'],'pocket_09_no_heat_ledger.npz'),('transfer_best',json.load(open(OUT/'FEB047_TRANSFER_BEST.json'))['params'],'state_cut8_c22512_c25512_ledger.npz')]
 rows=[]
 for label,params,ledger in cases:
  z=np.load(Path('/mnt/data/feb045')/ledger)
  for k in ('E','X','R','D','P','S'):setattr(v,k,np.ascontiguousarray(z[k]))
  v.exit_order=np.ascontiguousarray(np.argsort(v.X).astype(np.int64))
  r=run(v.E,v.X,v.R,v.D,v.P,v.S,v.t,v.a,v.b,v.exit_order,v.monitor,**params,max_orders_sec=10)
  ex,px,n,actions,per_sec,combined=r
  audit=v.evaluate(ex,px)
  audit.update(label=label,exits_early=int(n),actions=int(actions),max_portfolio_closes_per_sec=int(per_sec),max_original_entry_plus_close=int(combined),baseline=v.evaluate(v.X,v.P))
  rows.append(audit);print('LIMITED',json.dumps(audit),flush=True)
  np.savez_compressed(OUT/('FEB047_QUEUED_'+label+'.npz'),E=v.E,X=ex,R=v.R,D=v.D,P=px,S=v.S)
 (OUT/'FEB047_QUEUED_RESULTS.json').write_text(json.dumps(rows,indent=2))
