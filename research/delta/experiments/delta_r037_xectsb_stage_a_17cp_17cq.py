"""R037 XECTSB 17CP-17CQ: causal EMA9/21 cross->touch->touch-break->swing-break."""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile,time
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
D=86400000;H=3600000;T=10;S=1000;START=1767225600000;END=1768737600000
USD=1772953200000;UKD=1774746000000;P=np.array([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5";PR="2d5bc884d77e9ae6b327429ce28a0784928de925"
MS=250;STOP=300;TA=100;TD=30;MH=30
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
 x=t%D;ls=np.where(t>=UKD,7,8)*H;ns=np.where(t>=USD,12,13)*H
 l=(x>=ls)&(x<ls+30600000);n=(x>=ns)&(x<ns+32400000)
 return np.where(l&n,2,np.where(l,1,np.where(n,3,0))).astype(np.int8)
def p75(t,a,b):
 sp=P[sess(t)]*T;m=a+b;bid=((m-sp+T)//(2*T))*T
 return (bid+sp).astype(np.int64),bid.astype(np.int64)
def bars(t,b,tf):
 q=t//tf;st=np.r_[0,np.flatnonzero(q[1:]!=q[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"e":((q[st]+1)*tf).astype(np.int64),"c":b[en-1],"h":np.maximum.reduceat(b,st),"l":np.minimum.reduceat(b,st)}
def ema(x,n):
 y=np.full(len(x),np.nan);k=2/(n+1)
 if len(x)<n:return y
 y[n-1]=np.mean(x[:n])
 for i in range(n,len(x)):y[i]=k*x[i]+(1-k)*y[i-1]
 return y
def sigs(t,a,b,z):
 c,h,l,e=z["c"],z["h"],z["l"],z["e"];f=ema(c,9);s=ema(c,21)
 ix=[];sd=[];g={"crosses":0,"bull":0,"bear":0,"resets":0,"touches":0,"bots":0,"enters":0,"spread_rejects":0}
 st=0;side=sw=th=tl=ck=tk=bk=0
 for k in range(21,len(c)):
  if e[k]>END:break
  up=f[k-1]<=s[k-1] and f[k]>s[k];dn=f[k-1]>=s[k-1] and f[k]<s[k]
  if up or dn:
   if st in (1,2,3):g["resets"]+=1
   side=1 if up else -1;sw=int(np.max(h[k-10:k]) if side>0 else np.min(l[k-10:k]));st=1;ck=k;g["crosses"]+=1;g["bull" if side>0 else "bear"]+=1;continue
  if st==1 and k>ck:
   if l[k]<=f[k]<=h[k]:th=int(h[k]);tl=int(l[k]);tk=k;st=2;g["touches"]+=1
   continue
  if st==2 and k>tk:
   if (side>0 and h[k]>th) or (side<0 and l[k]<tl):bk=k;st=3;g["bots"]+=1
   continue
  if st==3 and k>bk and ((side>0 and c[k]>sw) or (side<0 and c[k]<sw)):
   j=int(np.searchsorted(t,int(e[k]),side="left"))
   if j<len(t) and t[j]<END and a[j]-b[j]<=MS:ix.append(j);sd.append(side);g["enters"]+=1
   elif j<len(t):g["spread_rejects"]+=1
   st=4
 return np.array(ix,np.int64),np.array(sd,np.int8),g
@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10
@njit(cache=True)
def ev(ix,sd,t,a,b):
 busy=-1;tr=bs=sr=nd=lg=ss=w=0;gp=gl=net=0.;stp=mh=en=0;u=0;days=np.empty(ix.size,np.int64)
 for z in range(ix.size):
  i=int(ix[z]);s=int(sd[z])
  if i<=busy:bs+=1;continue
  if a[i]-b[i]>MS:sr+=1;continue
  tr+=1;lg+=s>0;ss+=s<0;days[u]=t[i]//D;u+=1;entry=a[i] if s>0 else b[i];stop=qt(b[i]-STOP if s>0 else a[i]+STOP);sec=t[i]//1000;raw=0.;r=2;last=i
  for k in range(i+1,t.size):
   aa=a[k];bb=b[k];last=k
   if s>0 and bb<=stop:raw=(bb-entry)/S;r=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/S;r=0;break
   if t[k]//1000-sec>=MH:raw=((bb-entry) if s>0 else(entry-aa))/S;r=1;break
   fav=(bb-entry) if s>0 else(entry-aa)
   if fav>=TA:
    ns=qt(bb-TD if s>0 else aa+TD)
    if (s>0 and ns>stop) or (s<0 and ns<stop):stop=ns
  ed=raw-.01;net+=ed-.01;w+=ed>1e-12
  if raw>0:gp+=ed
  else:gl+=ed
  stp+=r==0;mh+=r==1;en+=r==2;busy=last
 if u:
  x=np.sort(days[:u]);nd=1
  for k in range(1,x.size):nd+=x[k]!=x[k-1]
 return tr,bs,sr,nd,lg,ss,w,gp,gl,net,stp,mh,en
def pack(ix,sd,t,a,b):
 q=ev(ix,sd,t,a,b);m={"signals":len(ix),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}};g={"minimum_trades_10":m["trades"]>=10,"minimum_distinct_days_5":m["distinct_days"]>=5,"direct_net_positive":m["direct_net_usd"]>0};g["screen_pass"]=all(g.values());return m,g
def main():
 st=time.monotonic();p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--output",type=Path,required=True);x=p.parse_args();hs=sh(x.source)
 if hs!=SHA:raise SystemExit("SHA mismatch")
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[(d.timestamp_ms_utc>=START)&(d.timestamp_ms_utc<END)];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit("chronology mismatch")
 a,b=p75(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64));cfg={}
 for n,tf in (("17CP_M5_EMA9_21_TOUCH_SWING10",300000),("17CQ_M15_EMA9_21_TOUCH_SWING10",900000)):
  ix,sd,di=sigs(t,a,b,bars(t,b,tf));m,g=pack(ix,sd,t,a,b);cfg[n]={"timeframe_ms":tf,"metrics":m,"gate":g,"diagnostics":di}
 surv=[n for n,v in cfg.items() if v["gate"]["screen_pass"]];surv.sort(key=lambda n:(cfg[n]["metrics"]["direct_net_usd"],cfg[n]["metrics"]["official_wins"],cfg[n]["metrics"]["trades"]),reverse=True)
 o={"schema":"delta-r037-xectsb-stage-a-17cp-17cq-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_XAUUSD_EMA_CROSS_TOUCH_SWING_BREAK_STAGE_A_SCREEN_CHECKPOINT_17CP_17CQ","family":"R037-XECTSB-v1","parent_checkpoint":"R037_VCE_RAW_RELEASE_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CO","prereg_commit":PR,"source_sha256":hs,"stage_a_ticks":len(t),"surface":"DUKAS_COINEXX_LIKE_P75","causal_same_bar_transitions":False,"configs":cfg,"finding":{"survivors":surv,"leader":surv[0] if surv else None,"decision":"ADVANCE_XECTSB_LEADER" if surv else "RETIRE_XECTSB_NO_STAGE_A_SURVIVOR","next":"R037_XECTSB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"post_result_rescue":False,"august_accessed":False,"mql5_authorized":False,"runtime_seconds":round(time.monotonic()-st,3)}
 atomic(x.output,o);print(json.dumps({"configs":{n:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"],"diag":v["diagnostics"]} for n,v in cfg.items()},"finding":o["finding"],"runtime_seconds":o["runtime_seconds"]},separators=(",",":")))
if __name__=="__main__":main()
