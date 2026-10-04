"""DELTA R037 IRH Stage-A official producer — Checkpoint 17AI.

Frozen entry source: R037-VCE-C03_BBKC_RELEASE from checkpoint 17A.
Frozen initial-hold refinement: at 3/5/10 seconds, if maximum executable favorable
excursion since entry has never exceeded zero, exit immediately. Protective stop
has priority. Otherwise continue the original DELTA stop/trail/30-second lifecycle.

No entry retuning, session/side/weekday filter, mature-exit tuning, August, or MQL5.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

DAY=86_400_000; TICK=10; SCALE=1000
START=1_767_225_600_000; END=1_768_737_600_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75=np.asarray([20,20,21,21],np.int64)
JAN_SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
STOP=300; ACT=100; DIST=30; HOLD=30; MAXSP=25*TICK

def sha256(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def atomic(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
   tmp=f.name;json.dump(obj,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(tmp,p);tmp=None
 finally:
  if tmp:
   try:os.unlink(tmp)
   except FileNotFoundError:pass

def p75(t,a,b):
 tod=t%DAY
 ls=np.where(t>=UK_DST,7,8)*3_600_000;le=ls+30_600_000
 ns=np.where(t>=US_DST,12,13)*3_600_000;ne=ns+32_400_000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75[s]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,b,tf=300_000):
 bucket=t//tf;st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((bucket[st]+1)*tf).astype(np.int64),"close":b[en-1].astype(np.int64),
         "high":np.maximum.reduceat(b,st).astype(np.int64),"low":np.minimum.reduceat(b,st).astype(np.int64)}

def atr(B,n):
 h,l,c=B["high"],B["low"],B["close"];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 out=np.full(len(tr),np.nan)
 if len(tr)>=n:
  cs=np.r_[0.,np.cumsum(tr)]
  out[n-1:]=(cs[n:]-cs[:-n])/n
 return out

def ema(x,n):
 out=np.full(len(x),np.nan)
 if len(x)<n:return out
 k=2/(n+1);out[n-1]=np.mean(x[:n])
 for i in range(n,len(x)):out[i]=k*x[i]+(1-k)*out[i-1]
 return out

def sma_std(x,n):
 xf=x.astype(np.float64);m=np.full(len(x),np.nan);sd=np.full(len(x),np.nan)
 if len(x)<n:return m,sd
 cs=np.r_[0.,np.cumsum(xf)];cs2=np.r_[0.,np.cumsum(xf*xf)]
 for i in range(n-1,len(x)):
  s=cs[i+1]-cs[i+1-n];s2=cs2[i+1]-cs2[i+1-n];mu=s/n
  m[i]=mu;sd[i]=np.sqrt(max(0.,s2/n-mu*mu))
 return m,sd

def q(x):return ((int(x)+TICK//2)//TICK)*TICK

def vce_c03_events(t,a,b):
 B=bars(t,b);cl=B["close"].astype(np.float64);mu,sd=sma_std(B["close"],20)
 a20=atr(B,20);e20=ema(B["close"],20);bbu=mu+2*sd;bbl=mu-2*sd;kcu=e20+1.5*a20;kcl=e20-1.5*a20
 sq=(bbu<kcu)&(bbl>kcl);ev=[]
 for k in range(20,len(cl)):
  edge=int(B["end"][k])
  if edge>END:break
  if not(bool(sq[k-1]) and not bool(sq[k])):continue
  side=1 if cl[k]>kcu[k] else(-1 if cl[k]<kcl[k] else 0)
  if not side:continue
  ii=int(np.searchsorted(t,edge,side="left"))
  if ii>=len(t) or int(t[ii])>=END:continue
  if int(a[ii]-b[ii])>MAXSP:continue
  ev.append((ii,side,edge,k))
 return ev

def trade(events,t,a,b,deadline):
 rows=[];last_exit=-1
 for ii,side,edge,bar in events:
  if ii<=last_exit:continue
  entry=int(a[ii]) if side>0 else int(b[ii]);stop=q(int(b[ii])-STOP if side>0 else int(a[ii])+STOP)
  es=int(t[ii]//1000);maxfav=-10**18;raw=None;reason=None;exi=None
  for k in range(ii+1,len(t)):
   if int(t[k])>=END:break
   aa=int(a[k]);bb=int(b[k]);sec=int(t[k]//1000)
   if side>0 and bb<=stop:raw=(bb-entry)/SCALE;reason="STOP";exi=k;break
   if side<0 and aa>=stop:raw=(entry-aa)/SCALE;reason="STOP";exi=k;break
   fav=(bb-entry) if side>0 else(entry-aa);maxfav=max(maxfav,fav)
   if deadline and sec-es>=deadline and maxfav<=0:
    raw=fav/SCALE;reason=f"IRH{deadline}";exi=k;break
   if sec-es>=HOLD:raw=fav/SCALE;reason="MAX_HOLD";exi=k;break
   if fav>=ACT:
    ns=q(bb-DIST if side>0 else aa+DIST)
    if(side>0 and ns>stop)or(side<0 and ns<stop):stop=ns
  if raw is None:
   exi=max(ii,int(np.searchsorted(t,END,side="left"))-1)
   raw=((int(b[exi])-entry) if side>0 else(entry-int(a[exi])))/SCALE;reason="END"
  net=raw-.02
  rows.append({"entry_index":ii,"side":side,"net":net,"official_win":net>1e-12,"reason":reason})
  last_exit=exi
 return rows

def metrics(rows):
 return {"trades":len(rows),"official_wins":sum(r["official_win"] for r in rows),
         "official_win_rate":sum(r["official_win"] for r in rows)/len(rows) if rows else 0.,
         "gross_profit":round(sum(max(r["net"],0.) for r in rows),2),
         "gross_loss":round(sum(min(r["net"],0.) for r in rows),2),
         "direct_net_usd":round(sum(r["net"] for r in rows),2),
         "irh_exits":sum(r["reason"].startswith("IRH") for r in rows)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 s=sha256(x.source)
 if s!=JAN_SHA:raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit(f"Stage-A chronology mismatch {len(t)}")
 a,b=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 ev=vce_c03_events(t,a,b);base=metrics(trade(ev,t,a,b,0));variants={}
 for d in(3,5,10):
  m=metrics(trade(ev,t,a,b,d));m["improvement_vs_base_usd"]=round(m["direct_net_usd"]-base["direct_net_usd"],2)
  m["prescreen_pass"]=m["trades"]>=5 and m["official_win_rate"]>=.5 and m["direct_net_usd"]>0 and m["direct_net_usd"]>base["direct_net_usd"]
  variants[str(d)]=m
 out={"schema":"delta-r037-irh-stage-a-17ai-v1","status":"COMPLETE_STAGE_A_PRESCREEN","unit":"R037_IRH_INITIAL_HOLD_REFINEMENT_PRESCREEN",
      "family":"R037-IRH-v1","prereg_commit":"ee4e632dc0ee51505121745bdc8fe0aaeffccd6d","source_sha256":s,
      "stage_a_ticks":len(t),"surface":"DUKAS_COINEXX_LIKE_P75","entry_source":"R037-VCE-C03_BBKC_RELEASE",
      "events":len(ev),"base":base,"variants":variants,"numeric_retuning":False,"august_accessed":False,
      "finding":{"survivors":[f"VCE_C03_IRH{d}" for d in(3,5,10) if variants[str(d)]["prescreen_pass"]],
                 "leading":"VCE_C03_IRH5" if variants["5"]["prescreen_pass"] else None,
                 "next":"R037_IRH_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if variants["5"]["prescreen_pass"] else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
      "mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"base":base,"variants":variants,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":main()
