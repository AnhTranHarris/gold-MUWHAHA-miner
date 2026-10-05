"""R037 17DA-17DD: source-default displacement-qualified session sweep harvest."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,pandas as pd
from delta_r037_session_liquidity_sweep_reclaim_17cw_17cz import (
 D,H,START,END,SHA,MAX_SPREAD,sha256_file,atomic_json,p75,bars,pack
)
PREREG="354bb0bf176d615b6495fc282d203e10c7385144"
ATR_LEN=14; MIN_RANGE_ATR=1.5; MIN_BODY_RANGE=0.5

def atr14(z):
 h,l,c=z['h'],z['l'],z['c'];tr=(h-l).astype(np.float64)
 if len(tr)>1:tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 out=np.full(len(tr),np.nan);cs=np.r_[0.,np.cumsum(tr)]
 for i in range(ATR_LEN-1,len(tr)):out[i]=(cs[i+1]-cs[i+1-ATR_LEN])/ATR_LEN
 return out

def qual(z,a,k):
 r=float(z['h'][k]-z['l'][k])
 return r>0 and np.isfinite(a[k]) and a[k]>0 and r>=MIN_RANGE_ATR*a[k] and abs(float(z['c'][k]-z['o'][k]))/r>=MIN_BODY_RANGE

def event(z,a,k,L,side,mode):
 if not qual(z,a,k):return False
 if mode=='WICK_RECLAIM':return (z['h'][k]>L and z['c'][k]<L) if side<0 else (z['l'][k]<L and z['c'][k]>L)
 if k<1:return False
 return (z['c'][k-1]>L and z['c'][k]<L) if side<0 else (z['c'][k-1]<L and z['c'][k]>L)

def emit(t,ask,bid,e,k,side,ix,sd,d,key):
 j=int(np.searchsorted(t,int(e[k]),side='left'))
 if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:ix.append(j);sd.append(side);d[key]+=1
 elif j<len(t):d['spread_rejects']+=1

def sigs(t,ask,bid,z,mode):
 e=z['e'];a=atr14(z);ix=[];sd=[]
 d={'trade_days':0,'london_asia_events':0,'ny_london_events':0,'ny_asia_events':0,'spread_rejects':0,'ambiguous_bars':0}
 for day0 in np.arange((START//D)*D,END,D,dtype=np.int64):
  asia=np.flatnonzero((e>day0-H)&(e<=day0+8*H)); london=np.flatnonzero((e>day0+8*H)&(e<=day0+13*H)); ny=np.flatnonzero((e>day0+13*H)&(e<=day0+21*H)&(e<=END))
  if len(asia)==0 or e[asia[0]]>day0:continue
  d['trade_days']+=1;ah=int(np.max(z['h'][asia]));al=int(np.min(z['l'][asia]));lh=int(np.max(z['h'][london])) if len(london) else 0;ll=int(np.min(z['l'][london])) if len(london) else 0
  uh=ul=False
  for k in london:
   hi=event(z,a,k,ah,-1,mode);lo=event(z,a,k,al,1,mode)
   if hi and lo:d['ambiguous_bars']+=1;continue
   if hi and not uh:emit(t,ask,bid,e,k,-1,ix,sd,d,'london_asia_events');uh=True
   elif lo and not ul:emit(t,ask,bid,e,k,1,ix,sd,d,'london_asia_events');ul=True
  nlh=nll=nah=nal=False
  for k in ny:
   hi=event(z,a,k,lh,-1,mode) if lh else False;lo=event(z,a,k,ll,1,mode) if ll else False
   if hi and lo:d['ambiguous_bars']+=1;continue
   if hi and not nlh:emit(t,ask,bid,e,k,-1,ix,sd,d,'ny_london_events');nlh=True;continue
   if lo and not nll:emit(t,ask,bid,e,k,1,ix,sd,d,'ny_london_events');nll=True;continue
   hi=event(z,a,k,ah,-1,mode);lo=event(z,a,k,al,1,mode)
   if hi and lo:d['ambiguous_bars']+=1;continue
   if hi and not nah:emit(t,ask,bid,e,k,-1,ix,sd,d,'ny_asia_events');nah=True
   elif lo and not nal:emit(t,ask,bid,e,k,1,ix,sd,d,'ny_asia_events');nal=True
 if not ix:return np.array([],np.int64),np.array([],np.int8),d
 o=np.argsort(np.asarray(ix),kind='stable');return np.asarray(ix,np.int64)[o],np.asarray(sd,np.int8)[o],d

def main():
 st=time.monotonic();ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);x=ap.parse_args();hs=sha256_file(x.source)
 if hs!=SHA:raise SystemExit('SHA mismatch')
 df=pd.read_csv(x.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64);df=df[(df.timestamp_ms_utc>=START)&(df.timestamp_ms_utc<END)];t=df.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit('chronology mismatch')
 ask,bid=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));cfg={}
 for n,tf,m in (('17DA_SSRP_WICK_M1',60000,'WICK_RECLAIM'),('17DB_SSRP_WICK_M5',300000,'WICK_RECLAIM'),('17DC_SSRP_FAILED_CLOSE_M1',60000,'FAILED_CLOSE_NEXT_BAR_RECLAIM'),('17DD_SSRP_FAILED_CLOSE_M5',300000,'FAILED_CLOSE_NEXT_BAR_RECLAIM')):
  ix,sd,di=sigs(t,ask,bid,bars(t,bid,tf),m);me,g=pack(ix,sd,t,ask,bid);cfg[n]={'bar_ms':tf,'sweep_mode':m,'metrics':me,'gate':g,'diagnostics':di}
 surv=[n for n,v in cfg.items() if v['gate']['screen_pass']];surv.sort(key=lambda n:(cfg[n]['metrics']['direct_net_usd'],cfg[n]['metrics']['official_wins'],cfg[n]['metrics']['trades']),reverse=True)
 out={'schema':'delta-r037-displacement-qualified-session-sweep-17da-17dd-v1','status':'COMPLETE_FAST_CAUSAL_STAGE_A_SCREEN','unit':'R037_DISPLACEMENT_QUALIFIED_SESSION_SWEEP_HARVEST_CHECKPOINT_17DA_17DD','parent_checkpoint':'R037_XAUUSD_SESSION_LIQUIDITY_SWEEP_RECLAIM_HARVEST_CHECKPOINT_17CW_17CZ','prereg_commit':PREREG,'source_sha256':hs,'stage_a_ticks':len(t),'surface':'DUKAS_COINEXX_LIKE_P75','source_defaults':{'session_timezone':'America/New_York','asia':'18:00-03:00','london':'03:00-07:59','new_york':'08:00-16:00','atr_length':14,'min_range_atr':1.5,'min_body_range':0.5},'configs':cfg,'finding':{'survivors':surv,'leader':surv[0] if surv else None,'decision':'ADVANCE_LEADER_TO_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'RETIRE_SSRP_QUALIFIED_SWEEP_NO_STAGE_A_SURVIVOR','next':'R037_SSRP_LEADER_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST'},'numeric_retuning':False,'post_result_rescue':False,'august_accessed':False,'mql5_authorized':False,'runtime_seconds':round(time.monotonic()-st,3)}
 atomic_json(x.output,out);print(json.dumps({'configs':{n:{'trades':v['metrics']['trades'],'days':v['metrics']['distinct_days'],'wins':v['metrics']['official_wins'],'net':v['metrics']['direct_net_usd'],'pass':v['gate']['screen_pass'],'diag':v['diagnostics']} for n,v in cfg.items()},'finding':out['finding'],'runtime_seconds':out['runtime_seconds']},separators=(',',':')))
if __name__=='__main__':main()
