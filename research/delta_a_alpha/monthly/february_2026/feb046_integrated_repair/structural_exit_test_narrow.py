"""FEB046 experimental pre-close failure-conditioned REDUCE-ONLY cut applied to original source proposals.
Source generator unchanged; physical admission re-run with changed *causal first-touch exits*. The old fixed proposal tape is still NOT fully endogenous original V1. No Martingale, no hindsight inputs.
"""
import os,sys,time,json
from pathlib import Path
import numpy as np
from numba import njit
R=Path('/mnt/data/feb044_work');F=Path('/mnt/data/feb045');OUT=Path('/mnt/data/feb046')
src=(F/'run_statecaps.py').read_text().split('log=[]')[0];ns={'__file__':str(F/'run_statecaps.py'),'__name__':'feb046_exp'};exec(compile(src,'feb045_pinned','exec'),ns)
m=ns['m'];h=ns['h'];base=ns['base'];order=ns['order'];params=ns['params'];s=m.S;phase=ns['ph'];prior=ns['r'];den=np.zeros_like(base)
for p in order[:9]:den|=p
m.spread=np.where(~(base&~den),np.inf,h.spr)
T=m.t;A=m.a;B=m.b
X0=m.X.copy();P0=m.P.copy();E=m.E;R0=m.R;D=m.D
print('LOADED',len(T),len(E),int(((s==22)|(s==25)).sum()), flush=True)
# signed displacement of two FRESH completed consecutive 5m candles by calendar bucket
k=T//300000;uni,first=np.unique(k,return_index=True);last=np.r_[first[1:]-1,len(T)-1];close=(A[last].astype(np.float64)+B[last].astype(np.float64))/2000
# table per bucket offset: completed last two bars availability and trend
startk=int(uni[0]); tab=np.zeros(int(uni[-1]-uni[0]+2),np.int8)
for i in range(2,len(uni)):
 if uni[i-1]==uni[i]-1 and uni[i-2]==uni[i]-2:
  tab[int(uni[i]-startk)]=np.sign(close[i-1]-close[i-2])
@njit
def first_failure(E,X,R,D,S,allowed,T,A,B,tab,k0,delay_ms,adverse_dollars,mode,phase_mask):
  out=X.copy();n=0
  for i in range(len(E)):
    if not allowed[i] or (S[i] not in (22,25)):continue
    if S[i]==22 and not (phase_mask & 1):continue
    if S[i]==25 and not (phase_mask & 2):continue
    en=E[i];oldX=X[i];d=D[i];origin=R[i]
    early=np.searchsorted(T,T[en]+delay_ms)
    if early>=oldX:continue
    for j in range(early,oldX):
       mark=B[j] if d>0 else A[j]
       adv=(mark-origin)*d/1000
       if adv>-adverse_dollars:continue
       lookup=int(T[j]//300000-k0)
       if lookup<0 or lookup>=len(tab):continue
       trend=tab[lookup]
       if mode==1 and trend*d>=0:continue
       if mode==2 and trend*d>0:continue
       out[i]=j;n+=1;break
  return out,n
allowed=base&~den
configs=[]
# Baseline
start=time.time();z,ld=m.run(**params);m.daily_and_exact(ld,z);print('BASE',z['net'],z['gl'],z['pf'],z['trades'],z['equity_dd'],'runtime',round(time.time()-start,2),flush=True)
for source_mask in [1,2,3]:
 for d in [180_000]:
  for adverse in [18.,24.]:
   for mode in [1]:
    ts=time.time();newx,changes=first_failure(E,X0,R0,D,s,allowed,T,A,B,tab,startk,d,adverse,mode,source_mask)
    m.X=newx
    updated=np.flatnonzero(newx<X0)
    m.P=P0.copy()
    m.P[updated]=(np.where(D[updated]>0,B[newx[updated]],A[newx[updated]])-R0[updated])*D[updated]/1000.-0.02
    out,ledger=m.run(**params)
    if out['net']>=199000 or (out['event_eq_dd_lb']<15000 and out['net']>=175000):m.daily_and_exact(ledger,out)
    row=dict(masks=source_mask,delay=d,adverse=adverse,mtf=mode,firstcuts=changes,net=out['net'],gl=out['gl'],pf=out['pf'],trades=out['trades'],dd=out.get('equity_dd'),eventdd=out['event_eq_dd_lb'],elapsed=round(time.time()-ts,2))
    configs.append(row);print('STRUCT',json.dumps(row),flush=True)
    (OUT/'STRUCTURAL_EXIT_NARROW.json').write_text(json.dumps({'baseline':{k:z[k] for k in ('net','gl','pf','trades','equity_dd')},'cases':configs},indent=2))