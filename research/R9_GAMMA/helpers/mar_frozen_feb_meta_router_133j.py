import sys,json,heapq,numpy as np
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import mar_replay_jan_milestone_133a as M
import jan_session_portfolio_131d as J
C0=np.load('/mnt/data/gamma02_jan_repro/mar_hb_online_cache_133b.npz');C={k:C0[k] for k in C0.files};C0.close()
B0=np.load('/mnt/data/gamma02_jan_repro/mar_baseline_components_133b.npz');B={k:B0[k] for k in B0.files};B0.close()
def q(pre):return tuple(B[pre+'_'+x] for x in ['E','X','R','D','P','H'])
WD=q('WD');COV=q('COV');COLD=q('COLD')
def pf(a):
 a=np.asarray(a,float);gl=a[a<0].sum();gp=a[a>0].sum();return float(gp/-gl if gl<0 else 999.)
def route_wd(lowq=703):
 E,X,R,D,P,H=WD;u,starts,counts=np.unique(E,return_index=True,return_counts=True);pending=[];hist=[];state=True;keep=[];seq=0
 for s,c in zip(starts,counts):
  ix=np.arange(s,s+c,dtype=np.int64);entry=int(E[s]);exit_=int(np.max(X[ix]));mean=float(np.mean(P[ix]))
  while pending and pending[0][0]<=entry:
   _,_,m=heapq.heappop(pending);hist.append(m)
  if len(hist)>=8:
   fast=np.asarray(hist[-8:]);fm=float(fast.mean());fp=pf(fast);slow=np.asarray(hist[-16:]) if len(hist)>=16 else np.asarray(hist);sm=float(slow.mean())
   if state and (fm<.5 or (len(slow)>=16 and sm<0.)):state=False
   elif (not state) and fm>=1.0 and fp>=1.0 and (len(slow)<16 or sm>=0.):state=True
  else:fm=999.
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
def learner(cap=1024):
 base=(C['cell8_n']>=4)&(C['cell8_mean']>=2.)&(C['cell8_pf']>=1.5)&(C['src16_n']>=8)&(C['src16_mean']>=2.)&(C['src16_pf']>=1.0);score=.65*C['cell8_mean']+.35*C['src16_mean']
 m=base&(score<=16.)&~((score>=4.)&(score<=6.));idx=np.flatnonzero(m);et=C['et'][idx];o=np.lexsort((-score[idx],et));idx=idx[o];et=et[o];idx=idx[np.r_[True,et[1:]!=et[:-1]]];kk=capidx(idx,cap)
 E=C['idx'][kk].astype(np.int64);X=np.searchsorted(M.t,C['xt'][kk]).astype(np.int64);D=C['d'][kk].astype(np.int8);R=np.where(D>0,M.a[E],M.b[E]).astype(np.int64);P=C['p'][kk].astype(float);H=(C['xt'][kk]-C['et'][kk])/1000.;o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,R,D,P,H))
def stats(Q):
 p=Q[4];gp=float(p[p>0].sum());gl=float(p[p<0].sum());return dict(net=float(p.sum()),trades=len(p),gross_loss=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,expectancy=float(np.mean(p)) if len(p) else 0.)
rows=[]
for lcap,scap in [(1024,1024),(896,896),(703,703),(512,512)]:
 wd=route_wd(703);G=learner(lcap);Q,_=J.merge_preserve_watchdog(wd,[G,COV,COLD],scap);s,_=J.score(M.t,*Q,f'MAR_OOS_FEB_LEARNER_L{lcap}_S{scap}',dict())
 rows.append(dict(lcap=lcap,scap=scap,wd=stats(wd),learner=stats(G),combined={k:s[k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks']},weekly={k:v['net'] for k,v in s['weekly'].items()},daily={k:v['net'] for k,v in s['daily'].items()}))
json.dump({'candidate':'MAR_FROZEN_FEB_META_ROUTER_133J','oos':True,'feb_rules_frozen':True,'rows':rows},open('/mnt/data/gamma02_jan_repro/mar_frozen_feb_meta_router_133j.json','w'),indent=2)
for r in rows:print(json.dumps({**{k:r[k] for k in ['lcap','scap']},**r['combined'],'wd_net':r['wd']['net'],'wd_gl':r['wd']['gross_loss'],'wd_pf':r['wd']['pf'],'learner_net':r['learner']['net'],'learner_gl':r['learner']['gross_loss'],'learner_pf':r['learner']['pf']}))