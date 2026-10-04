"""DELTA R037 psychological round-number liquidity Stage-A screen — 17AG.

Public/reconstructible price logic only. Tests $5/$10 XAUUSD psychological grids.
Trigger = strict tick sweep through a grid level; confirmation = first completed S5/S15
bar after the sweep closes back across the same level. Execution quote must remain
reclaimed. Same level/direction rearms only after price moves >= $1 back inside.
One position at a time. Frozen 30-second research lifecycle. No August / no MQL5.
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
MAXSP=25*TICK; STOP=300; ACT=100; DIST=30; HOLD=30; REARM=1000
CONFIGS=(
 ("C01_10_S5_RECLAIM",10_000,5_000),
 ("C02_5_S5_RECLAIM",5_000,5_000),
 ("C03_10_S15_RECLAIM",10_000,15_000),
 ("C04_5_S15_RECLAIM",5_000,15_000),
)

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
 return {"end":((bucket[st]+1)*tf).astype(np.int64),"close":b[en-1].astype(np.int64)}

def crossed(prev,cur,grid):
 # Return (side, level), side=-1 means upper sweep -> short fade; side=+1 lower sweep -> long fade.
 up=((prev//grid)+1)*grid
 if prev<up and cur>up:return -1,int(up)
 dn=(prev//grid)*grid
 if prev>dn and cur<dn:return 1,int(dn)
 return None

def proposals(t,a,b,grid,tf):
 B=bars(t,b,tf);E,C=B["end"],B["close"];out=[]
 # armed[(side, level)] = bool; rearm happens only after $1 inside the level.
 armed={}
 for i in range(1,len(t)):
  px=int(b[i]);prev=int(b[i-1])
  # update only keys currently disarmed; number of live keys stays small.
  if armed:
   for key,val in list(armed.items()):
    if val:continue
    side,level=key
    if (side<0 and px<=level-REARM) or (side>0 and px>=level+REARM):
     armed[key]=True
  cr=crossed(prev,px,grid)
  if cr is None:continue
  side,level=cr;key=(side,level)
  if key in armed and not armed[key]:continue
  armed[key]=False
  stm=int(t[i]);j=int(np.searchsorted(E,stm,side="right"))
  if j>=len(E):
   out.append({"eligible":False,"reason":"NO_CONFIRM_BAR","sweep_index":i,"side":side,"level":level});continue
  edge=int(E[j]);ii=int(np.searchsorted(t,edge,side="left"))
  if ii>=len(t) or int(t[ii])>=END:
   out.append({"eligible":False,"reason":"NO_EXEC","sweep_index":i,"side":side,"level":level});continue
  reclaimed=(int(C[j])<level) if side<0 else (int(C[j])>level)
  if not reclaimed:
   out.append({"eligible":False,"reason":"CONFIRM_FAIL","sweep_index":i,"side":side,"level":level});continue
  live=(int(b[ii])<level) if side<0 else (int(b[ii])>level)
  if not live:
   out.append({"eligible":False,"reason":"RELOST_AT_EXEC","sweep_index":i,"side":side,"level":level});continue
  if int(a[ii]-b[ii])>MAXSP:
   out.append({"eligible":False,"reason":"SPREAD","sweep_index":i,"side":side,"level":level});continue
  out.append({"eligible":True,"reason":"ELIGIBLE","sweep_index":i,"decision_index":ii,"side":side,"level":level,"day":int(t[ii])//DAY})
 return out

def trade(ev,t,a,b):
 i=int(ev["decision_index"]);side=int(ev["side"]);entry=int(a[i]) if side>0 else int(b[i])
 stop=q((int(b[i])-STOP) if side>0 else (int(a[i])+STOP));es=int(t[i])//1000
 net=-.01;gp=0.;gl=-.01;official=0;rawpos=0;exit_reason="END";last=i
 for k in range(i+1,len(t)):
  aa=int(a[k]);bb=int(b[k]);sec=int(t[k])//1000;last=k
  if side>0 and bb<=stop:raw=(bb-entry)/SCALE;exit_reason="STOP";break
  if side<0 and aa>=stop:raw=(entry-aa)/SCALE;exit_reason="STOP";break
  if sec-es>=HOLD:raw=((bb-entry) if side>0 else (entry-aa))/SCALE;exit_reason="MAX_HOLD";break
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
 return {"net":net,"gp":gp,"gl":gl,"official":official,"raw_positive":rawpos,"exit_reason":exit_reason,"exit_index":last}

def evaluate(P,t,a,b):
 eligible=[e for e in P if e.get("eligible")]
 rows=[];accepted=[];busy_until=-1
 for e in eligible:
  i=int(e["decision_index"])
  if i<=busy_until:continue
  x=trade(e,t,a,b);rows.append(x);accepted.append(e);busy_until=int(x["exit_index"])
 reasons={}
 for e in P:
  if not e.get("eligible"):reasons[e["reason"]]=reasons.get(e["reason"],0)+1
 return {"proposals":len(P),"eligible":len(eligible),"trades":len(rows),"distinct_days":len({e["day"] for e in accepted}),
  "long":sum(e["side"]>0 for e in accepted),"short":sum(e["side"]<0 for e in accepted),"rejections":reasons,
  "official_wins":sum(x["official"] for x in rows),"raw_positive_wins":sum(x["raw_positive"] for x in rows),
  "gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),
  "direct_net_usd":round(sum(x["net"] for x in rows),2),
  "exit_reasons":{z:sum(x["exit_reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 s=sha256(x.source)
 if s!=SHA:raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit(f"Stage-A chronology mismatch {len(t)}")
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 R={}
 for name,grid,tf in CONFIGS:
  m=evaluate(proposals(t,ask,bid,grid,tf),t,ask,bid)
  g={"minimum_trades_30":m["trades"]>=30,"minimum_distinct_days_6":m["distinct_days"]>=6,"direct_net_min_minus_2":m["direct_net_usd"]>=-2.0}
  g["prescreen_pass"]=all(g.values());g["strong_pass"]=g["prescreen_pass"] and m["direct_net_usd"]>=0
  R[name]={"metrics":m,"gate":g}
 rank=sorted([c[0] for c in CONFIGS],key=lambda n:(R[n]["gate"]["strong_pass"],R[n]["gate"]["prescreen_pass"],R[n]["metrics"]["direct_net_usd"],R[n]["metrics"]["official_wins"]),reverse=True)
 strong=[n for n in rank if R[n]["gate"]["strong_pass"]]
 out={"schema":"delta-r037-prn-stage-a-17ag-v1","status":"COMPLETE_STAGE_A_SCREEN","unit":"R037_PSYCHOLOGICAL_ROUND_LIQUIDITY_STAGE_A_SCREEN","family":"R037-PRN-v1","prereg_commit":"966e7ab5d868b6a622eaef5ea598deb0cd7e1b98","source_sha256":s,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,"configs":R,"ranking":rank,"finding":{"leading_config":rank[0],"strong_survivors":strong,"decision":"ADVANCE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "RETIRE_FAMILY_NO_RETUNE","next":"R037_PRN_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"ranking":rank,"configs":R,"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
