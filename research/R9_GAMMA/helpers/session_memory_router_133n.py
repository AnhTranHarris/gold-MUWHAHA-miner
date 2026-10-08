import sys, json, heapq, numpy as np
from collections import defaultdict, deque
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import source_drift_gate_133l as S
import feb_replay_jan_milestone_132a as F
import mar_replay_jan_milestone_133a as M
import jan_session_portfolio_131d as J
BASE='/mnt/data/gamma02_jan_repro';DAY=86400000

def pf(a):
 a=np.asarray(a,float);gp=a[a>0].sum();gl=a[a<0].sum();return float(gp/-gl if gl<0 else 999.)
class Router:
 def __init__(self,scout=2,priorcap=16,maxcap=512):
  self.scout=scout;self.priorcap=priorcap;self.maxcap=maxcap;self.long=defaultdict(lambda:deque(maxlen=64));self.sess=defaultdict(lambda:deque(maxlen=32));self.pending=[];self.seq=0
 def flush(self,now):
  while self.pending and self.pending[0][0]<=now:
   _,_,src,day,p=heapq.heappop(self.pending);self.long[src].append(float(p));self.sess[(src,day)].append(float(p))
 def push(self,xt,src,day,p):heapq.heappush(self.pending,(int(xt),self.seq,int(src),int(day),float(p)));self.seq+=1
 def cap(self,src,day):
  L=np.asarray(self.long[src],float);S=np.asarray(self.sess[(src,day)],float);nl,ns=len(L),len(S)
  # cross-session prior: only earned from realized history, no calendar labels
  prior=self.scout
  if nl>=16 and L[-16:].mean()>=1.0 and pf(L[-16:])>=1.25:prior=self.priorcap
  if nl>=32 and L[-32:].mean()>=2.0 and pf(L[-32:])>=1.5:prior=max(prior,self.priorcap*2)
  # fresh session starts guarded; session evidence earns capacity quickly
  cap=prior
  if ns>=2:
   q=S[-2:]
   if q.mean()<0 or pf(q)<.8:return 0
   if q.mean()>=.5 and pf(q)>=1.:cap=max(cap,8)
  if ns>=4:
   q=S[-4:]
   if q.mean()<0 or pf(q)<.9:return min(cap,self.scout)
   if q.mean()>=1. and pf(q)>=1.2:cap=max(cap,32)
  if ns>=8:
   q=S[-8:]
   if q.mean()<.25 or pf(q)<1.:return min(cap,4)
   if q.mean()>=1.5 and pf(q)>=1.4:cap=max(cap,128)
  if ns>=16:
   q=S[-16:]
   if q.mean()>=2. and pf(q)>=1.5:cap=max(cap,self.maxcap)
  return min(cap,self.maxcap)

def learner(C,t,a,b,R,globalcap=1024):
 idx,score=S.raw_eligible(C);keep=[];glob=[];by=defaultdict(list)
 for k in idx:
  now=int(C['et'][k]);R.flush(now);src=int(C['src'][k]);day=now//DAY;key=(src,day)
  while glob and glob[0][0]<=now:heapq.heappop(glob)
  h=by[key]
  while h and h[0][0]<=now:heapq.heappop(h)
  cap=R.cap(src,day);R.push(C['xt'][k],src,day,C['p'][k])
  if cap<=0 or len(h)>=cap or len(glob)>=globalcap:continue
  keep.append(k);rec=(int(C['xt'][k]),int(k));heapq.heappush(h,rec);heapq.heappush(glob,rec)
 kk=np.asarray(keep,np.int64);E=C['idx'][kk].astype(np.int64);X=np.minimum(np.searchsorted(t,C['xt'][kk]),len(t)-1).astype(np.int64);D=C['d'][kk].astype(np.int8);Rr=np.where(D>0,a[E],b[E]).astype(np.int64);P=C['p'][kk].astype(float);H=(C['xt'][kk]-C['et'][kk])/1000.;o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,Rr,D,P,H))
def stats(p):
 p=np.asarray(p,float);gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gl=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,exp=float(np.mean(p)) if len(p) else 0.)
def run(scout=2,priorcap=16,maxcap=512,gcap=1024):
 R=Router(scout,priorcap,maxcap);wdstate=None;out={}
 for mon,Mod in [('feb',F),('mar',M)]:
  C=S.load_cache(mon);B=S.load_base(mon);wd,wdstate=S.route_wd(B,Mod.t,wdstate,703);G=learner(C,Mod.t,Mod.a,Mod.b,R,gcap);cov=S.q(B,'COV');cold=S.q(B,'COLD');Q,_=J.merge_preserve_watchdog(wd,[G,cov,cold],1024);q=S.quickscore(Mod.t,Q);out[mon]=dict(combined={k:q[k] for k in ['net','trades','gross_loss','pf','win','expectancy','positive_days','positive_weeks']},learner=stats(G[4]),wd=stats(wd[4]),weekly=q['weekly'],daily=q['daily'])
 return out
if __name__=='__main__':
 rows=[]
 for scout in [1,2,4]:
  for prior in [8,16,32]:
   for mx in [128,256,512]:
    r=run(scout,prior,mx,1024);rows.append(dict(scout=scout,prior=prior,maxcap=mx,**r))
 json.dump({'candidate':'SESSION_MEMORY_ROUTER_133N','rows':rows},open(BASE+'/session_memory_router_133n.json','w'),indent=2)
 rows.sort(key=lambda r:(r['feb']['combined']['net'],r['feb']['combined']['pf']),reverse=True)
 for r in rows[:30]:print(json.dumps({'scout':r['scout'],'prior':r['prior'],'maxcap':r['maxcap'],'feb':r['feb']['combined'],'mar':r['mar']['combined'],'fl':r['feb']['learner'],'ml':r['mar']['learner']}))