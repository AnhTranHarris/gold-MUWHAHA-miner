"""FEB046 diagnostics: independent post-funded-loss L6 recovery OVERLAY, NOT fully coupled V1.
All recovery entries occur after prior accepted L3 ticket has genuinely closed at a loss.
Completed M5/H1 direction gate, actual Bid/Ask entry and first-touch exit; original accepted proposal stream
frozen (not regenerated) and recovery capacity gating based on baseline accepted inventory + recoveries.
Replaying both via independent full tick equity calculations. 0.01 per ticket, no Martingale.
"""
from pathlib import Path
import json,datetime
import numpy as np
from numba import njit
ROOT=Path('/mnt/data/feb046')
T=np.load('/mnt/data/feb044_work/quotes_t.npy',mmap_mode='r')
A=np.load('/mnt/data/feb044_work/quotes_a.npy',mmap_mode='r')
B=np.load('/mnt/data/feb044_work/quotes_b.npy',mmap_mode='r')
Z=np.load('/mnt/data/feb045/pocket_09_no_heat_ledger.npz');L={k:Z[k] for k in Z.files}
N=len(T)
@njit
def exits(t,a,b,entries,directions,tp,sl,max_sec):
    x=np.empty(len(entries),np.int64);p=np.empty(len(entries),np.float64)
    for i in range(len(entries)):
        e=entries[i];d=directions[i]
        start=a[e] if d>0 else b[e]
        deadline=t[e]+max_sec*1000
        j=e+1
        while j<len(t) and t[j]<=deadline:
            current=b[j] if d>0 else a[j]
            adv=(current-start)*d/1000.
            if adv>=tp or adv<=-sl:break
            j+=1
        if j>=len(t):j=len(t)-1
        elif t[j]>deadline:j=min(j,len(t)-1)
        x[i]=j
        current=b[j] if d>0 else a[j]
        p[i]=(current-start)*d/1000.-0.02
    return x,p

def q_metrics(ld,exact=True):
    E,X,R,D,P=[ld[k] for k in 'EXRDP'];lon=D>0;sho=D<0
    net=float(P.sum());gl=float(P[P<0].sum());gp=float(P[P>0].sum());o={'net':round(net,3),'gross_loss':round(gl,3),'pf':round(gp/(-gl),5),'trades':len(P)}
    if exact:
        nl=np.cumsum(np.bincount(E[lon],minlength=N)-np.bincount(X[lon],minlength=N))
        ns=np.cumsum(np.bincount(E[sho],minlength=N)-np.bincount(X[sho],minlength=N))
        rL=np.cumsum(np.bincount(E[lon],weights=R[lon],minlength=N)-np.bincount(X[lon],weights=R[lon],minlength=N))
        rS=np.cumsum(np.bincount(E[sho],weights=R[sho],minlength=N)-np.bincount(X[sho],weights=R[sho],minlength=N))
        real=np.cumsum(np.bincount(X,weights=P,minlength=N))
        eq=real+(nl*B-rL+rS-ns*A)/1000.-.02*(nl+ns)
        dd=np.maximum.accumulate(eq)-eq;tr=int(np.argmax(dd));pk=int(np.argmax(eq[:tr+1]))
        o.update(dd=round(float(dd[tr]),3),peak_tick=pk,trough_tick=tr,maxopen=int((nl+ns).max()))
    return o

def conditions(delay_ms=1000,struct='M5', direction='reverse'):
    losers=np.flatnonzero(L['P']<0)
    base_close=L['X'][losers]
    idx=np.searchsorted(T,T[base_close]+delay_ms,side='left');idx=np.minimum(idx,N-3)
    d=-L['D'][losers] if direction=='reverse' else L['D'][losers]
    bi=T[idx]//300000
    c1=np.searchsorted(T,bi*300000,side='left')-1
    c2=np.searchsorted(T,(bi-1)*300000,side='left')-1
    mom=(B[c1]+A[c1])-(B[c2]+A[c2])
    allow=c2>=0
    if struct=='M5':allow &= (mom*d)>0
    if struct=='H1':
        hr=T[idx]//3600000
        h1=np.searchsorted(T,hr*3600000,side='left')-1
        h2=np.searchsorted(T,(hr-1)*3600000,side='left')-1
        allow &=h2>=0
        allow &=((B[h1]+A[h1])-(B[h2]+A[h2]))*d>0
    if struct=='both':
        hr=T[idx]//3600000
        h1=np.searchsorted(T,hr*3600000,side='left')-1
        h2=np.searchsorted(T,(hr-1)*3600000,side='left')-1
        allow &=h2>=0
        allow &=((B[h1]+A[h1])-(B[h2]+A[h2]))*d>0
        allow &=(mom*d)>0
    # pre-entry spread constraint
    allow &= ((A[idx]-B[idx])<=3000)
    allow &=T[idx]>T[base_close]
    return idx[allow],d[allow],losers[allow]

def model(params):
    ent,dir,loser_idx=conditions(params['delay'],params['struct'],params['direction'])
    X,P=exits(T,A,B,ent,dir,params['tp'],params['sl'],params['hold'])
    # account-level entrance gate at the time of entry from original actual accepted portfolio
    baseline=np.cumsum(np.bincount(L['E'],minlength=N)-np.bincount(L['X'],minlength=N))
    base_rate=np.unique(T[L['E']]//1000,return_counts=True)
    rs=dict(zip(base_rate[0],base_rate[1]))
    active_heap=[];import heapq
    acc_ent=[];acc_ex=[];acc_p=[];acc_dir=[];acc_src=[];used_sec={};denials={'capacity':0,'rate':0,'own_cap':0}
    for j,e in enumerate(ent):
        while active_heap and active_heap[0]<=e:heapq.heappop(active_heap)
        second=int(T[e]//1000)
        if int(baseline[e])+len(active_heap)>=params['cap']:
            denials['capacity']+=1;continue
        if len(active_heap)>=params['own_cap']:
            denials['own_cap']+=1;continue
        if rs.get(second,0)+used_sec.get(second,0)>=params['rate']:
            denials['rate']+=1;continue
        # no duplicate entry per quote
        if acc_ent and e==acc_ent[-1]:continue
        acc_ent.append(e);acc_ex.append(X[j]);acc_p.append(P[j]);acc_dir.append(dir[j]);acc_src.append(L['S'][loser_idx[j]])
        used_sec[second]=used_sec.get(second,0)+1
        heapq.heappush(active_heap,int(X[j]))
    EE=np.asarray(acc_ent,np.int64);XX=np.asarray(acc_ex,np.int64);DD=np.asarray(acc_dir,np.int8);PP=np.asarray(acc_p,np.float64)
    if len(EE):
        if not np.all(np.isin(np.arange(len(EE)),np.arange(len(EE)))):raise AssertionError()
        RR=np.where(DD>0,A[EE],B[EE]);chk=(np.where(DD>0,B[XX],A[XX])-RR)*DD/1000.-.02
        assert np.max(abs(chk-PP))<1e-8
    else:RR=np.array([],np.int32)
    out=dict(E=np.r_[L['E'],EE],X=np.r_[L['X'],XX],R=np.r_[L['R'],RR],D=np.r_[L['D'],DD],P=np.r_[L['P'],PP],S=np.r_[L['S'],np.full(len(EE),62)])
    inc_p=PP.sum();inc_gl=PP[PP<0].sum();return out,dict(recovery_trades=len(EE),net_increment=round(float(inc_p),3),gross_loss_increment=round(float(inc_gl),3),denials=denials,source_breakdown={str(s):int(np.sum(np.array(acc_src)==s)) for s in set(acc_src)})
if __name__=='__main__':
  rows=[]
  base=q_metrics(L)
  print('BASE',json.dumps(base),flush=True)
  for st in ['M5','H1','both']:
   for side in ['reverse','continuation']:
    for tp,sl in [(3.,2.),(6.,3.),(10.,5.)]:
     par=dict(struct=st,direction=side,delay=1000,tp=tp,sl=sl,hold=240,cap=1536,own_cap=8,rate=10)
     new,rec=model(par)
     # only calculate costly exact DD for profitable recovery or close frontier
     score=q_metrics(new,exact=False)
     rows.append(dict(config=par,**score,**rec))
     print('REC',st,side,tp,sl,score['net'],score['gross_loss'],score['pf'],score['trades'],rec['recovery_trades'],rec['net_increment'],flush=True)
  rows.sort(key=lambda x:(x['net'],x['pf']),reverse=True)
  for i,row in enumerate(rows[:4]):
    new,rec=model(row['config']);exact=q_metrics(new,True);row.update(exact)
    print('EXACT',json.dumps({'config':row['config'],'new':exact}),flush=True)
  (ROOT/'RECOVERY_SCREEN.json').write_text(json.dumps({'base':base,'screen':rows},indent=2))