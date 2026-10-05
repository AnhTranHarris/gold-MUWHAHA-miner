"""R037 controlled-pause continuation Stage-A screen — 17CI-17CJ.

17CI: source-default basic SuperTrend pullback/rebound on completed M5 bars.
17CJ: source-default M30 NR7 current-session compression-zone tick breakout.

Research-only. No post-result tuning, timeframe/side rescue, August or MQL5.
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
PREREG="0c779b1cf94a9d4b29b3e5c0ea5a0b7f94b17409"
MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30

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

def tr_arr(b):
 h,l,c=b["h"].astype(float),b["l"].astype(float),b["c"].astype(float);tr=h-l
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 return tr

def rma(x,n):
 out=np.full(len(x),np.nan)
 if len(x)<n:return out
 out[n-1]=float(np.mean(x[:n]))
 for i in range(n,len(x)):out[i]=(out[i-1]*(n-1)+float(x[i]))/n
 return out

def supertrend(b,n=10,factor=3.0):
 h,l,c=b["h"].astype(float),b["l"].astype(float),b["c"].astype(float);atr=rma(tr_arr(b),n);hl=(h+l)/2
 ub=hl+factor*atr;lb=hl-factor*atr;fu=ub.copy();fl=lb.copy();st=np.full(len(c),np.nan);bull=np.zeros(len(c),dtype=np.bool_)
 for i in range(n,len(c)):
  if not np.isnan(fu[i-1]):
   fu[i]=ub[i] if (ub[i]<fu[i-1] or c[i-1]>fu[i-1]) else fu[i-1]
   fl[i]=lb[i] if (lb[i]>fl[i-1] or c[i-1]<fl[i-1]) else fl[i-1]
  if i==n:
   bull[i]=c[i]>=fu[i];st[i]=fl[i] if bull[i] else fu[i]
  else:
   if st[i-1]==fu[i-1]:
    bull[i]=c[i]>fu[i]
   else:
    bull[i]=not(c[i]<fl[i])
   st[i]=fl[i] if bull[i] else fu[i]
 return st,bull

def tick_at(t,tm):
 i=int(np.searchsorted(t,int(tm),side="left"));return i if i<len(t) else -1

def supertrend_signals(t,b):
 st,bull=supertrend(b,10,3.0);ix=[];sd=[];diag={"pullbacks":0,"confirmed":0}
 for i in range(12,len(b["c"])):
  p=i-1
  if np.isnan(st[p]) or np.isnan(st[i]):continue
  s=0
  if bull[p] and b["l"][p]<st[p] and b["c"][p]>st[p]:
   diag["pullbacks"]+=1
   if bull[i] and b["c"][i]>st[i] and b["h"][i]>b["h"][p]:s=1
  elif (not bull[p]) and b["h"][p]>st[p] and b["c"][p]<st[p]:
   diag["pullbacks"]+=1
   if (not bull[i]) and b["c"][i]<st[i] and b["l"][i]<b["l"][p]:s=-1
  if s:
   j=tick_at(t,b["end"][i])
   if j>=0:ix.append(j);sd.append(s);diag["confirmed"]+=1
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8),diag

def nr7_signals(t,ask,bid,b):
 rng=b["h"]-b["l"];ix=[];sd=[];diag={"nr7":0,"armed":0,"triggered":0,"expired":0};busy_until=-1
 for k in range(6,len(rng)):
  bar_day=(int(b["end"][k])-1)//DAY
  if any(((int(b["end"][j])-1)//DAY)!=bar_day for j in range(k-6,k+1)):continue
  if not all(int(rng[k])<int(rng[j]) for j in range(k-6,k)):continue
  diag["nr7"]+=1
  arm=tick_at(t,b["end"][k])
  if arm<0 or arm<=busy_until:continue
  zhi=int(np.max(b["h"][k-6:k+1]));zlo=int(np.min(b["l"][k-6:k+1]));expiry=(bar_day+1)*DAY
  diag["armed"]+=1;trigger=-1;s=0
  j=arm
  while j<len(t) and int(t[j])<expiry and int(t[j])<END:
   if int(ask[j])>=zhi+10:trigger=j;s=1;break
   if int(bid[j])<=zlo-10:trigger=j;s=-1;break
   j+=1
  if trigger>=0:
   ix.append(trigger);sd.append(s);diag["triggered"]+=1;busy_until=trigger
  else:
   diag["expired"]+=1;busy_until=int(np.searchsorted(t,expiry,side="left"))-1
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
 q=ev(idx,sd,t,ask,bid);m={"signals":int(idx.size),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
 g={"minimum_trades_10":m["trades"]>=10,"minimum_distinct_days_5":m["distinct_days"]>=5,"direct_net_positive":m["direct_net_usd"]>0};g["screen_pass"]=all(g.values());return m,g

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 hs=sh(x.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[(d.timestamp_ms_utc>=START)&(d.timestamp_ms_utc<END)];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ask,bid=p75(t,ar,br)
 b5=bars(t,bid,300_000);b30=bars(t,bid,1_800_000)
 i1,s1,d1=supertrend_signals(t,b5);i2,s2,d2=nr7_signals(t,ask,bid,b30)
 configs={}
 for n,ix,sd,diag in (("17CI_SUPERTREND_PULLBACK_M5",i1,s1,d1),("17CJ_NR7_M30_SESSION_BREAKOUT",i2,s2,d2)):
  m,g=pack(ix,sd,t,ask,bid);configs[n]={"metrics":m,"gate":g,"diagnostics":diag}
 surv=[n for n,v in configs.items() if v["gate"]["screen_pass"]];surv.sort(key=lambda n:(configs[n]["metrics"]["direct_net_usd"],configs[n]["metrics"]["official_wins"],configs[n]["metrics"]["trades"]),reverse=True)
 out={"schema":"delta-r037-controlled-pause-continuation-17ci-17cj-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_CONTROLLED_PAUSE_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CI_17CJ","family":"R037-CPC-v1","parent_checkpoint":"R037_VCE_QIM_CONFIRMATION_STAGE_A_SCREEN_CHECKPOINT_17CE_17CH","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","configs":configs,"finding":{"survivors":surv,"leader":surv[0] if surv else None,"decision":"ADVANCE_CONTROLLED_PAUSE_LEADER" if surv else "RETIRE_CONTROLLED_PAUSE_NO_STAGE_A_SURVIVOR","next":"R037_CONTROLLED_PAUSE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"august_accessed":False,"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"configs":{n:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"],"diag":v["diagnostics"]} for n,v in configs.items()},"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
