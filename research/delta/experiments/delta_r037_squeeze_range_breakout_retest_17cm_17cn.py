"""R037 squeeze-range breakout/retest Stage-A screen — 17CM-17CN.

Preregistered source-grounded lifecycle:
- M5 BB20/2.0 inside KC EMA20 +/-1.5*ATR20 defines a squeeze.
- Track the contiguous squeeze segment high/low and lock that range when squeeze ends.
- First later completed M5 close outside the locked range defines breakout direction.
- Do not chase release: wait for the first causal retest/hold of the broken range edge.
- 17CM confirms retest on completed M5; 17CN confirms on completed M1.
- A new M5 squeeze or completed close through the opposite locked edge invalidates event.
- Frozen DELTA P75 30-second execution; no tuning, no August, no MQL5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

DAY=86_400_000; HOUR=3_600_000; TICK=10; SCALE=1000
START=1_767_225_600_000; END=1_768_737_600_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="038d1750aaf510cd2929f7301f46af2a994d9d90"
MAX_SPREAD=250; STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30


def sh(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()


def atomic(p:Path,o:dict)->None:
 p.parent.mkdir(parents=True,exist_ok=True); q=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
   q=f.name; json.dump(o,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
  os.replace(q,p); q=None
 finally:
  if q:
   try: os.unlink(q)
   except FileNotFoundError: pass


def sess(t):
 tod=t%DAY; ls=np.where(t>=UK_DST,7,8)*HOUR; le=ls+30_600_000; ns=np.where(t>=US_DST,12,13)*HOUR; ne=ns+32_400_000
 il=(tod>=ls)&(tod<le); ny=(tod>=ns)&(tod<ne)
 return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)


def p75(t,a,b):
 sp=P75[sess(t)]*TICK; m=a.astype(np.int64)+b.astype(np.int64); bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)


def bars(t,bid,tf):
 buck=t//tf; st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1]; en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*tf).astype(np.int64),"o":bid[st].astype(np.int64),"c":bid[en-1].astype(np.int64),"h":np.maximum.reduceat(bid,st).astype(np.int64),"l":np.minimum.reduceat(bid,st).astype(np.int64)}


def atr(b,period):
 h,l,c=b["h"],b["l"],b["c"]; tr=(h-l).astype(np.float64)
 if len(tr)>1: tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 out=np.full(len(tr),np.nan,np.float64)
 if len(tr)>=period:
  cs=np.r_[0.0,np.cumsum(tr)]; out[period-1:]=(cs[period:]-cs[:-period])/period
 return out


def ema(x,period):
 x=x.astype(np.float64); out=np.full(len(x),np.nan,np.float64)
 if len(x)<period:return out
 k=2.0/(period+1.0); out[period-1]=float(np.mean(x[:period]))
 for i in range(period,len(x)): out[i]=k*x[i]+(1.0-k)*out[i-1]
 return out


def sma_std(x,period):
 x=x.astype(np.float64); m=np.full(len(x),np.nan,np.float64); s=np.full(len(x),np.nan,np.float64)
 if len(x)<period:return m,s
 cs=np.r_[0.0,np.cumsum(x)]; cs2=np.r_[0.0,np.cumsum(x*x)]
 for i in range(period-1,len(x)):
  sm=cs[i+1]-cs[i+1-period]; sm2=cs2[i+1]-cs2[i+1-period]; mu=sm/period; v=max(0.0,sm2/period-mu*mu); m[i]=mu; s[i]=np.sqrt(v)
 return m,s


def squeeze_state(b):
 mean,sd=sma_std(b["c"],20); a=atr(b,20); e=ema(b["c"],20)
 bu=mean+2.0*sd; bl=mean-2.0*sd; ku=e+1.5*a; kl=e-1.5*a
 return (bu<ku)&(bl>kl)


def breakout_events(m5):
 sq=squeeze_state(m5); h,l,c,e=m5["h"],m5["l"],m5["c"],m5["end"]
 events=[]; diag={"squeeze_segments":0,"locked_ranges":0,"breakouts":0,"bull_breakouts":0,"bear_breakouts":0,"locks_replaced_by_new_squeeze":0}
 in_sq=False; sq_hi=0; sq_lo=0; have_lock=False; lock_hi=0; lock_lo=0
 for k in range(20,len(c)):
  if int(e[k])>END:break
  if bool(sq[k]):
   if not in_sq:
    if have_lock: diag["locks_replaced_by_new_squeeze"]+=1
    in_sq=True; have_lock=False; sq_hi=int(h[k]); sq_lo=int(l[k]); diag["squeeze_segments"]+=1
   else:
    sq_hi=max(sq_hi,int(h[k])); sq_lo=min(sq_lo,int(l[k]))
   continue
  if in_sq:
   in_sq=False; have_lock=True; lock_hi=sq_hi; lock_lo=sq_lo; diag["locked_ranges"]+=1
  if have_lock:
   side=1 if int(c[k])>lock_hi else(-1 if int(c[k])<lock_lo else 0)
   if side:
    events.append((k,int(e[k]),side,lock_hi,lock_lo)); have_lock=False; diag["breakouts"]+=1
    if side>0:diag["bull_breakouts"]+=1
    else:diag["bear_breakouts"]+=1
 return events,sq,diag


def next_true_end(sq,end,start_idx):
 j=start_idx+1
 while j<len(sq):
  if bool(sq[j]):return int(end[j])
  j+=1
 return 2**63-1


def m5_retests(t,m5,events,sq):
 ix=[]; sd=[]; diag={"events":len(events),"retests":0,"invalid_opposite":0,"invalid_new_squeeze":0,"no_executable_tick":0,"no_retest_before_end":0}
 h,l,c,e=m5["h"],m5["l"],m5["c"],m5["end"]
 for bk,bedge,side,hi,lo in events:
  found=False
  for r in range(bk+1,len(c)):
   if int(e[r])>END:break
   if bool(sq[r]):diag["invalid_new_squeeze"]+=1;found=True;break
   if (side>0 and int(c[r])<lo) or (side<0 and int(c[r])>hi):diag["invalid_opposite"]+=1;found=True;break
   ok=(side>0 and int(l[r])<=hi and int(c[r])>hi) or (side<0 and int(h[r])>=lo and int(c[r])<lo)
   if ok:
    j=int(np.searchsorted(t,int(e[r]),side="left"))
    if j<len(t) and int(t[j])<END:ix.append(j);sd.append(side);diag["retests"]+=1
    else:diag["no_executable_tick"]+=1
    found=True;break
  if not found:diag["no_retest_before_end"]+=1
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8),diag


def m1_retests(t,m1,m5,events,sq):
 ix=[]; sd=[]; diag={"events":len(events),"retests":0,"invalid_opposite":0,"invalid_new_squeeze":0,"no_executable_tick":0,"no_retest_before_end":0}
 h,l,c,e=m1["h"],m1["l"],m1["c"],m1["end"]
 m5e=m5["end"]
 for bk,bedge,side,hi,lo in events:
  stop_new_sq=next_true_end(sq,m5e,bk)
  start=int(np.searchsorted(e,bedge,side="right")); found=False
  for r in range(start,len(c)):
   tm=int(e[r])
   if tm>END:break
   if tm>=stop_new_sq:diag["invalid_new_squeeze"]+=1;found=True;break
   if (side>0 and int(c[r])<lo) or (side<0 and int(c[r])>hi):diag["invalid_opposite"]+=1;found=True;break
   ok=(side>0 and int(l[r])<=hi and int(c[r])>hi) or (side<0 and int(h[r])>=lo and int(c[r])<lo)
   if ok:
    j=int(np.searchsorted(t,tm,side="left"))
    if j<len(t) and int(t[j])<END:ix.append(j);sd.append(side);diag["retests"]+=1
    else:diag["no_executable_tick"]+=1
    found=True;break
  if not found:diag["no_retest_before_end"]+=1
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
 started=time.monotonic(); ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 hs=sh(x.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[(d.timestamp_ms_utc>=START)&(d.timestamp_ms_utc<END)];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ask,bid=p75(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64));m5=bars(t,bid,300_000);m1=bars(t,bid,60_000)
 events,sq,bdiag=breakout_events(m5)
 i5,s5,d5=m5_retests(t,m5,events,sq);i1,s1,d1=m1_retests(t,m1,m5,events,sq)
 configs={}
 for n,ii,ss,dd in (("17CM_M5_SQUEEZE_RANGE_RETEST",i5,s5,d5),("17CN_M1_SQUEEZE_RANGE_RETEST",i1,s1,d1)):
  m,g=pack(ii,ss,t,ask,bid);configs[n]={"metrics":m,"gate":g,"diagnostics":dd}
 surv=[n for n,v in configs.items() if v["gate"]["screen_pass"]];surv.sort(key=lambda n:(configs[n]["metrics"]["direct_net_usd"],configs[n]["metrics"]["official_wins"],configs[n]["metrics"]["trades"]),reverse=True)
 out={"schema":"delta-r037-squeeze-range-breakout-retest-17cm-17cn-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_SQUEEZE_RANGE_BREAKOUT_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CM_17CN","family":"R037-SRBRT-v1","parent_checkpoint":"R037_XAUUSD_INSIDE_BAR_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CK_17CL","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","breakout_diagnostics":bdiag,"configs":configs,"finding":{"survivors":surv,"leader":surv[0] if surv else None,"decision":"ADVANCE_SRBRT_LEADER" if surv else "RETIRE_SRBRT_NO_STAGE_A_SURVIVOR","next":"R037_SRBRT_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"post_result_rescue":False,"august_accessed":False,"mql5_authorized":False,"runtime_seconds":round(time.monotonic()-started,3)}
 atomic(x.output,out);print(json.dumps({"breakouts":bdiag,"configs":{n:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"],"diag":v["diagnostics"]} for n,v in configs.items()},"finding":out["finding"],"runtime_seconds":out["runtime_seconds"]},separators=(",",":")))


if __name__=="__main__":main()
