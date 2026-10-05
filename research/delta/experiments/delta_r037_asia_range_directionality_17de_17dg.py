"""R037 17DE-17DG: XAUUSD Asia-range directionality harvest."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,pandas as pd
from delta_r037_session_liquidity_sweep_reclaim_17cw_17cz import D,H,START,END,SHA,MAX_SPREAD,sha256_file,atomic_json,p75,bars,pack
PREREG="b788e7aa4c3d83b7bea43beb453b705b34b340b1"
TF=900_000

def engulf(o,c,k,side):
 if k<1:return False
 if side>0:return c[k]>o[k] and c[k-1]<o[k-1] and o[k]<=c[k-1] and c[k]>=o[k-1]
 return c[k]<o[k] and c[k-1]>o[k-1] and o[k]>=c[k-1] and c[k]<=o[k-1]

def xbreak(t,ask,bid,z):
 e,o,c,h,l=z['e'],z['o'],z['c'],z['h'],z['l'];ix=[];sd=[];d={'trade_days':0,'long_signals':0,'short_signals':0,'spread_rejects':0,'body_rejects':0}
 for day0 in np.arange((START//D)*D,END,D,dtype=np.int64):
  asia=np.flatnonzero((e>day0)&(e<=day0+7*H));ks=np.flatnonzero((e>day0+8*H)&(e<=day0+D)&(e<=END))
  if not len(asia):continue
  d['trade_days']+=1;ah=int(np.max(h[asia]));al=int(np.min(l[asia]));ar=ah-al;ul=us=False
  if ar<=0:continue
  for k in ks:
   br=float(h[k]-l[k]);body=abs(float(c[k]-o[k]));strong=br>0 and body/br>=.60 and body/ar>=.30
   if not strong:
    if c[k]>ah or c[k]<al:d['body_rejects']+=1
    continue
   side=1 if (c[k]>ah and c[k]>o[k]) else (-1 if (c[k]<al and c[k]<o[k]) else 0)
   if side>0 and ul:continue
   if side<0 and us:continue
   if side:
    j=int(np.searchsorted(t,int(e[k]),side='left'))
    if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
     ix.append(j);sd.append(side)
     if side>0:ul=True;d['long_signals']+=1
     else:us=True;d['short_signals']+=1
    elif j<len(t):d['spread_rejects']+=1
 if not ix:return np.array([],np.int64),np.array([],np.int8),d
 q=np.argsort(np.asarray(ix),kind='stable');return np.asarray(ix,np.int64)[q],np.asarray(sd,np.int8)[q],d

def sunalgo(t,ask,bid,z,mode):
 e,o,c,h,l=z['e'],z['o'],z['c'],z['h'],z['l'];ix=[];sd=[];d={'trade_days':0,'long_signals':0,'short_signals':0,'sweeps_seen':0,'engulf_rejects':0,'spread_rejects':0}
 for day0 in np.arange((START//D)*D,END,D,dtype=np.int64):
  asia=np.flatnonzero((e>day0)&(e<=day0+8*H));ks=np.flatnonzero((e>day0+13*H)&(e<=day0+16*H+30*60_000)&(e<=END))
  if not len(asia):continue
  d['trade_days']+=1;ah=int(np.max(h[asia]));al=int(np.min(l[asia]));used=False
  for k in ks:
   side=0
   if mode=='SAME_BAR':
    if h[k]>ah and c[k]<ah:side=-1
    elif l[k]<al and c[k]>al:side=1
   else:
    if k>0 and c[k-1]>ah and c[k]<ah:side=-1
    elif k>0 and c[k-1]<al and c[k]>al:side=1
   if not side:continue
   d['sweeps_seen']+=1
   if not engulf(o,c,k,side):d['engulf_rejects']+=1;continue
   if used:continue
   j=int(np.searchsorted(t,int(e[k]),side='left'))
   if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
    ix.append(j);sd.append(side);used=True
    if side>0:d['long_signals']+=1
    else:d['short_signals']+=1
   elif j<len(t):d['spread_rejects']+=1;used=True
 return np.asarray(ix,np.int64),np.asarray(sd,np.int8),d

def main():
 st=time.monotonic();ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);x=ap.parse_args();hs=sha256_file(x.source)
 if hs!=SHA:raise SystemExit('SHA mismatch')
 df=pd.read_csv(x.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64);df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)];t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit('chronology mismatch')
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));z=bars(t,bid,TF);cfg={}
 for n,kind in (('17DE_XBREAK_M15_CONTINUATION','XBREAK'),('17DF_SUNALGO_M15_SAME_BAR','SAME_BAR'),('17DG_SUNALGO_M15_NEXT_BAR','NEXT_BAR')):
  ix,sd,di=xbreak(t,ask,bid,z) if kind=='XBREAK' else sunalgo(t,ask,bid,z,kind);me,g=pack(ix,sd,t,ask,bid);cfg[n]={'mode':kind,'metrics':me,'gate':g,'diagnostics':di}
 surv=[n for n,v in cfg.items() if v['gate']['screen_pass']];surv.sort(key=lambda n:(cfg[n]['metrics']['direct_net_usd'],cfg[n]['metrics']['official_wins'],cfg[n]['metrics']['trades']),reverse=True)
 out={'schema':'delta-r037-asia-range-directionality-17de-17dg-v1','status':'COMPLETE_FAST_CAUSAL_STAGE_A_SCREEN','unit':'R037_XAUUSD_ASIA_RANGE_DIRECTIONALITY_HARVEST_CHECKPOINT_17DE_17DG','parent_checkpoint':'R037_DISPLACEMENT_QUALIFIED_SESSION_SWEEP_HARVEST_CHECKPOINT_17DA_17DD','prereg_commit':PREREG,'source_sha256':hs,'stage_a_ticks':len(t),'surface':'DUKAS_COINEXX_LIKE_P75','configs':cfg,'finding':{'survivors':surv,'leader':surv[0] if surv else None,'decision':'ADVANCE_LEADER_TO_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'RETIRE_ASIA_RANGE_DIRECTIONALITY_NO_STAGE_A_SURVIVOR','next':'R037_ASIA_RANGE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST'},'numeric_retuning':False,'post_result_rescue':False,'august_accessed':False,'mql5_authorized':False,'runtime_seconds':round(time.monotonic()-st,3)}
 atomic_json(x.output,out);print(json.dumps({'configs':{n:{'trades':v['metrics']['trades'],'days':v['metrics']['distinct_days'],'wins':v['metrics']['official_wins'],'net':v['metrics']['direct_net_usd'],'pass':v['gate']['screen_pass'],'diag':v['diagnostics']} for n,v in cfg.items()},'finding':out['finding'],'runtime_seconds':out['runtime_seconds']},separators=(',',':')))
if __name__=='__main__':main()
