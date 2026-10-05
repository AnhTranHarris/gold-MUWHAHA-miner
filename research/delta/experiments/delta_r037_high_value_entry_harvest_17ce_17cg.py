"""DELTA R037 high-value entry source harvest 17CE-17CG.

Preregistered Stage-A source screens:
17CE M5 MetaQuotes Kumo+AO; 17CF M1 EMA13/50+OBV reclaim;
17CG M5 MetaQuotes Darvas entry grammar. Completed bars only.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
DAY=86400000;HOUR=3600000;MIN=60000;TICK=10;SCALE=1000;END=1768737600000
US=1772953200000;UK=1774746000000;P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="248b3628ef3d3a357ff4272286e48292f4490f34"
MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30

def sh(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def atomic(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);q=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
   q=f.name;json.dump(x,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(q,p);q=None
 finally:
  if q:
   try:os.unlink(q)
   except FileNotFoundError:pass
def sess(t):
 tod=t%DAY;ls=np.where(t>=UK,7,8)*HOUR;le=ls+30600000;ns=np.where(t>=US,12,13)*HOUR;ne=ns+32400000
 il=(tod>=ls)&(tod<le);ny=(tod>=ns)&(tod<ne)
 return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)
def p75(t,a,b):
 sp=P75[sess(t)]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)
def bars(t,a,b,tf):
 mid=((a.astype(np.int64)+b.astype(np.int64))//2);mid=((mid+5)//10)*10;buck=t//tf
 st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*tf).astype(np.int64),"o":mid[st],"h":np.maximum.reduceat(mid,st),"l":np.minimum.reduceat(mid,st),"c":mid[en-1],"v":(en-st).astype(np.int64)}
def sma(x,n):
 out=np.full(len(x),np.nan,np.float64)
 if len(x)>=n:
  cs=np.r_[0.,np.cumsum(x,dtype=np.float64)];out[n-1:]=(cs[n:]-cs[:-n])/n
 return out
def ema(x,n):
 out=np.empty(len(x),np.float64)
 if not len(x):return out
 a=2./(n+1.);out[0]=float(x[0])
 for i in range(1,len(x)):out[i]=a*float(x[i])+(1-a)*out[i-1]
 return out
def atr14(b):
 h,l,c=b["h"],b["l"],b["c"];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 return sma(tr,14)
def ti(t,e):
 j=int(np.searchsorted(t,int(e),side="left"));return j if j<len(t) else -1
def midrange(h,l,n):
 out=np.full(len(h),np.nan,np.float64)
 for i in range(n-1,len(h)):out[i]=(float(np.max(h[i-n+1:i+1]))+float(np.min(l[i-n+1:i+1])))/2.
 return out
def kumo(t,b):
 h,l,c,e=b["h"],b["l"],b["c"],b["end"];med=(h+l)/2.;ten=midrange(h,l,8);kij=midrange(h,l,29);sb=midrange(h,l,34);sa=(ten+kij)/2.;ao=sma(med,5)-sma(med,34)
 ix=[];sd=[]
 for i in range(34,len(c)):
  if np.isnan(sa[i]) or np.isnan(sb[i]) or np.isnan(ao[i-1]) or np.isnan(ao[i]):continue
  s=1 if ao[i]>0 and ao[i-1]<0 and sa[i]<sb[i] and c[i]>sa[i] and c[i]>sb[i] else (-1 if ao[i]<0 and ao[i-1]>0 and sa[i]>sb[i] and c[i]<sa[i] and c[i]<sb[i] else 0)
  if s:
   j=ti(t,e[i])
   if j>=0:ix.append(j);sd.append(s)
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8)
def obv(v,c):
 x=np.zeros(len(c),np.float64)
 for i in range(1,len(c)):x[i]=x[i-1]+(v[i] if c[i]>c[i-1] else (-v[i] if c[i]<c[i-1] else 0))
 return x
def ny(e):
 tod=(int(e)-1)%DAY;wd=((int(e)-1)//DAY+3)%7
 return wd not in (0,5,6) and 14*HOUR+30*MIN<=tod<16*HOUR
def emaobv(t,b):
 c,l,h,e,v=b["c"],b["l"],b["h"],b["end"],b["v"];e13,e50=ema(c,13),ema(c,50);o=obv(v,c);oe=ema(o,20);ix=[];sd=[];state=0
 for i in range(50,len(c)):
  if not ny(e[i]):state=0;continue
  if e13[i]>e50[i]:
   if c[i]<e13[i] and l[i]>e50[i] and c[i]>e50[i]:state=1
   elif state==1 and c[i]>e13[i] and o[i]>oe[i]:
    j=ti(t,e[i])
    if j>=0:ix.append(j);sd.append(1)
    state=0
   elif c[i]<=e50[i]:state=0
  elif e13[i]<e50[i]:
   if c[i]>e13[i] and h[i]<e50[i] and c[i]<e50[i]:state=-1
   elif state==-1 and c[i]<e13[i] and o[i]<oe[i]:
    j=ti(t,e[i])
    if j>=0:ix.append(j);sd.append(-1)
    state=0
   elif c[i]>=e50[i]:state=0
  else:state=0
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8)
def darvas(t,b):
 h,l,c,e,v=b["h"],b["l"],b["c"],b["end"],b["v"];atr=atr14(b);ix=[];sd=[];state=0;bull=True;top=bottom=conf=nb=0;avg=0.;d={"extremes":0,"boxes":0,"breakouts":0,"narrow_resets":0}
 for i in range(50,len(c)):
  if np.isnan(atr[i]):continue
  if state==0:
   ph=np.max(h[i-49:i]);pl=np.min(l[i-49:i])
   if h[i]>ph:bull=True;top=int(h[i]);bottom=int(l[i]);conf=0;avg=float(v[i]);nb=1;state=1;d["extremes"]+=1
   elif l[i]<pl:bull=False;top=int(h[i]);bottom=int(l[i]);conf=0;avg=float(v[i]);nb=1;state=1;d["extremes"]+=1
   continue
  if state==1:
   nb+=1;avg=(avg*(nb-1)+float(v[i]))/nb
   if bull:
    if l[i]<bottom:bottom=int(l[i])
    if h[i]>top:top=int(h[i]);conf=0;continue
    conf+=1
   else:
    if h[i]>top:top=int(h[i])
    if l[i]<bottom:bottom=int(l[i]);conf=0;continue
    conf+=1
   if conf>=3:
    if top-bottom<.5*atr[i]:d["narrow_resets"]+=1;state=0;continue
    state=2;d["boxes"]+=1
   continue
  if state==2:
   s=0
   if float(v[i])>=1.3*avg:
    if bull and c[i]>top:s=1
    elif (not bull) and c[i]<bottom:s=-1
   if s:
    j=ti(t,e[i])
    if j>=0:ix.append(j);sd.append(s);d["breakouts"]+=1
    state=0
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8),d
@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10
@njit(cache=True)
def ev(idx,side,t,ask,bid):
 busy=-1;tr=bs=sr=dn=lg=sh=w=st=mh=en=0;gp=gl=net=0.;days=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;sh+=s<0;days[dn]=int(t[i]//DAY);dn+=1;entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]);bb=int(bid[k]);last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if int(t[k])//1000-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else (entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else (entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if (s>0 and ns>stop) or (s<0 and ns<stop):stop=ns
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
def met(idx,sd,t,ask,bid):
 q=ev(idx,sd,t,ask,bid);m={"signals":int(idx.size),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
 g={"minimum_trades_20":m["trades"]>=20,"minimum_distinct_days_5":m["distinct_days"]>=5,"direct_net_min_minus_1":m["direct_net_usd"]>=-1.};g["screen_pass"]=bool(all(g.values()));g["strong_pass"]=bool(g["screen_pass"] and m["direct_net_usd"]>=0);return m,g
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();hs=sh(a.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[d.timestamp_ms_utc<END];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ask,bid=p75(t,ar,br);b1=bars(t,ar,br,60000);b5=bars(t,ar,br,300000)
 i1,s1=kumo(t,b5);i2,s2=emaobv(t,b1);i3,s3,dd=darvas(t,b5);sets={"17CE_KUMO_AO_M5":(i1,s1),"17CF_EMA_OBV_RECLAIM_M1_NY":(i2,s2),"17CG_DARVAS_M5":(i3,s3)};cfg={};surv=[]
 for n,(ix,sd) in sets.items():
  m,g=met(ix,sd,t,ask,bid);cfg[n]={"metrics":m,"gate":g}
  if n=="17CG_DARVAS_M5":cfg[n]["diagnostics"]=dd
  if g["screen_pass"]:surv.append(n)
 out={"schema":"delta-r037-high-value-entry-source-harvest-17ce-17cg-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_HIGH_VALUE_ENTRY_SOURCE_HARVEST_17CE_17CG","parent_checkpoint":"R037_BREAKER_BLOCK_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CC_17CD","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"execution_surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,"configs":cfg,"finding":{"survivors":surv,"decision":"ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "RETIRE_BATCH_NO_EXECUTABLE_SURVIVOR","next":"R037_HIGH_VALUE_ENTRY_SURVIVOR_INDEPENDENT_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False}
 atomic(a.output,out);print(json.dumps({"configs":{k:{"signals":v["metrics"]["signals"],"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"]} for k,v in cfg.items()},"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
