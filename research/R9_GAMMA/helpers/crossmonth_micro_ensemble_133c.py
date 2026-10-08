import sys,json,heapq,datetime as dt,os
from collections import defaultdict,deque
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import gamma02_mar_native_portfolio_130r as N
BASE='/mnt/data/gamma02_jan_repro';DAY=86400000

def pf(a):
 a=np.asarray(a,float);gp=a[a>0].sum();gl=a[a<0].sum();return float(gp/-gl if gl<0 else 999.)
def load_npz(p):
 z=np.load(p);d={k:z[k] for k in z.files};z.close();return d
def q(B,pre):return tuple(B[pre+'_'+x] for x in ['E','X','R','D','P','H'])
def stats(P):
 P=np.asarray(P,float);gp=float(P[P>0].sum());gl=float(P[P<0].sum());return dict(net=float(P.sum()),trades=int(len(P)),gross_loss=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(P>0)) if len(P) else 0.,expectancy=float(np.mean(P)) if len(P) else 0.)
def cap_arrays(Q,cap):
 E,X,R,D,P,H=Q;o=np.argsort(E,kind='stable');E,X,R,D,P,H=[z[o] for z in Q];h=[];keep=[];mo=0
 for k,now in enumerate(E):
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:continue
  keep.append(k);heapq.heappush(h,(int(X[k]),k));mo=max(mo,len(h))
 kk=np.asarray(keep,np.int64);return tuple(z[kk] for z in (E,X,R,D,P,H)),mo
def dedup(parts):
 seen=set();outs=[[] for _ in range(6)]
 for Q in parts:
  E,X,R,D,P,H=Q
  for k in range(len(E)):
   key=int(E[k])
   if key in seen:continue
   seen.add(key)
   for j,z in enumerate((E,X,R,D,P,H)):outs[j].append(z[k])
 dts=[np.int64,np.int64,np.int64,np.int8,float,float];return tuple(np.asarray(x,dtype=dts[j]) for j,x in enumerate(outs))
def merge(wd,parts,cap=1024):
 S=dedup(parts);S,_=cap_arrays(S,cap);Q=tuple(np.concatenate([wd[j],S[j]]) for j in range(6));o=np.lexsort((np.arange(len(Q[0])),Q[0]));return tuple(z[o] for z in Q)
def score(D,Q,bench):
 t=D[0];E,X,R,Dr,P,H=Q;s=stats(P);o=np.argsort(X,kind='stable');pp=P[o];bal=np.cumsum(pp);prior=np.r_[0.,bal[:-1]];peak=np.maximum.accumulate(prior);s['balance_dd']=float(np.max(peak-bal)) if len(pp) else 0.;daily={};weekly={}
 for x,v in zip(X,P):
  z=dt.datetime.fromtimestamp(int(t[min(int(x),len(t)-1)])/1000,dt.timezone.utc);ds=z.strftime('%Y-%m-%d');ws=f'{z.isocalendar().year}-W{z.isocalendar().week:02d}';daily[ds]=daily.get(ds,0.)+float(v);weekly[ws]=weekly.get(ws,0.)+float(v)
 s.update(daily=daily,weekly=weekly,positive_days=sum(daily.get(k,0)>0 for k in bench['daily']),beat_days=sum(daily.get(k,0)>=v['net'] for k,v in bench['daily'].items()),positive_weeks=sum(weekly.get(k,0)>0 for k in bench['weekly']),beat_weeks=sum(weekly.get(k,0)>=v['net'] for k,v in bench['weekly'].items()))
 return s

def route_wd(B,t,state=None,lowq=703):
 E,X,R,D,P,H=q(B,'WD');state=state or {'pending':[],'hist':[],'gate':True,'seq':0};pending=state['pending'];hist=state['hist'];on=state['gate'];seq=state['seq'];keep=[];u,starts,counts=np.unique(E,return_index=True,return_counts=True)
 for s,c in zip(starts,counts):
  ix=np.arange(s,s+c,dtype=np.int64);entry=int(t[E[s]]);exit_=int(np.max(t[X[ix]]));mean=float(np.mean(P[ix]))
  while pending and pending[0][0]<=entry:
   _,_,m=heapq.heappop(pending);hist.append(m)
  if len(hist)>=8:
   f=np.asarray(hist[-8:]);fm=float(f.mean());fp=pf(f);slow=np.asarray(hist[-16:]) if len(hist)>=16 else np.asarray(hist);sm=float(slow.mean())
   if on and (fm<.5 or (len(slow)>=16 and sm<0.)):on=False
   elif (not on) and fm>=1.0 and fp>=1.0 and (len(slow)<16 or sm>=0.):on=True
  else:fm=999.
  if on:
   quota=len(ix) if (len(hist)<8 or fm>=2.) else min(lowq,len(ix));keep.extend(ix[:quota].tolist())
  heapq.heappush(pending,(exit_,seq,mean));seq+=1
 kk=np.asarray(keep,np.int64);return tuple(z[kk] for z in (E,X,R,D,P,H)),{'pending':pending,'hist':hist[-128:],'gate':on,'seq':seq}

class MicroGov:
 def __init__(self,p):
  self.p=p;self.pending=[];self.pending_final=[];self.seq=0;self.day_micro=defaultdict(list);self.prior_micro=defaultdict(lambda:deque(maxlen=256));self.day_final=defaultdict(list);self.prior_final=defaultdict(lambda:deque(maxlen=128));self.last_day={}
 def rollover(self,src,day):
  old=self.last_day.get(src)
  if old is None:self.last_day[src]=day;return
  if old!=day:
   self.prior_micro[src].extend(self.day_micro.pop((src,old),[]));self.prior_final[src].extend(self.day_final.pop((src,old),[]));self.last_day[src]=day
 def flush(self,now):
  while self.pending and self.pending[0][0]<=now:
   _,_,s,d,v=heapq.heappop(self.pending);self.day_micro[(s,d)].append(float(v))
  while self.pending_final and self.pending_final[0][0]<=now:
   _,_,s,d,v=heapq.heappop(self.pending_final);self.day_final[(s,d)].append(float(v))
 def cap(self,src,day):
  self.rollover(src,day);p=self.p;cur=np.asarray(self.day_micro[(src,day)],float);prior=np.asarray(self.prior_micro[src],float);cf=np.asarray(self.day_final[(src,day)],float)
  cap=p['freshcap'] if len(prior)<p['minprior'] else p['priorcap']
  if len(cur)>=p['fw']:
   f=cur[-p['fw']:];fm=float(f.mean());fp=pf(f)
   if len(prior)<p['minprior']:
    if fm<=p['new_off'] or fp<p['new_pf_off']:cap=p['offcap']
    elif fm>=p['new_on'] and fp>=p['new_pf_on']:cap=p['maxcap']
    else:cap=p['midcap']
   else:
    b=prior[-min(len(prior),p['lw']):];bm=float(b.mean());delta=fm-bm
    if fm<p['abs_off'] and delta<=-p['drift_off']:cap=p['offcap']
    elif delta<=-p['drift_warn']:cap=min(cap,p['warncap'])
    else:cap=p['maxcap']
  if len(cf)>=p['ffw']:
   f=cf[-p['ffw']:]
   if f.mean()<p['final_off'] or pf(f)<p['final_pf_off']:cap=min(cap,p['final_cap'])
  return max(0,int(cap))
 def push(self,et,xt,src,day,micro,pnl):
  heapq.heappush(self.pending,(int(et+30000),self.seq,int(src),int(day),float(micro)));heapq.heappush(self.pending_final,(int(xt),self.seq,int(src),int(day),float(pnl)));self.seq+=1

def learner(mon,D,G,gov,gcap=1024):
 t,a,b=D[:3];z=load_npz(f'{BASE}/{mon}_hb_eligible_micro_133c.npz');active=[];bysrc=defaultdict(list);keep=[]
 for k in range(len(z['et'])):
  now=int(z['et'][k]);gov.flush(now);src=int(z['src'][k]);day=now//DAY;gov.rollover(src,day)
  while active and active[0][0]<=now:heapq.heappop(active)
  h=bysrc[src]
  while h and h[0][0]<=now:heapq.heappop(h)
  cap=gov.cap(src,day);gov.push(z['et'][k],z['xt'][k],src,day,z['m30'][k],z['p'][k])
  if cap<=0 or len(h)>=cap or len(active)>=gcap:continue
  keep.append(k);rec=(int(z['xt'][k]),k);heapq.heappush(h,rec);heapq.heappush(active,rec)
 kk=np.asarray(keep,np.int64);E=z['idx'][kk].astype(np.int64);X=np.minimum(np.searchsorted(t,z['xt'][kk]),len(t)-1).astype(np.int64);Dr=z['d'][kk].astype(np.int8);R=np.where(Dr>0,a[E],b[E]).astype(np.int64);P=z['p'][kk].astype(float);H=(z['xt'][kk]-z['et'][kk])/1000.;o=np.argsort(E,kind='stable');return tuple(x[o] for x in (E,X,R,Dr,P,H))
def native(mon):
 z=load_npz(f'{BASE}/{mon}_native_pf10_stream_133c.npz');return tuple(z[x] for x in ['E','X','R','D','P','H'])
def eval_config(par):
 gov=MicroGov(par);wdstate=None;out={}
 for mon,m in [('feb',2),('mar',3)]:
  D=N.load_month(m);B=load_npz(f'{BASE}/{mon}_baseline_components_133b.npz');wd,wdstate=route_wd(B,D[0],wdstate,703);G=learner(mon,D,par,gov,1024);COV=q(B,'COV');COLD=q(B,'COLD');NAT=native(mon);bench=json.load(open(f'{BASE}/r9_synth_{mon}_daily_weekly.json'))
  # test two priority orders
  Q=merge(wd,[NAT,G,COV,COLD],1024);s=score(D,Q,bench);out[mon]={'score':s,'learner':stats(G[4]),'native':stats(NAT[4]),'wd':stats(wd[4])}
 return out

CONFIGS=[
 dict(name='A',fw=8,lw=64,minprior=32,freshcap=8,priorcap=128,midcap=64,maxcap=1024,offcap=0,warncap=64,new_off=-.50,new_on=-.05,new_pf_off=.45,new_pf_on=.75,abs_off=0.,drift_off=.75,drift_warn=.35,ffw=4,final_off=-.25,final_pf_off=.8,final_cap=16),
 dict(name='B',fw=8,lw=64,minprior=32,freshcap=16,priorcap=256,midcap=128,maxcap=1024,offcap=2,warncap=64,new_off=-.60,new_on=-.10,new_pf_off=.40,new_pf_on=.70,abs_off=0.,drift_off=.75,drift_warn=.35,ffw=4,final_off=-.5,final_pf_off=.7,final_cap=32),
 dict(name='C',fw=16,lw=96,minprior=32,freshcap=16,priorcap=256,midcap=128,maxcap=1024,offcap=2,warncap=64,new_off=-.50,new_on=-.05,new_pf_off=.45,new_pf_on=.75,abs_off=0.,drift_off=.6,drift_warn=.3,ffw=8,final_off=-.25,final_pf_off=.8,final_cap=16),
 dict(name='D',fw=8,lw=128,minprior=16,freshcap=32,priorcap=512,midcap=128,maxcap=1024,offcap=4,warncap=128,new_off=-.75,new_on=-.20,new_pf_off=.35,new_pf_on=.65,abs_off=-.1,drift_off=1.0,drift_warn=.5,ffw=8,final_off=-1.,final_pf_off=.5,final_cap=64),
 dict(name='E',fw=4,lw=64,minprior=16,freshcap=8,priorcap=256,midcap=64,maxcap=1024,offcap=0,warncap=32,new_off=-.50,new_on=0.,new_pf_off=.5,new_pf_on=.8,abs_off=0.,drift_off=.5,drift_warn=.25,ffw=4,final_off=0.,final_pf_off=.9,final_cap=8),
 dict(name='F',fw=8,lw=64,minprior=16,freshcap=16,priorcap=512,midcap=128,maxcap=1024,offcap=0,warncap=64,new_off=-.45,new_on=-.1,new_pf_off=.5,new_pf_on=.75,abs_off=-.05,drift_off=.6,drift_warn=.3,ffw=4,final_off=-.25,final_pf_off=.75,final_cap=16),
]
if __name__=='__main__':
 rows=[]
 for p in CONFIGS:
  r=eval_config(p);row={'params':p,'feb':r['feb'],'mar':r['mar']};rows.append(row);print(json.dumps({'name':p['name'],'feb':{k:r['feb']['score'][k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','beat_days','positive_weeks','beat_weeks']},'mar':{k:r['mar']['score'][k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','beat_days','positive_weeks','beat_weeks']},'fl':r['feb']['learner'],'ml':r['mar']['learner']}),flush=True)
 Path(BASE+'/crossmonth_micro_ensemble_133c.json').write_text(json.dumps({'candidate':'CROSSMONTH_MICRO_ENSEMBLE_133C','rows':rows},indent=2))