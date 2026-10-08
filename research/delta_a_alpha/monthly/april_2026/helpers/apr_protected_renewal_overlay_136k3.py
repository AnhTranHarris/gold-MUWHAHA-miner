from __future__ import annotations
import json,heapq,time
from collections import deque,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,sys
sys.path.insert(0,'/mnt/data/april_vertical_work')
import apr_vertical_portfolio_136g as A
O=Path('/mnt/data/april_vertical_work')

def load(path,prefix):
 z=np.load(path);return tuple(z[f'{prefix}_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
N=load(O/'apr_native_conviction_refine_streams_136h.npz','WIN87')
HV=load(O/'apr_session_grid_streams_136b.npz','HIGHVOL_PF8')
AS=load(O/'apr_session_grid_streams_136b.npz','ASIA_PF8')
REN=load(O/'apr_phase_renewal_streams_136e.npz','PF5')
SYN=dict(net=38353.96,gross_loss=-2414.22,pf=16.886688,win=.86759242,expectancy=1.207694)

def bucket(ms,scope):
 d=datetime.fromtimestamp(int(ms)/1000,tz=timezone.utc)
 return d.hour if scope=='HOUR' else d.hour*6+d.minute//10

def rolling(Q,scope,nlook):
 E,X,R,D,P,H=Q;E=np.asarray(E,np.int64);X=np.asarray(X,np.int64);P=np.asarray(P,float)
 xo=np.argsort(X,kind='stable');ptr=0;hist=defaultdict(lambda:deque(maxlen=nlook))
 n=np.zeros(len(E),np.int16);net=np.zeros(len(E));pf=np.zeros(len(E));win=np.zeros(len(E))
 for ii in np.argsort(E,kind='stable'):
  now=int(E[ii])
  while ptr<len(xo) and int(X[xo[ptr]])<=now:
   j=int(xo[ptr]);hist[bucket(E[j],scope)].append(float(P[j]));ptr+=1
  q=list(hist[bucket(now,scope)])
  if q:
   a=np.asarray(q);gp=a[a>0].sum();gl=a[a<=0].sum();n[ii]=len(a);net[ii]=a.sum();pf[ii]=gp/-gl if gl<0 else 999.;win[ii]=(a>0).mean()
 return n,net,pf,win

def core():
 rec=A.dedup([('NATIVE',N),('HIGHVOL',HV),('ASIA',AS),('RECOVERY',A.REC)])
 q,mo,sk=A.caprec(rec,176)
 return q,A.score(q),mo,sk
CORE,CORE_SCORE,CORE_MO,CORE_SK=core()

def overlay(gate,cap):
 E,X,R,D,P,H=REN
 hp=[];out=[];sk=0;mo=0
 for i in range(len(E)):
  e=int(E[i])
  while hp and hp[0][0]<=e:heapq.heappop(hp)
  if not gate[i]:continue
  if len(hp)>=cap:sk+=1;continue
  r=(e,int(X[i]),int(R[i]),int(D[i]),float(P[i]),float(H[i]),'RENEWAL')
  out.append(r);heapq.heappush(hp,(int(X[i]),i));mo=max(mo,len(hp))
 return out,mo,sk

def allm(s):return s['net']>=SYN['net'] and s['gross_loss']>=SYN['gross_loss'] and s['pf']>=SYN['pf'] and s['win']>=SYN['win'] and s['expectancy']>=SYN['expectancy'] and s['positive_weeks']==s['active_weeks']

def main():
 t0=time.time();rows=[]
 stats={(scope,n):rolling(REN,scope,n) for scope in ['HOUR','HOUR10'] for n in [8,16,32]}
 for scope in ['HOUR','HOUR10']:
  for nlook in [8,16,32]:
   rn,rnet,rpf,rwin=stats[(scope,nlook)];minn=max(4,nlook//2)
   for pft in [3.,5.,8.,12.,20.]:
    for wt in [.85,.90,.95]:
     gate=(rn>=minn)&(rnet>0)&(rpf>=pft)&(rwin>=wt)
     for cap in [4,8,16,32,64]:
      ov,mo,sk=overlay(gate,cap);combined=sorted(CORE+ov,key=lambda r:(r[0],0 if r[6]=='RENEWAL' else 1));s=A.score(combined);s.update(scope=scope,nlook=nlook,minn=minn,pfthr=pft,winthr=wt,overlay_cap=cap,overlay_trades=len(ov),overlay_maxopen=mo,overlay_skips=sk,core_trades=CORE_SCORE['trades'],core_net=CORE_SCORE['net'],all_metrics=allm(s));rows.append(s)
 good=[r for r in rows if r['all_metrics']];good.sort(key=lambda r:(-r['trades'],-r['net'],abs(r['gross_loss'])))
 out={'unit':'DAA_APRIL_PROTECTED_RENEWAL_OVERLAY_136K3','status':'COMPLETE','core':{**{k:CORE_SCORE[k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','active_days','positive_weeks','active_weeks']},'cap':176,'maxopen':CORE_MO,'skips':CORE_SK},'all_metric_count':len(good),'top_trade':good[:60],'top_net':sorted(good,key=lambda r:(-r['net'],-r['trades']))[:60],'runtime_s':time.time()-t0,'causal_rule':'renewal overlay never displaces quality core; gate uses only already-closed same hour/subphase shadow renewal outcomes'}
 (O/'apr_protected_renewal_overlay_136k3.json').write_text(json.dumps(out,indent=2))
 print('CORE',out['core']);print('GOOD',len(good),'runtime',out['runtime_s'])
 for r in good[:20]:print(json.dumps({k:r[k] for k in ['scope','nlook','pfthr','winthr','overlay_cap','overlay_trades','net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','active_days','positive_weeks','active_weeks','overlay_maxopen','overlay_skips']}))
if __name__=='__main__':main()