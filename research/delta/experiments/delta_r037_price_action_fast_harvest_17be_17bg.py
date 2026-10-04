"""DELTA R037 price-action fast harvest 17BE-17BG.

Three preregistered, independent, source-only Stage-A screens:
17BE TBR: M1 three-bar reversal + EMA9/EMA21 trend confirmation.
17BF PCR: M1 no-EMA pullback candle reversal.
17BG FAKEY: M5 mother/inside/false-break/opposite-break pattern.

All signals use completed bars only. Entry is first executable P75 tick at/after
the confirmation bar right edge. Frozen 30-second DELTA execution. No tuning.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DAY=86_400_000; HOUR=3_600_000; TICK=10; SCALE=1000
END=1_768_737_600_000
US=1_772_953_200_000; UK=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="95a7ed14925c4acba1ca19fd6db78a21c5ab33f6"
MAX_SPREAD=250; STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()

def atomic(p:Path,x:dict)->None:
 p.parent.mkdir(parents=True,exist_ok=True); q=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
   q=f.name; json.dump(x,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
  os.replace(q,p); q=None
 finally:
  if q:
   try: os.unlink(q)
   except FileNotFoundError: pass

def sess(t):
 tod=t%DAY
 ls=np.where(t>=UK,7,8)*HOUR; le=ls+30_600_000
 ns=np.where(t>=US,12,13)*HOUR; ne=ns+32_400_000
 il=(tod>=ls)&(tod<le); ny=(tod>=ns)&(tod<ne)
 return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)

def p75(t,a,b):
 sp=P75[sess(t)]*TICK
 m=a.astype(np.int64)+b.astype(np.int64)
 bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,mid,tf):
 buck=t//tf
 st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1]
 en=np.r_[st[1:],len(t)]
 return {
  "end_ms":((buck[st]+1)*tf).astype(np.int64),
  "open":mid[st].astype(np.int64),
  "high":np.maximum.reduceat(mid,st).astype(np.int64),
  "low":np.minimum.reduceat(mid,st).astype(np.int64),
  "close":mid[en-1].astype(np.int64)
 }

def ema(x,n):
 out=np.empty(len(x),np.float64)
 if len(x)==0:return out
 a=2.0/(n+1.0); out[0]=float(x[0])
 for i in range(1,len(x)): out[i]=a*float(x[i])+(1.0-a)*out[i-1]
 return out

def tick_index_for_bar_end(t,end_ms):
 j=int(np.searchsorted(t,int(end_ms),side="left"))
 return j if j<len(t) else -1

def tbr_events(t,b):
 o,h,l,c,e=b["open"],b["high"],b["low"],b["close"],b["end_ms"]
 e9,e21=ema(c,9),ema(c,21)
 idx=[]; side=[]
 for i in range(21,len(c)):
  b1=i-2; b2=i-1; b3=i; s=0
  if c[b1]<o[b1] and l[b2]<l[b1] and l[b2]<l[b3] and c[b3]>h[b1] and c[b3]>h[b2] and e9[b3]>e21[b3]:
   s=1
  elif c[b1]>o[b1] and h[b2]>h[b1] and h[b2]>h[b3] and c[b3]<l[b1] and c[b3]<l[b2] and e9[b3]<e21[b3]:
   s=-1
  if s:
   j=tick_index_for_bar_end(t,e[b3])
   if j>=0: idx.append(j); side.append(s)
 return np.asarray(idx,np.int64),np.asarray(side,np.int8)

def pcr_events(t,b):
 o,h,l,c,e=b["open"],b["high"],b["low"],b["close"],b["end_ms"]
 idx=[]; side=[]
 for i in range(10,len(c)):
  s=0
  # Bars3->2->1 are i-3,i-2,i-1; i is completed reversal bar.
  if c[i-3]>c[i-2]>c[i-1] and c[i]>c[i-1]:
   floor=np.min(l[i-5:i+1])
   if l[i-1]<=floor or l[i]<=floor: s=1
  elif c[i-3]<c[i-2]<c[i-1] and c[i]<c[i-1]:
   ceil=np.max(h[i-9:i+1])
   if h[i-1]>=ceil or h[i]>=ceil: s=-1
  if s:
   j=tick_index_for_bar_end(t,e[i])
   if j>=0: idx.append(j); side.append(s)
 return np.asarray(idx,np.int64),np.asarray(side,np.int8)

def fakey_events(t,b):
 h,l,e=b["high"],b["low"],b["end_ms"]
 idx=[];side=[]
 for i in range(3,len(h)):
  m=i-3; ib=i-2; br=i-1; rv=i
  if not (h[ib]<h[m] and l[ib]>l[m]): continue
  up= h[br]>h[m] and l[br]>=l[m]
  dn= l[br]<l[m] and h[br]<=h[m]
  s=0
  if dn and h[rv]>h[m]: s=1
  elif up and l[rv]<l[m]: s=-1
  if s:
   j=tick_index_for_bar_end(t,e[rv])
   if j>=0: idx.append(j);side.append(s)
 return np.asarray(idx,np.int64),np.asarray(side,np.int8)

@njit(cache=True)
def qt(x): return ((int(x)+5)//10)*10

@njit(cache=True)
def evaltr(idx,side,t,ask,bid):
 busy=-1;tr=bs=sr=dn=lg=sh=w=st=mh=en=0;gp=gl=net=0.
 days=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]); s=int(side[z])
  if i<=busy: bs+=1; continue
  if int(ask[i]-bid[i])>MAX_SPREAD: sr+=1; continue
  tr+=1; lg+=s>0; sh+=s<0; days[dn]=int(t[i]//DAY); dn+=1
  entry=int(ask[i]) if s>0 else int(bid[i])
  stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP)
  sec0=int(t[i])//1000; raw=0.; reason=2; last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]); bb=int(bid[k]); sec=int(t[k])//1000; last=k
   if s>0 and bb<=stop: raw=(bb-entry)/SCALE; reason=0; break
   if s<0 and aa>=stop: raw=(entry-aa)/SCALE; reason=0; break
   if sec-sec0>=MAX_HOLD: raw=((bb-entry) if s>0 else (entry-aa))/SCALE; reason=1; break
   fav=(bb-entry) if s>0 else (entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if (s>0 and ns>stop) or (s<0 and ns<stop): stop=ns
  else:
   aa=int(ask[last]);bb=int(bid[last]);raw=((bb-entry) if s>0 else (entry-aa))/SCALE
  ex=raw-.01; net+=ex-.01; w+=ex>1e-12
  if raw>0: gp+=ex
  else: gl+=ex
  if reason==0: st+=1
  elif reason==1: mh+=1
  else: en+=1
  busy=last
 d=0
 if dn:
  x=np.sort(days[:dn]); d=1
  for k in range(1,x.size): d+=x[k]!=x[k-1]
 return tr,bs,sr,d,lg,sh,w,gp,gl,net,st,mh,en

def metrics(idx,sd,t,ask,bid):
 tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en=evaltr(idx,sd,t,ask,bid)
 m={"signals":int(idx.size),"busy_skips":int(bs),"spread_rejects":int(sr),"trades":int(tr),
    "distinct_days":int(nd),"long":int(lg),"short":int(sh),"official_wins":int(w),
    "gross_profit":round(float(gp),2),"gross_loss":round(float(gl),2),"direct_net_usd":round(float(net),2),
    "exit_reasons":{"STOP":int(st),"MAX_HOLD":int(mh),"END":int(en)}}
 g={"minimum_trades_20":tr>=20,"minimum_distinct_days_5":nd>=5,"direct_net_min_minus_1":m["direct_net_usd"]>=-1.}
 g["screen_pass"]=bool(all(g.values())); g["strong_pass"]=bool(g["screen_pass"] and m["direct_net_usd"]>=0)
 return m,g

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
 hsh=sha(a.source)
 if hsh!=SHA: raise SystemExit("canonical January SHA mismatch: "+hsh)
 d=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 d=d[d.timestamp_ms_utc<END]
 t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]): raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64); br=d.bid_raw.to_numpy(np.int64)
 native=(ar+br)//2; ea,eb=p75(t,ar,br)
 b1=bars(t,native,60_000); b5=bars(t,native,300_000)
 event_sets={
  "17BE_TBR9_21":tbr_events(t,b1),
  "17BF_PCR":pcr_events(t,b1),
  "17BG_FAKEY":fakey_events(t,b5)
 }
 configs={}; survivors=[]
 for n,(idx,sd) in event_sets.items():
  m,g=metrics(idx,sd,t,ea,eb)
  configs[n]={"metrics":m,"gate":g}
  if g["screen_pass"]: survivors.append(n)
 decision="ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "RETIRE_BATCH_NO_EXECUTABLE_SURVIVOR"
 nxt="R037_PRICE_ACTION_SURVIVOR_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
 out={
  "schema":"delta-r037-price-action-fast-harvest-17be-17bg-v1",
  "status":"COMPLETE_FAST_CAUSAL_PRESCREEN",
  "unit":"R037_PRICE_ACTION_FAST_HARVEST_17BE_17BG",
  "parent_checkpoint":"R037_IER_STAGE_A_SCREEN_CHECKPOINT_17BD",
  "prereg_commit":PREREG,
  "source_sha256":hsh,"stage_a_ticks":int(len(t)),
  "signal_surfaces":{"17BE_TBR9_21":"NATIVE_DUKAS_M1_MID","17BF_PCR":"NATIVE_DUKAS_M1_MID","17BG_FAKEY":"NATIVE_DUKAS_M5_MID"},
  "execution_surface":"DUKAS_COINEXX_LIKE_P75",
  "numeric_retuning":False,"august_accessed":False,
  "diagnostics":{"m1_bars":int(len(b1["close"])),"m5_bars":int(len(b5["close"]))},
  "configs":configs,
  "finding":{"survivors":survivors,"decision":decision,"next":nxt},
  "mql5_authorized":False
 }
 atomic(a.output,out)
 print(json.dumps({"configs":{k:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"]} for k,v in configs.items()},"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
