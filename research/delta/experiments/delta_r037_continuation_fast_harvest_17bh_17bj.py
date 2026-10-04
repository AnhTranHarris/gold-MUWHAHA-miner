"""DELTA R037 controlled-pause continuation fast harvest 17BH-17BJ.

17BH: M1 Three-Bar Play continuation.
17BI: M15 Inside-Bar continuation baseline.
17BJ: M15 Inside-Bar continuation with source-published XAU quality filters.

Completed bars only. Inside-Bar entries trigger causally on P75 quote crossing the
Mother-Bar boundary during the one immediately subsequent M15 bar. Frozen DELTA
30-second execution after trigger. No post-result tuning.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DAY=86_400_000; HOUR=3_600_000; TICK=10; SCALE=1000; END=1_768_737_600_000
US=1_772_953_200_000; UK=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="f5d82ec9e5b07f28e737b03dc4c907ce95731bbe"
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
   q=f.name;json.dump(x,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(q,p);q=None
 finally:
  if q:
   try:os.unlink(q)
   except FileNotFoundError:pass

def sess(t):
 tod=t%DAY;ls=np.where(t>=UK,7,8)*HOUR;le=ls+30_600_000;ns=np.where(t>=US,12,13)*HOUR;ne=ns+32_400_000
 il=(tod>=ls)&(tod<le);ny=(tod>=ns)&(tod<ne)
 return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)

def p75(t,a,b):
 sp=P75[sess(t)]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,mid,tf):
 buck=t//tf;st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end_ms":((buck[st]+1)*tf).astype(np.int64),"open":mid[st].astype(np.int64),
 "high":np.maximum.reduceat(mid,st).astype(np.int64),"low":np.minimum.reduceat(mid,st).astype(np.int64),
 "close":mid[en-1].astype(np.int64)}

def atr14(b):
 h,l,c=b["high"],b["low"],b["close"];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 cs=np.r_[0.,np.cumsum(tr)];out=np.zeros(len(tr),np.float64)
 for i in range(13,len(tr)):out[i]=(cs[i+1]-cs[i-13])/14.
 return out

def tick_at_or_after(t,tm):
 j=int(np.searchsorted(t,int(tm),side="left"));return j if j<len(t) else -1

def play3(t,b):
 o,h,l,c,e=b["open"],b["high"],b["low"],b["close"],b["end_ms"];idx=[];sd=[]
 for i in range(2,len(c)):
  a=i-2;q=i-1;r=i;s=0
  if c[a]>o[a] and c[q]<o[q] and l[q]>l[a] and o[r]>o[q] and c[r]>c[q] and c[r]>h[q]:s=1
  elif c[a]<o[a] and c[q]>o[q] and h[q]<h[a] and o[r]<o[q] and c[r]<c[q] and c[r]<l[q]:s=-1
  if s:
   j=tick_at_or_after(t,e[r])
   if j>=0:idx.append(j);sd.append(s)
 return np.asarray(idx,np.int64),np.asarray(sd,np.int8)

def inside_events(t,ask,bid,b,quality=False):
 o,h,l,c,e=b["open"],b["high"],b["low"],b["close"],b["end_ms"];a14=atr14(b)
 idx=[];sd=[];patterns=0;qualified=0;expired=0
 for i in range(14,len(c)):
  m=i-1;s=i
  if not (h[s]<h[m] and l[s]>l[m]):continue
  patterns+=1
  mr=float(h[m]-l[m])
  if mr<=0 or c[m]==o[m]:continue
  if quality:
   body=abs(float(c[m]-o[m]))/mr
   inside=float(h[s]-l[s])/mr
   if body<0.80 or inside>0.50 or a14[m]<=0 or mr<0.60*a14[m]:continue
  qualified+=1
  direction=1 if c[m]>o[m] else -1
  start=tick_at_or_after(t,e[s]);stop=tick_at_or_after(t,e[s]+900_000)
  if start<0:continue
  if stop<0:stop=len(t)
  found=-1
  if direction>0:
   level=int(h[m])
   for k in range(start,stop):
    if int(ask[k])>=level:found=k;break
  else:
   level=int(l[m])
   for k in range(start,stop):
    if int(bid[k])<=level:found=k;break
  if found>=0:idx.append(found);sd.append(direction)
  else:expired+=1
 return np.asarray(idx,np.int64),np.asarray(sd,np.int8),{"patterns":patterns,"qualified":qualified,"expired":expired}

@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10

@njit(cache=True)
def evaltr(idx,side,t,ask,bid):
 busy=-1;tr=bs=sr=dn=lg=sh=w=st=mh=en=0;gp=gl=net=0.;days=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;sh+=s<0;days[dn]=int(t[i]//DAY);dn+=1
  entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP)
  sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]);bb=int(bid[k]);sec=int(t[k])//1000;last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if sec-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else (entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else (entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if (s>0 and ns>stop) or (s<0 and ns<stop):stop=ns
  else:
   aa=int(ask[last]);bb=int(bid[last]);raw=((bb-entry) if s>0 else (entry-aa))/SCALE
  ex=raw-.01;net+=ex-.01;w+=ex>1e-12
  if raw>0:gp+=ex
  else:gl+=ex
  if reason==0:st+=1
  elif reason==1:mh+=1
  else:en+=1
  busy=last
 nd=0
 if dn:
  x=np.sort(days[:dn]);nd=1
  for k in range(1,x.size):nd+=x[k]!=x[k-1]
 return tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en

def metrics(idx,sd,t,ask,bid):
 tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en=evaltr(idx,sd,t,ask,bid)
 m={"signals":int(idx.size),"busy_skips":int(bs),"spread_rejects":int(sr),"trades":int(tr),"distinct_days":int(nd),
 "long":int(lg),"short":int(sh),"official_wins":int(w),"gross_profit":round(float(gp),2),"gross_loss":round(float(gl),2),
 "direct_net_usd":round(float(net),2),"exit_reasons":{"STOP":int(st),"MAX_HOLD":int(mh),"END":int(en)}}
 g={"minimum_trades_20":tr>=20,"minimum_distinct_days_5":nd>=5,"direct_net_min_minus_1":m["direct_net_usd"]>=-1.}
 g["screen_pass"]=bool(all(g.values()));g["strong_pass"]=bool(g["screen_pass"] and m["direct_net_usd"]>=0)
 return m,g

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
 hsh=sha(a.source)
 if hsh!=SHA:raise SystemExit("canonical January SHA mismatch: "+hsh)
 d=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[d.timestamp_ms_utc<END]
 t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);native=(ar+br)//2;ea,eb=p75(t,ar,br)
 b1=bars(t,native,60_000);b15=bars(t,native,900_000)
 a_idx,a_sd=play3(t,b1)
 b_idx,b_sd,b_diag=inside_events(t,ea,eb,b15,False)
 q_idx,q_sd,q_diag=inside_events(t,ea,eb,b15,True)
 sets={"17BH_3BP_M1":(a_idx,a_sd),"17BI_IB_M15_BASE":(b_idx,b_sd),"17BJ_IB_M15_PUBLISHED_QUALITY":(q_idx,q_sd)}
 configs={};survivors=[]
 for n,(idx,sd) in sets.items():
  m,g=metrics(idx,sd,t,ea,eb);configs[n]={"metrics":m,"gate":g}
  if n=="17BI_IB_M15_BASE":configs[n]["pattern_diagnostics"]=b_diag
  if n=="17BJ_IB_M15_PUBLISHED_QUALITY":configs[n]["pattern_diagnostics"]=q_diag
  if g["screen_pass"]:survivors.append(n)
 decision="ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "RETIRE_BATCH_NO_EXECUTABLE_SURVIVOR"
 nxt="R037_CONTINUATION_SURVIVOR_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"
 out={"schema":"delta-r037-continuation-fast-harvest-17bh-17bj-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN",
 "unit":"R037_CONTROLLED_PAUSE_CONTINUATION_FAST_HARVEST_17BH_17BJ","parent_checkpoint":"R037_PRICE_ACTION_FAST_HARVEST_CHECKPOINT_17BE_17BG",
 "prereg_commit":PREREG,"source_sha256":hsh,"stage_a_ticks":int(len(t)),
 "signal_surfaces":{"17BH_3BP_M1":"NATIVE_DUKAS_M1_MID","17BI_IB_M15_BASE":"NATIVE_DUKAS_M15_MID","17BJ_IB_M15_PUBLISHED_QUALITY":"NATIVE_DUKAS_M15_MID"},
 "execution_surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,
 "diagnostics":{"m1_bars":int(len(b1["close"])),"m15_bars":int(len(b15["close"]))},"configs":configs,
 "finding":{"survivors":survivors,"decision":decision,"next":nxt},"mql5_authorized":False}
 atomic(a.output,out)
 print(json.dumps({"configs":{k:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"]} for k,v in configs.items()},"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":main()
