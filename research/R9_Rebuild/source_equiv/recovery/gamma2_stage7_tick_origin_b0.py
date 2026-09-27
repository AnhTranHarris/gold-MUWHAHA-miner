import ast,json,sys,time
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
from gamma2_rebuilt_golden import replay_hybrid,nonoverlap,metrics
TARGET={'trades':30943,'winners':25368,'win_rate':0.8198300100184209,'net':5131.0509999771375,'gross_loss':-6091.20650000407,'max_drawdown':40.79750000011154}
H=.10
src=Path('/mnt/data/gamma2_source_contract_stage2_batch.py').read_text().replace('@njit(cache=True)','@njit(cache=False)')
tree=ast.parse(src); body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in ('floor_s','gen')]
ns={'np':np,'njit':njit,'H':H}; exec(compile(ast.Module(body=body,type_ignores=[]),'<s2>','exec'),ns); gen=ns['gen']

def score(m):
 return (abs(m['trades']-TARGET['trades'])/TARGET['trades']+abs(m['winners']-TARGET['winners'])/TARGET['winners']+
         abs(m['net']-TARGET['net'])/10000+abs(m['gross_loss']-TARGET['gross_loss'])/10000+
         abs(m['max_drawdown']-TARGET['max_drawdown'])/100)

@njit(cache=False)
def landmarks(t,mid,first_ix,last_ix,karr,side,level,vi,c):
 n=len(karr); out=np.empty((n,12),np.int64); valid=np.ones((n,12),np.uint8)
 for r in range(n):
  k=karr[r]; kp=k+1
  out[r,0]=t[first_ix[k]]; out[r,1]=t[last_ix[k]]
  out[r,4]=t[first_ix[kp]]; out[r,5]=t[last_ix[kp]]
  for off,colh,coll in ((0,2,3),(1,6,7)):
   j=k+off; a=first_ix[j]; b=last_ix[j]; hi=-1e300; lo=1e300; thi=t[a];tlo=t[a]
   for i in range(a,b+1):
    p=mid[i]
    if p>hi: hi=p;thi=t[i]
    if p<lo: lo=p;tlo=t[i]
   out[r,colh]=thi;out[r,coll]=tlo
  for sec_off,col_break,col_rec in ((0,8,9),(1,10,11)):
   j=k+sec_off;a=first_ix[j];b=last_ix[j];fb=-1;fr=-1
   for i in range(a,b+1):
    p=mid[i]
    if side[r]<0:
     if fb<0 and p>=level[r]: fb=t[i]
     if fr<0 and p<=level[r]-.25: fr=t[i]
    else:
     if fb<0 and p<=level[r]: fb=t[i]
     if fr<0 and p>=level[r]+.25: fr=t[i]
   if fb<0: out[r,col_break]=out[r,0 if sec_off==0 else 4];valid[r,col_break]=0
   else: out[r,col_break]=fb
   if fr<0: out[r,col_rec]=out[r,0 if sec_off==0 else 4];valid[r,col_rec]=0
   else: out[r,col_rec]=fr
 return out,valid

z=np.load('/mnt/data/R9B_FAST_CACHE/m01.npz',mmap_mode='r');t=np.asarray(z['t']);mid=np.asarray(z['mid']);sec=np.asarray(z['sec_ids']);atr=np.asarray(z['atrsec']);al=np.asarray(z['align_long']);ash=np.asarray(z['align_short'])
ts=t//1000;ch=np.empty(len(ts),bool);ch[0]=1;ch[1:]=ts[1:]!=ts[:-1];first_ix=np.flatnonzero(ch);last_ix=np.r_[first_ix[1:]-1,len(t)-1];first=t[first_ix];h=np.maximum.reduceat(mid,first_ix);l=np.minimum.reduceat(mid,first_ix);c=mid[last_ix]
r=json.load(open('/mnt/data/GAMMA2_SOURCE_CONTRACT_STAGE2_B0.json'))['best'][0]
X0=gen(sec,first,h,l,c,atr,al,ash,r['level_shift'],r['bar_shift'],r['vel_intervals'],r['liq_len'],r['liq_end_shift'],r['break_mode'],r['reclaim_mode'],r['no_same'],r['cont_mode'],r['reset_state'],r['persistence'])
k=np.searchsorted(first,X0[:,0].astype(np.int64));side=X0[:,1].astype(np.int8);level=X0[:,2]
LM,V=landmarks(t,mid,first_ix,last_ix,k,side,level,r['vel_intervals'],c)
labels=['first_k','last_k','high_k','low_k','first_kp1','last_kp1','high_kp1','low_kp1','break_k','reclaim_k','break_kp1','reclaim_kp1']
rows=[];t0=time.time()
for col,label in enumerate(labels):
 sig=LM[:,col]; aj=np.clip(k,0,len(sec)-1); ac=np.where(side>0,al[aj],ash[aj]).astype(float)
 X=np.column_stack([sig.astype(float),side.astype(float),level,ac]); O=replay_hybrid(t,mid,X); K=nonoverlap(X,O);m=metrics(O[K,0])
 m.update(label=label,raw_signals=int(len(X0)),landmark_found_share=float(V[:,col].mean()),future_feature_share=float(np.mean(sig[K] < first[np.minimum(k[K]+1,len(first)-1)])))
 m['score']=score(m); rows.append(m)
rows.sort(key=lambda x:x['score'])
out={'unit':'R9B_GAMMA2_SOURCE_EQUIV_TICK_ORIGIN_010G_B0','target':TARGET,'base':r,'best':rows,'elapsed_s':time.time()-t0,'august_accessed':False}
Path('/mnt/data/GAMMA2_STAGE7_TICK_ORIGIN_B0.json').write_text(json.dumps(out,indent=2,sort_keys=True))
for x in rows: print(json.dumps(x))
