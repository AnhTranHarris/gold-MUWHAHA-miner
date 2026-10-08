import sys,json,heapq,itertools
import numpy as np
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import feb_replay_jan_milestone_132a as F
import jan_session_portfolio_131d as J
C0=np.load('/mnt/data/gamma02_jan_repro/feb_hb_online_cache_133b.npz');C={k:C0[k] for k in C0.files};C0.close()
B0=np.load('/mnt/data/gamma02_jan_repro/feb_baseline_components_133b.npz');B={k:B0[k] for k in B0.files};B0.close();BEN=J.SYN

def q(pre):return tuple(B[pre+'_'+x] for x in ['E','X','R','D','P','H'])
WD=q('WD');COV=q('COV');COLD=q('COLD');RULES=[q(x) for x in B['rule_names'].tolist()]

def st(p):
 p=np.asarray(p,float);gp=float(p[p>0].sum());gl=float(p[p<0].sum());bal=peak=dd=0.
 for v in p:bal+=float(v);peak=max(peak,bal);dd=max(dd,peak-bal)
 return dict(net=float(p.sum()),trades=int(len(p)),gross_loss=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,expectancy=float(np.mean(p)) if len(p) else 0.,balance_dd=float(dd))
def capidx(idx,cap):
 o=np.argsort(C['et'][idx],kind='stable');idx=idx[o];h=[];keep=[]
 for k in idx:
  now=int(C['et'][k]);
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:continue
  keep.append(k);heapq.heappush(h,(int(C['xt'][k]),int(k)))
 return np.asarray(keep,np.int64)
def makeq(idx):
 E=C['idx'][idx].astype(np.int64);X=np.searchsorted(F.t,C['xt'][idx]).astype(np.int64);D=C['d'][idx].astype(np.int8);R=np.where(D>0,F.a[E],F.b[E]).astype(np.int64);P=C['p'][idx].astype(float);H=(C['xt'][idx]-C['et'][idx])/1000.;o=np.argsort(E,kind='stable');return tuple(z[o] for z in (E,X,R,D,P,H))
base=(C['cell8_n']>=4)&(C['cell8_mean']>=2.)&(C['cell8_pf']>=1.5)&(C['src16_n']>=8)&(C['src16_mean']>=2.)&(C['src16_pf']>=1.0)
score=.65*C['cell8_mean']+.35*C['src16_mean']
configs=[
 ('BAND16_EXCL4_6',16.,(4.,6.),'NONE'),
 ('BAND16_EXCL4_6_LAST',16.,(4.,6.),'CELL_LAST_POS'),
 ('BAND16_EXCL4_65',16.,(4.,6.5),'NONE'),
 ('BAND14_EXCL4_6',14.,(4.,6.),'NONE'),
 ('BAND12_EXCL4_6',12.,(4.,6.),'NONE'),
 ('BAND16_NOEXCL',16.,None,'NONE')]
rows=[]
for name,hi,mid,last in configs:
 m=base&(score<=hi)
 if mid:m &= ~((score>=mid[0])&(score<=mid[1]))
 if last=='CELL_LAST_POS':m &= C['cell8_last']>0
 idx=np.flatnonzero(m);et=C['et'][idx];o=np.lexsort((-score[idx],et));idx=idx[o];et=et[o];idx=idx[np.r_[True,et[1:]!=et[:-1]]]
 for lcap in [703,896,1024]:
  kk=capidx(idx,lcap);G=makeq(kk);gs=st(G[4])
  for scap in [703,896,1024]:
   Q,meta=J.merge_preserve_watchdog(WD,[G,COV,COLD,*RULES],scap)
   s,_=J.score(F.t,*Q,name+f'_LC{lcap}_SC{scap}',dict(rule=name,learner_cap=lcap,supp_cap=scap))
   rows.append(dict(rule=name,learner_cap=lcap,supp_cap=scap,learner=gs,combined={k:s[k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks']},weekly={k:v['net'] for k,v in s['weekly'].items()},daily={k:v['net'] for k,v in s['daily'].items()}))
rows.sort(key=lambda r:(r['combined']['positive_weeks'],r['combined']['beat_weeks'],r['combined']['positive_days'],r['combined']['beat_days'],r['combined']['net'],r['combined']['pf']),reverse=True)
json.dump({'candidate':'CELL2_SCORE_BAND_EXACT_133H','causal':True,'rows':rows},open('/mnt/data/gamma02_jan_repro/cell2_band_exact_133h.json','w'),indent=2)
for r in rows[:60]:print(json.dumps({**{k:r[k] for k in ['rule','learner_cap','supp_cap']},**r['combined'],'learner_net':r['learner']['net'],'learner_gl':r['learner']['gross_loss'],'learner_pf':r['learner']['pf']}))