"""R037 source-default Quasimodo entry screen 17CA-17CB.

Reconstructs the July-2026 MetaQuotes Part-49 QM entry grammar on fixed M5/M15
lanes, then evaluates entries under frozen DELTA P75 30-second economics.
No source-EA exit/risk management is imported. No tuning, August, or MQL5.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DAY=86_400_000;HOUR=3_600_000;TICK=10;SCALE=1000;END=1_768_737_600_000
US_DST=1_772_953_200_000;UK_DST=1_774_746_000_000;P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="15155390a68b3e3eb53147737f735b34083d0030"
LOOK=5;MAX_WAIT=30;TREND_PIVOTS=2
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
 il=(tod>=ls)&(tod<le);ny=(tod>=ns)&(tod<ne);return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)

def p75(t,a,b):
 sp=P75[sess(t)]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,a,b,tf):
 mid=(a.astype(np.int64)+b.astype(np.int64))//2;mid=((mid+5)//10)*10;buck=t//tf
 st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*tf).astype(np.int64),"o":mid[st].astype(np.int64),
         "h":np.maximum.reduceat(mid,st).astype(np.int64),"l":np.minimum.reduceat(mid,st).astype(np.int64),
         "c":mid[en-1].astype(np.int64)}

def qm_signals(t,b):
 e,h,l,c=b["end"],b["h"],b["l"],b["c"];n=len(c)
 piv=[];idx=[];side=[];days=[]
 active=None;last_bos=-1;last_shoulder=-1
 d={"bars":n,"confirmed_highs":0,"confirmed_lows":0,"same_type_replacements":0,
    "alternating_appends":0,"bearish_patterns":0,"bullish_patterns":0,"prior_trend_rejects":0,
    "shared_shoulder_rejects":0,"armed":0,"superseded":0,"expired":0,"head_invalidations":0,
    "retrace_entries":0}

 def trend_ok(is_bull,shoulder_index):
  if shoulder_index-TREND_PIVOTS<0:return False
  earlier=piv[shoulder_index-TREND_PIVOTS]
  later=piv[shoulder_index]
  # With default TrendPivots=2 and alternating pivots, these are same type.
  return later[1]<earlier[1] if is_bull else later[1]>earlier[1]

 def check_pattern(reveal_i):
  nonlocal active,last_bos,last_shoulder
  if len(piv)<4:return
  sidx=len(piv)-4
  shoulder,leg,head,bos=piv[-4],piv[-3],piv[-2],piv[-1]
  is_bull=None
  if shoulder[0]==1 and leg[0]==-1 and head[0]==1 and bos[0]==-1 and head[1]>shoulder[1] and leg[1]<shoulder[1] and bos[1]<leg[1]:
   is_bull=False;d["bearish_patterns"]+=1
  elif shoulder[0]==-1 and leg[0]==1 and head[0]==-1 and bos[0]==1 and head[1]<shoulder[1] and leg[1]>shoulder[1] and bos[1]>leg[1]:
   is_bull=True;d["bullish_patterns"]+=1
  if is_bull is None:return
  if bos[2]==last_bos:return
  if shoulder[2]==last_shoulder:
   d["shared_shoulder_rejects"]+=1;return
  if not trend_ok(is_bull,sidx):
   d["prior_trend_rejects"]+=1;return
  if active is not None:d["superseded"]+=1
  active={"bull":is_bull,"line":shoulder[1],"head":head[1],"arm_i":reveal_i,"bos_k":bos[2],"shoulder_k":shoulder[2]}
  last_bos=bos[2];last_shoulder=shoulder[2];d["armed"]+=1

 def add_pivot(typ,price,k,reveal_i):
  if not piv:
   piv.append((typ,int(price),int(k)));d["alternating_appends"]+=1;check_pattern(reveal_i);return
  if piv[-1][0]==typ:
   more=(typ==1 and price>piv[-1][1]) or (typ==-1 and price<piv[-1][1])
   if more:
    piv[-1]=(typ,int(price),int(k));d["same_type_replacements"]+=1;check_pattern(reveal_i)
   return
  piv.append((typ,int(price),int(k)));d["alternating_appends"]+=1
  if len(piv)>24:del piv[:len(piv)-24]
  check_pattern(reveal_i)

 for i in range(2*LOOK,n):
  # First manage any setup armed on an earlier completed bar.
  if active is not None and i>active["arm_i"]:
   if i-active["arm_i"]>MAX_WAIT:
    active=None;d["expired"]+=1
   else:
    close=int(c[i])
    if active["bull"]:
     if close<active["head"]:active=None;d["head_invalidations"]+=1
     elif close<=active["line"]:
      j=int(np.searchsorted(t,int(e[i]),side="left"))
      if j<len(t):idx.append(j);side.append(1);days.append((int(e[i])-1)//DAY);d["retrace_entries"]+=1
      active=None
    else:
     if close>active["head"]:active=None;d["head_invalidations"]+=1
     elif close>=active["line"]:
      j=int(np.searchsorted(t,int(e[i]),side="left"))
      if j<len(t):idx.append(j);side.append(-1);days.append((int(e[i])-1)//DAY);d["retrace_entries"]+=1
      active=None

  # Source default LOOK=5: candidate k is known only after five closed bars to its right.
  k=i-LOOK
  hh=int(h[k]);ll=int(l[k]);ph=True;pl=True
  for j in range(1,LOOK+1):
   if int(h[k-j])>=hh or int(h[k+j])>=hh:ph=False
   if int(l[k-j])<=ll or int(l[k+j])<=ll:pl=False
   if not ph and not pl:break
  # Article handles high then low if a rare bar qualifies as both.
  if ph:d["confirmed_highs"]+=1;add_pivot(1,hh,k,i)
  if pl:d["confirmed_lows"]+=1;add_pivot(-1,ll,k,i)

 return np.asarray(idx,np.int64),np.asarray(side,np.int8),np.asarray(days,np.int64),d

@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10
@njit(cache=True)
def ev(idx,side,days,t,ask,bid):
 busy=-1;tr=bs=sr=nd=lg=sh=w=0;gp=gl=net=0.;st=mh=en=0;u=0;used=np.empty(idx.size,np.int64)
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
  ex=raw-.01;net+=ex-.01;w+=ex>1e-12
  if raw>0:gp+=ex
  else:gl+=ex
  if reason==0:st+=1
  elif reason==1:mh+=1
  else:en+=1
  busy=last
 if u:
  x=np.sort(used[:u]);nd=1
  for k in range(1,x.size):nd+=x[k]!=x[k-1]
 return tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();hs=sh(a.source)
 if hs!=SHA:raise SystemExit("canonical January SHA mismatch: "+hs)
 d=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[d.timestamp_ms_utc<END];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology/tick mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ask,bid=p75(t,ar,br);cfg={}
 for name,tf in (("17CA_M5_QM_SOURCE_DEFAULT",300_000),("17CB_M15_QM_SOURCE_DEFAULT",900_000)):
  ix,sd,dy,diag=qm_signals(t,bars(t,ar,br,tf));q=ev(ix,sd,dy,t,ask,bid)
  m={"signals":int(ix.size),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
  gate={"minimum_trades_20":m["trades"]>=20,"minimum_distinct_days_5":m["distinct_days"]>=5,"nonnegative_direct_net":m["direct_net_usd"]>=0};gate["screen_pass"]=all(gate.values())
  cfg[name]={"timeframe_ms":tf,"metrics":m,"gate":gate,"diagnostics":diag}
 surv=[k for k,v in cfg.items() if v["gate"]["screen_pass"]]
 out={"schema":"delta-r037-quasimodo-source-default-stage-a-17ca-17cb-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_QUASIMODO_SOURCE_DEFAULT_STAGE_A_SCREEN_CHECKPOINT_17CA_17CB","family":"R037-QM-v1","parent_checkpoint":"R037_SWEEP_IFVG_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17BZ","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"source_defaults":{"swing_lookback_each_side":LOOK,"entry_buffer_points":0,"wait_for_rejection_close":False,"max_wait_bars":MAX_WAIT,"skip_shared_shoulder":True,"require_prior_trend":True,"trend_pivots":TREND_PIVOTS},"configs":cfg,"finding":{"survivors":surv,"decision":"ADVANCE_QM_SURVIVOR" if surv else "RETIRE_QM_NO_STAGE_A_SURVIVOR","next":"R037_QUASIMODO_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"numeric_retuning":False,"august_accessed":False,"mql5_authorized":False}
 atomic(a.output,out);print(json.dumps({"configs":{k:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"]} for k,v in cfg.items()},"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
