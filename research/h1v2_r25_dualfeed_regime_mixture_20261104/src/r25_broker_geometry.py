"""H1V2 R25: broker-conditioned, causal-quote research harness (NOT an EA).

Source-exact frozen historical Jan/Feb/Jun/Jul 2026 Dukascopy and Coinexx-linked
MT5 ticks. SOURCE as-of at first occupied UTC second, actual observed +100ms
quote fill. No future-known teacher labels enter action selection. Quota is joined
ONLY after decisions, and across source months independently. Pure exploratory
IN-SAMPLE market evidence; no certified dealer fills or live profitability.

Three independent novel mechanism families are evaluated in complete UTC calendars:
  XSC: cross-scale impulse continuation with bid/ask causal quote confirmation;
  LSR: liquidity/spread contraction following opposite-scale rejection;
  HGR: quote-grammar relief + burst-level microstructure displacement.
Each uses source-specific spread/volatility price geometry, short horizon and
one-position realized first-TP/STOP/censored/timeout replay. All outcomes kept.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time
import zipfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from numba import njit

BASE = Path('/mnt/data')
OUT = BASE/'h1v2_r25'/'results'
MONTHS = ('01','02','06','07')
SOURCES = ('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
RAW_PINS = {
 ('DUKASCOPY_RAW','01'):'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 ('DUKASCOPY_RAW','02'):'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
 ('DUKASCOPY_RAW','06'):'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
 ('DUKASCOPY_RAW','07'):'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7',
 ('MT5_BROKER_EXPORT','01'):'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',
 ('MT5_BROKER_EXPORT','02'):'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',
 ('MT5_BROKER_EXPORT','06'):'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',
 ('MT5_BROKER_EXPORT','07'):'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d',
}
POLICIES = ('XSC_CROSSSCALE_IMPULSE','LSR_LIQUIDITY_SNAP_REJECTION','HGR_QUOTE_GRAMMAR_RELIEF')
COHORT = 'R24_FIRST_OBSERVED_1S_GAP300_FRESHAFT15_CAP4000'
FEE_RAW=20
STOP_MIN_RAW=100
GAP_MS=15000
FILL_MS=100
STALE_FILL_MS=1000


def sha(path:Path)->str:
 with path.open('rb') as fh:return hashlib.file_digest(fh,'sha256').hexdigest()


def rawpath(source:str,mon:str)->Path:
 if source==SOURCES[0]:return BASE/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 if source==SOURCES[1]:return BASE/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
 raise ValueError('INVALID_SOURCE')


def load_source(source:str,mon:str):
 path=rawpath(source,mon)
 if sha(path)!=RAW_PINS[source,mon]:raise RuntimeError('SOURCE_SHA_MISMATCH '+source+' '+mon)
 if source==SOURCES[0]:
  z=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=z.timestamp_ms_utc.to_numpy(copy=True);b=z.bid_raw.to_numpy(copy=True);a=z.ask_raw.to_numpy(copy=True)
 else:
  z=pd.read_csv(path,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  offset=2 if mon in ('01','02') else 3
  t=z.time_msc.to_numpy(copy=True)-offset*3600000
  b=np.rint(z.bid.to_numpy(copy=True)*1000).astype(np.int32)
  a=np.rint(z.ask.to_numpy(copy=True)*1000).astype(np.int32)
 del z
 if source==SOURCES[1] and mon=='06':
  # Original R24 June source clock: July server month supplies the UTC June tail.
  jp=rawpath(source,'07')
  if sha(jp)!=RAW_PINS[source,'07']:raise RuntimeError('JULY_HALO_SHA')
  j=pd.read_csv(jp,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  tj=j.time_msc.to_numpy(copy=True)-3*3600000
  hi=int(datetime(2026,7,1,tzinfo=timezone.utc).timestamp()*1000)+60000
  mask=(tj>t[-1])&(tj<=hi)
  if not mask.any() or tj[mask][0]-t[-1]<=15000:raise RuntimeError('JUNE_JULY_HALO_CONTRACT')
  t=np.r_[t,tj[mask]]
  b=np.r_[b,np.rint(j.bid.to_numpy()[mask]*1000).astype(np.int32)]
  a=np.r_[a,np.rint(j.ask.to_numpy()[mask]*1000).astype(np.int32)]
  del j,tj
 if not len(t) or np.any(np.diff(t)<0) or np.any(a<b):raise RuntimeError('INVALID_SOURCE_QUOTE_ORDER')
 return t,b,a


def refs(mon):
 z=zipfile.ZipFile(BASE/'R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip')
 with z.open(f'results/R23_DUKASCOPY_RAW_{mon}_COMPLETE_QUARTERS.csv') as f:df=pd.read_csv(f)
 d=df[df.scenario=='A1_TP050_STOP100_H60_CAP4000_Q8'].copy()
 expected={'01':(2976,27980),'02':(2688,33523),'06':(2880,31758),'07':(2976,24324)}[mon]
 assert len(d)==expected[0]
 r=d.original_R9_SYNTH_reference.to_numpy(np.int32)
 assert r.sum()==expected[1]
 qt=(pd.to_datetime(d.utc_quarter,utc=True).astype('int64').to_numpy()//1_000_000).astype(np.int64)
 assert np.all(np.diff(qt)==900000)
 return qt,r


def candidate_ordinals(t,b,a,step=1000):
 if step<=0:raise ValueError('INVALID_DECISION_GRID')
 s=np.flatnonzero(np.r_[True,np.diff(t//step)!=0]).astype(np.int32)
 reset=np.flatnonzero(np.r_[True,np.diff(t)>GAP_MS]).astype(np.int32)
 epoch=reset[np.searchsorted(reset,s,side='right')-1]
 sp=a[s].astype(np.int64)-b[s].astype(np.int64)
 good=(t[s]-t[epoch]>=300000)&(sp>=0)&(sp<=4000)
 return s[good]


def prefix_features(t,b,a,sig):
 """As-of only; every j <= original exact decision source ordinal s."""
 s=np.asarray(sig,np.int32);n=len(s)
 if not n:return np.empty((0,26),np.float32)
 now=t[s];bs=b[s].astype(np.int64);aa=a[s].astype(np.int64)
 sp=aa-bs
 X=np.zeros((n,26),np.float32)
 X[:,0]=sp
 mid=bs+aa
 mids={}
 for k,(win,name) in enumerate(((1000,'1s'),(3000,'3s'),(10000,'10s'),(30000,'30s'),(300000,'300s'))):
  j=np.searchsorted(t,now-win,side='left')
  if np.any(j>s):raise AssertionError('FUTURE_PREFIX_INDEX')
  bb=b[j].astype(np.int64);ab=a[j].astype(np.int64)
  X[:,1+3*k]=(mid-bb-ab)*0.5
  X[:,2+3*k]=bs-bb
  X[:,3+3*k]=aa-ab
  mids[name]=j
 X[:,16]=(s-mids['3s'])/3.0
 X[:,17]=(s-mids['30s'])/30.0
 X[:,18]=sp-(a[mids['3s']].astype(np.int64)-b[mids['3s']].astype(np.int64))
 X[:,19]=sp-(a[mids['30s']].astype(np.int64)-b[mids['30s']].astype(np.int64))
 X[:,20]=np.log1p(np.maximum(sp,0))
 X[:,21]=np.abs(X[:,4])/(1+sp)  # move3 / execution spread
 X[:,22]=(now//3600000)%24 # UTC hour as-of label
 X[:,23]=(now//60000)%15 # minute of 15-min, asof UTC bucket
 X[:,24]=np.minimum(now-t[np.maximum(s-1,0)],300000)
 X[:,25]=np.abs(X[:,10])/(1+np.abs(X[:,13])) # 30s / 300s ratio
 assert np.all(np.isfinite(X))
 return X


@njit(cache=False)
def select_policy(policy:int, row):
 """Decision is a pure function of current and historical quote features.

    The market source is reflected only by its observed spread and timing;
    broker-specific geometry parameters are later injected as source contract.
    No label, R9 volume reference or future tick ordinal enters this function.
    Returns (BUY=1/SELL=-1/WAIT=0, target_raw,stop_raw,horizon_ms).
 """
 sp=row[0]; m1=row[1];m3=row[4];m10=row[7];m30=row[10];m300=row[13]
 bid3=row[5];ask3=row[6]; qps=row[16]; qps30=row[17]
 spr3=row[18];spr30=row[19]
 if sp<0 or sp>4000:return 0,0,0,0
 sign3=1 if m3>0 else (-1 if m3<0 else 0)
 sign30=1 if m30>0 else (-1 if m30<0 else 0)
 direction=0; h=0
 if policy==0:
  # Accelerating *two-scale* bid+ask impulse and sustained slow trend,
  # not the invalidated simple 3s sign-only control.
  if sign3!=0 and sign3==sign30 and abs(m3)>0.45*sp+80 and (bid3*ask3>0) and abs(m10)>0.20*sp:
   if m10*sign3>0 and m300*sign30>0 and spr30<=0.15*sp:
    direction=sign3;h=10000
 elif policy==1:
  # Reject the 30s prior direction after recent 3s overshoot and spread relief.
  if sign3!=0 and sign30!=0 and sign3!=sign30 and abs(m3)>0.32*sp+60:
   if spr3<0 and spr30<0 and qps>1.2 and qps30>0.6 and bid3*ask3>0:
    direction=sign3;h=12000
 elif policy==2:
  # Liquidity event grammar: bid+ask leadership and slow compression,
  # with rapid tape and contraction, but no simple price-only 3s signal.
  if qps>1.5*qps30 and qps>1.1 and spr3<0 and spr30<0:
   if abs(bid3-ask3)>0.15*sp and abs(m1)>0.10*sp and abs(m3)>0.15*sp:
    direction=sign3;h=7000
 if direction==0:return 0,0,0,0
 # Different broker market geometry: target and stop adapted to observed
 # bid/ask spread plus past quote travel, never actual future target label.
 target=int(max(100,min(3200,0.45*sp+0.32*abs(m3)+20)))
 stop=int(max(100,min(4000,0.55*sp+0.14*abs(m30))))
 # If stop encodes catastrophic spread, abstain rather than widen infinitely.
 if stop>2500:return 0,0,0,0
 return direction,target,stop,h


@njit(cache=False)
def oneposition(t,b,a,signal,fill,X,policy,month0,monthend):
 """Strict chronological replay from actual quote ordinals.

    Uses labels only after as-of action, prevents a second simultaneous entry.
    Price units are raw 0.001 quoted XAUUSD. No dealer/commission model.
    Return one attempted row per accepted signal, including unfilled events;
    arrays record source original ordinal and true first quote exit ordinal.
    OUTCOME 1=TP,0=STOP,2=TIMEOUT,3=CENSORED,4=UNFILLED.
 """
 N=len(signal)
 out=np.empty((N,11),np.int64);k=0;blocked_until=-999999999999999
 for i in range(N):
  s=signal[i]
  if t[s]<month0 or t[s]>=monthend:continue
  if t[s]<=blocked_until:continue
  side,tp,st,h=select_policy(policy,X[i])
  if side==0:continue
  fi=fill[i]
  if fi<0:
   out[k,0]=s;out[k,1]=-1;out[k,2]=-1;out[k,3]=side
   out[k,4]=4;out[k,5]=0;out[k,6]=tp;out[k,7]=st;out[k,8]=h;out[k,9]=0;out[k,10]=int(X[i,0]);k+=1
   continue
  openms=t[fi];deadline=openms+h
  if side>0:
   target=a[fi]+FEE_RAW+tp;stop=b[fi]-st
  else:
   target=b[fi]-FEE_RAW-tp;stop=a[fi]+st
  status=3;ex=-1
  # Actual observed quote order, all same-ms updates after the fill are examined.
  for j in range(fi+1,len(t)):
   if t[j]-t[j-1]>GAP_MS:
    status=3;ex=j;break
   if t[j]>deadline:
    status=2;ex=j;break
   if side>0:
    if b[j]<=stop:status=0;ex=j;break
    if b[j]>=target:status=1;ex=j;break
   else:
    if a[j]>=stop:status=0;ex=j;break
    if a[j]<=target:status=1;ex=j;break
   if t[j]==deadline:
    status=2;ex=j;break
  if ex<0:
   blocked_until=monthend;net=0
  else:
   blocked_until=t[ex]
   net=0 if status==3 else ((b[ex]-a[fi]-FEE_RAW) if side>0 else (b[fi]-a[ex]-FEE_RAW))
  out[k,0]=s;out[k,1]=fi;out[k,2]=ex;out[k,3]=side
  out[k,4]=status;out[k,5]=net;out[k,6]=tp;out[k,7]=st;out[k,8]=h;out[k,9]=int(X[i,4]);out[k,10]=int(X[i,0]);k+=1
 return out[:k]


def reference_calendar(mon,qt,ref,source,policy,events,t):
 """Every original 15m, hour and day including zero-reference buckets.
 Quota compares only ACTUAL observed fills, not causal predicted signals.
 True entries are filled quote times, while source label is at signal ordinal.
 """
 qt=np.asarray(qt,np.int64);r=np.asarray(ref,np.int32)
 valid=events[:,1]>=0
 filled=events[valid]
 if len(filled):
  entry=t[filled[:,1]].astype(np.int64)
  k=np.searchsorted(qt,entry//900000*900000)
  inside=(k<len(qt))&(qt[np.minimum(k,len(qt)-1)]==entry//900000*900000)
  if not np.all(inside):raise AssertionError('SOURCE_FILL_OUTSIDE_MONTH')
  count=np.bincount(k,minlength=len(r))
  good=np.bincount(k,weights=(filled[:,4]==1).astype(np.int32),minlength=len(r)).astype(np.int32)
  bad=np.bincount(k,weights=(filled[:,4]==0).astype(np.int32),minlength=len(r)).astype(np.int32)
  cens=np.bincount(k,weights=(filled[:,4]==3).astype(np.int32),minlength=len(r)).astype(np.int32)
  timed=np.bincount(k,weights=(filled[:,4]==2).astype(np.int32),minlength=len(r)).astype(np.int32)
  price=np.bincount(k,weights=filled[:,5],minlength=len(r))
 else:count=np.zeros(len(r),np.int32);good=count.copy();bad=count.copy();cens=count.copy();timed=count.copy();price=np.zeros(len(r))
 prec=np.divide(good,good+bad,out=np.zeros(len(r),np.float64),where=good+bad>0)
 meets=(r>0)&(count>=r)&(prec>=.80)&(good+bad>0)
 quarters=[]
 for i in range(len(r)):
  quarters.append({'source':source,'month':mon,'policy':policy,'utc_quarter':datetime.fromtimestamp(int(qt[i])/1000,timezone.utc).isoformat(),
   'reference':int(r[i]),'fills':int(count[i]),'tp':int(good[i]),'stop':int(bad[i]),'timeout':int(timed[i]),'censored':int(cens[i]),
   'correct_completed':None if not good[i]+bad[i] else float(prec[i]),'net_quote_raw_known_excluding_censored':float(price[i]),
   'active_joint_pass':int(meets[i]) if r[i]>0 else None,'source_exact_no_dealer_fill':True})
 hours=[];days=[]
 for unit,skip,target in [('hour',4,hours),('day',96,days)]:
  for start in range(0,len(r),skip):
   qn=int(r[start:start+skip].sum());fn=int(count[start:start+skip].sum());gn=int(good[start:start+skip].sum());bn=int(bad[start:start+skip].sum())
   pr=gn/(gn+bn) if gn+bn else None
   target.append({'source':source,'month':mon,'policy':policy,'utc_'+unit:datetime.fromtimestamp(int(qt[start])/1000,timezone.utc).isoformat(),
    'reference':qn,'fills':fn,'tp':gn,'stop':bn,'timeout':int(timed[start:start+skip].sum()),'censored':int(cens[start:start+skip].sum()),
    'correct_completed':pr,'net_quote_raw_known_excluding_censored':float(price[start:start+skip].sum()),
    'active_joint_pass':int(fn>=qn and pr is not None and pr>=.80) if qn>0 else None})
 def scored(rows):
  active=[x for x in rows if x['reference']>0];joint=[x for x in active if x['active_joint_pass']==1]
  return {'active':len(active),'volume':sum(x['fills']>=x['reference'] for x in active),'joint':len(joint),
   'tp':sum(x['tp'] for x in rows),'stop':sum(x['stop'] for x in rows),'timeout':sum(x['timeout'] for x in rows),
   'censored':sum(x['censored'] for x in rows),'fill':sum(x['fills'] for x in rows),
   'ref':sum(x['reference'] for x in rows),'net_quote_raw_known_excluding_censored':sum(x['net_quote_raw_known_excluding_censored'] for x in rows)}
 return quarters,hours,days,scored(quarters),scored(hours),scored(days)


def write_records(path:Path,rows:list[dict]):
 path.parent.mkdir(exist_ok=True,parents=True)
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run_case(source:str,mon:str,policies=POLICIES):
 start=time.perf_counter()
 t,b,a=load_source(source,mon)
 qt,ref=refs(mon)
 srcs=candidate_ordinals(t,b,a)
 X=prefix_features(t,b,a,srcs)
 target=t[srcs]+FILL_MS
 idx=np.searchsorted(t,target,side='left').astype(np.int32)
 safe=np.minimum(idx,len(t)-1)
 valid=(idx<len(t))&(safe>srcs)&(t[safe]-target<=STALE_FILL_MS)&((a[safe]-b[safe])<=4000)&(a[safe]>=b[safe])
 fill=np.where(valid,idx,-1).astype(np.int32)
 stats=[]
 outfolder=OUT/source/mon;outfolder.mkdir(parents=True,exist_ok=True)
 for pname in policies:
  p=POLICIES.index(pname)
  events=oneposition(t,b,a,srcs,fill,X,p,int(qt[0]),int(qt[-1]+900000))
  qr,hr,dr,sq,sh,sd=reference_calendar(mon,qt,ref,source,pname,events,t)
  np.savez_compressed(outfolder/f'{pname}_ALL_ATTEMPTED_SOURCE_ORDINALS.npz',selected=events,columns=np.array(('signal_source_ordinal','fill_source_ordinal','exit_source_ordinal','side','status','net_quote_raw','target_raw','stop_raw','max_horizon_ms','observed_mid3_raw','observed_signal_spread_raw')))
  write_records(outfolder/f'{pname}_FULL_{len(qr)}_QUARTERS.csv',qr)
  write_records(outfolder/f'{pname}_FULL_{len(hr)}_HOURS.csv',hr)
  write_records(outfolder/f'{pname}_FULL_{len(dr)}_DAYS.csv',dr)
  completed=sq['tp']+sq['stop']
  r={'source':source,'month':mon,'policy':pname,'reference_month':int(ref.sum()),'raw_quote_count':len(t),
     'first_occupied_1s_eligible_signals':len(srcs),'first_observed_100ms_fill_valid':int(valid.sum()),
     'attempts':len(events),'unfilled_attempts':int((events[:,4]==4).sum()),
     'source_completed_tp_first_fraction':sq['tp']/completed if completed else None,
     'strict_completed_tp_first':sq['tp'],'strict_completed_stop_first':sq['stop'],
     'full_calendar_quarters':len(qr),'full_calendar_hours':len(hr),'full_calendar_days':len(dr),
     'quarters':sq,'hours':sh,'days':sd,'elapsed_s':round(time.perf_counter()-start,2),
     'original_source_sha':RAW_PINS[source,mon],
     'original_research_contract':'NEW_15_S_V5_QUOTE_FRESHNESS_1S_SIGNAL_100MS_FIRST_OBSERVED_FILL','r9_volume_runtime_feature':False,
     'future_labels_runtime_feature':False,'broker_execution_cash_verified':False,'source_price_net_not_account_usd':True,'censored_net_not_imputed':True,
     'model_fitted':False,'blind_OOS':False,
     'failure_reasons':['THIS_IS_UNFITTED_PRESPECIFIED_MECHANISM_CYCLE','IN_SAMPLE_FOUR_EXPOSED_MONTHS','NOT_LIVE_DEALER_FILLS']}
  stats.append(r)
  print(json.dumps({k:r[k] for k in ('source','month','policy','attempts','source_completed_tp_first_fraction','quarters','hours','days')},default=str),flush=True)
  (outfolder/f'{pname}_REPLAY_COMPLETE_RECEIPT.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
 (outfolder/'SOURCE_CONTRACT_RECEIPT.json').write_text(json.dumps({'source':source,'mon':mon,'sha256':RAW_PINS[source,mon],
  'source_rows':len(t),'eligible_1s_signals':len(srcs),'fill_valid':int(valid.sum()),
  'utc_full_quarters':len(qt),'utc_ref':int(ref.sum()),'complete':True},indent=2)+'\n')
 return stats


if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=SOURCES,required=True)
 ap.add_argument('--month',choices=MONTHS,required=True)
 ap.add_argument('--policy',choices=POLICIES,default=None)
 args=ap.parse_args()
 run_case(args.source,args.month,policies=(args.policy,) if args.policy else POLICIES)
