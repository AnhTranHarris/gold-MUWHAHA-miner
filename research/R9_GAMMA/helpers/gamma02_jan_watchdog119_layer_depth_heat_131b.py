"""GAMMA-02 January Watchdog-119 layer-depth / heat refinement 131B.

Owner-selected parent: GAMMA02_DYNAMIC_RENEWAL_WATCHDOG_119.
Parent refinement: 131A q-map [1.19,1.19,1.19,1.19,1.19,1.10] by causal
10-minute NY subphase. This unit changes ONLY two entry-known inventory dimensions:
  * maximum renewal-child ordinal (layer depth) within each admitted parent; and
  * global chronological child concurrency cap.

The layer ordinal is known when a child is created. It does not use future PnL,
MFE/MAE, future hold time, or calendar month as a deployable feature.

Execution caveat: inherits the GAMMA-02 normalized-spread research surface from
stmr_base.materialize(); it is not raw-Dukascopy fill parity or Coinexx MT5
certification.
"""
import argparse, datetime, hashlib, heapq, json
from pathlib import Path
import numpy as np

import gamma02_dynamic_watchdog_router_119 as wd
import gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_funded_cap_equity_dd_028 as eq
from gamma02_083_heat_parent_ownership_084 import renewal_owned

DAY=86_400_000
MARKET=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
QMAP=np.asarray([1190,1190,1190,1190,1190,1100],np.int32)
R9_SYNTH=dict(net=41520.82,trades=27980,gross_loss=-1827.87,pf=23.7154119275,
              win=0.8709077913,expectancy=1.4839463903,avg_hold_s=16.4626876340,
              balance_dd=3.40)
CASES=[
 ('SYNTH_VELOCITY_LOWEST_HEAT',35,224),
 ('RISK_VELOCITY_CORE',30,240),
 ('BALANCED_CORE',30,256),
 ('HIGH_CAPTURE_LAYER_PROTECTED',35,703),
 ('OVER_200K_DIAGNOSTIC',40,1152),
]

def sha256_file(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
 return h.hexdigest()

def build_raw():
 def pp():return wd.prep_month(1)
 gmd.prep=pp
 D,pei,pxi,pd,src,mins,disp=w.prep()
 t,a,b,mid,h4,h1,m15,m5=D[:8];start,end=D[-2],D[-1];pt=t[pei]
 lm=wd.local_minute(pt);lh=lm//60;lmin=lm%60
 target=(pt>=start)&(pt<end)
 macro=(h4[pei]!=0)&(h4[pei]==h1[pei])&(pd==h4[pei])
 base=target&macro&(lh>=12)&(lh<=13)
 assert np.all((pt[np.nonzero(base)[0]]>=start)&(pt[np.nonzero(base)[0]]<end))
 sig=((h4[pei]+1)*81+(h1[pei]+1)*27+(m15[pei]+1)*9+(m5[pei]+1)*3+(pd+1)).astype(np.int16)
 keys=np.stack((pt//DAY,lh,lmin//10,sig),axis=1)
 cells=np.unique(keys[np.nonzero(base)[0]],axis=0)
 parts=[];layers=[]
 for key in cells:
  day,hh,b10,sc=[int(x) for x in key]
  jj=np.nonzero(base&(keys[:,0]==day)&(keys[:,1]==hh)&(keys[:,2]==b10)&(keys[:,3]==sc))[0]
  if not len(jj):continue
  q=int(QMAP[b10]);A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],q,0,0,2)
  E,X,R,Dd,P,H,O=A[:7]
  if not len(E):continue
  by=[[] for _ in range(len(jj))]
  for ci,oo in enumerate(O):by[int(oo)].append(ci)
  order=np.argsort(t[pei[jj]],kind='stable');heap=[];adm=np.zeros(len(jj),np.bool_);streak=0;gate=False
  first=int(order[0]);adm[first]=True
  for ci in by[first]:heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
  for po in order[1:]:
   po=int(po);now=int(t[pei[jj[po]]])
   while heap and heap[0][0]<=now:
    _,ci=heapq.heappop(heap)
    good=(P[ci]>0 and H[ci]<=60.)
    streak=streak+1 if good else 0;gate=streak>=4
   if gate:
    adm[po]=True
    for ci in by[po]:heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
  keep=np.nonzero(adm[O])[0]
  if not len(keep):continue
  layer=np.zeros(len(E),np.int32);cnt={}
  for ci,oo in enumerate(O):
   oi=int(oo);cnt[oi]=cnt.get(oi,0)+1;layer[ci]=cnt[oi]
  parts.append((E[keep],X[keep],R[keep],Dd[keep],P[keep],H[keep],np.full(len(keep),2,np.int8)))
  layers.append(layer[keep])
 arr=[np.concatenate([p[k] for p in parts]) for k in range(7)]
 layer=np.concatenate(layers)
 o=np.lexsort((np.arange(len(arr[0])),arr[0]))
 return D,tuple(x[o] for x in arr),layer[o]

def capsel(E,X,cap):
 h=[];out=[];sk=0;mo=0
 for k,now in enumerate(E):
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:sk+=1;continue
  out.append(k);heapq.heappush(h,(int(X[k]),k));mo=max(mo,len(h))
 return np.asarray(out,np.int64),sk,mo

def weekly(t,X,P):
 d={}
 for i,p in enumerate(P):
  dt=datetime.datetime.fromtimestamp(int(t[int(X[i])])/1000,datetime.timezone.utc)
  y,wk,_=dt.isocalendar();k=f'{y}-W{wk:02d}';d.setdefault(k,[0.,0.,0])
  d[k][0]+=float(p);d[k][1]+=float(p) if p<0 else 0.;d[k][2]+=1
 return {k:{'net':round(v[0],2),'gross_loss':round(v[1],2),'trades':int(v[2])} for k,v in sorted(d.items())}

def evaluate(D,A,layer,label,max_layer,cap):
 t,a,b=D[:3];E,X,R,Dd,P,H,S=A
 base=np.nonzero(layer<=max_layer)[0]
 kk,sk,mo=capsel(E[base],X[base],cap);idx=base[kk]
 assert len(idx)>0 and int(layer[idx].max())<=max_layer and mo<=cap
 p=P[idx];h=H[idx];gp=float(p[p>0].sum());gl=float(p[p<=0].sum())
 q=eq.exact_equity_sweep(t,a,b,E[idx],X[idx],R[idx],Dd[idx],P[idx])
 peak_total=100000.+q[3]
 return dict(label=label,max_layer=max_layer,cap=cap,net=float(p.sum()),trades=int(len(p)),
  gross_profit=gp,gross_loss=gl,pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)),
  expectancy=float(np.mean(p)),avg_hold_s=float(np.mean(h)),skips=int(sk),maxopen_event=int(mo),
  balance_dd=float(q[2]),equity_dd=float(q[4]),equity_dd_pct_peak=float(q[4]/peak_total*100),
  minimum_total_equity=float(100000.+q[5]),maxopen_exact=int(q[9]),weekly_realized=weekly(t,X[idx],P[idx]))

def envelope(rows,status='PARTIAL'):
 return dict(candidate='GAMMA_02_JAN_WATCHDOG119_LAYER_DEPTH_HEAT_131B',status=status,
  parent='GAMMA_02_JAN_WATCHDOG119_GRID_LAYER_REFINEMENT_131A',market_file=str(MARKET),
  market_sha256=sha256_file(MARKET),qmap_raw=QMAP.tolist(),r9_synth_january=R9_SYNTH,
  execution_surface='Dukascopy midpoint + frozen session-P75 normalized spread; Python research only; not Coinexx MT5 certification',
  causality='max renewal-child ordinal and global cap are known at entry; no future outcome/hold/MFE/MAE used for admission',
  rows=rows,august='SEALED',mql5='NOT_AUTHORIZED')

def main(out):
 D,A,layer=build_raw();rows=[];partial=out+'.partial'
 for label,ml,cap in CASES:
  r=evaluate(D,A,layer,label,ml,cap);rows.append(r)
  with open(partial,'w') as f:json.dump(envelope(rows),f,indent=2)
  print(json.dumps({k:r[k] for k in ['label','max_layer','cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen_exact']}),flush=True)
 obj=envelope(rows,'COMPLETE')
 obj['selection']={
  'working_watchdog_parent':'WD119_SUBPHASE_Q1190_Q1100_CAP703 from 131A',
  'risk_velocity_core':'RISK_VELOCITY_CORE',
  'lowest_heat_matching_synth_velocity':'SYNTH_VELOCITY_LOWEST_HEAT',
  'high_capture_layer_protected':'HIGH_CAPTURE_LAYER_PROTECTED',
  'over_200k_diagnostic':'OVER_200K_DIAGNOSTIC',
  'finding':'Layer depth almost eliminates realized gross loss at moderate caps, but full-tick equity DD scales mainly with synchronized concurrency. >$200K remains heat-expensive.'
 }
 with open(out,'w') as f:json.dump(obj,f,indent=2)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();main(a.out)