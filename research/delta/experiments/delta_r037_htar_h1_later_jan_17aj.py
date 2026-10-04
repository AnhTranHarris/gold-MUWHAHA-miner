"""DELTA R037 higher-timeframe anchored reversal Stage-A screen — 17AI.

Preregistered public/reconstructible sequence:
causally confirmed H1/H4 swing liquidity anchor -> S5 wick sweep + close back inside
-> S5 CISD through sweep-bar open -> post-CISD reversal FVG -> retrace/rejection
-> P75 tick execution. Frozen 30-second lifecycle. No fitting / no August / no MQL5.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np, pandas as pd

DAY=86_400_000; TICK=10; SCALE=1000
WARMUP=1_768_348_800_000; ECON=1_768_737_600_000; END=1_769_904_000_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75PTS=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
S5=5_000; W=1; CISD_BARS=6; FVG_BARS=2; RETRACE_BARS=6
MAXSP=25*TICK; STOP=300; ACT=100; DIST=30; HOLD=30
PREREG="5cb4f19ea4c098ce9d8589d59bd4a6bb874ef778"
CONFIGS=(("C01_H1_ANCHOR",3_600_000),)

def sha256(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def atomic(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);n=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",prefix="."+p.name+".",suffix=".tmp",dir=p.parent,delete=False) as f:
   n=f.name;json.dump(o,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(n,p);n=None
 finally:
  if n:
   try:os.unlink(n)
   except FileNotFoundError:pass

def p75(t,a,b):
 tod=t%DAY
 ls=np.where(t>=UK_DST,7,8)*3_600_000;le=ls+30_600_000
 ns=np.where(t>=US_DST,12,13)*3_600_000;ne=ns+32_400_000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75PTS[s]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def q(x):return ((int(x)+TICK//2)//TICK)*TICK

def bars(t,b,tf):
 bucket=t//tf;st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((bucket[st]+1)*tf).astype(np.int64),"open":b[st].astype(np.int64),"high":np.maximum.reduceat(b,st).astype(np.int64),"low":np.minimum.reduceat(b,st).astype(np.int64),"close":b[en-1].astype(np.int64)}

def swings(B):
 H,L,E=B["high"],B["low"],B["end"];out=[]
 for k in range(W,len(H)-W):
  if H[k]>H[k-1] and H[k]>H[k+1]:out.append((int(E[k+W]),1,int(H[k])))
  if L[k]<L[k-1] and L[k]<L[k+1]:out.append((int(E[k+W]),-1,int(L[k])))
 out.sort(key=lambda x:x[0]);return out

def proposals(t,a,b,anchor_tf):
 B=bars(t,b,S5);A=bars(t,b,anchor_tf)
 O,H,L,C,E=(B[k] for k in ("open","high","low","close","end"))
 rev=swings(A);ri=0;hi=None;lo=None;consumed_hi=False;consumed_lo=False
 state=None;out=[];cnt={"anchors_high":0,"anchors_low":0,"sweeps":0,"cisd":0,"fvg":0,"retrace":0}
 for i in range(len(E)):
  edge=int(E[i])
  while ri<len(rev) and rev[ri][0]<=edge:
   _,sd,lv=rev[ri]
   if sd>0:
    hi=lv;consumed_hi=False;cnt["anchors_high"]+=1
   else:
    lo=lv;consumed_lo=False;cnt["anchors_low"]+=1
   ri+=1
  if state is None:
   if lo is not None and not consumed_lo and int(L[i])<lo and int(C[i])>lo and int(C[i])>int(O[i]):
    state={"side":1,"level":lo,"sweep_i":i,"sweep_open":int(O[i]),"phase":"SWEEP"};consumed_lo=True;cnt["sweeps"]+=1
   elif hi is not None and not consumed_hi and int(H[i])>hi and int(C[i])<hi and int(C[i])<int(O[i]):
    state={"side":-1,"level":hi,"sweep_i":i,"sweep_open":int(O[i]),"phase":"SWEEP"};consumed_hi=True;cnt["sweeps"]+=1
   continue
  sd=state["side"]
  if state["phase"]=="SWEEP":
   if i-state["sweep_i"]>CISD_BARS:state=None;continue
   if (sd>0 and int(C[i])>state["sweep_open"]) or (sd<0 and int(C[i])<state["sweep_open"]):
    state["phase"]="CISD";state["cisd_i"]=i;cnt["cisd"]+=1
   continue
  if state["phase"]=="CISD":
   if i-state["cisd_i"]>FVG_BARS:state=None;continue
   if i<2:continue
   if sd>0 and int(L[i])>int(H[i-2]):zl=int(H[i-2]);zh=int(L[i])
   elif sd<0 and int(H[i])<int(L[i-2]):zl=int(H[i]);zh=int(L[i-2])
   else:continue
   state["phase"]="FVG";state["fvg_i"]=i;state["zl"]=zl;state["zh"]=zh;state["mid"]=(zl+zh)//2;cnt["fvg"]+=1
   continue
  if state["phase"]=="FVG":
   if i-state["fvg_i"]>RETRACE_BARS:state=None;continue
   mid=state["mid"];zl=state["zl"];zh=state["zh"]
   ok=(sd>0 and int(L[i])<=mid and int(C[i])>mid and int(C[i])>int(O[i]) and int(C[i])>=zl) or (sd<0 and int(H[i])>=mid and int(C[i])<mid and int(C[i])<int(O[i]) and int(C[i])<=zh)
   if not ok:continue
   ii=int(np.searchsorted(t,edge,side="left"))
   if ii>=len(t) or int(t[ii])>=END:out.append({"eligible":False,"reason":"NO_EXEC","decision_ms":edge});state=None;continue
   if int(a[ii]-b[ii])>MAXSP:out.append({"eligible":False,"reason":"SPREAD","decision_ms":edge});state=None;continue
   live=(sd>0 and int(b[ii])>=zl) or (sd<0 and int(b[ii])<=zh)
   if not live:out.append({"eligible":False,"reason":"RELOST_AT_EXEC","decision_ms":edge});state=None;continue
   out.append({"eligible":True,"decision_index":ii,"decision_ms":int(t[ii]),"side":sd,"day":int(t[ii])//DAY,"anchor":state["level"],"zl":zl,"zh":zh});cnt["retrace"]+=1;state=None
 return out,cnt

def trade(ev,t,a,b):
 i=int(ev["decision_index"]);side=int(ev["side"]);entry=int(a[i]) if side>0 else int(b[i])
 stop=q(int(b[i])-STOP if side>0 else int(a[i])+STOP);es=int(t[i])//1000
 net=-.01;gp=0.;gl=-.01;official=0;rawpos=0;last=i;reason="END"
 for k in range(i+1,len(t)):
  aa=int(a[k]);bb=int(b[k]);sec=int(t[k])//1000;last=k
  if side>0 and bb<=stop:raw=(bb-entry)/SCALE;reason="STOP";break
  if side<0 and aa>=stop:raw=(entry-aa)/SCALE;reason="STOP";break
  if sec-es>=HOLD:raw=((bb-entry) if side>0 else (entry-aa))/SCALE;reason="MAX_HOLD";break
  fav=(bb-entry) if side>0 else (entry-aa)
  if fav>=ACT:
   ns=q(bb-DIST if side>0 else aa+DIST)
   if (side>0 and ns>stop) or (side<0 and ns<stop):stop=ns
 else:
  aa=int(a[last]);bb=int(b[last]);raw=((bb-entry) if side>0 else (entry-aa))/SCALE
 deal=raw-.01;net+=deal
 if deal>1e-12:official=1
 if raw>0:rawpos=1;gp+=deal
 else:gl+=deal
 return {"net":net,"gp":gp,"gl":gl,"official":official,"raw_positive":rawpos,"reason":reason,"exit_index":last}

def evaluate(P,t,a,b):
 elig=[e for e in P if e.get("eligible")];rows=[];accepted=[];busy=-1
 for e in elig:
  i=int(e["decision_index"])
  if i<=busy:continue
  x=trade(e,t,a,b);rows.append(x);accepted.append(e);busy=int(x["exit_index"])
 rej={}
 for e in P:
  if not e.get("eligible"):rej[e["reason"]]=rej.get(e["reason"],0)+1
 return {"proposals":len(P),"eligible":len(elig),"trades":len(rows),"distinct_days":len({e["day"] for e in accepted}),"long":sum(e["side"]>0 for e in accepted),"short":sum(e["side"]<0 for e in accepted),"rejections":rej,"official_wins":sum(x["official"] for x in rows),"raw_positive_wins":sum(x["raw_positive"] for x in rows),"gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),"direct_net_usd":round(sum(x["net"] for x in rows),2),"exit_reasons":{z:sum(x["reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 s=sha256(x.source)
 if s!=SHA:raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 df=df[(df.timestamp_ms_utc>=WARMUP)&(df.timestamp_ms_utc<END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)==0 or np.any(t[1:]<t[:-1]):raise SystemExit(f"holdout chronology mismatch {len(t)}")
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 R={}
 for name,tf in CONFIGS:
  P,stage=proposals(t,ask,bid,tf);m=evaluate(P,t,ask,bid)
  g={"minimum_trades_4":m["trades"]>=4,"minimum_distinct_days_3":m["distinct_days"]>=3,"direct_net_min_minus_1":m["direct_net_usd"]>=-1}
  g["prescreen_pass"]=all(g.values());g["strong_pass"]=g["prescreen_pass"] and m["direct_net_usd"]>=0
  R[name]={"anchor_seconds":tf,"stage_counts":stage,"metrics":m,"gate":g}
 rank=sorted([c[0] for c in CONFIGS],key=lambda n:(R[n]["gate"]["strong_pass"],R[n]["gate"]["prescreen_pass"],R[n]["metrics"]["direct_net_usd"],R[n]["metrics"]["official_wins"]),reverse=True)
 strong=[n for n in rank if R[n]["gate"]["strong_pass"]]
 out={"schema":"delta-r037-htar-h1-later-jan-17aj-v1","status":"COMPLETE_INDEPENDENT_LATER_JAN_VALIDATION","unit":"R037_HTAR_H1_INDEPENDENT_LATER_JAN_VALIDATION","family":"R037-HTAR-v1","candidate":"R037-HTAR-C01_H1_ANCHOR","prereg_commit":PREREG,"source_sha256":s,"warmup_ticks":int(len(t)),"economics_ticks":int(np.sum(t>=ECON)),"window":{"warmup_start_ms":WARMUP,"economics_start_ms":ECON,"end_exclusive_ms":END},"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,"configs":R,"ranking":rank,"finding":{"leading_config":rank[0],"holdout_survivors":strong,"decision":"ADVANCE_FROZEN_H1_MONTH_BY_MONTH" if strong else "RETIRE_HTAR_H1_NO_RETUNE","next":"R037_HTAR_H1_FEB_JUL_ROBUSTNESS_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"ranking":rank,"configs":R,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":main()
