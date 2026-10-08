import sys,json,heapq,numpy as np
from collections import defaultdict,deque
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import source_drift_gate_133l as S
import feb_replay_jan_milestone_132a as F
import mar_replay_jan_milestone_133a as M
import jan_session_portfolio_131d as J
BASE='/mnt/data/gamma02_jan_repro'; DAY=86400000

def pf(a):
 a=np.asarray(a,float);gp=a[a>0].sum();gl=a[a<0].sum();return float(gp/-gl if gl<0 else 999.)
class Cert:
 def __init__(self,scout=2,prior=16,active=256,need=2):
  self.scout=scout;self.prior=prior;self.active=active;self.need=need;self.pending=[];self.seq=0
  self.cur=defaultdict(list);self.done=defaultdict(lambda:deque(maxlen=8));self.last_day={}
 def finalize_before(self,src,day):
  ld=self.last_day.get(src)
  if ld is None:self.last_day[src]=day;return
  if day!=ld:
   vals=self.cur.pop((src,ld),[]);net=sum(vals);pp=pf(vals) if vals else 0.;self.done[src].append((net,pp,len(vals)));self.last_day[src]=day
 def flush(self,now):
  while self.pending and self.pending[0][0]<=now:
   _,_,src,day,p=heapq.heappop(self.pending);self.cur[(src,day)].append(float(p))
 def certified(self,src):
  h=list(self.done[src]);
  if len(h)<self.need:return False
  last=h[-self.need:]
  return all(net>0 and pp>=1.05 and n>=2 for net,pp,n in last)
 def cap(self,src,day):
  self.finalize_before(src,day);vals=self.cur[(src,day)];cert=self.certified(src)
  base=self.prior if cert else self.scout
  n=len(vals)
  if n>=2:
   q=np.asarray(vals[-2:],float)
   if q.mean()<0 or pf(q)<.8:return 0
  if n>=4:
   q=np.asarray(vals[-4:],float)
   if q.mean()<0 or pf(q)<.9:return min(base,self.scout)
   if cert and q.mean()>=1. and pf(q)>=1.2:base=max(base,64)
  if n>=8:
   q=np.asarray(vals[-8:],float)
   if q.mean()<.25 or pf(q)<1.:return min(base,4)
   if cert and q.mean()>=1.5 and pf(q)>=1.4:base=max(base,self.active)
  return min(base,self.active)
 def push(self,xt,src,day,p):heapq.heappush(self.pending,(int(xt),self.seq,int(src),int(day),float(p)));self.seq+=1

def learner(C,t,a,b,R,gcap=1024):
 idx,score=S.raw_eligible(C);keep=[];glob=[];by=defaultdict(list)
 for k in idx:
  now=int(C['et'][k]);R.flush(now);src=int(C['src'][k]);day=now//DAY;key=(src,day)
  while glob and glob[0][0]<=now:heapq.heappop(glob)
  h=by[key]
  while h and h[0][0]<=now:heapq.heappop(h)
  cap=R.cap(src,day);R.push(C['xt'][k],src,day,C['p'][k])
  if cap<=0 or len(h)>=cap or len(glob)>=gcap:continue
  keep.append(k);rec=(int(C['xt'][k]),int(k));heapq.heappush(h,rec);heapq.heappush(glob,rec)
 kk=np.asarray(keep,np.int64);E=C['idx'][kk].astype(np.int64);X=np.minimum(np.searchsorted(t,C['xt'][kk]),len(t)-1).astype(np.int64);D=C['d'][kk].astype(np.int8);Rr=np.where(D>0,a[E],b[E]).astype(np.int64);P=C['p'][kk].astype(float);H=(C['xt'][kk]-C['et'][kk])/1000.;o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,Rr,D,P,H))
def stats(p):
 p=np.asarray(p,float);gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gl=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,exp=float(np.mean(p)) if len(p) else 0.)
def run(scout,prior,active,need):
 R=Cert(scout,prior,active,need);wdstate=None;out={}
 for mon,Mod in [('feb',F),('mar',M)]:
  C=S.load_cache(mon);B=S.load_base(mon);wd,wdstate=S.route_wd(B,Mod.t,wdstate,703);G=learner(C,Mod.t,Mod.a,Mod.b,R,1024);cov=S.q(B,'COV');cold=S.q(B,'COLD');Q,_=J.merge_preserve_watchdog(wd,[G,cov,cold],1024);q=S.quickscore(Mod.t,Q);out[mon]=dict(combined={k:q[k] for k in ['net','trades','gross_loss','pf','win','expectancy','positive_days','positive_weeks']},learner=stats(G[4]),wd=stats(wd[4]),weekly=q['weekly'],daily=q['daily'])
 return out
if __name__=='__main__':
 rows=[]
 for scout in [1,2,4,8]:
  for prior in [8,16,32]:
   for active in [64,128,256]:
    for need in [1,2]:
     r=run(scout,prior,active,need);rows.append(dict(scout=scout,prior=prior,active=active,need=need,**r))
 json.dump({'candidate':'SESSION_CERTIFICATION_ROUTER_133O','rows':rows},open(BASE+'/session_certification_router_133o.json','w'),indent=2)
 rows.sort(key=lambda r:(r['feb']['combined']['net'],r['feb']['combined']['pf']),reverse=True)
 for r in rows[:36]:print(json.dumps({'scout':r['scout'],'prior':r['prior'],'active':r['active'],'need':r['need'],'feb':r['feb']['combined'],'mar':r['mar']['combined'],'fl':r['feb']['learner'],'ml':r['mar']['learner']}))