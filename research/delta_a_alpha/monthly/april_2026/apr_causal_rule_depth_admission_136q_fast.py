from __future__ import annotations
import json,sys,time,heapq
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/april_vertical_work')
import apr_vertical_portfolio_136g as A
O=Path('/mnt/data/april_vertical_work')
SYN=dict(net=38353.96,trades=31758,gross_loss=-2414.22,pf=16.886688,win=.86759242,expectancy=1.207694)
# protected core
z0=np.load(O/'apr_native_conviction_refine_streams_136h.npz');N=tuple(z0[f'WIN87_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
z1=np.load(O/'apr_session_grid_streams_136b.npz');HV=tuple(z1[f'HIGHVOL_PF8_{k}'] for k in ['E_MS','X_MS','R','D','P','H']);AS=tuple(z1[f'ASIA_PF8_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
CORE,_,_=A.caprec(A.dedup([('NATIVE',N),('HIGHVOL',HV),('ASIA',AS),('RECOVERY',A.REC)]),176); CS=A.score(CORE)
CGP=CS['gross_profit']; CGL=CS['gross_loss']; CNET=CS['net']; CN=CS['trades']; CWIN=CS['win']*CN
z=np.load(O/'apr_all_renewal_rule_depth_136p1.npz')
# flatten
parts=[]
for ri in range(7):
 E,X,R,D,P,H,L=[z[f'R{ri}_{k}'] for k in ['E_MS','X_MS','R','D','P','H','LAYER']]
 parts.append((E,X,R,D,P,H,np.full(len(E),ri,np.int8),L.astype(np.int16)))
E=np.concatenate([q[0] for q in parts]);X=np.concatenate([q[1] for q in parts]);R=np.concatenate([q[2] for q in parts]);D=np.concatenate([q[3] for q in parts]);P=np.concatenate([q[4] for q in parts]);H=np.concatenate([q[5] for q in parts]);RI=np.concatenate([q[6] for q in parts]);L=np.concatenate([q[7] for q in parts])
ord=np.lexsort((L,RI,E));E,X,R,D,P,H,RI,L=[q[ord] for q in [E,X,R,D,P,H,RI,L]]
# keys
keys=sorted(set(zip(RI.tolist(),L.tolist())))
idx_by={k:np.flatnonzero((RI==k[0])&(L==k[1])) for k in keys}
PFTH=np.array([1.25,1.5,2.,2.5,3.,5.,10.]); WTH=np.array([.60,.70,.75,.80,.85,.90,.95]); MINN=[2,4,8,12]

def features(lookback):
 ncl=np.zeros(len(E),np.int16);win=np.zeros(len(E),np.float32);pf=np.zeros(len(E),np.float32);net=np.zeros(len(E),np.float32)
 for k,idx in idx_by.items():
  # history for same key sorted by exit; cumulative arrays
  xo=X[idx]; po=P[idx]; so=np.argsort(xo,kind='stable'); xs=xo[so]; ps=po[so]
  csum=np.r_[0.,np.cumsum(ps)]; cwin=np.r_[0,np.cumsum(ps>0)]; cgp=np.r_[0.,np.cumsum(np.where(ps>0,ps,0.))]; cgl=np.r_[0.,np.cumsum(np.where(ps<=0,ps,0.))]
  n=np.searchsorted(xs,E[idx],side='left') # strict exit < entry
  a=np.maximum(0,n-lookback); nn=n-a
  sm=csum[n]-csum[a]; ww=cwin[n]-cwin[a]; gp=cgp[n]-cgp[a]; gl=cgl[n]-cgl[a]
  ncl[idx]=nn; net[idx]=sm; win[idx]=np.divide(ww,nn,out=np.zeros_like(sm),where=nn>0); pf[idx]=np.where(gl<0,gp/(-gl),np.where(gp>0,999.,0.))
 return ncl,win,pf,net

def combo_score(mask):
 q=P[mask]; n=len(q); gp=float(q[q>0].sum());gl=float(q[q<=0].sum());net=float(q.sum());wins=int((q>0).sum())
 t=CN+n; G=CGP+gp; Ls=CGL+gl; N=CNET+net; W=CWIN+wins
 return dict(net=N,trades=t,gross_loss=Ls,pf=float(G/-Ls if Ls<0 else 999.),win=float(W/t),expectancy=float(N/t),renewal_raw=n)

def allm(s):return s['net']>=SYN['net'] and s['gross_loss']>=SYN['gross_loss'] and s['pf']>=SYN['pf'] and s['win']>=SYN['win'] and s['expectancy']>=SYN['expectancy']

def rec_from_mask(mask):
 ii=np.flatnonzero(mask); out=[]
 for i in ii:out.append((int(E[i]),int(X[i]),int(R[i]),int(D[i]),float(P[i]),float(H[i]),f'RENEW_R{int(RI[i])}_L{int(L[i])}'))
 out.sort(key=lambda r:(r[0],r[6]));return out

def capov(rec,cap):
 hp=[];out=[];sk=0;mo=0
 for i,r in enumerate(rec):
  while hp and hp[0][0]<=r[0]:heapq.heappop(hp)
  if len(hp)>=cap:sk+=1;continue
  out.append(r);heapq.heappush(hp,(r[1],i));mo=max(mo,len(hp))
 return out,mo,sk

def run(lb):
 t0=time.time(); ncl,win,pf,net=features(lb); cand=[]; masks={}
 for mn in MINN:
  if mn>lb:continue
  for p0 in PFTH:
   for w0 in WTH:
    mask=(ncl>=mn)&(pf>=p0)&(win>=w0)&(net>0)
    s=combo_score(mask);s.update(lookback=lb,min_n=mn,min_pf=float(p0),min_win=float(w0),all_metrics=allm(s));cand.append(s)
    if s['all_metrics']:masks[(mn,float(p0),float(w0))]=mask
 good=[s for s in cand if s['all_metrics']];good.sort(key=lambda s:(-s['trades'],-s['net'],abs(s['gross_loss'])))
 # cap only top 18 velocity + 12 net unique configs
 picks=[]
 for s in good[:18]+sorted(good,key=lambda s:(-s['net'],-s['trades']))[:12]:
  k=(s['min_n'],s['min_pf'],s['min_win'])
  if k not in picks:picks.append(k)
 caprows=[]; cache={}
 for k in picks:
  raw=rec_from_mask(masks[k])
  for cap in [448,600,703,800,900]:
   ov,mo,sk=capov(raw,cap); rec=sorted(CORE+ov,key=lambda r:(r[0],0 if r[6].startswith('RENEW') else 1)); s=A.score(rec);s.update(lookback=lb,min_n=k[0],min_pf=k[1],min_win=k[2],renewal_cap=cap,renewal_trades=len(ov),renewal_maxopen=mo,renewal_skips=sk,all_metrics=allm(s));caprows.append(s);cache[(k,cap)]=rec
 capgood=[s for s in caprows if s['all_metrics']];capgood.sort(key=lambda s:(-s['trades'],-s['net'],abs(s['gross_loss'])))
 topnet=sorted(capgood,key=lambda s:(-s['net'],-s['trades']))
 exact=[]
 for s in capgood[:4]+topnet[:4]:
  k=(s['min_n'],s['min_pf'],s['min_win']);ck=(k,s['renewal_cap'])
  if any(x['lookback']==lb and x['min_n']==k[0] and x['min_pf']==k[1] and x['min_win']==k[2] and x['renewal_cap']==s['renewal_cap'] for x in exact):continue
  q=dict(s);q['exact_equity']=A.exact(cache[ck]);exact.append(q)
 out=dict(unit=f'DAA_APRIL_CAUSAL_RULE_DEPTH_ADMISSION_136Q_LB{lb}',status='COMPLETE_ATOMIC_BLOCK',lookback=lb,core={k:CS[k] for k in ['net','trades','gross_loss','pf','win','expectancy']},screened=len(cand),screen_all_metric=len(good),capped_all_metric=len(capgood),top_trade=capgood[:30],top_net=topnet[:30],exact_shortlist=exact,runtime_s=time.time()-t0,causality='Only exact rule+depth shadow outcomes with exit_ms < current child entry_ms are used. No current/future outcome, month or date.')
 (O/f'apr_causal_rule_depth_admission_136q_lb{lb}.json').write_text(json.dumps(out,indent=2))
 print('LB',lb,'screen',len(cand),'screen_good',len(good),'cap_good',len(capgood),'runtime',out['runtime_s'])
 for s in capgood[:10]:print({k:s[k] for k in ['min_n','min_pf','min_win','renewal_cap','renewal_trades','net','trades','gross_loss','pf','win','expectancy','renewal_maxopen','renewal_skips']})
if __name__=='__main__':run(int(sys.argv[1]))