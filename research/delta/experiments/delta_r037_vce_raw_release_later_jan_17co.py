"""R037 unchanged VCE BB/KC raw-release independent later-January validation — 17CO.

The Stage-A control must exactly reproduce the preserved direct fingerprint before
the holdout result is allowed to persist.

Frozen source grammar:
- M5.
- prior completed bar: BB20/2.0 fully inside KC EMA20 +/-1.5 ATR20.
- current completed bar: squeeze releases and close is beyond current KC.
- no EMA150, queue-imbalance, session, side, momentum or retest filter.
- entry on first executable P75 tick after completed release bar.
- frozen 30-second execution.

Independent holdout:
- warmup data starts 2026-01-14 00:00 UTC.
- economic signals start 2026-01-18 12:00 UTC.
- economic signals end at the final January tick.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile,time
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DAY=86_400_000;HOUR=3_600_000;TICK=10;SCALE=1000;TF=300_000
JAN_START=1_767_225_600_000
HOLD_WARM=1_768_348_800_000
HOLD_START=1_768_737_600_000
FEB_START=1_769_904_000_000
US_DST=1_772_953_200_000;UK_DST=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="105243f7bede082a37012c85de75bb8f0f1c1c63"
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

def proposals(t,ask,bid,signal_start,end_exclusive):
 b=bars(t,bid);c=b["c"].astype(np.float64);m,sd=sma_std(b["c"],20);a=atr(b,20);e=ema(b["c"],20)
 bu=m+2*sd;bl=m-2*sd;ku=e+1.5*a;kl=e-1.5*a;sq=(bu<ku)&(bl>kl)
 ix=[];side=[];days=[];diag={"bars":len(c),"release":0,"breakout":0,"spread_reject":0,"prewindow_release":0}
 for k in range(20,len(c)):
  edge=int(b["end"][k])
  if edge>=end_exclusive:break
  if not(bool(sq[k-1]) and not bool(sq[k])):continue
  if edge<signal_start:
   diag["prewindow_release"]+=1;continue
  diag["release"]+=1
  s=1 if c[k]>ku[k] else(-1 if c[k]<kl[k] else 0)
  if not s:continue
  diag["breakout"]+=1
  i=int(np.searchsorted(t,edge,side="left"))
  if i>=len(t) or int(t[i])>=end_exclusive:continue
  if int(ask[i]-bid[i])>MAX_SPREAD:diag["spread_reject"]+=1;continue
  ix.append(i);side.append(s);days.append((edge-1)//DAY)
 return np.asarray(ix,np.int64),np.asarray(side,np.int8),np.asarray(days,np.int64),diag

@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10

@njit(cache=True)
def ev(idx,side,days,t,ask,bid,end_exclusive):
 busy=-1;tr=bs=sr=nd=lg=shrt=w=0;gp=gl=net=0.;st=mh=en=0;u=0;used=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;shrt+=s<0;used[u]=days[z];u+=1
  entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   if int(t[k])>=end_exclusive:break
   aa=int(ask[k]);bb=int(bid[k]);last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if int(t[k])//1000-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else(entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else(entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if(s>0 and ns>stop)or(s<0 and ns<stop):stop=ns
  if reason==2:
   raw=((int(bid[last])-entry) if s>0 else(entry-int(ask[last])))/SCALE
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

def run_slice(df,data_start,signal_start,end_exclusive):
 d=df[(df.timestamp_ms_utc>=data_start)&(df.timestamp_ms_utc<end_exclusive)]
 t=d.timestamp_ms_utc.to_numpy(np.int64)
 if not len(t) or np.any(t[1:]<t[:-1]):raise SystemExit("slice chronology failure")
 ask,bid=p75(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64))
 idx,side,days,diag=proposals(t,ask,bid,signal_start,end_exclusive)
 q=ev(idx,side,days,t,ask,bid,end_exclusive)
 m={"signals":int(idx.size),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
 return m,diag,int(len(t))

def main():
 started=time.monotonic();ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 hs=sh(x.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 d=d[(d.timestamp_ms_utc>=JAN_START)&(d.timestamp_ms_utc<FEB_START)]
 if np.any(d.timestamp_ms_utc.to_numpy(np.int64)[1:]<d.timestamp_ms_utc.to_numpy(np.int64)[:-1]):raise SystemExit("January chronology failure")
 ctrl,ctrl_diag,ctrl_ticks=run_slice(d,JAN_START,JAN_START,HOLD_START)
 if not(ctrl["trades"]==27 and ctrl["official_wins"]==20 and ctrl["distinct_days"]==11 and abs(ctrl["direct_net_usd"]-.71)<1e-9):
  raise SystemExit("Stage-A C03/C04 control mismatch: "+json.dumps({"metrics":ctrl,"diag":ctrl_diag},sort_keys=True))
 hold,hold_diag,hold_ticks=run_slice(d,HOLD_WARM,HOLD_START,FEB_START)
 gate={"minimum_trades_10":hold["trades"]>=10,"minimum_distinct_days_5":hold["distinct_days"]>=5,"direct_net_nonnegative":hold["direct_net_usd"]>=0}
 gate["validation_pass"]=all(gate.values())
 out={"schema":"delta-r037-vce-raw-release-later-jan-17co-v1","status":"COMPLETE_INDEPENDENT_LATER_JAN_VALIDATION","unit":"R037_VCE_RAW_RELEASE_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CO","candidate":"R037-VCE-C03_BBKC_RELEASE","parent_checkpoint":"R037_SQUEEZE_RANGE_BREAKOUT_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CM_17CN","prereg_commit":PREREG,"source_sha256":hs,"stage_a_control":{"metrics":ctrl,"diagnostics":ctrl_diag,"ticks":ctrl_ticks},"later_jan":{"warmup_start_ms":HOLD_WARM,"economic_start_ms":HOLD_START,"end_exclusive_ms":FEB_START,"metrics":hold,"diagnostics":hold_diag,"ticks":hold_ticks,"gate":gate},"finding":{"decision":"ADVANCE_VCE_RAW_RELEASE_MONTHLY_VALIDATION" if gate["validation_pass"] else "RETIRE_VCE_RAW_RELEASE_AFTER_LATER_JAN_FAIL","next":"R037_VCE_RAW_RELEASE_FEB_JUL_MONTH_BY_MONTH_VALIDATION" if gate["validation_pass"] else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"post_result_rescue":False,"august_accessed":False,"mql5_authorized":False,"runtime_seconds":round(time.monotonic()-started,3)}
 atomic(x.output,out);print(json.dumps({"control":ctrl,"holdout":hold,"gate":gate,"finding":out["finding"],"runtime_seconds":out["runtime_seconds"]},separators=(",",":")))

if __name__=="__main__":main()
