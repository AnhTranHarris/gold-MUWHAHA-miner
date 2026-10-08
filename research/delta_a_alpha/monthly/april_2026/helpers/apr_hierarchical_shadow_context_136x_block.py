from __future__ import annotations
import json,heapq,sys,time,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/april_vertical_work')
import apr_vertical_portfolio_136g as A
import apr_campaign_transition_map_136t0_fast as M
O=Path('/mnt/data/april_vertical_work')
ap=argparse.ArgumentParser();ap.add_argument('--family',required=True);ap.add_argument('--lookback',type=int,required=True);args=ap.parse_args()
SYN=dict(net=38353.96,trades=31758,gross_loss=-2414.22,pf=16.886688,win=.86759242,expectancy=1.207694)
BEN=M.BEN;CORE=M.CORE;CS=A.score(CORE);CGP=CS['gross_profit'];CGL=CS['gross_loss'];CNET=CS['net'];CN=CS['trades'];CWIN=CS['win']*CN
E,X,R,D,P,H,L,RI=M.E,M.X,M.R,M.D,M.P,M.H,M.L,M.RI
# descriptor metadata from M: RH hour, RB 10m-bin index, RG geom, DB depth band
if args.family=='RULE': keys=[(int(RI[i]),) for i in range(len(E))]
elif args.family=='RULE_DB': keys=[(int(RI[i]),int(M.DB[i])) for i in range(len(E))]
elif args.family=='HOURBIN_DB': keys=[(int(M.RH[i]),int(M.RB[i]),int(M.DB[i])) for i in range(len(E))]
elif args.family=='GEOM_DB': keys=[(int(M.RG[i]),int(M.DB[i])) for i in range(len(E))]
else: raise SystemExit('bad family')
groups={}
for i,k in enumerate(keys):groups.setdefault(k,[]).append(i)

def features(lb):
 ncl=np.zeros(len(E),np.int16);win=np.zeros(len(E),np.float32);pf=np.zeros(len(E),np.float32);net=np.zeros(len(E),np.float32);exp=np.zeros(len(E),np.float32)
 for idx0 in groups.values():
  idx=np.asarray(idx0,np.int64);xo=X[idx];pv=P[idx];so=np.argsort(xo,kind='stable');xs=xo[so];ps=pv[so]
  csum=np.r_[0.,np.cumsum(ps)];cwin=np.r_[0,np.cumsum(ps>0)];cgp=np.r_[0.,np.cumsum(np.where(ps>0,ps,0.))];cgl=np.r_[0.,np.cumsum(np.where(ps<=0,ps,0.))]
  n=np.searchsorted(xs,E[idx],side='left');a=np.maximum(0,n-lb);nn=n-a;sm=csum[n]-csum[a];ww=cwin[n]-cwin[a];gp=cgp[n]-cgp[a];gl=cgl[n]-cgl[a]
  ncl[idx]=nn;net[idx]=sm;win[idx]=np.divide(ww,nn,out=np.zeros_like(sm),where=nn>0);pf[idx]=np.divide(gp,-gl,out=np.full_like(sm,999.),where=gl<0);pf[idx][(gl>=0)&(gp<=0)]=0.;exp[idx]=np.divide(sm,nn,out=np.zeros_like(sm),where=nn>0)
 return ncl,win,pf,net,exp

def scalar(mask):
 q=P[mask];gp=float(q[q>0].sum());gl=float(q[q<=0].sum());wins=int((q>0).sum());n=len(q);T=CN+n;G=CGP+gp;Ls=CGL+gl;N=CNET+float(q.sum());W=CWIN+wins
 return dict(net=N,trades=T,gross_loss=Ls,pf=float(G/-Ls if Ls<0 else 999.),win=float(W/T),expectancy=float(N/T),renewal_raw=n)
def allm(s):return s['net']>=SYN['net'] and s['gross_loss']>=SYN['gross_loss'] and s['pf']>=SYN['pf'] and s['win']>=SYN['win'] and s['expectancy']>=SYN['expectancy']
def raw(mask):
 out=[]
 for i in np.flatnonzero(mask):out.append((int(E[i]),int(X[i]),int(R[i]),int(D[i]),float(P[i]),float(H[i]),f'RENEW_R{int(RI[i])}_L{int(L[i])}'))
 out.sort(key=lambda r:(r[0],r[6]));return out
def capov(rr,cap):
 hp=[];out=[];sk=0;mo=0
 for i,r in enumerate(rr):
  while hp and hp[0][0]<=r[0]:heapq.heappop(hp)
  if len(hp)>=cap:sk+=1;continue
  out.append(r);heapq.heappush(hp,(r[1],i));mo=max(mo,len(hp))
 return out,mo,sk

t0=time.time();n,w,pf,net,ex=features(args.lookback);screen=[];masks={}
for mn in [4,8,16]:
 if mn>args.lookback:continue
 for p0 in [2.,5.,10.]:
  for w0 in [.80,.90,.95]:
   for e0 in [0.,.10]:
    mask=(n>=mn)&(pf>=p0)&(w>=w0)&(net>0)&(ex>=e0);s=scalar(mask);s.update(family=args.family,lookback=args.lookback,min_n=mn,min_pf=p0,min_win=w0,min_exp=e0,all_metrics=allm(s));s['violations']=sum([s['net']<SYN['net'],s['gross_loss']<SYN['gross_loss'],s['pf']<SYN['pf'],s['win']<SYN['win'],s['expectancy']<SYN['expectancy']]);screen.append(s);masks[(mn,p0,w0,e0)]=mask
# cap best raw by metric gates / nearest
rawgood=sorted([s for s in screen if s['all_metrics'] and s['renewal_raw']>0],key=lambda s:(-s['trades'],-s['net']))
near=sorted([s for s in screen if s['renewal_raw']>0],key=lambda s:(s['violations'],abs(s['gross_loss']-SYN['gross_loss']),-s['trades']))[:8]
picks=[]
for s in rawgood[:10]+near:
 k=(s['min_n'],s['min_pf'],s['min_win'],s['min_exp'])
 if k not in picks:picks.append(k)
rows=[]
for k in picks:
 rr=raw(masks[k])
 for cap in [256,448,512,600,703,819]:
  ov,mo,sk=capov(rr,cap);rec=sorted(CORE+ov,key=lambda r:(r[0],0 if r[6].startswith('RENEW') else 1));s=A.score(rec);s.update(family=args.family,lookback=args.lookback,min_n=k[0],min_pf=k[1],min_win=k[2],min_exp=k[3],cap=cap,renewal_trades=len(ov),renewal_maxopen=mo,renewal_skips=sk,all_metrics=allm(s),all_plus_trades=allm(s) and s['trades']>=SYN['trades'],beat_synth_days=sum(s['daily'].get(d,0)>v for d,v in BEN['daily'].items()),beat_synth_weeks=sum(s['weekly'].get(w,0)>v for w,v in BEN['weekly'].items()))
  rows.append(s)
good=[s for s in rows if s['all_metrics']];plus=[s for s in good if s['all_plus_trades']]
out={'unit':'DAA_APRIL_HIERARCHICAL_CONTEXTUAL_TRANSITION_GOVERNOR_136X_BLOCK','status':'COMPLETE_ATOMIC_BLOCK','family':args.family,'lookback':args.lookback,'group_count':len(groups),'screened':len(screen),'raw_all_metric_count':len(rawgood),'capped_all_metric_count':len(good),'all_plus_trade_count':len(plus),'top_trade':sorted(good,key=lambda s:(-s['trades'],-s['net']))[:12],'top_net':sorted(good,key=lambda s:(-s['net'],-s['trades']))[:12],'runtime_s':time.time()-t0,'causality':'Rolling shadow metrics use only candidate exits strictly before current entry; no month/date/current/future outcome. Family is causal structural context, not calendar identity.'}
fn=O/f'apr_hierarchical_shadow_context_136x_{args.family.lower()}_lb{args.lookback}.json';fn.write_text(json.dumps(out,indent=2))
print(json.dumps({'file':fn.name,'groups':len(groups),'rawgood':len(rawgood),'capgood':len(good),'plus':len(plus),'runtime':out['runtime_s']}))
for s in out['top_trade'][:5]:print({k:s[k] for k in ['family','lookback','min_n','min_pf','min_win','min_exp','cap','renewal_trades','net','trades','gross_loss','pf','win','expectancy','beat_synth_days','beat_synth_weeks','renewal_maxopen','renewal_skips','all_plus_trades']})