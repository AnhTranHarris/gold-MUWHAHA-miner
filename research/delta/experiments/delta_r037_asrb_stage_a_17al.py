"""DELTA R037 Asian-session range breakout Stage-A screen — 17AL.

Public/reconstructible source family: freeze 00:00-06:00 UTC range, then seek
causal S5 breakout confirmation during 07:00-10:00 UTC. C01 requires one full
persistence bar outside; C02 requires a causal boundary retest/rejection within
six S5 bars. Frozen 30-second P75 execution. No retuning / August / MQL5.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
DAY=86_400_000;TICK=10;SCALE=1000
START=1_767_225_600_000;END=1_768_737_600_000
US_DST=1_772_953_200_000;UK_DST=1_774_746_000_000
P75PTS=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="21d85a854b0c6b6123ef05f980ea97d978fe88da"
S5=5_000;MAXSP=25*TICK;STOP=300;ACT=100;DIST=30;HOLD=30

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
 tod=t%DAY;ls=np.where(t>=UK_DST,7,8)*3_600_000;le=ls+30_600_000
 ns=np.where(t>=US_DST,12,13)*3_600_000;ne=ns+32_400_000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75PTS[s]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)
def q(x):return ((int(x)+TICK//2)//TICK)*TICK
def bars(t,b,tf):
 bucket=t//tf;st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((bucket[st]+1)*tf).astype(np.int64),"open":b[st].astype(np.int64),"high":np.maximum.reduceat(b,st).astype(np.int64),"low":np.minimum.reduceat(b,st).astype(np.int64),"close":b[en-1].astype(np.int64)}
def proposals(t,a,b,profile):
 B=bars(t,b,S5);E,O,H,L,C=(B[k] for k in ("end","open","high","low","close"));out=[];cnt={"days":0,"breakouts":0,"confirmations":0}
 for day in np.unique(t//DAY):
  d=int(day)*DAY;r0=d;r1=d+6*3_600_000;w0=d+7*3_600_000;w1=d+10*3_600_000
  if w0>=END or d+DAY<=START:continue
  i0=int(np.searchsorted(t,r0));i1=int(np.searchsorted(t,r1))
  if i1<=i0:continue
  rh=int(np.max(b[i0:i1]));rl=int(np.min(b[i0:i1]));cnt["days"]+=1
  j0=int(np.searchsorted(E,w0,side="right"));j1=int(np.searchsorted(E,min(w1,END),side="right"))
  used_up=used_dn=False
  for j in range(j0,min(j1,len(E))):
   side=0;level=0
   if not used_up and int(C[j])>rh:side=1;level=rh
   elif not used_dn and int(C[j])<rl:side=-1;level=rl
   else:continue
   cnt["breakouts"]+=1
   k=-1
   if profile==1:
    if j+1<j1 and ((side>0 and int(C[j+1])>level) or (side<0 and int(C[j+1])<level)):k=j+1
   else:
    for z in range(j+1,min(j+7,j1)):
     touch=(int(L[z])<=level if side>0 else int(H[z])>=level)
     reject=(int(C[z])>level and int(C[z])>int(O[z])) if side>0 else (int(C[z])<level and int(C[z])<int(O[z]))
     if touch and reject:k=z;break
   if k<0:continue
   edge=int(E[k]);ii=int(np.searchsorted(t,edge,side="left"));cnt["confirmations"]+=1
   if side>0:used_up=True
   else:used_dn=True
   if ii>=len(t) or int(t[ii])>=min(w1,END):out.append({"eligible":False,"reason":"NO_EXEC"});continue
   if int(a[ii]-b[ii])>MAXSP:out.append({"eligible":False,"reason":"SPREAD"});continue
   live=(int(b[ii])>level) if side>0 else (int(b[ii])<level)
   if not live:out.append({"eligible":False,"reason":"RELOST_AT_EXEC"});continue
   out.append({"eligible":True,"decision_index":ii,"side":side,"day":d})
 return out,cnt
def trade(ev,t,a,b):
 i=int(ev["decision_index"]);side=int(ev["side"]);entry=int(a[i]) if side>0 else int(b[i]);stop=q(int(b[i])-STOP if side>0 else int(a[i])+STOP);es=int(t[i])//1000
 net=-.01;gp=0.;gl=-.01;off=0;rawp=0;last=i;reason="END"
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
 if deal>1e-12:off=1
 if raw>0:rawp=1;gp+=deal
 else:gl+=deal
 return {"net":net,"gp":gp,"gl":gl,"official":off,"raw_positive":rawp,"reason":reason,"exit_index":last}
def evaluate(P,t,a,b):
 elig=[e for e in P if e.get("eligible")];rows=[];accepted=[];busy=-1
 for e in elig:
  i=int(e["decision_index"])
  if i<=busy:continue
  x=trade(e,t,a,b);rows.append(x);accepted.append(e);busy=int(x["exit_index"])
 rej={}
 for e in P:
  if not e.get("eligible"):rej[e["reason"]]=rej.get(e["reason"],0)+1
 return {"proposals":len(P),"eligible":len(elig),"trades":len(rows),"distinct_days":len({e["day"] for e in accepted}),"long":sum(e["side"]>0 for e in accepted),"short":sum(e["side"]<0 for e in accepted),"rejections":rej,"official_wins":sum(x["official"] for x in rows),"gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),"direct_net_usd":round(sum(x["net"] for x in rows),2),"exit_reasons":{z:sum(x["reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 s=sha256(x.source)
 if s!=SHA:raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):raise SystemExit("Stage-A chronology mismatch")
 a,b=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));R={}
 for name,p in (("C01_PERSIST",1),("C02_RETEST",2)):
  P,c=proposals(t,a,b,p);m=evaluate(P,t,a,b)
  g={"minimum_trades_4":m["trades"]>=4,"minimum_distinct_days_3":m["distinct_days"]>=3,"direct_net_min_minus_1":m["direct_net_usd"]>=-1}
  g["prescreen_pass"]=all(g.values());g["strong_pass"]=g["prescreen_pass"] and m["direct_net_usd"]>=0
  R[name]={"stage_counts":c,"metrics":m,"gate":g}
 rank=sorted(R,key=lambda n:(R[n]["gate"]["strong_pass"],R[n]["gate"]["prescreen_pass"],R[n]["metrics"]["direct_net_usd"],R[n]["metrics"]["official_wins"]),reverse=True)
 strong=[n for n in rank if R[n]["gate"]["strong_pass"]]
 out={"schema":"delta-r037-asrb-stage-a-17al-v1","status":"COMPLETE_STAGE_A_SCREEN","unit":"R037_ASIAN_SESSION_RANGE_BREAKOUT_STAGE_A_SCREEN","family":"R037-ASRB-v1","prereg_commit":PREREG,"source_sha256":s,"stage_a_ticks":len(t),"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,"configs":R,"ranking":rank,"finding":{"leading_config":rank[0],"strong_survivors":strong,"decision":"ADVANCE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "RETIRE_FAMILY_NO_RETUNE","next":"R037_ASRB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"ranking":rank,"configs":R,"finding":out["finding"]},separators=(",",":")))
if __name__=="__main__":main()
