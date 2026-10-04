"""DELTA R037 Structure-Anchored VWAP Fast retest Stage-A screen 17BU-17BV."""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
DAY=86_400_000;HOUR=3_600_000;TICK=10;SCALE=1000;END=1_768_737_600_000
US_DST=1_772_953_200_000;UK_DST=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="79f607d93c476c3df815a1d13b19aa3d3d065de8"
LOOK=30;MED=50;CAP=4.0;AWAY=5;TOUCH=.25;ATR_LEN=13;MAX_LEG=4000
MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30
CONFIGS=(("17BU_C01_SAVWAP_FAST_M1",60_000),("17BV_C02_SAVWAP_FAST_M5",300_000))
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def atomic(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);n=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
   n=f.name;json.dump(o,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(n,p);n=None
 finally:
  if n:
   try:os.unlink(n)
   except FileNotFoundError:pass
def sess(t):
 tod=t%DAY;ls=np.where(t>=UK_DST,7,8)*HOUR;le=ls+30_600_000;ns=np.where(t>=US_DST,12,13)*HOUR;ne=ns+32_400_000
 il=(tod>=ls)&(tod<le);iny=(tod>=ns)&(tod<ne)
 return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)
def surface(t,a,b):
 sp=P75[sess(t)]*TICK;m2=a.astype(np.int64)+b.astype(np.int64);bid=((m2-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)
def bars(t,a,b,tf):
 mid=((a.astype(np.int64)+b.astype(np.int64))//2);mid=((mid+5)//10)*10
 buck=t//tf;st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*tf).astype(np.int64),"o":mid[st].astype(np.int64),"h":np.maximum.reduceat(mid,st).astype(np.int64),"l":np.minimum.reduceat(mid,st).astype(np.int64),"c":mid[en-1].astype(np.int64),"v":(en-st).astype(np.float64)}
def atr(b):
 h,l,c=b["h"],b["l"],b["c"];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 out=np.full(len(tr),np.nan);cs=np.r_[0.,np.cumsum(tr)]
 if len(tr)>=ATR_LEN:out[ATR_LEN-1:]=(cs[ATR_LEN:]-cs[:-ATR_LEN])/ATR_LEN
 return out
def signals(t,b):
 n=len(b["end"]);aa=atr(b);idx=[];side=[];days=[]
 leg=0;anchor=-1;away=0;sw=sp=sp2=0.;diag={"anchors_bull":0,"anchors_bear":0,"same_type_refresh":0,"flips":0,"away_bars":0,"touches":0,"qualified_retests":0,"zero_sigma_fallbacks":0}
 for i in range(max(LOOK,MED),n):
  ph=np.max(b["h"][i-LOOK:i]);pl=np.min(b["l"][i-LOOK:i]);newhi=b["h"][i]>ph;newlo=b["l"][i]<pl
  typ=0
  if newhi and newlo:typ=1 if b["c"][i]>=b["o"][i] else -1
  elif newlo:typ=1
  elif newhi:typ=-1
  if typ:
   if leg==typ:diag["same_type_refresh"]+=1
   elif leg!=0:diag["flips"]+=1
   leg=typ;anchor=i;away=0;sw=sp=sp2=0.
   if leg>0:diag["anchors_bull"]+=1
   else:diag["anchors_bear"]+=1
  if leg==0 or anchor<0:continue
  if i-anchor>=MAX_LEG:leg=0;anchor=-1;away=0;continue
  med=float(np.median(b["v"][max(0,i-MED):i]))
  w=float(b["v"][i]);w=min(w,CAP*med) if med>0 else 1.0
  px=(float(b["h"][i])+float(b["l"][i]))/2.0
  sw+=w;sp+=px*w;sp2+=px*px*w
  if sw<=0:continue
  vw=sp/sw;var=max(sp2/sw-vw*vw,0.0);sig=var**0.5
  if sig>0:tol=TOUCH*sig
  else:
   av=float(aa[i]);tol=.1*av if np.isfinite(av) else TICK;diag["zero_sigma_fallbacks"]+=1
  touch=(b["l"][i]<=vw+tol and b["h"][i]>=vw-tol)
  outside=(b["l"][i]>vw+tol) if leg>0 else (b["h"][i]<vw-tol)
  committed=away
  if touch:
   diag["touches"]+=1
   if committed>=AWAY and i>anchor:
    j=int(np.searchsorted(t,int(b["end"][i]),side="left"))
    if j<len(t):idx.append(j);side.append(leg);days.append((int(b["end"][i])-1)//DAY);diag["qualified_retests"]+=1
   away=0
  elif outside:
   away+=1;diag["away_bars"]+=1
 return np.asarray(idx,np.int64),np.asarray(side,np.int8),np.asarray(days,np.int64),diag
@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10
@njit(cache=True)
def evalx(idx,side,days,t,ask,bid):
 busy=-1;tr=bs=sr=nd=lg=sh=wins=0;gp=gl=net=0.;st=mh=en=0;used=np.empty(idx.size,np.int64);u=0
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;sh+=s<0;used[u]=days[z];u+=1;entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]);bb=int(bid[k]);last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if int(t[k])//1000-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else (entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else (entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if (s>0 and ns>stop) or (s<0 and ns<stop):stop=ns
  ex=raw-.01;net+=ex-.01;wins+=ex>1e-12
  if raw>0:gp+=ex
  else:gl+=ex
  if reason==0:st+=1
  elif reason==1:mh+=1
  else:en+=1
  busy=last
 if u:
  x=np.sort(used[:u]);nd=1
  for k in range(1,x.size):nd+=x[k]!=x[k-1]
 return tr,bs,sr,nd,lg,sh,wins,gp,gl,net,st,mh,en
def metric(idx,s,d,t,a,b):
 x=evalx(idx,s,d,t,a,b);m={"signals":int(idx.size),"trades":int(x[0]),"busy_skips":int(x[1]),"spread_rejects":int(x[2]),"distinct_days":int(x[3]),"long":int(x[4]),"short":int(x[5]),"official_wins":int(x[6]),"gross_profit":round(float(x[7]),2),"gross_loss":round(float(x[8]),2),"direct_net_usd":round(float(x[9]),2),"exit_reasons":{"STOP":int(x[10]),"MAX_HOLD":int(x[11]),"END":int(x[12])}}
 g={"minimum_trades_20":m["trades"]>=20,"minimum_distinct_days_5":m["distinct_days"]>=5,"nonnegative_direct_net":m["direct_net_usd"]>=0};g["screen_pass"]=all(g.values());return m,g
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);q=ap.parse_args()
 hs=sha(q.source)
 if hs!=SHA:raise SystemExit("canonical SHA mismatch "+hs)
 d=pd.read_csv(q.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[d.timestamp_ms_utc<END];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ask,bid=surface(t,ar,br);res={};sur=[]
 for name,tf in CONFIGS:
  ix,si,dy,di=signals(t,bars(t,ar,br,tf));m,g=metric(ix,si,dy,t,ask,bid);res[name]={"timeframe_ms":tf,"metrics":m,"gate":g,"diagnostics":di}
  if g["screen_pass"]:sur.append(name)
 out={"schema":"delta-r037-savwap-fast-retest-stage-a-17bu-17bv-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_STRUCTURE_ANCHORED_VWAP_FAST_RETEST_STAGE_A_SCREEN_CHECKPOINT_17BU_17BV","parent_checkpoint":"R037_AVPBR_SUPPLY_CALIBRATED_STAGE_A_SCREEN_CHECKPOINT_17BR_17BT","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"source_defaults":{"fast_lookback":LOOK,"price_source":"hl2","weighting":"cumulative","volume_clamp_multiple":CAP,"volume_median_lookback":MED,"away_bars":AWAY,"touch_tolerance_sigma":TOUCH,"zero_sigma_atr_fallback":0.1,"max_leg_bars":MAX_LEG},"volume_proxy":"Dukascopy tick count per derived bar","configs":res,"finding":{"survivors":sur,"decision":"ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION" if sur else "RETIRE_SAVWAP_FAST_NO_STAGE_A_SURVIVOR","next":"R037_SAVWAP_SURVIVOR_INDEPENDENT_LATER_JAN_VALIDATION" if sur else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"august_accessed":False,"mql5_authorized":False}
 atomic(q.output,out);print(json.dumps({"configs":{k:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"],"diag":v["diagnostics"]} for k,v in res.items()},"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
