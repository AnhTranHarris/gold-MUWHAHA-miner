"""DELTA R037 PDHSR C02 independent later-January validation.

Frozen candidate from 17AD:
first strict PDH/PDL sweep -> first completed S5 close reclaim -> enter only
if execution quote still remains reclaimed. No retuning. Source-only validation.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np, pandas as pd

DAY=86_400_000; TICK=10; SCALE=1000
WARMUP_START=1_768_348_800_000
HOLDOUT_START=1_768_737_600_000
JAN_END=1_769_904_000_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75PTS=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
MAXSP=25*TICK; STOP=300; ACT=100; DIST=30; HOLD=30

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

def first_sweep(t,b,i0,i1,pdh,pdl):
 seg=b[i0:i1];u=np.flatnonzero(seg>pdh);d=np.flatnonzero(seg<pdl)
 if not u.size and not d.size:return None
 ui=i0+int(u[0]) if u.size else len(t)+1; di=i0+int(d[0]) if d.size else len(t)+1
 if ui<di:return ui,-1,pdh,"PDH"
 return di,1,pdl,"PDL"

def proposals(t,a,b):
 B5=bars(t,b,5000);E,C=B5["end"],B5["close"];days=np.unique(t//DAY);out=[]
 for k in range(1,len(days)):
  day=int(days[k]);prev=int(days[k-1]);d0=day*DAY;d1=min((day+1)*DAY,JAN_END)
  ip0=int(np.searchsorted(t,prev*DAY));ip1=int(np.searchsorted(t,(prev+1)*DAY))
  i0=int(np.searchsorted(t,d0));i1=int(np.searchsorted(t,d1))
  if ip1<=ip0 or i1<=i0:continue
  pdh=int(np.max(b[ip0:ip1]));pdl=int(np.min(b[ip0:ip1]))
  sw=first_sweep(t,b,i0,i1,pdh,pdl)
  if sw is None:continue
  si,side,level,kind=sw;stm=int(t[si])
  j0=int(np.searchsorted(E,stm,side="right"));j1=int(np.searchsorted(E,d1,side="right"));rj=-1
  for j in range(j0,min(j1,len(E))):
   if (side<0 and int(C[j])<level) or (side>0 and int(C[j])>level):
    rj=j;break
  if rj<0:
   out.append({"eligible":False,"reason":"NO_RECLAIM","day":d0,"side":side,"level_kind":kind});continue
  edge=int(E[rj]);ii=int(np.searchsorted(t,edge,side="left"))
  if ii>=i1:
   out.append({"eligible":False,"reason":"NO_EXEC","day":d0,"side":side,"level_kind":kind});continue
  if not ((int(b[ii])<level) if side<0 else (int(b[ii])>level)):
   out.append({"eligible":False,"reason":"RELOST_AT_EXEC","day":d0,"side":side,"level_kind":kind});continue
  if int(a[ii]-b[ii])>MAXSP:
   out.append({"eligible":False,"reason":"SPREAD","day":d0,"side":side,"level_kind":kind});continue
  out.append({"eligible":True,"reason":"ELIGIBLE","day":d0,"decision_index":ii,"side":side,"level_kind":kind})
 return out

def trade(ev,t,a,b):
 i=int(ev["decision_index"]);side=int(ev["side"]);entry=int(a[i]) if side>0 else int(b[i]);stop=q((int(b[i])-STOP) if side>0 else (int(a[i])+STOP));es=int(t[i])//1000
 net=-.01;gp=0.;gl=-.01;official=0;rawpos=0;exit_reason="END";end=min(len(t),int(np.searchsorted(t,min((ev["day"]+1)*DAY,JAN_END),side="left")));last=i
 for k in range(i+1,end):
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
 return {"net":net,"gp":gp,"gl":gl,"official":official,"raw_positive":rawpos,"exit_reason":exit_reason}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 s=sha256(x.source)
 if s!=SHA:raise SystemExit("canonical January SHA mismatch: "+s)
 df=pd.read_csv(x.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 df=df[(df.timestamp_ms_utc>=WARMUP_START)&(df.timestamp_ms_utc<JAN_END)]
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if t.size==0 or np.any(t[1:]<t[:-1]):raise SystemExit(f"chronology mismatch {t.size}")
 holdout_ticks=int(np.sum(t>=HOLDOUT_START))
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 allp=proposals(t,ask,bid)
 P=[e for e in allp if e.get("decision_index") is not None and int(t[e["decision_index"]])>=HOLDOUT_START]
 eligible=[e for e in P if e.get("eligible")]
 rows=[trade(e,t,ask,bid) for e in eligible]
 reasons={}
 for e in P:
  if not e.get("eligible"):reasons[e["reason"]]=reasons.get(e["reason"],0)+1
 levels={}
 for e,xr in zip(eligible,rows):
  z=levels.setdefault(e["level_kind"],{"trades":0,"wins":0,"net":0.0});z["trades"]+=1;z["wins"]+=xr["official"];z["net"]+=xr["net"]
 for z in levels.values():z["net"]=round(z["net"],2)
 m={"proposals":len(P),"eligible":len(eligible),"distinct_days":len({e["day"] for e in eligible}),"long":sum(e["side"]>0 for e in eligible),"short":sum(e["side"]<0 for e in eligible),"rejections":reasons,
    "trades":len(rows),"official_wins":sum(x["official"] for x in rows),"raw_positive_wins":sum(x["raw_positive"] for x in rows),
    "gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),"direct_net_usd":round(sum(x["net"] for x in rows),2),"level_contribution":levels,
    "exit_reasons":{z:sum(x["exit_reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}}
 gate={"minimum_proposals_6":m["proposals"]>=6,"minimum_trades_5":m["trades"]>=5,"minimum_distinct_days_4":m["distinct_days"]>=4,"direct_net_nonnegative":m["direct_net_usd"]>=0}
 gate["validation_pass"]=all(gate.values())
 out={"schema":"delta-r037-pdhsr-c02-independent-later-jan-v1","status":"COMPLETE_INDEPENDENT_VALIDATION","unit":"R037_PDHSR_C02_INDEPENDENT_LATER_JAN_VALIDATION","candidate":"R037-PDHSR-C02_S5_CLOSE_RECLAIM","parent_checkpoint":"R037_PDH_PDL_SWEEP_RECLAIM_STAGE_A_SCREEN_CHECKPOINT_17AD","prereg_commit":"e9a8ff5f08f136af9b4d9fb52e991610797a8f4e","source_sha256":s,"surface":"DUKAS_COINEXX_LIKE_P75","warmup_start_ms":WARMUP_START,"holdout_start_ms":HOLDOUT_START,"holdout_end_ms_exclusive":JAN_END,"loaded_ticks":int(t.size),"holdout_ticks":holdout_ticks,"candidate_retuned":False,"posthoc_level_split":False,"august_accessed":False,"metrics":m,"gate":gate,"decision":"ADVANCE_MONTH_BY_MONTH_VALIDATION" if gate["validation_pass"] else "RETIRE_C02_NO_RETUNE","next":"R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION" if gate["validation_pass"] else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST","mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"metrics":m,"gate":gate,"next":out["next"]},separators=(",",":")))
if __name__=="__main__":main()
