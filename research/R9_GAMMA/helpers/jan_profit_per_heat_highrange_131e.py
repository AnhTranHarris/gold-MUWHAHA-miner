import json,heapq,numpy as np
import gamma02_dynamic_watchdog_router_119 as wd
import gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
from gamma02_083_heat_parent_ownership_084 import renewal_owned
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
DAY=86400000
QMAP=np.asarray([1190,1190,1190,1190,1190,1100],np.int32)
OUT='/mnt/data/gamma02_jan_repro/jan_profit_per_heat_highrange_131e.json'

def build_raw():
 def pp():return wd.prep_month(1)
 gmd.prep=pp
 D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b,mid,h4,h1,m15,m5=D[:8];start,end=D[-2],D[-1];pt=t[pei]
 lm=wd.local_minute(pt);lh=lm//60;lmin=lm%60;target=(pt>=start)&(pt<end);macro=(h4[pei]!=0)&(h4[pei]==h1[pei])&(pd==h4[pei]);base=target&macro&(lh>=12)&(lh<=13)
 sig=((h4[pei]+1)*81+(h1[pei]+1)*27+(m15[pei]+1)*9+(m5[pei]+1)*3+(pd+1)).astype(np.int16);keys=np.stack((pt//DAY,lh,lmin//10,sig),axis=1);cells=np.unique(keys[np.nonzero(base)[0]],axis=0)
 parts=[];layers=[]
 for key in cells:
  day,hh,b10,sc=[int(x) for x in key];jj=np.nonzero(base&(keys[:,0]==day)&(keys[:,1]==hh)&(keys[:,2]==b10)&(keys[:,3]==sc))[0]
  if not len(jj):continue
  q=int(QMAP[b10]);A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],q,0,0,2);E,X,R,Dd,P,H,O=A[:7]
  if not len(E):continue
  by=[[] for _ in range(len(jj))]
  for ci,oo in enumerate(O):by[int(oo)].append(ci)
  order=np.argsort(t[pei[jj]],kind='stable');heap=[];adm=np.zeros(len(jj),np.bool_);streak=0;gate=False
  first=int(order[0]);adm[first]=True
  for ci in by[first]:heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
  for po in order[1:]:
   po=int(po);now=int(t[pei[jj[po]]])
   while heap and heap[0][0]<=now:
    _,ci=heapq.heappop(heap);good=(P[ci]>0 and H[ci]<=60.);streak=streak+1 if good else 0;gate=streak>=4
   if gate:
    adm[po]=True
    for ci in by[po]:heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
  keep=np.nonzero(adm[O])[0]
  if not len(keep):continue
  layer=np.zeros(len(E),np.int32);cnt={}
  for ci,oo in enumerate(O):
   oi=int(oo);cnt[oi]=cnt.get(oi,0)+1;layer[ci]=cnt[oi]
  parts.append((E[keep],X[keep],R[keep],Dd[keep],P[keep],H[keep]));layers.append(layer[keep])
 arr=[np.concatenate([p[k] for p in parts]) for k in range(6)];layer=np.concatenate(layers);o=np.lexsort((np.arange(len(arr[0])),arr[0]));return tuple(x[o] for x in arr),layer[o]

def capsel(E,X,cap):
 h=[];out=[]
 for k,now in enumerate(E):
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:continue
  out.append(k);heapq.heappush(h,(int(X[k]),k))
 return np.asarray(out,np.int64)

def main():
 A,layer=build_raw();E,X,R,D,P,H=A
 cov=J.build_coverage();cold=J.build_coldstart(50,450,64);rules=[L.build_rule(k,l,st,cap) for k,l,n,st,cap in L.LEAN];supp=[cov,cold,*rules]
 rows=[]
 for ml,cap in [(35,512),(35,544),(35,576),(35,608),(35,640),(35,672),(35,703),(40,512),(40,576),(40,640)]:
  base=np.nonzero(layer<=ml)[0]; kk=capsel(E[base],X[base],cap);idx=base[kk];wdq=tuple(z[idx] for z in A)
  Q,meta=J.merge_preserve_watchdog(wdq,supp,512);meta.update(max_layer=ml,watchdog_cap=cap,cold_cap=64,wd_net=float(np.sum(wdq[4])),wd_trades=int(len(wdq[4])))
  s,_=J.score(J.DATA[0],*Q,f'L{ml}_C{cap}',meta);s['net_per_equity_dd']=float(s['net']/s['equity_dd']);rows.append(s)
  print(json.dumps({k:s[k] for k in ['name','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','beat_weeks','wd_net','wd_trades','net_per_equity_dd']}),flush=True)
 json.dump({'candidate':'GAMMA_02_JAN_WD119_PROFIT_PER_HEAT_ATOMIC_131E','session_portfolio':'131D LEAN4+COLD64 frozen','rows':rows},open(OUT,'w'),indent=2)
if __name__=='__main__':main()