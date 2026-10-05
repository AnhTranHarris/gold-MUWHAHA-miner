"""R037 VCE + queue-imbalance causal confirmation Stage-A screen — 17CE-17CH.

Control 17CE reproduces the frozen R037-VCE-C04 M5 BB/KC release + MOM12
entry grammar. 17CF/17CG/17CH apply the already-frozen QIM absolute
imbalance thresholds 0.25/0.50/0.75 only at the first executable tick
after the completed VCE signal bar, requiring imbalance sign alignment.

No parameter fitting, session/side rescue, exit retuning, August or MQL5.
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
PREREG="26d6e97a7ea5c2a6fadc7b903a6dde193b85cf9d"
TF=300_000;MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30
PROFILES=(("17CE_VCE_C04_CONTROL",None),("17CF_VCE_QI025_ALIGN",.25),("17CG_VCE_QI050_ALIGN",.50),("17CH_VCE_QI075_ALIGN",.75))

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

def bars(t,bid):
 buck=t//TF;st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*TF).astype(np.int64),"c":bid[en-1].astype(np.int64),"h":np.maximum.reduceat(bid,st).astype(np.int64),"l":np.minimum.reduceat(bid,st).astype(np.int64)}

def atr(b,n):
 h,l,c=b["h"],b["l"],b["c"];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 out=np.full(len(tr),np.nan)
 if len(tr)>=n:
  cs=np.r_[0.,np.cumsum(tr)];out[n-1:]=(cs[n:]-cs[:-n])/n
 return out

def ema(x,n):
 out=np.full(len(x),np.nan)
 if len(x)<n:return out
 k=2./(n+1.);out[n-1]=float(np.mean(x[:n]))
 for i in range(n,len(x)):out[i]=k*float(x[i])+(1-k)*out[i-1]
 return out

def sma_std(x,n):
 m=np.full(len(x),np.nan);s=np.full(len(x),np.nan)
 if len(x)<n:return m,s
 xf=x.astype(np.float64);cs=np.r_[0.,np.cumsum(xf)];cs2=np.r_[0.,np.cumsum(xf*xf)]
 for i in range(n-1,len(x)):
  a=cs[i+1]-cs[i+1-n];b=cs2[i+1]-cs2[i+1-n];q=a/n;v=max(0.,b/n-q*q);m[i]=q;s[i]=np.sqrt(v)
 return m,s

def vce_c04(t,ask,bid):
 b=bars(t,bid);c=b["c"].astype(np.float64);m,sd=sma_std(b["c"],20);a=atr(b,20);e=ema(b["c"],20)
 bu=m+2*sd;bl=m-2*sd;ku=e+1.5*a;kl=e-1.5*a;sq=(bu<ku)&(bl>kl)
 ix=[];side=[];days=[];diag={"bars":len(c),"release":0,"breakout":0,"mom12_pass":0,"spread_reject":0}
 for k in range(20,len(c)):
  if int(b["end"][k])>END:break
  if not(bool(sq[k-1]) and not bool(sq[k])):continue
  diag["release"]+=1
  s=1 if c[k]>ku[k] else(-1 if c[k]<kl[k] else 0)
  if not s:continue
  diag["breakout"]+=1
  mom=c[k]-c[k-12]
  if (s>0 and mom<=0) or(s<0 and mom>=0):continue
  diag["mom12_pass"]+=1
  i=int(np.searchsorted(t,int(b["end"][k]),side="left"))
  if i>=len(t):continue
  if int(ask[i]-bid[i])>MAX_SPREAD:diag["spread_reject"]+=1;continue
  ix.append(i);side.append(s);days.append((int(b["end"][k])-1)//DAY)
 return np.asarray(ix,np.int64),np.asarray(side,np.int8),np.asarray(days,np.int64),diag

@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10

@njit(cache=True)
def ev(idx,side,days,t,ask,bid):
 busy=-1;tr=bs=sr=nd=lg=shrt=w=0;gp=gl=net=0.;st=mh=en=0;u=0;used=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;shrt+=s<0;used[u]=days[z];u+=1
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
  if reason==0:st+=1
  elif reason==1:mh+=1
  else:en+=1
  busy=last
 if u:
  x=np.sort(used[:u]);nd=1
  for k in range(1,x.size):nd+=x[k]!=x[k-1]
 return tr,bs,sr,nd,lg,shrt,w,gp,gl,net,st,mh,en

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 hs=sh(x.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw","ask_volume","bid_volume"],dtype={"timestamp_ms_utc":np.int64,"ask_raw":np.int64,"bid_raw":np.int64,"ask_volume":np.float64,"bid_volume":np.float64})
 d=d[(d.timestamp_ms_utc>=START)&(d.timestamp_ms_utc<END)];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);av=d.ask_volume.to_numpy(float);bv=d.bid_volume.to_numpy(float);ask,bid=p75(t,ar,br)
 idx,side,days,diag=vce_c04(t,ask,bid)
 den=av+bv;imb=np.zeros(len(t));valid=np.isfinite(den)&np.isfinite(av)&np.isfinite(bv)&(den>0);imb[valid]=(bv[valid]-av[valid])/den[valid];imb=np.clip(imb,-1,1)
 configs={}
 for name,thr in PROFILES:
  if thr is None:mask=np.ones(idx.size,dtype=bool)
  else:mask=valid[idx]&(np.abs(imb[idx])>=thr)&(np.sign(imb[idx]).astype(np.int8)==side)
  ii=idx[mask];ss=side[mask];dd=days[mask];q=ev(ii,ss,dd,t,ask,bid)
  m={"source_proposals":int(idx.size),"qi_pass":int(mask.sum()),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
  configs[name]={"threshold":thr,"metrics":m}
 ctrl=configs["17CE_VCE_C04_CONTROL"]["metrics"]
 if not(ctrl["trades"]==27 and ctrl["official_wins"]==20 and abs(ctrl["direct_net_usd"]-.71)<1e-9 and ctrl["distinct_days"]==11):
  raise SystemExit("VCE control fingerprint mismatch: "+json.dumps(ctrl,sort_keys=True))
 for name,thr in PROFILES[1:]:
  m=configs[name]["metrics"];ret=m["trades"]/ctrl["trades"]
  gate={"minimum_trades_10":m["trades"]>=10,"minimum_distinct_days_5":m["distinct_days"]>=5,"retention_vs_control_min_0_35":ret>=.35,"direct_net_exceeds_control":m["direct_net_usd"]>ctrl["direct_net_usd"]}
  gate["screen_pass"]=all(gate.values());configs[name]["retention_vs_control"]=round(ret,6);configs[name]["gate"]=gate
 surv=[k for k,_ in PROFILES[1:] if configs[k]["gate"]["screen_pass"]]
 surv.sort(key=lambda k:(configs[k]["metrics"]["direct_net_usd"],configs[k]["metrics"]["official_wins"],configs[k]["metrics"]["trades"]),reverse=True)
 out={"schema":"delta-r037-vce-qim-confirmation-stage-a-17ce-17ch-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_VCE_QIM_CONFIRMATION_STAGE_A_SCREEN_CHECKPOINT_17CE_17CH","family":"R037-VQCF-v1","parent_checkpoint":"R037_BREAKER_BLOCK_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CC_17CD","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","vce_diagnostics":diag,"queue_imbalance":"(bid_volume-ask_volume)/(bid_volume+ask_volume) at first executable VCE tick","configs":configs,"finding":{"survivors":surv,"leader":surv[0] if surv else None,"decision":"ADVANCE_VCE_QIM_LEADER" if surv else "RETIRE_VCE_QIM_NO_STAGE_A_SURVIVOR","next":"R037_VCE_QIM_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"august_accessed":False,"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"control":ctrl,"candidates":{k:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"ret":v.get("retention_vs_control"),"pass":v.get("gate",{}).get("screen_pass")} for k,v in configs.items() if k!="17CE_VCE_C04_CONTROL"},"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
