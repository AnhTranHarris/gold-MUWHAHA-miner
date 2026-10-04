"""DELTA R037 XAUUSD M5 ATR-qualified golden-pocket impulse retrace entry screen 17BW."""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
DAY=86_400_000;HOUR=3_600_000;TICK=10;SCALE=1000;END=1_768_737_600_000
US_DST=1_772_953_200_000;UK_DST=1_774_746_000_000;P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5";PREREG="48e0ce12f2c7bebb23f0fa3c5f7b882099f84dbc"
PIV=3;ATR_LEN=14;MIN_IMP=2.5;RETRACE=.705;VALID=15;TF=300_000
MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30
def sh(p):
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
 il=(tod>=ls)&(tod<le);iny=(tod>=ns)&(tod<ne);return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)
def surface(t,a,b):
 sp=P75[sess(t)]*TICK;m2=a.astype(np.int64)+b.astype(np.int64);bid=((m2-sp+TICK)//(2*TICK))*TICK;return (bid+sp).astype(np.int64),bid.astype(np.int64)
def bars(t,a,b):
 mid=(a.astype(np.int64)+b.astype(np.int64))//2;mid=((mid+5)//10)*10;buck=t//TF;st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((buck[st]+1)*TF).astype(np.int64),"o":mid[st].astype(np.int64),"h":np.maximum.reduceat(mid,st).astype(np.int64),"l":np.minimum.reduceat(mid,st).astype(np.int64),"c":mid[en-1].astype(np.int64)}
def atr(b):
 h,l,c=b["h"],b["l"],b["c"];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 out=np.full(len(tr),np.nan);cs=np.r_[0.,np.cumsum(tr)]
 if len(tr)>=ATR_LEN:out[ATR_LEN-1:]=(cs[ATR_LEN:]-cs[:-ATR_LEN])/ATR_LEN
 return out
def signals(t,b):
 n=len(b["end"]);aa=atr(b);ix=[];si=[];dy=[];last_type=0;last_price=0;last_k=-1;pending=False;ps=0;entry=0.;expiry=-1
 d={"confirmed_highs":0,"confirmed_lows":0,"same_type_supersedes":0,"opposite_legs":0,"qualified_impulses":0,"unqualified_legs":0,"pending_superseded":0,"expired":0,"fills":0}
 for i in range(max(ATR_LEN-1,2*PIV),n):
  k=i-PIV;typ=0;price=0
  if k>=PIV and k+PIV<n:
   hh=int(b["h"][k]);ll=int(b["l"][k]);is_hi=all(hh>int(b["h"][k-j]) and hh>int(b["h"][k+j]) for j in range(1,PIV+1));is_lo=all(ll<int(b["l"][k-j]) and ll<int(b["l"][k+j]) for j in range(1,PIV+1))
   if is_hi and is_lo:typ=1 if b["c"][k]<b["o"][k] else -1;price=hh if typ==1 else ll
   elif is_hi:typ=1;price=hh
   elif is_lo:typ=-1;price=ll
  if typ:
   if typ>0:d["confirmed_highs"]+=1
   else:d["confirmed_lows"]+=1
   if last_type==typ:
    more=(typ>0 and price>last_price) or (typ<0 and price<last_price)
    if more:last_price=price;last_k=k;d["same_type_supersedes"]+=1
   elif last_type!=0:
    d["opposite_legs"]+=1;av=float(aa[i]);rng=abs(price-last_price)
    if np.isfinite(av) and av>0 and rng>=MIN_IMP*av:
     side=1 if last_type<0 and typ>0 else -1
     lo=min(last_price,price);hi=max(last_price,price);entry=(hi-RETRACE*(hi-lo)) if side>0 else (lo+RETRACE*(hi-lo))
     if pending:d["pending_superseded"]+=1
     pending=True;ps=side;expiry=i+VALID;d["qualified_impulses"]+=1
    else:d["unqualified_legs"]+=1
    last_type=typ;last_price=price;last_k=k
   else:last_type=typ;last_price=price;last_k=k
  if pending:
   if i>expiry:pending=False;d["expired"]+=1
   elif int(b["l"][i])<=entry<=int(b["h"][i]):
    j=int(np.searchsorted(t,int(b["end"][i]),side="left"))
    if j<len(t):ix.append(j);si.append(ps);dy.append((int(b["end"][i])-1)//DAY);d["fills"]+=1
    pending=False
 return np.asarray(ix,np.int64),np.asarray(si,np.int8),np.asarray(dy,np.int64),d
@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10
@njit(cache=True)
def ev(idx,side,days,t,ask,bid):
 busy=-1;tr=bs=sr=nd=lg=sh=wins=0;gp=gl=net=0.;st=mh=en=0;u=0;used=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;sh+=s<0;used[u]=days[z];u+=1;entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for q in range(i+1,t.size):
   aa=int(ask[q]);bb=int(bid[q]);last=q
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if int(t[q])//1000-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else (entry-aa))/SCALE;reason=1;break
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
  for q in range(1,x.size):nd+=x[q]!=x[q-1]
 return tr,bs,sr,nd,lg,sh,wins,gp,gl,net,st,mh,en
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args();hs=sh(x.source)
 if hs!=SHA:raise SystemExit("SHA mismatch "+hs)
 d=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);d=d[d.timestamp_ms_utc<END];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A mismatch")
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ask,bid=surface(t,ar,br);ix,si,dy,diag=signals(t,bars(t,ar,br));q=ev(ix,si,dy,t,ask,bid)
 m={"signals":int(ix.size),"trades":int(q[0]),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),"official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),"gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),"exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
 gate={"minimum_trades_20":m["trades"]>=20,"minimum_distinct_days_5":m["distinct_days"]>=5,"nonnegative_direct_net":m["direct_net_usd"]>=0};gate["screen_pass"]=all(gate.values())
 out={"schema":"delta-r037-fib-golden-pocket-retrace-stage-a-17bw-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN","unit":"R037_FIB_GOLDEN_POCKET_IMPULSE_RETRACE_STAGE_A_SCREEN_CHECKPOINT_17BW","parent_checkpoint":"R037_STRUCTURE_ANCHORED_VWAP_FAST_RETEST_STAGE_A_SCREEN_CHECKPOINT_17BU_17BV","prereg_commit":PREREG,"source_sha256":hs,"stage_a_ticks":int(len(t)),"source_defaults":{"timeframe":"M5","pivot_length":PIV,"atr_length":ATR_LEN,"minimum_impulse_atr":MIN_IMP,"entry_retracement":RETRACE,"validity_bars":VALID},"metrics":m,"gate":gate,"diagnostics":diag,"finding":{"decision":"ADVANCE_INDEPENDENT_LATER_JAN_VALIDATION" if gate["screen_pass"] else "RETIRE_FIB_GOLDEN_POCKET_NO_STAGE_A_SURVIVOR","next":"R037_FIB_GOLDEN_POCKET_INDEPENDENT_LATER_JAN_VALIDATION" if gate["screen_pass"] else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},"august_accessed":False,"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"metrics":m,"gate":gate,"diagnostics":diag,"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
