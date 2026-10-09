"""FEB047 research-only frozen-accepted-ledger counterfactual: causal profitable-cohort reduction.
Does NOT reproduce new source proposals or native V1 L6. No month/day feature in trading logic.
Accepted entries fixed by FEB045; all early reductions settle at observed Bid/Ask.
"""
import sys,json,time
from pathlib import Path
import numpy as np
from numba import njit
F=Path('/mnt/data/feb045'); OUT=Path('/mnt/data/feb047')
z=np.load(F/'pocket_09_no_heat_ledger.npz'); E,X,R,D,P,S=[np.ascontiguousarray(z[k]) for k in ('E','X','R','D','P','S')]
t=np.load('/mnt/data/feb044_work/quotes_t.npy',mmap_mode='r')
a=np.load('/mnt/data/feb044_work/quotes_a.npy',mmap_mode='r')
b=np.load('/mnt/data/feb044_work/quotes_b.npy',mmap_mode='r')
t=np.ascontiguousarray(t); a=np.ascontiguousarray(a); b=np.ascontiguousarray(b)
exit_order=np.ascontiguousarray(np.argsort(X).astype(np.int64))
# 5s monitor at FIRST available quote of a wall-clock bucket; no artificial bars.
monitor=np.ascontiguousarray(np.flatnonzero(np.r_[True, np.diff(t//5000)>0]).astype(np.int64))
@njit
def simulate(E,X,R,D,P,S,t,a,b,exit_order,monitor,dd_trigger,stress_limit,profit_min,close_batch,cooldown_seconds,side_limit,source_mode,protect_frac):
    n=len(E); N=len(t)
    Ex=X.copy();PX=P.copy()
    alive=np.zeros(n,np.uint8)
    account=100000.; nlong=0;nshort=0;long_prices=0.;short_prices=0.;peak=100000.
    ei=0;xi=0;mi=0;prev_action=-1_000_000_000_000;reductions=0;red_profit=0.;action_count=0
    while ei<n or xi<n or mi<len(monitor):
        next_e=E[ei] if ei<n else N
        next_x=X[exit_order[xi]] if xi<n else N
        next_m=monitor[mi] if mi<len(monitor) else N
        current=min(next_e,next_x,next_m)
        if current==N:break
        while xi<n and X[exit_order[xi]]<=current:
            j=exit_order[xi];xi+=1
            if not alive[j]:continue
            alive[j]=0;account+=PX[j]
            if D[j]>0:nlong-=1;long_prices-=R[j]
            else:nshort-=1;short_prices-=R[j]
        while ei<n and E[ei]<=current:
            j=ei;ei+=1;alive[j]=1
            if D[j]>0:nlong+=1;long_prices+=R[j]
            else:nshort+=1;short_prices+=R[j]
        if next_m==current:
            mi+=1
            floatp=(nlong*b[current]-long_prices+short_prices-nshort*a[current])/1000.-.02*(nlong+nshort)
            equity=account+floatp
            if equity>peak:peak=equity
            dd=peak-equity
            side_stress=max(nlong,nshort)*10.0
            # account state only; 5s sampled observed tick for dynamic decisions
            if t[current]-prev_action>=cooldown_seconds*1000 and (dd>=dd_trigger or side_stress>=stress_limit) and max(nlong,nshort)>=side_limit:
                count=0;potential=0
                # target dominant direction, not future outcome; optional S22/S25 only.
                dom=1 if nlong>=nshort else -1
                for j in range(ei):
                    if not alive[j] or D[j]!=dom:continue
                    if source_mode==1 and S[j]!=22:continue
                    if source_mode==2 and S[j]!=25:continue
                    if source_mode==3 and S[j] not in (22,25):continue
                    pnl=((b[current]-R[j]) if D[j]>0 else (R[j]-a[current]))/1000.-.02
                    if pnl >= profit_min:potential+=1
                want=min(close_batch, int(max(nlong,nshort)*protect_frac))
                if want>0 and potential>=want//2:
                    for j in range(ei):
                        if count>=want:break
                        if not alive[j] or D[j]!=dom:continue
                        if source_mode==1 and S[j]!=22:continue
                        if source_mode==2 and S[j]!=25:continue
                        if source_mode==3 and S[j] not in (22,25):continue
                        pnl=((b[current]-R[j]) if D[j]>0 else (R[j]-a[current]))/1000.-.02
                        if pnl<profit_min:continue
                        alive[j]=0;Ex[j]=current;PX[j]=pnl;account+=pnl
                        if D[j]>0:nlong-=1;long_prices-=R[j]
                        else:nshort-=1;short_prices-=R[j]
                        count+=1;reductions+=1;red_profit+=pnl
                    if count>0:prev_action=t[current];action_count+=1
    # Original exit events were in heap, but if all entries processed after last monitor, they get settled by loop.
    return Ex,PX,reductions,red_profit,action_count

def evaluate(Ex,PX):
    N=len(t); long=D>0; sho=D<0
    gp=float(PX[PX>0].sum());gl=float(PX[PX<0].sum());net=float(PX.sum())
    nl=np.cumsum(np.bincount(E[long],minlength=N)-np.bincount(Ex[long],minlength=N),dtype=np.int32)
    ns=np.cumsum(np.bincount(E[sho],minlength=N)-np.bincount(Ex[sho],minlength=N),dtype=np.int32)
    pl=np.cumsum(np.bincount(E[long],weights=R[long],minlength=N)-np.bincount(Ex[long],weights=R[long],minlength=N))
    ps=np.cumsum(np.bincount(E[sho],weights=R[sho],minlength=N)-np.bincount(Ex[sho],weights=R[sho],minlength=N))
    realized=np.cumsum(np.bincount(Ex,weights=PX,minlength=N))
    equity=realized+(nl.astype(np.float64)*b-pl+ps-ns.astype(np.float64)*a)/1000.-.02*(nl+ns)
    dd=np.maximum.accumulate(equity)-equity
    out=dict(net=round(net,3),gl=round(gl,3),pf=round(gp/-gl,4),trades=len(PX),dd=round(float(dd.max()),3),max_open=int(np.max(nl+ns)),reconcile_max_error=float(np.max(np.abs(PX-((np.where(long,b[Ex]-R,R-a[Ex]))/1000.-.02)))) )
    return out
if __name__=='__main__':
    t0=time.monotonic();base=evaluate(X,P);print('BASE',json.dumps(base),flush=True)
    params=[]
    # high profit reduction while adverse risk already accumulating; multiple correlated campaign pressure
    for trig in (3500.,6000.,8500.):
      for stress in (9000.,14000.):
       for batch in (64,192):
        for src in (0,3):
         params.append(dict(dd_trigger=trig,stress_limit=stress,profit_min=1.,close_batch=batch,cooldown_seconds=30.,side_limit=300,source_mode=src,protect_frac=0.35))
    rows=[]
    for k,p in enumerate(params):
      ex,px,nclose,profit,actions=simulate(E,X,R,D,P,S,t,a,b,exit_order,monitor,**p)
      # cheap conditional prefilter before expensive full DD computation
      net=float(px.sum());gl=float(px[px<0].sum());
      row=dict(index=k,params=p,net_screen=round(net,3),gl_screen=round(gl,3),early_exits=int(nclose),profit_of_early_exits=round(profit,2),actions=int(actions))
      if net>=190000:
       row.update(evaluate(ex,px))
      rows.append(row);print('CASE',json.dumps(row),flush=True)
      (OUT/'FEB047_PROFIT_PROTECTION_SCREEN.json').write_text(json.dumps(rows,indent=2))
    print('COMPLETE',len(rows),'time',time.monotonic()-t0,flush=True)