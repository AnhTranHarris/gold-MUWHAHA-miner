from __future__ import annotations
import json,heapq,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/april_vertical_work')
import apr_vertical_portfolio_136g as A
O=Path('/mnt/data/april_vertical_work')
SYN=dict(net=38353.96,gross_loss=-2414.22,pf=16.886688,win=.86759242,expectancy=1.207694)
BEN=json.load(open(O/'r9_synth_apr_daily_weekly_136.json'))
z0=np.load(O/'apr_native_conviction_refine_streams_136h.npz');N=tuple(z0[f'WIN87_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
z1=np.load(O/'apr_session_grid_streams_136b.npz');HV=tuple(z1[f'HIGHVOL_PF8_{k}'] for k in ['E_MS','X_MS','R','D','P','H']);AS=tuple(z1[f'ASIA_PF8_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
CORE,_,_=A.caprec(A.dedup([('NATIVE',N),('HIGHVOL',HV),('ASIA',AS),('RECOVERY',A.REC)]),176);CS=A.score(CORE);CGP=CS['gross_profit'];CGL=CS['gross_loss'];CNET=CS['net'];CN=CS['trades'];CWIN=CS['win']*CN
z=np.load(O/'apr_renewal_owner_stream_136s0.npz');diag=json.load(open(O/'apr_all_renewal_rule_depth_136p1.json'));meta={int(r['rule_index']):r['rule'] for r in diag['rules']};parts=[]
for ri in range(7):
 E,X,R,D,P,H,L,OWN=[z[f'R{ri}_{k}'] for k in ['E_MS','X_MS','R','D','P','H','LAYER','OWNER']];C=np.asarray(OWN,np.int64)+ri*100000;parts.append((E,X,R,D,P,H,L.astype(np.int16),np.full(len(E),ri,np.int8),C))
E=np.concatenate([q[0] for q in parts]);X=np.concatenate([q[1] for q in parts]);R=np.concatenate([q[2] for q in parts]);D=np.concatenate([q[3] for q in parts]);P=np.concatenate([q[4] for q in parts]);H=np.concatenate([q[5] for q in parts]);L=np.concatenate([q[6] for q in parts]);RI=np.concatenate([q[7] for q in parts]);C=np.concatenate([q[8] for q in parts]);ord=np.lexsort((L,C,E));E,X,R,D,P,H,L,RI,C=[q[ord] for q in [E,X,R,D,P,H,L,RI,C]]
prev_p=np.full(len(E),np.nan,np.float32);prev_h=np.full(len(E),np.nan,np.float32);cum=np.zeros(len(E),np.float32);streak=np.zeros(len(E),np.int16)
for c in np.unique(C):
 idx=np.flatnonzero(C==c);idx=idx[np.argsort(L[idx],kind='stable')];ps=[]
 for i in idx:
  if ps:
   prev_p[i]=ps[-1][0];prev_h[i]=ps[-1][1];cum[i]=sum(x[0] for x in ps);st=0
   for x in reversed(ps):
    if x[0]>0:st+=1
    else:break
   streak[i]=st
  ps.append((float(P[i]),float(H[i])))
PBU=np.where(np.isnan(prev_p),-1,np.where(prev_p<=0,0,np.where(prev_p<.5,1,np.where(prev_p<1.,2,np.where(prev_p<2.,3,4))))).astype(np.int8);HBU=np.where(np.isnan(prev_h),-1,np.where(prev_h<=30,0,np.where(prev_h<=60,1,np.where(prev_h<=120,2,np.where(prev_h<=180,3,np.where(prev_h<=300,4,5)))))).astype(np.int8);SBU=np.minimum(streak,3).astype(np.int8);CBU=np.where(cum<=0,0,np.where(cum<1.,1,np.where(cum<3.,2,3))).astype(np.int8);DB=np.where(L<=3,0,np.where(L<=7,1,2)).astype(np.int8);RH=np.array([int(meta[int(r)]['hour']) for r in RI],np.int8);RB=np.array([int(meta[int(r)]['bin'])//10 for r in RI],np.int8);RG=np.array([0 if meta[int(r)]['geom']=='q050' else 1 for r in RI],np.int8)
def K(fam,i):
 if fam=='RL_PREV':return (int(RI[i]),int(L[i]),int(PBU[i]))
 if fam=='RL_PH':return (int(RI[i]),int(L[i]),int(PBU[i]),int(HBU[i]))
 if fam=='RB_PHSC':return (int(RI[i]),int(DB[i]),int(PBU[i]),int(HBU[i]),int(SBU[i]),int(CBU[i]))
 if fam=='HB_L_PH':return (int(RH[i]),int(RB[i]),int(L[i]),int(PBU[i]),int(HBU[i]))
 if fam=='GEOM_BAND_PH':return (int(RG[i]),int(DB[i]),int(PBU[i]),int(HBU[i]),int(SBU[i]))
 raise KeyError(fam)
def scalar(mask):
 q=P[mask];gp=float(q[q>0].sum());gl=float(q[q<=0].sum());wins=int((q>0).sum());n=len(q);T=CN+n;G=CGP+gp;Ls=CGL+gl;N=CNET+float(q.sum());W=CWIN+wins
 return dict(net=N,trades=T,gross_loss=Ls,pf=float(G/-Ls if Ls<0 else 999.),win=float(W/T),expectancy=float(N/T),renewal_trades=n)
def allm(s):return s['net']>=SYN['net'] and s['gross_loss']>=SYN['gross_loss'] and s['pf']>=SYN['pf'] and s['win']>=SYN['win'] and s['expectancy']>=SYN['expectancy']
def capov(rr,cap):
 hp=[];out=[];sk=0;mo=0
 for i,r in enumerate(rr):
  while hp and hp[0][0]<=r[0]:heapq.heappop(hp)
  if len(hp)>=cap:sk+=1;continue
  out.append(r);heapq.heappush(hp,(r[1],i));mo=max(mo,len(hp))
 return out,mo,sk
def run(fam):
 keys=[K(fam,i) for i in range(len(E))];groups={}
 for i,k in enumerate(keys):groups.setdefault(k,[]).append(i)
 st={}
 for k,ii in groups.items():
  a=P[np.asarray(ii,np.int64)];gp=a[a>0].sum();gl=a[a<=0].sum();st[k]=(len(a),float(a.sum()),float(gp/-gl if gl<0 else 999.),float(np.mean(a>0)))
 rawrows=[];sels={}
 for mn in [10,20,40,80,120]:
  for pf0 in [1.5,2.,3.,5.,10.,20.]:
   for w0 in [.70,.80,.85,.90,.95]:
    sel={k for k,m in st.items() if m[0]>=mn and m[1]>0 and m[2]>=pf0 and m[3]>=w0};mask=np.fromiter((k in sel for k in keys),bool,count=len(keys));s=scalar(mask);s.update(min_n=mn,min_pf=pf0,min_win=w0,cells=len(sel),all_metrics=allm(s));s['violations']=sum([s['net']<SYN['net'],s['gross_loss']<SYN['gross_loss'],s['pf']<SYN['pf'],s['win']<SYN['win'],s['expectancy']<SYN['expectancy']]);rawrows.append(s);sels[(mn,pf0,w0)]=(sel,mask)
 # replay only all-metric raw configs and best 10 near-misses
 candidates=sorted([r for r in rawrows if r['all_metrics']],key=lambda r:(-r['trades'],-r['net']))[:16]
 near=sorted(rawrows,key=lambda r:(r['violations'],abs(r['gross_loss']-SYN['gross_loss']),-r['trades']))[:12]
 seen=set();caprows=[];cache={}
 for s in candidates+near:
  kk=(s['min_n'],s['min_pf'],s['min_win']);
  if kk in seen:continue
  seen.add(kk);sel,mask=sels[kk];rr=[(int(E[i]),int(X[i]),int(R[i]),int(D[i]),float(P[i]),float(H[i]),f'RENEW_R{int(RI[i])}_L{int(L[i])}') for i in np.flatnonzero(mask)];rr.sort(key=lambda r:(r[0],r[6]))
  for cap in [176,320,448,600,703,900]:
   ov,mo,sk=capov(rr,cap);rec=sorted(CORE+ov,key=lambda r:(r[0],0 if r[6].startswith('RENEW') else 1));q=A.score(rec);q.update(family=fam,min_n=kk[0],min_pf=kk[1],min_win=kk[2],cells=len(sel),renewal_cap=cap,renewal_trades=len(ov),renewal_maxopen=mo,renewal_skips=sk,all_metrics=allm(q));q['beat_synth_days']=sum(q['daily'].get(k,0)>v for k,v in BEN['daily'].items());q['beat_synth_weeks']=sum(q['weekly'].get(k,0)>v for k,v in BEN['weekly'].items());caprows.append(q);cache[(kk,cap)]=(sel,rec)
 good=sorted([r for r in caprows if r['all_metrics'] and r['renewal_trades']>0],key=lambda r:(-r['trades'],-r['net'],abs(r['gross_loss'])));topnet=sorted(good,key=lambda r:(-r['net'],-r['trades']))
 out={'unit':f'DAA_APRIL_CAMPAIGN_TRANSITION_MAP_136T0_{fam}','status':'COMPLETE_RESEARCH_UPPER_BOUND','family':fam,'cell_count':len(st),'raw_all_metric_count':sum(r['all_metrics'] for r in rawrows),'capped_all_metric_count':len(good),'top_trade':good[:30],'top_net':topnet[:30],'raw_near':near,'caveat':'Cell features are causal at entry; selection is April outcome-discovered and must be walk-forward/cross-month qualified.'};(O/f'apr_campaign_transition_map_136t0_{fam.lower()}.json').write_text(json.dumps(out,indent=2));print(fam,'cells',len(st),'rawgood',out['raw_all_metric_count'],'capgood',len(good));
 for r in good[:10]:print({k:r[k] for k in ['min_n','min_pf','min_win','cells','renewal_cap','renewal_trades','net','trades','gross_loss','pf','win','expectancy','beat_synth_days','beat_synth_weeks','renewal_maxopen']})
if __name__=='__main__':run(sys.argv[1])