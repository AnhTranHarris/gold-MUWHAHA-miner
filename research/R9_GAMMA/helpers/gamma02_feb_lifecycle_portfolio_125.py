import json, heapq, numpy as np
from numba import njit
import sys
sys.path.insert(0,'/mnt/data')
import stmr_janjul as j, stmr_base as c
from gamma02_feb_native_markout_124 import build_events
from gamma02_feb_lifecycle_quality_125 import precompute_hits, TP_LEVELS, SL_LEVELS, HOLDS
INF=np.int64(9223372036854775807)
@njit(cache=True)
def choose_outcomes(tp_t,tp_p,sl_t,sl_p,h_t,h_p,tp,sl,hold_ms):
 n=h_t.shape[0];hi=-1;ti=-1;si=-1
 for z in range(HOLDS.size):
  if HOLDS[z]==hold_ms:hi=z
 if tp>0:
  for z in range(TP_LEVELS.size):
   if TP_LEVELS[z]==tp:ti=z
 if sl>0:
  for z in range(SL_LEVELS.size):
   if SL_LEVELS[z]==sl:si=z
 xt=np.empty(n,np.int64);pnl=np.empty(n,np.float64);reason=np.empty(n,np.int8)
 for k in range(n):
  ht=h_t[k,hi];tt=tp_t[k,ti] if ti>=0 else INF;st=sl_t[k,si] if si>=0 else INF
  if tt<=st and tt<=ht:xt[k]=tt;pnl[k]=tp_p[k,ti];reason[k]=1
  elif st<tt and st<=ht:xt[k]=st;pnl[k]=sl_p[k,si];reason[k]=2
  else:xt[k]=ht;pnl[k]=h_p[k,hi];reason[k]=3
 return xt,pnl,reason
def metric(p):
 gp=float(p[p>0].sum());gl=float(p[p<=0].sum());return dict(net=float(p.sum()),trades=int(p.size),gp=gp,gl=gl,pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0) if p.size else 0),exp=float(np.mean(p) if p.size else 0))
def cap_select(E,X,P,R,S,cap):
 order=np.argsort(E,kind='stable');E=E[order];X=X[order];P=P[order];R=R[order];S=S[order];active=[];accepted=[];sk=0;mo=0
 for k in range(len(E)):
  now=int(E[k])
  while active and active[0][0]<=now:heapq.heappop(active)
  if len(active)>=cap:sk+=1;continue
  accepted.append(k);heapq.heappush(active,(int(X[k]),k));mo=max(mo,len(active))
 q=np.asarray(accepted,np.int64);return E[q],X[q],P[q],R[q],S[q],sk,mo
def summarize(E,X,P,R,S,cap,sk,mo):
 m=metric(P);o=np.argsort(X,kind='stable');pp=P[o];bal=np.cumsum(pp);prior=np.r_[0.,bal[:-1]];peak=np.maximum.accumulate(prior);bdd=float(np.max(peak-bal)) if len(pp) else 0.
 m.update(cap=cap,skips=sk,maxopen=mo,balance_dd=bdd,tp=int(np.sum(R==1)),sl=int(np.sum(R==2)),age=int(np.sum(R==3)))
 return m
def build(mode='maxnet'):
 t,sa,sb,start,end=j.load_month(2,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);h4,h1,m15,m5=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));idx,d,hr,sig,disp=build_events(t,mid,h4,h1,m15,m5,start,end,50)
 L=json.load(open('/mnt/data/gamma02_feb_lifecycle_quality_125.json'))['cells'];Es=[];Xs=[];Ps=[];Rs=[];Ss=[];chosen=[]
 for ci,z in enumerate(L,1):
  cell=z['cell']
  if mode=='quality':
   if z['top_quality']:cfg=z['top_quality'][0]
   elif z['top_net'][0]['pf']>=2.0:cfg=z['top_net'][0]
   else:continue
  elif mode=='quality_strict':
   if not z['top_quality']:continue
   cfg=z['top_quality'][0]
  else:cfg=z['top_net'][0]
  m=(hr==cell['hour'])&(sig==cell['sigcode']);ii=idx[m];dd=d[m];H=precompute_hits(t,a,b,ii,dd,TP_LEVELS,SL_LEVELS,HOLDS);xt,pnl,reason=choose_outcomes(*H,int(cfg['tp']),int(cfg['sl']),int(cfg['hold_ms']))
  Es.append(t[ii]);Xs.append(xt);Ps.append(pnl);Rs.append(reason);Ss.append(np.full(len(ii),ci,np.int16));chosen.append(dict(cell_id=ci,cell=cell,config=cfg))
 E=np.concatenate(Es);X=np.concatenate(Xs);P=np.concatenate(Ps);R=np.concatenate(Rs);S=np.concatenate(Ss);o=np.argsort(E,kind='stable');return (E[o],X[o],P[o],R[o],S[o]),chosen
def main():
 out={'candidate':'GAMMA02_FEB_NATIVE_LIFECYCLE_PORTFOLIO_125','modes':{}}
 for mode in ('maxnet','quality','quality_strict'):
  A,chosen=build(mode);rows=[]
  for cap in (32,64,96,128,160,192,256,320,384,512):
   B=cap_select(*A,cap);rows.append(summarize(*B[:5],cap,B[5],B[6]))
  out['modes'][mode]={'candidate_events':len(A[0]),'chosen':chosen,'rows':rows};json.dump(out,open('/mnt/data/gamma02_feb_lifecycle_portfolio_125.partial.json','w'),indent=2)
 json.dump(out,open('/mnt/data/gamma02_feb_lifecycle_portfolio_125.json','w'),indent=2)
if __name__=='__main__':main()
