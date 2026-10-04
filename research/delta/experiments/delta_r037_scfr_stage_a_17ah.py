"""DELTA R037 SCFR Stage-A screen — Checkpoint 17AH.

Sequence-only candidate reconstructed from public liquidity-sweep/CISD/FVG logic:
confirmed S5 swing -> wick sweep + close back inside -> CISD through sweep-bar open
-> post-sweep classic three-bar FVG -> retrace/rejection -> tick execution.

Preregistered constants only. No fitting, no August, no MQL5.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np, pandas as pd

DAY=86_400_000; TICK=10; SCALE=1000
START=1_767_225_600_000; END=1_768_737_600_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75PTS=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
TF=5_000; W=2; CISD_BARS=6; FVG_BARS=2; RETRACE_BARS=6
MAXSP=25*TICK; STOP=300; ACT=100; DIST=30; HOLD=30
PREREG="9e6e204e2fbf657a5cf3729e919b2ec25fa86c94"

def sha256(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()

def atomic(p,o):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); n=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",prefix="."+p.name+".",suffix=".tmp",dir=p.parent,delete=False) as f:
   n=f.name; json.dump(o,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
  os.replace(n,p); n=None
 finally:
  if n:
   try: os.unlink(n)
   except FileNotFoundError: pass

def p75(t,a,b):
 tod=t%DAY
 ls=np.where(t>=UK_DST,7,8)*3_600_000; le=ls+30_600_000
 ns=np.where(t>=US_DST,12,13)*3_600_000; ne=ns+32_400_000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75PTS[s]*TICK; m=a.astype(np.int64)+b.astype(np.int64); bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def q(x): return ((int(x)+TICK//2)//TICK)*TICK

def bars(t,b):
 bucket=t//TF; st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]; en=np.r_[st[1:],len(t)]
 return {
  "start":(bucket[st]*TF).astype(np.int64),
  "end":((bucket[st]+1)*TF).astype(np.int64),
  "open":b[st].astype(np.int64),
  "high":np.maximum.reduceat(b,st).astype(np.int64),
  "low":np.minimum.reduceat(b,st).astype(np.int64),
  "close":b[en-1].astype(np.int64)
 }

def swing_reveals(B):
 H,L,E=B["high"],B["low"],B["end"]; out=[]
 for k in range(W,len(H)-W):
  if all(H[k]>H[k-j] and H[k]>H[k+j] for j in range(1,W+1)):
   out.append((int(E[k+W]),1,int(H[k])))
  if all(L[k]<L[k-j] and L[k]<L[k+j] for j in range(1,W+1)):
   out.append((int(E[k+W]),-1,int(L[k])))
 out.sort(key=lambda x:x[0]); return out

def proposals(t,a,b):
 B=bars(t,b); O,H,L,C,E=(B[k] for k in ("open","high","low","close","end"))
 rev=swing_reveals(B); ri=0; hi=None; lo=None; consumed_hi=None; consumed_lo=None
 state=None; out=[]; counts={"sweeps":0,"cisd":0,"fvg":0,"retrace":0}
 for i in range(len(E)):
  edge=int(E[i])
  while ri<len(rev) and rev[ri][0]<=edge:
   _,sd,lv=rev[ri]
   if sd>0:
    hi=lv
    if consumed_hi!=hi: consumed_hi=None
   else:
    lo=lv
    if consumed_lo!=lo: consumed_lo=None
   ri+=1

  if state is None:
   if lo is not None and consumed_lo!=lo and int(L[i])<lo and int(C[i])>lo and int(C[i])>int(O[i]):
    state={"side":1,"level":lo,"sweep_i":i,"sweep_open":int(O[i]),"phase":"SWEEP"}
    consumed_lo=lo; counts["sweeps"]+=1
   elif hi is not None and consumed_hi!=hi and int(H[i])>hi and int(C[i])<hi and int(C[i])<int(O[i]):
    state={"side":-1,"level":hi,"sweep_i":i,"sweep_open":int(O[i]),"phase":"SWEEP"}
    consumed_hi=hi; counts["sweeps"]+=1
   continue

  sd=state["side"]
  if state["phase"]=="SWEEP":
   if i-state["sweep_i"]>CISD_BARS:
    state=None; continue
   if (sd>0 and int(C[i])>state["sweep_open"]) or (sd<0 and int(C[i])<state["sweep_open"]):
    state["phase"]="CISD"; state["cisd_i"]=i; counts["cisd"]+=1
   continue

  if state["phase"]=="CISD":
   if i-state["cisd_i"]>FVG_BARS:
    state=None; continue
   if i<2: continue
   if sd>0 and int(L[i])>int(H[i-2]):
    zl=int(H[i-2]); zh=int(L[i])
   elif sd<0 and int(H[i])<int(L[i-2]):
    zl=int(H[i]); zh=int(L[i-2])
   else:
    continue
   state["phase"]="FVG"; state["fvg_i"]=i; state["zl"]=zl; state["zh"]=zh; state["mid"]=(zl+zh)//2; counts["fvg"]+=1
   continue

  if state["phase"]=="FVG":
   if i-state["fvg_i"]>RETRACE_BARS:
    state=None; continue
   mid=state["mid"]; zl=state["zl"]; zh=state["zh"]
   ok=(sd>0 and int(L[i])<=mid and int(C[i])>mid and int(C[i])>int(O[i]) and int(C[i])>=zl) or (sd<0 and int(H[i])>=mid and int(C[i])<mid and int(C[i])<int(O[i]) and int(C[i])<=zh)
   if not ok: continue
   ii=int(np.searchsorted(t,edge,side="left"))
   if ii>=len(t) or int(t[ii])>=END:
    out.append({"eligible":False,"reason":"NO_EXEC"}); state=None; continue
   if int(a[ii]-b[ii])>MAXSP:
    out.append({"eligible":False,"reason":"SPREAD"}); state=None; continue
   live=(sd>0 and int(b[ii])>=zl) or (sd<0 and int(b[ii])<=zh)
   if not live:
    out.append({"eligible":False,"reason":"RELOST_AT_EXEC"}); state=None; continue
   out.append({"eligible":True,"decision_index":ii,"side":sd,"day":int(t[ii])//DAY,"level":state["level"],"zl":zl,"zh":zh})
   counts["retrace"]+=1; state=None
 return out,counts

def trade(ev,t,a,b):
 i=int(ev["decision_index"]); side=int(ev["side"]); entry=int(a[i]) if side>0 else int(b[i])
 stop=q(int(b[i])-STOP if side>0 else int(a[i])+STOP); es=int(t[i])//1000
 net=-.01; gp=0.; gl=-.01; official=0; rawpos=0; last=i; reason="END"
 for k in range(i+1,len(t)):
  aa=int(a[k]); bb=int(b[k]); sec=int(t[k])//1000; last=k
  if side>0 and bb<=stop: raw=(bb-entry)/SCALE; reason="STOP"; break
  if side<0 and aa>=stop: raw=(entry-aa)/SCALE; reason="STOP"; break
  if sec-es>=HOLD: raw=((bb-entry) if side>0 else (entry-aa))/SCALE; reason="MAX_HOLD"; break
  fav=(bb-entry) if side>0 else (entry-aa)
  if fav>=ACT:
   ns=q(bb-DIST if side>0 else aa+DIST)
   if (side>0 and ns>stop) or (side<0 and ns<stop): stop=ns
 else:
  aa=int(a[last]); bb=int(b[last]); raw=((bb-entry) if side>0 else (entry-aa))/SCALE
 deal=raw-.01; net+=deal
 if deal>1e-12: official=1
 if raw>0: rawpos=1; gp+=deal
 else: gl+=deal
 return {"net":net,"gp":gp,"gl":gl,"official":official,"raw_positive":rawpos,"reason":reason,"exit_index":last}

def evaluate(P,t,a,b):
 eligible=[e for e in P if e.get("eligible")]; rows=[]; accepted=[]; busy=-1
 for e in eligible:
  i=int(e["decision_index"])
  if i<=busy: continue
  x=trade(e,t,a,b); rows.append(x); accepted.append(e); busy=int(x["exit_index"])
 rej={}
 for e in P:
  if not e.get("eligible"): rej[e["reason"]]=rej.get(e["reason"],0)+1
 return {
  "proposals":len(P),"eligible":len(eligible),"trades":len(rows),"distinct_days":len({e["day"] for e in accepted}),
  "long":sum(e["side"]>0 for e in accepted),"short":sum(e["side"]<0 for e in accepted),"rejections":rej,
  "official_wins":sum(x["official"] for x in rows),"raw_positive_wins":sum(x["raw_positive"] for x in rows),
  "gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),
  "direct_net_usd":round(sum(x["net"] for x in rows),2),
  "exit_reasons":{z:sum(x["reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}
 }

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); x=ap.parse_args()
 s=sha256(x.source)
 if s!=SHA: raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]): raise SystemExit(f"Stage-A chronology mismatch {len(t)}")
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 P,stage=proposals(t,ask,bid); m=evaluate(P,t,ask,bid)
 gate={"minimum_trades_12":m["trades"]>=12,"minimum_distinct_days_4":m["distinct_days"]>=4,"direct_net_min_minus_1":m["direct_net_usd"]>=-1.0}
 gate["prescreen_pass"]=all(gate.values()); gate["strong_pass"]=gate["prescreen_pass"] and m["direct_net_usd"]>=0
 out={
  "schema":"delta-r037-scfr-stage-a-17ah-v1","status":"COMPLETE_STAGE_A_SCREEN","unit":"R037_SWEEP_CISD_FVG_RETRACE_STAGE_A_SCREEN","family":"R037-SCFR-v1",
  "prereg_commit":PREREG,"source_sha256":s,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,
  "stage_counts":stage,"metrics":m,"gate":gate,
  "finding":{"decision":"ADVANCE_INDEPENDENT_LATER_JAN_VALIDATION" if gate["strong_pass"] else "RETIRE_FAMILY_NO_RETUNE","next":"R037_SCFR_INDEPENDENT_LATER_JAN_VALIDATION" if gate["strong_pass"] else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
  "mql5_authorized":False
 }
 atomic(x.output,out); print(json.dumps({"stage_counts":stage,"metrics":m,"gate":gate,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
