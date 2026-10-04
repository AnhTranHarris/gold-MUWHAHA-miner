"""R037 17AA London ORB sweep-reclaim reversal prescreen."""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
DAY=86400000;T=10;SCALE=1000;START=1767225600000;END=1768737600000
US=1772953200000;UK=1774746000000;P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
MAXSP=250;STOP=300;ACT=100;DIST=30;HOLD=30
CFG=("C01_FIRST_TICK_RECLAIM","C02_FIRST_COMPLETED_S5_RECLAIM","C03_FIRST_COMPLETED_S15_RECLAIM")
def sh(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def aw(p,o):
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
 tod=t%DAY;ls=np.where(t>=UK,7,8)*3600000;le=ls+30600000;ns=np.where(t>=US,12,13)*3600000;ne=ns+32400000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75[s]*T;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+T)//(2*T))*T;return bid+sp,bid
def q(x):return((int(x)+T//2)//T)*T
def bars(t,b,tf):
 k=t//tf;st=np.r_[0,np.flatnonzero(k[1:]!=k[:-1])+1];en=np.r_[st[1:],len(t)]
 return {"end":((k[st]+1)*tf).astype(np.int64),"close":b[en-1].astype(np.int64)}
def event(t,a,b,day,cfg,B=None):
 d0=day*DAY;rs=d0+7*3600000;re=d0+8*3600000;we=d0+10*3600000
 i0=int(np.searchsorted(t,rs));i1=int(np.searchsorted(t,re));iw=int(np.searchsorted(t,we))
 if i1<=i0 or iw<=i1:return None
 hi=int(np.max(b[i0:i1]));lo=int(np.min(b[i0:i1]));seg=b[i1:iw]
 u=np.flatnonzero(seg>hi);d=np.flatnonzero(seg<lo)
 if not u.size and not d.size:return None
 ui=i1+int(u[0]) if u.size else len(t)+1;di=i1+int(d[0]) if d.size else len(t)+1
 sw=min(ui,di);swept=1 if ui<di else -1;boundary=hi if swept>0 else lo
 if cfg=="C01_FIRST_TICK_RECLAIM":
  x=b[sw+1:iw];z=np.flatnonzero(x<boundary) if swept>0 else np.flatnonzero(x>boundary)
  if not z.size:return None
  ii=sw+1+int(z[0])
 else:
  E=B["end"];C=B["close"];j=int(np.searchsorted(E,int(t[sw]),side="right"));j1=int(np.searchsorted(E,we,side="right"));ii=None
  while j<min(j1,len(E)):
   c=int(C[j])
   if (swept>0 and c<boundary) or (swept<0 and c>boundary):
    ii=int(np.searchsorted(t,int(E[j]),side="left"))
    if ii>=len(t) or ii>=iw:return None
    if not ((int(b[ii])<boundary) if swept>0 else (int(b[ii])>boundary)):return {"i":ii,"side":-swept,"ok":False,"reason":"RELOST","day":d0}
    break
   j+=1
  if ii is None:return None
 if int(a[ii]-b[ii])>MAXSP:return {"i":ii,"side":-swept,"ok":False,"reason":"SPREAD","day":d0}
 return {"i":ii,"side":-swept,"ok":True,"reason":"ELIGIBLE","day":d0}
def props(t,a,b,cfg):
 B=bars(t,b,5000) if cfg==CFG[1] else (bars(t,b,15000) if cfg==CFG[2] else None);out=[]
 for d in range(START//DAY,(END-1)//DAY+1):
  e=event(t,a,b,d,cfg,B)
  if e is not None:out.append(e)
 return out
def one(e,t,a,b):
 i=e["i"];side=e["side"];entry=int(a[i]) if side>0 else int(b[i]);stop=q(int(b[i])-STOP if side>0 else int(a[i])+STOP);es=int(t[i])//1000;net=-.01;gp=0.;gl=-.01;win=0;rawp=0;reason="END";last=i
 lim=min(len(t),int(np.searchsorted(t,min(e["day"]+DAY,END),side="left")))
 for k in range(i+1,lim):
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
 deal=raw-.01;net+=deal;win=int(deal>1e-12);rawp=int(raw>0)
 if raw>0:gp+=deal
 else:gl+=deal
 return net,gp,gl,win,rawp,reason
def ev(P,t,a,b):
 E=[x for x in P if x["ok"]];R=[one(x,t,a,b) for x in E]
 return {"proposals":len(P),"eligible":len(E),"distinct_days":len({x["day"] for x in E}),"trades":len(R),"official_wins":sum(x[3] for x in R),"raw_positive_wins":sum(x[4] for x in R),"gross_profit":round(sum(x[1] for x in R),2),"gross_loss":round(sum(x[2] for x in R),2),"direct_net_usd":round(sum(x[0] for x in R),2),"spread_rejected":sum(x["reason"]=="SPREAD" for x in P),"relost_rejected":sum(x["reason"]=="RELOST" for x in P),"exit_reasons":{z:sum(x[5]==z for x in R) for z in ("STOP","MAX_HOLD","END")}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
 h=sh(a.source)
 if h!=SHA:raise SystemExit("sha mismatch "+h)
 df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64);df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)];t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit("chronology mismatch")
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));R={}
 for c in CFG:
  m=ev(props(t,ask,bid,c),t,ask,bid);g={"minimum_proposals_8":m["proposals"]>=8,"minimum_distinct_days_4":m["distinct_days"]>=4,"direct_net_min_minus_2":m["direct_net_usd"]>=-2};g["prescreen_pass"]=all(g.values());g["strong_pass"]=g["prescreen_pass"] and m["direct_net_usd"]>=0;R[c]={"metrics":m,"gate":g}
 rank=sorted(CFG,key=lambda c:(R[c]["gate"]["strong_pass"],R[c]["gate"]["prescreen_pass"],R[c]["metrics"]["direct_net_usd"],R[c]["metrics"]["official_wins"],R[c]["metrics"]["trades"]),reverse=True);surv=[c for c in rank if R[c]["gate"]["strong_pass"]]
 o={"schema":"delta-r037-london-orb-sweep-reclaim-reversal-17aa-v1","status":"COMPLETE_STAGE_A_PRESCREEN","unit":"R037_LONDON_ORB_SWEEP_RECLAIM_REVERSAL_CHECKPOINT_17AA","family":"R037-LORB-SRR-v1","prereg_commit":"78db1c2b1806fb2605f3715cb1510ce31210902e","source_sha256":h,"stage_a_ticks":len(t),"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,"configs":R,"ranking":rank,"finding":{"leading_config":rank[0],"strong_survivors":surv,"decision":"ADVANCE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "RETIRE_FAMILY_NO_RETUNE","next":"R037_LORB_SRR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if surv else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},"mql5_authorized":False};aw(a.output,o);print(json.dumps({"ranking":rank,"configs":R,"finding":o["finding"]},separators=(",",":")))
if __name__=="__main__":main()
