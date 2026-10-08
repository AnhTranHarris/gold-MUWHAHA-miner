import sys,os,heapq,json,hashlib,numpy as np
from pathlib import Path
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import gamma02_dynamic_watchdog_router_119 as wd
import gamma02_m1_density as gmd
import jan_profit_per_heat_atomic_131e as P
BASE=Path('/mnt/data/gamma02_jan_repro')
orig=wd.prep_month;DATA=orig(2)
wd.prep_month=lambda m:DATA
P.wd.prep_month=lambda m:DATA
P.gmd.prep=lambda:DATA
A,layer=P.build_raw();E,X,R,D,PN,H=A
print('RAW',len(E),float(PN.sum()),flush=True)
def capidx(E,X,cap):
 h=[];out=[]
 for k,now in enumerate(E):
  while h and h[0][0]<=now:heapq.heappop(h)
  if len(h)>=cap:continue
  out.append(k);heapq.heappush(h,(int(X[k]),k))
 return np.asarray(out,np.int64)
for ml,cap in [(25,256),(30,256),(30,384),(35,384),(35,512),(35,600),(35,640),(35,703)]:
 base=np.flatnonzero(layer<=ml);kk=capidx(E[base],X[base],cap);ix=base[kk];out=BASE/f'feb_wd_L{ml}_C{cap}_134e.npz';tmp=out.with_suffix('.tmp')
 with open(tmp,'wb') as f:np.savez_compressed(f,E=E[ix],X=X[ix],R=R[ix],D=D[ix],P=PN[ix],H=H[ix])
 os.replace(tmp,out);p=PN[ix];gp=p[p>0].sum();gl=p[p<0].sum();print(json.dumps({'ml':ml,'cap':cap,'net':float(p.sum()),'trades':len(p),'gl':float(gl),'pf':float(gp/-gl if gl<0 else 999),'win':float((p>0).mean())}),flush=True)