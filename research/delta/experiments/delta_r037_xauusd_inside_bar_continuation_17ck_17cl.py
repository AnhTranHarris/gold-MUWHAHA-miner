"""R037 XAUUSD-informed Inside-Bar continuation Stage-A screen — 17CK-17CL.

Public/source-grounded grammar:
- Main Bar followed by a fully contained Signal/Inside Bar.
- Main Bar direction selects breakout direction.
- XAUUSD research-derived fixed quality filters: Main-Bar body >=80% range,
  Signal-Bar range <=50% Main-Bar range.
- M15 and H1 lanes fixed before compute.
- One pending pattern at a time; one-bar causal breakout lifetime.
- Entry evaluated on P75 executable quote. Frozen DELTA 30-second execution.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DAY=86_400_000;HOUR=3_600_000;TICK=10;SCALE=1000
START=1_767_225_600_000;END=1_768_737_600_000
US_DST=1_772_953_200_000;UK_DST=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="db42a2c1f3ca3508be429b1040013705ec635dea"
MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30
BODY_MIN=.80;INSIDE_MAX=.50;OFFSET=10

def sh(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def atomic(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);q=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
   q=f.name;json.dump(o,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(q,p);q=None
 finally:
  if q:
   try:os.unlink(q)
   except FileNotFoundError:pass

def sess(t):
 tod=t%DAY;ls=np.where(t>=UK_DST,7,8)*HOUR;le=ls+30_600_000;ns=np.where(t>=US_DST,12,13)*HOUR;ne=ns+32_400_000
 il=(tod>=ls)&(tod<le);ny=(tod>=ns)&(tod<ne)
 return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)

def p75(t,a,b):
 sp=P75[sess(t)]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,bid,tf):
 buck=t//tf;st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*tf).astype(np.int64),"o":bid[st].astype(np.int64),"c":bid[en-1].astype(np.int64),"h":np.maximum.reduceat(bid,st).astype(np.int64),"l":np.minimum.reduceat(bid,st).astype(np.int64)}

def inside_bar_events(t,ask,bid,b,tf):
 o,c,h,l,e=b["o"],b["c"],b["h"],b["l"],b["end"];ix=[];sd=[]
 diag={"patterns":0,"quality_pass":0,"armed":0,"triggered":0,"expired":0,"pending_busy_skips":0}
 pending_until=-1
 for i in range(1,len(c)):
  # If prior pending still lives through this signal close, source one-pending rule skips.
  if int(e[i])<=pending_until:
   diag["pending_busy_skips"]+=1
   continue
  mr=int(h[i-1]-l[i-1]);sr=int(h[i]-l[i])
  if mr<=0:continue
  if not(int(h[i])<int(h[i-1]) and int(l[i])>int(l[i-1])):continue
  diag["patterns"]+=1
  body=abs(int(c[i-1])-int(o[i-1]))/mr
  inside=sr/mr
  if body<BODY_MIN or inside>INSIDE_MAX:continue
  side=1 if int(c[i-1])>int(o[i-1]) else(-1 if int(c[i-1])<int(o[i-1]) else 0)
  if not side:continue
  diag["quality_pass"]+=1
  arm=int(np.searchsorted(t,int(e[i]),side="left"))
  if arm>=len(t):continue
  expiry=int(e[i])+tf
  pending_until=expiry
  diag["armed"]+=1
  trg=-1
  for j in range(arm,len(t)):
   if int(t[j])>=expiry or int(t[j])>=END:break
   if side>0 and int(ask[j])>=int(h[i-1])+OFFSET:trg=j;break
   if side<0 and int(bid[j])<=int(l[i-1])-OFFSET:trg=j;break
  if trg>=0:
   ix.append(trg);sd.append(side);diag["triggered"]+=1
   pending_until=int(t[trg])
  else:
   diag["expired"]+=1
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8),diag

@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10

@njit(cache=True)
def ev(idx,side,t,ask,bid):
 busy=-1;tr=bs=sr=nd=lg=shrt=w=0;gp=gl=net=0.;stp=mh=en=0;u=0;used=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;shrt+=s<0;used[u]=int(t[i]//DAY);u+=1
  entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]);bb=int(bid[k]);last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if int(t[k])//1000-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else(entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else(entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if(s>0 and ns>stop)or(s<0 and ns<stop):stop=ns
  exitdeal=raw-.01;net+=exitdeal-.01;w+=exitdeal>1e-12
  if raw>0:gp+=exitdeal
  else:gl+=exitdeal
  if reason==0:stp+=1
  elif reason==1:mh+=1
  else:en+=1
  busy=last
 if u:
  x=np.sort(used[:u]);nd=1
  for k in range(1,x.size):nd+=x[k]!=x[k-1]
 return tr,bs,sr,nd,lg,shrt,w,gp,gl,net,stp,mh,en

def pack(idx,sd,t,ask,bid):
 q=ev(idx,sd,t,ask,bid)
 m={"signals":int(idx.size),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
 g={"minimum_trades_10":m["trades"]>=10,"minimum_distinct_days_5":m["distinct_days"]>=5,"direct_net_positive":m["direct_net_usd"]>0};g["screen_pass"]=all(g.values())
 return m,g

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 hs=sh(x.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[(d.timestamp_ms_utc>=START)&(d.timestamp_ms_utc<END)];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ask,bid=p75(t,ar,br)
 configs={}
 for n,tf in (("17CK_XIBC_M15_BODY80_INSIDE50",900_000),("17CL_XIBC_H1_BODY80_INSIDE50",3_600_000)):
  b=bars(t,bid,tf);ix,sd,diag=inside_bar_events(t,ask,bid,b,tf);m,g=pack(ix,sd,t,ask,bid);configs[n]={"timeframe_ms":tf,"metrics":m,"gate":g,"diagnostics":diag}
 surv=[n for n,v in configs.items() if v["gate"]["screen_pass"]];surv.sort(key=lambda n:(configs[n]["metrics"]["direct_net_usd"],configs[n]["metrics"]["official_wins"],configs[n]["metrics"]["trades"]),reverse=True)
 out={"schema":"delta-r037-xauusd-inside-bar-continuation-17ck-17cl-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_XAUUSD_INSIDE_BAR_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CK_17CL","family":"R037-XIBC-v1","parent_checkpoint":"R037_CONTROLLED_PAUSE_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CI_17CJ","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","configs":configs,"finding":{"survivors":surv,"leader":surv[0] if surv else None,"decision":"ADVANCE_XAUUSD_INSIDE_BAR_LEADER" if surv else "RETIRE_XAUUSD_INSIDE_BAR_NO_STAGE_A_SURVIVOR","next":"R037_XAUUSD_INSIDE_BAR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"august_accessed":False,"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"configs":{n:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"],"diag":v["diagnostics"]} for n,v in configs.items()},"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
