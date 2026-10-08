import sys, json, heapq, numpy as np
from collections import deque
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import feb_replay_jan_milestone_132a as F
import mar_replay_jan_milestone_133a as M
import jan_session_portfolio_131d as J
from gamma02_feb_native_markout_124 import build_events
BASE='/mnt/data/gamma02_jan_repro'; HORIZONS=[30,60,120,300]

def group_features(et,xt,p,key,W=16):
 n=np.zeros(len(et),np.int16);mean=np.zeros(len(et),np.float32);pff=np.zeros(len(et),np.float32);win=np.zeros(len(et),np.float32);dd=np.zeros(len(et),np.float32)
 vals,inv=np.unique(key,return_inverse=True);order=np.argsort(inv,kind='stable');cuts=np.flatnonzero(np.diff(inv[order]))+1;groups=np.split(order,cuts)
 for idxs in groups:
  pending=[];q=deque();s=gp=gl=0.;wins=0;seq=0
  for i in idxs:
   now=int(et[i])
   while pending and pending[0][0]<=now:
    _,_,v=heapq.heappop(pending);v=float(v)
    if len(q)>=W:
     old=q.popleft();s-=old
     if old>0:gp-=old;wins-=1
     elif old<0:gl-=old
    q.append(v);s+=v
    if v>0:gp+=v;wins+=1
    elif v<0:gl+=v
   nn=len(q);n[i]=nn
   if nn:
    mean[i]=s/nn;pff[i]=gp/-gl if gl<0 else 999.;win[i]=wins/nn
    a=np.asarray(q,float);bal=np.cumsum(a);prior=np.r_[0.,bal[:-1]];peak=np.maximum.accumulate(prior);dd[i]=float(np.max(peak-bal))
   heapq.heappush(pending,(int(xt[i]),seq,float(p[i])));seq+=1
 return n,mean,pff,win,dd

def prep(Mod,label):
 t,a,b,mid,h4,h1,m15,m5,start,end=Mod.DATA
 idx,d,hr,sig,disp=build_events(t,mid,h4,h1,m15,m5,start,end,50);et=t[idx];entry=np.where(d>0,a[idx],b[idx]).astype(np.int64);cell=hr.astype(np.int64)*1000+sig.astype(np.int64)
 out=dict(idx=idx,d=d,hr=hr,sig=sig,disp=disp,et=et,cell=cell)
 for sec in HORIZONS:
  x=np.searchsorted(t,et+sec*1000,side='left');x=np.minimum(x,len(t)-1);ex=np.where(d>0,b[x],a[x]).astype(np.int64);p=((ex-entry)*d)/1000.-.02;xt=t[x]
  out[f'x{sec}']=x;out[f'p{sec}']=p;out[f'xt{sec}']=xt
  for W in [4,8,16,32]:
   n,m,pf,w,dd=group_features(et,xt,p,cell,W);out[f'n{sec}_{W}']=n;out[f'm{sec}_{W}']=m;out[f'pf{sec}_{W}']=pf;out[f'w{sec}_{W}']=w;out[f'dd{sec}_{W}']=dd
 np.savez_compressed(f'{BASE}/{label}_native_online_cache_133p.npz',**out);return out

def load_or_prep(Mod,label):
 p=f'{BASE}/{label}_native_online_cache_133p.npz'
 try:
  z=np.load(p);return {k:z[k] for k in z.files}
 except: return prep(Mod,label)

def capsel(E,X,cap):
 o=np.argsort(E,kind='stable');Eo=E[o];h=[];keep=[]
 for oi,k in enumerate(o):
  now=int(E[k])
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:continue
  keep.append(k);heapq.heappush(h,(int(X[k]),int(k)))
 return np.asarray(keep,np.int64)

def learner(Mod,C,minn=8,meanthr=.5,pfthr=1.25,W=16,cap=512,score_mode='meanpf'):
 t,a,b=Mod.t,Mod.a,Mod.b;N=len(C['idx']);bestscore=np.full(N,-1e30,float);bestsec=np.zeros(N,np.int16)
 for sec in HORIZONS:
  n=C[f'n{sec}_{W}'];m=C[f'm{sec}_{W}'];pff=C[f'pf{sec}_{W}'];dd=C[f'dd{sec}_{W}'];elig=(n>=minn)&(m>=meanthr)&(pff>=pfthr)
  if score_mode=='meanpf':sc=m*np.log1p(np.minimum(pff,20.))-.02*dd
  elif score_mode=='mean':sc=m-.02*dd
  else:sc=m*pff/(1.+dd)
  take=elig&(sc>bestscore);bestscore[take]=sc[take];bestsec[take]=sec
 idx=np.flatnonzero(bestsec>0);E=C['idx'][idx].astype(np.int64);D=C['d'][idx].astype(np.int8);X=np.empty(len(idx),np.int64);P=np.empty(len(idx),float);H=np.empty(len(idx),float)
 for sec in HORIZONS:
  m=bestsec[idx]==sec;X[m]=C[f'x{sec}'][idx[m]];P[m]=C[f'p{sec}'][idx[m]];H[m]=(C[f'xt{sec}'][idx[m]]-C['et'][idx[m]])/1000.
 R=np.where(D>0,a[E],b[E]).astype(np.int64);kk=capsel(E,X,cap);E,X,R,D,P,H=[z[kk] for z in (E,X,R,D,P,H)];o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,R,D,P,H))
def st(p):
 p=np.asarray(p,float);gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gl=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,exp=float(np.mean(p)) if len(p) else 0.)
if __name__=='__main__':
 Cf=load_or_prep(F,'feb');rows=[]
 for W in [8,16,32]:
  for minn in [4,8,12,16]:
   if minn>W:continue
   for mt in [0.,.5,1.,2.]:
    for pt in [1.,1.25,1.5,2.]:
     for cap in [128,256,512,703]:
      G=learner(F,Cf,minn,mt,pt,W,cap);s=st(G[4]);s.update(W=W,minn=minn,meanthr=mt,pfthr=pt,cap=cap);rows.append(s)
 rows.sort(key=lambda r:(r['net'],r['pf']),reverse=True);json.dump({'rows':rows},open(BASE+'/native_online_lifecycle_133p_screen.json','w'),indent=2)
 for r in rows[:40]:print(json.dumps(r))