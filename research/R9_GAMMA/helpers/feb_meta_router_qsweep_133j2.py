import sys,json,heapq,numpy as np
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import feb_replay_jan_milestone_132a as F
import jan_session_portfolio_131d as J
C0=np.load('/mnt/data/gamma02_jan_repro/feb_hb_online_cache_133b.npz');C={k:C0[k] for k in C0.files};C0.close()
B0=np.load('/mnt/data/gamma02_jan_repro/feb_baseline_components_133b.npz');B={k:B0[k] for k in B0.files};B0.close()
BEN=J.SYN

def q(pre):return tuple(B[pre+'_'+x] for x in ['E','X','R','D','P','H'])
WD=q('WD');COV=q('COV');COLD=q('COLD');RULES=[q(x) for x in B['rule_names'].tolist()]

def pf(a):
 a=np.asarray(a,float);gl=a[a<0].sum();gp=a[a>0].sum();return float(gp/-gl if gl<0 else 999.)
def route_wd(lowq=128):
 E,X,R,D,P,H=WD;u,starts,counts=np.unique(E,return_index=True,return_counts=True);pending=[];hist=[];state=True;keep=[];seq=0
 for s,c in zip(starts,counts):
  ix=np.arange(s,s+c,dtype=np.int64);entry=int(E[s]);exit_=int(np.max(X[ix]));mean=float(np.mean(P[ix]))
  while pending and pending[0][0]<=entry:
   _,_,m=heapq.heappop(pending);hist.append(m)
  if len(hist)>=8:
   fast=np.asarray(hist[-8:]);fm=float(fast.mean());fp=pf(fast);slow=np.asarray(hist[-16:]) if len(hist)>=16 else np.asarray(hist);sm=float(slow.mean())
   if state and (fm<0.5 or (len(slow)>=16 and sm<0.)): state=False
   elif (not state) and fm>=1.0 and fp>=1.0 and (len(slow)<16 or sm>=0.):state=True
  else: fm=999.
  if state:
   quota=len(ix) if (len(hist)<8 or fm>=2.) else min(lowq,len(ix));keep.extend(ix[:quota].tolist())
  heapq.heappush(pending,(exit_,seq,mean));seq+=1
 kk=np.asarray(keep,np.int64);return tuple(z[kk] for z in WD)

def capidx(idx,cap):
 o=np.argsort(C['et'][idx],kind='stable');idx=idx[o];h=[];keep=[]
 for k in idx:
  now=int(C['et'][k])
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:continue
  keep.append(k);heapq.heappush(h,(int(C['xt'][k]),int(k)))
 return np.asarray(keep,np.int64)
def learner(rule,cap=1024):
 base=(C['cell8_n']>=4)&(C['cell8_mean']>=2.)&(C['cell8_pf']>=1.5)&(C['src16_n']>=8)&(C['src16_mean']>=2.)&(C['src16_pf']>=1.0);score=.65*C['cell8_mean']+.35*C['src16_mean']
 if rule=='BAND16_EXCL4_6':m=base&(score<=16.)&~((score>=4.)&(score<=6.))
 elif rule=='BAND14_EXCL4_6':m=base&(score<=14.)&~((score>=4.)&(score<=6.))
 else:m=base&(score<=16.)
 idx=np.flatnonzero(m);et=C['et'][idx];o=np.lexsort((-score[idx],et));idx=idx[o];et=et[o];idx=idx[np.r_[True,et[1:]!=et[:-1]]];kk=capidx(idx,cap)
 E=C['idx'][kk].astype(np.int64);X=np.searchsorted(F.t,C['xt'][kk]).astype(np.int64);D=C['d'][kk].astype(np.int8);R=np.where(D>0,F.a[E],F.b[E]).astype(np.int64);P=C['p'][kk].astype(float);H=(C['xt'][kk]-C['et'][kk])/1000.;o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,R,D,P,H))

def ss(q):
 p=q[4];gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=len(p),gross_loss=gl,pf=float(gp/-gl if gl<0 else 999.))
rows=[]
for qv in [128,256,384,512,703]:
 wdname=f'ROUTED_WD_Q{qv}';wd=route_wd(qv)
 for lr in ['BAND16_EXCL4_6','BAND14_EXCL4_6']:
  G=learner(lr,1024)
  for partsname,parts in [('ALL',[G,COV,COLD,*RULES]),('CORE',[G,COV,COLD])]:
   Q,meta=J.merge_preserve_watchdog(wd,parts,1024)
   s,_=J.score(F.t,*Q,f'{wdname}_{lr}_{partsname}',dict(wd=wdname,learner=lr,parts=partsname))
   rows.append(dict(wd=wdname,learner=lr,parts=partsname,wd_stats=ss(wd),learner_stats=ss(G),combined={k:s[k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks']},weekly={k:v['net'] for k,v in s['weekly'].items()},daily={k:v['net'] for k,v in s['daily'].items()}))
rows.sort(key=lambda r:(r['combined']['positive_weeks'],r['combined']['beat_weeks'],r['combined']['positive_days'],r['combined']['beat_days'],r['combined']['net'],r['combined']['pf']),reverse=True)
json.dump({'candidate':'FEB_META_ROUTER_QSWEEP_133J2','causal':True,'rows':rows},open('/mnt/data/gamma02_jan_repro/feb_meta_router_qsweep_133j2.json','w'),indent=2)
for r in rows:print(json.dumps({**{k:r[k] for k in ['wd','learner','parts']},**r['combined'],'wd_net':r['wd_stats']['net'],'wd_gl':r['wd_stats']['gross_loss'],'wd_pf':r['wd_stats']['pf'],'learner_net':r['learner_stats']['net'],'learner_gl':r['learner_stats']['gross_loss'],'learner_pf':r['learner_stats']['pf']}))