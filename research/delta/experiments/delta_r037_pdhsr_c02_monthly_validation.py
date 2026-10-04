"""DELTA R037 PDHSR C02 month-by-month robustness validation.

Frozen candidate from 17AD/17AE. Sequential February-July 2026 validation.
No retuning, no post-hoc PDH/PDL split, August sealed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np, pandas as pd

DAY=86_400_000; TICK=10; SCALE=1000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75PTS=np.asarray([20,20,21,21],np.int64)
MAXSP=25*TICK; STOP=300; ACT=100; DIST=30; HOLD=30
EXPECTED=[
 ("2026-01","d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"),
 ("2026-02","ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d"),
 ("2026-03","814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177"),
 ("2026-04","30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f"),
 ("2026-05","3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d"),
 ("2026-06","34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2"),
 ("2026-07","e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7"),
]

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

def first_sweep(t,b,i0,i1,pdh,pdl):
 seg=b[i0:i1];u=np.flatnonzero(seg>pdh);d=np.flatnonzero(seg<pdl)
 if not u.size and not d.size:return None
 ui=i0+int(u[0]) if u.size else len(t)+1;di=i0+int(d[0]) if d.size else len(t)+1
 if ui<di:return ui,-1,pdh,"PDH"
 return di,1,pdl,"PDL"

def last_day_levels(t,b):
 days=np.unique(t//DAY)
 d=int(days[-1]);i0=int(np.searchsorted(t,d*DAY));i1=int(np.searchsorted(t,(d+1)*DAY))
 return d,int(np.max(b[i0:i1])),int(np.min(b[i0:i1]))

def month_proposals(t,a,b,seed_pdh,seed_pdl):
 B5=bars(t,b,5000);E,C=B5["end"],B5["close"];days=np.unique(t//DAY);out=[]
 prev_pdh=int(seed_pdh);prev_pdl=int(seed_pdl)
 for k,dayv in enumerate(days):
  day=int(dayv);d0=day*DAY;d1=(day+1)*DAY;i0=int(np.searchsorted(t,d0));i1=int(np.searchsorted(t,d1))
  if i1<=i0:continue
  pdh,pdl=prev_pdh,prev_pdl
  sw=first_sweep(t,b,i0,i1,pdh,pdl)
  if sw is not None:
   si,side,level,kind=sw;stm=int(t[si])
   j0=int(np.searchsorted(E,stm,side="right"));j1=int(np.searchsorted(E,d1,side="right"));rj=-1
   for j in range(j0,min(j1,len(E))):
    if (side<0 and int(C[j])<level) or (side>0 and int(C[j])>level):
     rj=j;break
   if rj<0:
    out.append({"eligible":False,"reason":"NO_RECLAIM","day":d0,"side":side,"level_kind":kind})
   else:
    edge=int(E[rj]);ii=int(np.searchsorted(t,edge,side="left"))
    if ii>=i1:out.append({"eligible":False,"reason":"NO_EXEC","day":d0,"side":side,"level_kind":kind})
    elif not ((int(b[ii])<level) if side<0 else (int(b[ii])>level)):
     out.append({"eligible":False,"reason":"RELOST_AT_EXEC","day":d0,"side":side,"level_kind":kind})
    elif int(a[ii]-b[ii])>MAXSP:
     out.append({"eligible":False,"reason":"SPREAD","day":d0,"side":side,"level_kind":kind})
    else:
     out.append({"eligible":True,"reason":"ELIGIBLE","day":d0,"decision_index":ii,"side":side,"level_kind":kind})
  prev_pdh=int(np.max(b[i0:i1]));prev_pdl=int(np.min(b[i0:i1]))
 return out

def trade(ev,t,a,b):
 i=int(ev["decision_index"]);side=int(ev["side"]);entry=int(a[i]) if side>0 else int(b[i]);stop=q((int(b[i])-STOP) if side>0 else (int(a[i])+STOP));es=int(t[i])//1000
 net=-.01;gp=0.;gl=-.01;official=0;rawpos=0;exit_reason="END";end=min(len(t),int(np.searchsorted(t,(ev["day"]+1)*DAY,side="left")));last=i
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

def metrics(P,t,a,b):
 eligible=[e for e in P if e.get("eligible")];rows=[trade(e,t,a,b) for e in eligible];reasons={}
 for e in P:
  if not e.get("eligible"):reasons[e["reason"]]=reasons.get(e["reason"],0)+1
 levels={}
 for e,x in zip(eligible,rows):
  z=levels.setdefault(e["level_kind"],{"trades":0,"wins":0,"net":0.0});z["trades"]+=1;z["wins"]+=x["official"];z["net"]+=x["net"]
 for z in levels.values():z["net"]=round(z["net"],2)
 return {"proposals":len(P),"eligible":len(eligible),"distinct_days":len({e["day"] for e in eligible}),"long":sum(e["side"]>0 for e in eligible),"short":sum(e["side"]<0 for e in eligible),"rejections":reasons,"trades":len(rows),"official_wins":sum(x["official"] for x in rows),"raw_positive_wins":sum(x["raw_positive"] for x in rows),"gross_profit":round(sum(x["gp"] for x in rows),2),"gross_loss":round(sum(x["gl"] for x in rows),2),"direct_net_usd":round(sum(x["net"] for x in rows),2),"level_contribution":levels,"exit_reasons":{z:sum(x["exit_reason"]==z for x in rows) for z in ("STOP","MAX_HOLD","END")}}

def load(path,expected):
 s=sha256(path)
 if s!=expected:raise SystemExit(f"SHA mismatch {path}: {s}")
 df=pd.read_csv(path,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
 t=df.timestamp_ms_utc.to_numpy(np.int64)
 if t.size==0 or np.any(t[1:]<t[:-1]):raise SystemExit(f"chronology mismatch {path}: {t.size}")
 a,b=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
 return s,t,a,b

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--sources",type=Path,nargs=7,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 for p,(m,h) in zip(x.sources,EXPECTED):
  if sha256(p)!=h:raise SystemExit(f"{m} canonical SHA mismatch")
 _,tj,aj,bj=load(x.sources[0],EXPECTED[0][1]);_,seed_pdh,seed_pdl=last_day_levels(tj,bj)
 monthly={}; total_trades=total_wins=0;agg_net=0.;agg_gp=0.;agg_gl=0.
 for idx in range(1,7):
  month,expected=EXPECTED[idx];_,t,a,b=load(x.sources[idx],expected)
  P=month_proposals(t,a,b,seed_pdh,seed_pdl);m=metrics(P,t,a,b);monthly[month]=m
  total_trades+=m["trades"];total_wins+=m["official_wins"];agg_net+=m["direct_net_usd"];agg_gp+=m["gross_profit"];agg_gl+=m["gross_loss"]
  _,seed_pdh,seed_pdl=last_day_levels(t,b)
 nonneg=sum(v["direct_net_usd"]>=0 for v in monthly.values())
 gate={"total_trades_min_24":total_trades>=24,"nonnegative_months_min_4":nonneg>=4,"aggregate_net_nonnegative":agg_net>=0}
 gate["robustness_pass"]=all(gate.values())
 out={"schema":"delta-r037-pdhsr-c02-monthly-validation-v1","status":"COMPLETE_MONTH_BY_MONTH_VALIDATION","unit":"R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION","candidate":"R037-PDHSR-C02_S5_CLOSE_RECLAIM","parent_checkpoint":"R037_PDHSR_C02_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17AE","prereg_commit":"04341c0531990e8f3685baf4066aaf85b3c1ac32","months":monthly,"aggregate":{"trades":total_trades,"official_wins":total_wins,"gross_profit":round(agg_gp,2),"gross_loss":round(agg_gl,2),"direct_net_usd":round(agg_net,2),"nonnegative_months":nonneg},"gate":gate,"candidate_retuned":False,"posthoc_level_split":False,"august_accessed":False,"decision":"ADVANCE_SURROGATE_PARENT_INTEGRATION" if gate["robustness_pass"] else "RETIRE_C02_NO_RETUNE","next":"R037_PDHSR_C02_SURROGATE_PARENT_INTEGRATION_VALIDATION" if gate["robustness_pass"] else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST","mql5_authorized":False}
 atomic(x.output,out);print(json.dumps({"aggregate":out["aggregate"],"gate":gate,"months":monthly,"next":out["next"]},separators=(",",":")))
if __name__=="__main__":main()
