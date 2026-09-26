import gzip, shutil, json, hashlib, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
CACHE_GZ=Path('/mnt/data/alignment005/MM_C30_B1B_M01_CAUSAL_CACHE.npz.gz')
CACHE=Path('/mnt/data/alignment005/MM_C30_B1B_M01_CAUSAL_CACHE.npz')
OUT=Path('/mnt/data/R9B_GAMMA2_SOURCE_EQUIV_SWEEPGEN_007.json')
H=.10
TARGET={'trades':30943,'winners':25368,'win':0.8198300100184209,'net':5131.0509999771375,'gl':-6091.20650000407}

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

@njit
def floor_jan(sec):
 sod=sec%86400; london=(sod>=28800 and sod<59400); ny=(sod>=46800 and sod<79200)
 if london and ny:return 1.75
 if london:return 2.0
 if ny:return 1.75
 return 2.5

@njit
def gen_completed(sec_ids,first_t,hmid,lmid,cmid,m5atr,along,ashort,mode):
 maxn=120000; X=np.empty((maxn,4),np.float64); n=0
 state=0; level=0.; started=0; minute=-1; trades=0; cooldown=-1
 for j in range(21,len(sec_ids)):
  sec=sec_ids[j]; prev=j-1; mn=sec//60
  if mn!=minute:
   minute=mn; trades=0
   if mode!=3: state=0; level=0.; started=0
  if sec<cooldown or trades>=5: continue
  av=m5atr[j]
  if not np.isfinite(av) or av+1e-12<floor_jan(sec): continue
  upper=-1e18; lower=1e18
  for q in range(prev-20,prev):
   hb=hmid[q]-H; lb=lmid[q]-H
   if hb>upper: upper=hb
   if lb<lower: lower=lb
  pb_hi=hmid[prev]-H; pb_lo=lmid[prev]-H; pb_cl=cmid[prev]-H
  start=cmid[prev-4]-H; p0=start; travel=0.
  for q in range(prev-3,prev+1):
   v=cmid[q]-H; travel+=abs(v-p0); p0=v
  disp=pb_cl-start; eff=abs(disp)/(travel+1e-9)
  if mode==2:
   if pb_hi>=upper+.10 and pb_cl<=upper-.15 and disp<=-.15 and eff>=.30:
    X[n,0]=first_t[j];X[n,1]=-1;X[n,2]=upper;X[n,3]=ashort[j];n+=1;trades+=1;cooldown=sec+1
   elif pb_lo<=lower-.10 and pb_cl>=lower+.15 and disp>=.15 and eff>=.30:
    X[n,0]=first_t[j];X[n,1]=1;X[n,2]=lower;X[n,3]=along[j];n+=1;trades+=1;cooldown=sec+1
   continue
  if state==0:
   if mode==0:
    if pb_cl+H>=upper+.10: state=1;level=upper;started=sec
    elif pb_cl<=lower-.10: state=-1;level=lower;started=sec
   else:
    if pb_hi+2*H>=upper+.10: state=1;level=upper;started=sec
    elif pb_lo<=lower-.10: state=-1;level=lower;started=sec
  if state==1:
   if pb_cl+H<=level-.15: state=2;started=sec
  elif state==-1:
   if pb_cl>=level+.15: state=-2;started=sec
  elif state==2:
   if disp<=-.15 and eff>=.30:
    X[n,0]=first_t[j];X[n,1]=-1;X[n,2]=level;X[n,3]=ashort[j];n+=1;trades+=1;cooldown=sec+1;state=0;level=0.;started=0
  elif state==-2:
   if disp>=.15 and eff>=.30:
    X[n,0]=first_t[j];X[n,1]=1;X[n,2]=level;X[n,3]=along[j];n+=1;trades+=1;cooldown=sec+1;state=0;level=0.;started=0
  if state!=0 and started>0 and sec-started>20: state=0;level=0.;started=0
 return X[:n]

@njit
def replay(t,bid,ask,sec_ids,along,ashort,X):
 n=len(X);o=np.empty((n,6),np.float64)
 for k in range(n):
  sig=int(X[k,0]);i=np.searchsorted(t,sig);side=int(X[k,1]);sec=t[i]//1000;j=np.searchsorted(sec_ids,sec)
  if j>=len(sec_ids) or sec_ids[j]!=sec:o[k,:]=np.nan;continue
  ac=along[j] if side>0 else ashort[j]
  if ac>=3: stopd=1.;act=.10;trail=.04
  else: stopd=3.;act=.18;trail=.05
  entry=ask[i] if side>0 else bid[i]; stop=bid[i]-stopd if side>0 else ask[i]+stopd;ot=t[i];mfe=0.;mae=0.;done=False
  for q in range(i+1,len(t)):
   tt=t[q];fav=bid[q]-entry if side>0 else entry-ask[q];adv=entry-bid[q] if side>0 else ask[q]-entry
   if fav>mfe:mfe=fav
   if adv>mae:mae=adv
   if (side>0 and bid[q]<=stop) or (side<0 and ask[q]>=stop) or tt-ot>=60000:
    ex=bid[q] if side>0 else ask[q];o[k,0]=(ex-entry)*side;o[k,1]=(tt-ot)/1000.;o[k,2]=mfe;o[k,3]=mae;o[k,4]=tt;o[k,5]=ac;done=True;break
   if fav>=act:
    cand=bid[q]-trail if side>0 else ask[q]+trail
    if side>0:
     if cand>stop:stop=cand
    else:
     if cand<stop:stop=cand
  if not done:o[k,:]=np.nan
 return o

@njit
def nonoverlap(X,O):
 ix=np.argsort(X[:,0]);keep=np.empty(len(ix),np.int64);n=0;free=-1
 for q in ix:
  if X[q,0]<=free or not np.isfinite(O[q,0]):continue
  keep[n]=q;n+=1;free=int(O[q,4])
 return keep[:n]

def met(v):
 gp=float(v[v>0].sum());gl=float(v[v<0].sum());eq=np.cumsum(v);pk=np.maximum.accumulate(np.r_[0.,eq])[:-1]
 return {'trades':int(len(v)),'winners':int((v>0).sum()),'win':float((v>0).mean()) if len(v) else 0.,'net':float(v.sum()),'gl':gl,'pf':float(gp/-gl) if gl<0 else 999.,'maxdd':float((pk-eq).max()) if len(v) else 0.}

def main():
 st=time.time()
 if not CACHE.exists():
  with gzip.open(CACHE_GZ,'rb') as fi,open(CACHE,'wb') as fo:shutil.copyfileobj(fi,fo)
 z=np.load(CACHE);sec=z['sec_ids'].astype(np.int64);h=z['h'];l=z['l'];c=z['c'];atr=z['m5_atr'];al=z['align_long'];ash=z['align_short']
 d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False);ask0=d.ask_raw.to_numpy(np.float64)/1000.;bid0=d.bid_raw.to_numpy(np.float64)/1000.;mid=(ask0+bid0)*.5;bid=mid-H;ask=mid+H
 ticksec=t//1000;first_i=np.searchsorted(ticksec,sec,side='left').astype(np.int64);first_t=t[first_i]
 labels=['close_break_close_reclaim','wick_break_close_reclaim','samebar_wick_close_reclaim','wick_break_close_reclaim_no_minute_reset']
 rows=[]
 for mode,label in enumerate(labels):
  X=gen_completed(sec,first_t,h,l,c,atr,al,ash,mode);O=replay(t,bid,ask,sec,al,ash,X);ix=nonoverlap(X,O);m=met(O[ix,0]);m.update(variant=label,raw_signals=int(len(X)),trade_count_delta=m['trades']-TARGET['trades'],winner_delta=m['winners']-TARGET['winners'],win_delta=m['win']-TARGET['win'],net_delta=m['net']-TARGET['net']);rows.append(m);print(label,m,flush=True)
 out={'unit':'R9B_GAMMA2_SOURCE_EQUIV_SWEEPGEN_007','status':'SOURCE_EQUIVALENCE_DIAGNOSTIC','target':TARGET,'rows':rows,'raw_sha256':sha256(RAW),'frozen_alignment_cache_sha256':sha256(CACHE),'elapsed_s':time.time()-st,'august_sealed':True}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
