import sys, json, heapq, numpy as np
from collections import defaultdict, deque
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import source_drift_gate_133l as S
import feb_replay_jan_milestone_132a as F
import mar_replay_jan_milestone_133a as M
import jan_session_portfolio_131d as J
BASE='/mnt/data/gamma02_jan_repro'

def pf(a):
 a=np.asarray(a,float);gp=a[a>0].sum();gl=a[a<0].sum();return float(gp/-gl if gl<0 else 999.)
class Gear:
 def __init__(self,variant='A'):
  self.variant=variant;self.hist=defaultdict(lambda:deque(maxlen=64));self.pending=[];self.seq=0
 def flush(self,now):
  while self.pending and self.pending[0][0]<=now:
   _,_,src,p=heapq.heappop(self.pending);self.hist[src].append(float(p))
 def push(self,xt,src,p):heapq.heappush(self.pending,(int(xt),self.seq,int(src),float(p)));self.seq+=1
 def cap(self,src):
  h=np.asarray(self.hist[src],float);n=len(h)
  if n<4:return 2
  f4=h[-4:];m4=float(f4.mean());p4=pf(f4)
  if m4<0 or p4<.8:return 0
  cap=4
  f8=h[-8:] if n>=8 else h;m8=float(f8.mean());p8=pf(f8)
  if n>=8 and m8>=.5 and p8>=1.1:cap=16
  if n>=16:
   f16=h[-16:];m16=float(f16.mean());p16=pf(f16)
   if m16>=1. and p16>=1.25:cap=64
  if n>=24:
   f24=h[-24:];m24=float(f24.mean());p24=pf(f24)
   if m24>=1.5 and p24>=1.5:cap=256
  if n>=32:
   f32=h[-32:];m32=float(f32.mean());p32=pf(f32)
   if self.variant=='A':
    if m32>=2. and p32>=2.:cap=1024
   elif self.variant=='B':
    if m32>=1.5 and p32>=1.5:cap=1024
   elif self.variant=='C':
    if m32>=2.5 and p32>=2.5:cap=1024
  # fast degradation wall, preserving a tiny scout channel
  if n>=8 and m4<.5:cap=min(cap,4)
  return cap

def learner(C,t,a,b,gear,globalcap=1024):
 idx,score=S.raw_eligible(C);keep=[];active=[];asrc=defaultdict(list)
 for k in idx:
  now=int(C['et'][k]);gear.flush(now)
  while active and active[0][0]<=now:heapq.heappop(active)
  src=int(C['src'][k]);h=asrc[src]
  while h and h[0][0]<=now:heapq.heappop(h)
  cap=gear.cap(src);gear.push(C['xt'][k],src,C['p'][k])
  if cap<=0 or len(h)>=cap or len(active)>=globalcap:continue
  keep.append(k);rec=(int(C['xt'][k]),int(k));heapq.heappush(h,rec);heapq.heappush(active,rec)
 kk=np.asarray(keep,np.int64);E=C['idx'][kk].astype(np.int64);X=np.minimum(np.searchsorted(t,C['xt'][kk]),len(t)-1).astype(np.int64);D=C['d'][kk].astype(np.int8);R=np.where(D>0,a[E],b[E]).astype(np.int64);P=C['p'][kk].astype(float);H=(C['xt'][kk]-C['et'][kk])/1000.;o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,R,D,P,H))

def stats(p):
 p=np.asarray(p,float);gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gl=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,exp=float(np.mean(p)) if len(p) else 0.)
def quick(t,Q):
 E,X,R,D,P,H=Q;p=np.asarray(P,float);gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=len(p),gl=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)),exp=float(np.mean(p)))
def run(variant='A',carry=True,gcap=1024,wdq=703,scap=1024):
 gear=Gear(variant);wdstate=None;res={}
 for mon,Mod in [('feb',F),('mar',M)]:
  C=S.load_cache(mon);B=S.load_base(mon);wd,wdstate=S.route_wd(B,Mod.t,wdstate,wdq);G=learner(C,Mod.t,Mod.a,Mod.b,gear,gcap);cov=S.q(B,'COV');cold=S.q(B,'COLD');Q,_=J.merge_preserve_watchdog(wd,[G,cov,cold],scap);q=S.quickscore(Mod.t,Q);res[mon]=dict(combined={k:q[k] for k in ['net','trades','gross_loss','pf','win','expectancy','positive_days','positive_weeks']},learner=stats(G[4]),wd=stats(wd[4]),weekly=q['weekly'],daily=q['daily'])
  if mon=='feb' and not carry:gear=Gear(variant);wdstate=None
 return res
if __name__=='__main__':
 rows=[]
 for v in ['A','B','C']:
  for gcap in [256,512,703,1024]:
   r=run(v,True,gcap,703,1024);rows.append(dict(variant=v,gcap=gcap,**r))
 json.dump({'candidate':'SOURCE_EARNED_TRANCHE_133M','rows':rows},open(BASE+'/source_earned_tranche_133m.json','w'),indent=2)
 for r in rows:print(json.dumps({'variant':r['variant'],'gcap':r['gcap'],'feb':r['feb']['combined'],'mar':r['mar']['combined'],'fl':r['feb']['learner'],'ml':r['mar']['learner']}))