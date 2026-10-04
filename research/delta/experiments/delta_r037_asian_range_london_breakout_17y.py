"""DELTA R037 Asian Range -> London Breakout Stage-A screen — 17Y.

Frozen prereg: 00:00-06:00 UTC P75 Bid Asian range; 06:00-10:00 breakout window;
one accepted trade/day; zero configurable buffer; <=25-point spread; frozen 30s lifecycle.
Configs test only causal trigger timing: strict tick, completed S5 close, completed S15 close.
No threshold tuning, August, exit tuning, side split, or MQL5.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd

DAY=86_400_000; TICK=10; SCALE=1000
START=1_767_225_600_000; END=1_768_737_600_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75PTS=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
MAXSP=25*TICK; STOP=300; ACT=100; DIST=30; HOLD=30
CONFIGS=("C01_FIRST_STRICT_TICK","C02_FIRST_COMPLETED_S5_CLOSE","C03_FIRST_COMPLETED_S15_CLOSE")

def sha256(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
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
 ls=np.where(t>=UK_DST,7,8)*3_600_000; le=ls+30_600_000
 ns=np.where(t>=US_DST,12,13)*3_600_000; ne=ns+32_400_000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75PTS[s]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def q(x):return ((int(x)+TICK//2)//TICK)*TICK

def bars(t,b,tf):
 bucket=t//tf;st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((bucket[st]+1)*tf).astype(np.int64),"close":b[en-1].astype(np.int64)}

def day_event(t,a,b,day,cfg,B=None):
 r0=day*DAY;r1=r0+6*3_600_000;w1=r0+10*3_600_000
 i0=int(np.searchsorted(t,r0));i1=int(np.searchsorted(t,r1));iw=int(np.searchsorted(t,w1))
 if i1<=i0 or iw<=i1:return None
 hi=int(np.max(b[i0:i1]));lo=int(np.min(b[i0:i1]))
 if cfg=="C01_FIRST_STRICT_TICK":
  seg=b[i1:iw];u=np.flatnonzero(seg>hi);d=np.flatnonzero(seg<lo)
  if not u.size and not d.size:return None
  ui=i1+int(u[0]) if u.size else len(t)+1;di=i1+int(d[0]) if d.size else len(t)+1
  ii=min(ui,di);side=1 if ui<di else -1;edge=int(t[ii])
 else:
  E=B["end"];C=B["close"];j0=int(np.searchsorted(E,r1,side="left"));j1=int(np.searchsorted(E,w1,side="right"))
  ii=None;side=0;edge=0
  for j in range(j0,min(j1,len(E))):
   c=int(C[j])
   if c>hi or c<lo:
    side=1 if c>hi else -1;edge=int(E[j]);ii=int(np.searchsorted(t,edge,side="left"))
    if ii>=len(t) or ii>=iw:return None
    if not ((int(b[ii])>hi) if side>0 else (int(b[ii])<lo)):return {"decision_index":ii,"side":side,"eligible":False,"reason":"RELOST_AT_EXEC","day":r0,"hi":hi,"lo":lo}
    break
  if ii is None:return None
 if int(a[ii]-b[ii])>MAXSP:return {"decision_index":ii,"side":side,"eligible":False,"reason":"SPREAD","day":r0,"hi":hi,"lo":lo}
 return {"decision_index":ii,"side":side,"eligible":True,"reason":"ELIGIBLE","day":r0,"hi":hi,"lo":lo}

def proposals(t,a,b,cfg):
 B=None
 if cfg=="C02_FIRST_COMPLETED_S5_CLOSE":B=bars(t,b,5000)
 elif cfg=="C03_FIRST_COMPLETED_S15_CLOSE":B=bars(t,b,15000)
 d0=START//DAY;d1=(END-1)//DAY;out=[]
 for d in range(d0,d1+1):
  e=day_event(t,a,b,d,cfg,B)
  if e is not None:out.append(e)
 return out

def trade(ev,t,a,b):
 i=int(ev["decision_index"]);side=int(ev["side"]);entry=int(a[i]) if side>0 else int(b[i]);stop=q((int(b[i])-STOP) if side>0 else (int(a[i])+STOP));es=int(t[i])//1000
 net=-.01;gp=0.;gl=-.01;official=0;rawpos=0;exit_reason="END"
 end=min(len(t),int(np.searchsorted(t,min((ev["day"]+1)*DAY,END),side="left")))
 last=i
 for k in range(i+1,end):
  aa=int(a[k]);bb=int(b[k]);sec=int(t[k])//1000;last=k
  if side>0 and bb<=stop:
   raw=(bb-entry)/SCALE;exit_reason="STOP";break
  if side<0 and aa>=stop:
   raw=(entry-aa)/SCALE;exit_reason="STOP";break
  if sec-es>=HOLD:
   raw=((bb-entry) if side>0 else (entry-aa))/SCALE;exit_reason="MAX_HOLD";break
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
 return {"net":net,"gp":gp,"gl":gl,"official":official,"raw_positive":rawpos,"exit_reason":exit_reason}

def evaluate(P,t,a,b):
 eligible=[e for e in P if e["eligible"]]
 rows=[trade(e,t,a,b) for e in eligible]
 return {
  "proposals":len(P),"eligible":len(eligible),"distinct_days":len({e["day"] for e in eligible}),
  "long":sum(e["side"]>0 for e in eligible),"short":sum(e["side"]<0 for e in eligible),
  "spread_rejected":sum(e["reason"]=="SPREAD" for e in P),"relost_rejected":sum(e["reason"]=="RELOST_AT_EXEC" for e in P),
  "trades":len(rows),"official_wins":sum(x["official"] for x in rows),"raw_positive_wins":sum(x["raw_positive"] for x in rows),
  "gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),"direct_net_usd":round(sum(x["net"] for x in rows),2),
  "exit_reasons":{z:sum(x["exit_reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
 s=sha256(a.source)
 if s!=SHA:raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit(f"Stage-A chronology mismatch {len(t)}")
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 R={}
 for c in CONFIGS:
  z=evaluate(proposals(t,ask,bid,c),t,ask,bid)
  g={"minimum_proposals_8":z["proposals"]>=8,"minimum_distinct_days_4":z["distinct_days"]>=4,"direct_net_min_minus_2":z["direct_net_usd"]>=-2.0}
  g["prescreen_pass"]=all(g.values());g["strong_pass"]=g["prescreen_pass"] and z["direct_net_usd"]>=0
  R[c]={"metrics":z,"gate":g}
 rank=sorted(CONFIGS,key=lambda c:(R[c]["gate"]["strong_pass"],R[c]["gate"]["prescreen_pass"],R[c]["metrics"]["direct_net_usd"],R[c]["metrics"]["official_wins"],R[c]["metrics"]["trades"]),reverse=True)
 strong=[c for c in rank if R[c]["gate"]["strong_pass"]]
 out={"schema":"delta-r037-asian-range-london-breakout-stage-a-17y-v1","status":"COMPLETE_STAGE_A_SCREEN","unit":"R037_ASIAN_RANGE_LONDON_BREAKOUT_STAGE_A_SCREEN_CHECKPOINT_17Y","family":"R037-ARLB-v1","prereg_commit":"8ea57494b5d4bb6b8dd072b00a45bdb71adffa9b","source_sha256":s,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,"configs":R,"ranking":rank,"finding":{"leading_config":rank[0],"strong_survivors":strong,"decision":"ADVANCE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "RETIRE_FAMILY_NO_RETUNE","next":"R037_ARLB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False}
 atomic(a.output,out);print(json.dumps({"ranking":rank,"configs":R,"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
