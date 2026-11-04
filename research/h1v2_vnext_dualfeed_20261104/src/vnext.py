"""Additive H1V2 VNext research, exact-source multibroker candidate router.

NOT MT5 executable; NO historical OOS or live dealer PnL claims.
Original R24 first_crossing and build_tree are imported byte-exact from pinned
R24 source ZIP SHA 1afb2d42244aa911c580148ff7cfe349a674e28e5c36e7ed328dfec329af0e84.
Original R9 EA/H1V2 engine remains immutable.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,os,sys,time,zipfile
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from numba import njit

BASE=Path(os.environ.get('H1V2_VNEXT_DATA_ROOT','/mnt/data')).resolve()
REPO_R24=Path(__file__).resolve().parents[2]/'h1v2_r23_hourly_causal_20261104'/'frozen_r24_archive'/'source'
R24=REPO_R24 if (REPO_R24/'r24_firstpass_engine.py').is_file() else BASE/'h1v2_vnext'/'frozen_r24'/'source'
if not (R24/'r24_firstpass_engine.py').is_file():raise RuntimeError('ORIGINAL_R24_SOURCE_MISSING: extract frozen SHA-pinned original R24 ZIP before research')
sys.path.insert(0,str(R24))
from r24_firstpass_engine import build_tree,first_crossing  # preserved exact R24 segment tree

MONTHS=('01','02','06','07')
SRC=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
SHA={
 'DUKASCOPY_RAW':{'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2','07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'},
 'MT5_BROKER_EXPORT':{'01':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8','02':'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05','06':'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4','07':'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'}}
REFERENCE={'01':27980,'02':33523,'06':31758,'07':24324}
REFERENCE_ZIP=BASE/'R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip'
FEE_RAW=20;GAP_MS=15000;WARMUP_MS=300000;DELAY_MS=100;FILL_STALE_MS=1000;QUARTER_MS=900000


def sha(path:Path)->str:
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def raw_filename(src:str,mon:str)->Path:
 if src=='DUKASCOPY_RAW':return BASE/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 if src=='MT5_BROKER_EXPORT':return BASE/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
 raise ValueError('UNKNOWN SOURCE '+src)

def load_month(src:str,mon:str):
 """Original source-UTC geometry, preserve full original same-ms ordinal order."""
 p=raw_filename(src,mon)
 if sha(p)!=SHA[src][mon]:raise RuntimeError('RAW_SOURCE_SHA_DRIFT '+str(p))
 if src=='DUKASCOPY_RAW':
  d=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=d.timestamp_ms_utc.to_numpy(copy=True);b=d.bid_raw.to_numpy(copy=True);a=d.ask_raw.to_numpy(copy=True)
 else:
  d=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  offset=(2 if mon in ('01','02') else 3)*3600000
  t=d.time_msc.to_numpy(copy=True)-offset
  b=np.rint(d.bid.to_numpy(copy=True)*1000).astype(np.int32)
  a=np.rint(d.ask.to_numpy(copy=True)*1000).astype(np.int32)
  if mon=='06':
   july=raw_filename(src,'07')
   if sha(july)!=SHA[src]['07']:raise RuntimeError('BROKER_JULY_HALO_SHA_DRIFT')
   hd=pd.read_csv(july,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
   jt=hd.time_msc.to_numpy(copy=True)-3*3600000
   lim=int(datetime(2026,7,1,tzinfo=timezone.utc).timestamp()*1000)+60000
   mask=(jt>t[-1])&(jt<=lim)
   if not mask.any() or jt[mask][0]-t[-1]<=GAP_MS:raise RuntimeError('ORIGINAL_JUNE_TAIL_HALOGAP_MISMATCH')
   t=np.r_[t,jt[mask]];b=np.r_[b,np.rint(hd.bid.to_numpy(copy=True)[mask]*1000).astype(np.int32)];a=np.r_[a,np.rint(hd.ask.to_numpy(copy=True)[mask]*1000).astype(np.int32)]
 if len(t)==0 or np.any(np.diff(t)<0) or np.any(a<b):raise RuntimeError('BAD_SOURCE_QUOTES')
 return t,b,a

def quota(mon:str):
 if not REFERENCE_ZIP.is_file():raise RuntimeError('ORIGINAL_R23_QUARTER_SOURCE_ZIP_NOT_PRESENT')
 with zipfile.ZipFile(REFERENCE_ZIP) as z:
  with z.open(f'results/R23_DUKASCOPY_RAW_{mon}_COMPLETE_QUARTERS.csv') as f:
   r=pd.read_csv(f,usecols=['scenario','utc_quarter','original_R9_SYNTH_reference'])
 r=r[r.scenario=='A1_TP050_STOP100_H60_CAP4000_Q8']
 epoch=pd.to_datetime(r.utc_quarter,utc=True).astype('int64').to_numpy()//1000000
 count=r.original_R9_SYNTH_reference.to_numpy(np.int32)
 expected={'01':2976,'02':2688,'06':2880,'07':2976}[mon]
 if len(count)!=expected or int(count.sum())!=REFERENCE[mon] or len(np.unique(epoch))!=expected or not np.all(np.diff(epoch)==QUARTER_MS):raise RuntimeError('REFERENCE_DRIFT')
 return epoch,count

def first_seconds(t,b,a,src,clock_ms=1000):
 ix=np.flatnonzero(np.r_[True,np.diff(t//clock_ms)!=0]).astype(np.int32)
 gaps=np.flatnonzero(np.diff(t)>GAP_MS).astype(np.int32)+1
 epoch=np.r_[0,gaps]
 pos=np.searchsorted(epoch,ix,side='right')-1
 age=t[ix]-t[epoch[pos]]
 spread=(a[ix].astype(np.int64)-b[ix])
 cap=8000 if src=='DUKASCOPY_RAW' else 4000
 mask=(age>=WARMUP_MS)&(spread>=0)&(spread<=cap)
 return ix[mask],gaps,age[mask]

def prefix_features(t,b,a,si,ages):
 """ONLY actual quote ordinals <= signal. All horizons are backward-looking."""
 n=len(si);ts=t[si];mid=b.astype(np.int64)+a.astype(np.int64)
 out=np.zeros((n,23),np.float32)
 spread=(a[si].astype(np.int64)-b[si]);out[:,0]=spread
 prev=np.maximum(si-1,0)
 out[:,1]=(a[prev].astype(np.int64)-b[prev])-spread  # spread compression positive
 out[:,2]=ages/1000.0
 win=(3000,15000,60000,300000,900000,3600000)
 for h,w in enumerate(win):
  j=np.searchsorted(t,ts-w,side='right')-1
  j=np.maximum(j,0)
  assert np.all(j<=si) and np.all(t[j]<=ts)
  out[:,3+h]=((mid[si]-mid[j])*0.5).astype(np.float32)
  out[:,9+h]=(si-j).astype(np.float32)
 # instantaneous bid-ask motion divergence, absolute quote event rate & weekday
 j3=np.maximum(np.searchsorted(t,ts-3000,side='right')-1,0)
 out[:,15]=(b[si].astype(np.int64)-b[j3])-(a[si].astype(np.int64)-a[j3])
 out[:,16]=((mid[si]-mid[prev])*0.5).astype(np.float32)
 out[:,17]=(a[si].astype(np.int64)-b[si])/(20.0+np.abs(out[:,5]))
 out[:,18]=out[:,9]/3.0
 out[:,19]=np.sin(2*np.pi*(ts//3600000%24)/24)
 out[:,20]=np.cos(2*np.pi*(ts//3600000%24)/24)
 out[:,21]=(ts//86400000+3)%7
 out[:,22]=np.minimum((ts-t[prev]).astype(np.float32),300000)
 return out

def _sign(v):return np.sign(v).astype(np.int8)

def policy(features,src:str,cycle:int):
 """Foresight-free three-stage structural/flow/regime routing; genuine WAIT=-1."""
 n=len(features);sp=features[:,0];s3=features[:,3];s15=features[:,4];s60=features[:,5];s300=features[:,6];s900=features[:,7];s3600=features[:,8]
 density=features[:,10];qrate=features[:,18];tight=features[:,1]>0
 # All quantities measured at source signal or earlier. Always compare
 # direction against *observed local quoted-price spread*, no absolute thresholds shared by broker.
 broker_scale=1.40 if src=='DUKASCOPY_RAW' else .60
 req=broker_scale*(sp+80)
 quiet_spread=(sp<=(4000 if src=='DUKASCOPY_RAW' else 1250))
 htf=np.sign(s900+s3600*.35)
 trend=np.sign(s60+0.60*s300)
 side=np.full(n,-1,np.int8);strength=np.zeros(n,np.float32)
 # Cycle A: old 15m/1h direction + 3s pullback reclaim, not naive 3s sign.
 pull=(np.sign(s15)!=np.sign(s3))&(np.sign(s15)==trend)&(np.sign(s15)!=0)&(np.abs(s15)>=req)&(density>=2)
 sc_a=np.where(pull,(np.abs(s15)-broker_scale*sp)/(100+sp)+np.minimum(np.abs(s60),2000)/(2000+sp),-100).astype(np.float32)
 sd_a=np.where(s15>0,0,1).astype(np.int8)
 # Cycle B: dual Bid/Ask leadership & compressed-spread impulse with
 # 15s + 60s alignment. Strong 3s motion is not enough without 60s confirmation.
 imp=(np.sign(s3)==np.sign(s15))&(np.sign(s15)==np.sign(s60))&(np.sign(s3)!=0)&(np.abs(s3)>=.7*req)&(qrate>=1)
 sc_b=np.where(imp,np.abs(s3)/(sp+100)+np.minimum(np.abs(s15),3000)/(sp+3000)+np.maximum(features[:,15],0)/(sp+100),-100).astype(np.float32)
 sd_b=np.where(s3>0,0,1).astype(np.int8)
 # Cycle C: composite head: 15m/1h trend vote + mean-reverting microburst,
 # choose strongest (A or B) or HTF-aligned flow reacceleration; optional WAIT.
 long_vote=(htf==trend)&(trend!=0)&(np.sign(s15)==trend)&(np.abs(s300)>=2*req)&(np.abs(s3)>=.35*req)
 sc_c=np.where(long_vote,np.abs(s300)/(sp+1600)+np.abs(s15)/(sp+1000),-100).astype(np.float32)
 sd_c=np.where(trend>0,0,1).astype(np.int8)
 if cycle==1:
  sel=sc_a;choose=sd_a;floor=.20 if src=='DUKASCOPY_RAW' else .08
 elif cycle==2:
  sel=sc_b;choose=sd_b;floor=.25 if src=='DUKASCOPY_RAW' else .10
 elif cycle==3:
  st=np.stack((sc_a,sc_b,sc_c),axis=1)
  arg=np.argmax(st,axis=1)
  sel=st[np.arange(n),arg];choose=np.where(arg==0,sd_a,np.where(arg==1,sd_b,sd_c)).astype(np.int8)
  floor=.30 if src=='DUKASCOPY_RAW' else .12
 else:raise ValueError('UNKNOWN EXPERIMENT CYCLE')
 allow=quiet_spread&(sel>floor)
 # broker-adaptive side selection; stop and target scale with observed local
 # spread+past price motion, not with future reachability or quota.
 side[allow]=choose[allow];strength=sel
 vol=np.maximum(np.maximum(np.abs(s3),np.abs(s15)*.35),70)
 if cycle==1:
  h=np.full(n,30000 if src=='MT5_BROKER_EXPORT' else 60000,np.int32)
  stop=np.maximum(100,np.rint(.55*sp+.45*vol)).astype(np.int32)
  tp=np.maximum(100,np.rint(.22*vol)).astype(np.int32)
 elif cycle==2:
  h=np.where(sp>1000,90000,30000).astype(np.int32)
  stop=np.maximum(150,np.rint(.65*sp+.35*vol)).astype(np.int32)
  tp=np.maximum(100,np.rint(.30*vol)).astype(np.int32)
 else:
  h=np.where((sp>1200)|(qrate<5),90000,np.where(qrate>30,15000,30000)).astype(np.int32)
  stop=np.maximum(120,np.rint(.60*sp+.40*vol)).astype(np.int32)
  tp=np.maximum(100,np.rint(.25*vol)).astype(np.int32)
 h=np.clip(h,15000,90000).astype(np.int32)
 # Protect against distorted extreme rare price regimes.
 stop=np.clip(stop,100,6000).astype(np.int32);tp=np.clip(tp,100,4000).astype(np.int32)
 return side,h,tp,stop,strength

@njit(cache=False)
def replay_positions(t,b,a,si,fi,side,hor,tp,stop,size,bmax,bmin,amax,amin,gaps,slip=0,fee=20):
 """Original R24 exact first observed crossing, with source gap censor.

 Output source ordinals are signal, fill, actual exit and raw PnL; code:
  1 TARGET; 0 STOP; 2 TIMEOUT; 3 CENSORED; 4 UNFILLED.
 Unknown canceled positions are not a dealer-flat certificate. Reentry is
 optimistic after next observed quote gap + 300sec warmup (research ONLY).
 """
 n=len(si);result=np.full((n,7),-1,np.int64)
 last_exit_ms=np.int64(-9223372036854775000);w=0
 for k in range(n):
  if side[k]<0 or t[si[k]]<=last_exit_ms:continue
  f=fi[k]
  if f<0:
   result[w,0]=si[k];result[w,1]=-1;result[w,2]=-1;result[w,3]=4;result[w,4]=side[k];result[w,5]=hor[k];result[w,6]=0;w+=1
   continue
  if t[f]<=last_exit_ms:continue
  max_t=t[f]+hor[k]
  hlimit=np.searchsorted(t,max_t,side='right')
  end=np.searchsorted(t,max_t,side='left')
  gp=np.searchsorted(gaps,f+1,side='left')
  gix=gaps[gp] if gp<len(gaps) else len(t)
  right=min(hlimit,gix)
  s=side[k]
  if s==0:
   price_target=np.int64(a[f])+fee+2*slip+tp[k]
   price_stop=np.int64(b[f])-stop[k]
   event,cause=first_crossing(bmax,bmin,size,f+1,right,price_target,price_stop)
  else:
   price_target=np.int64(b[f])-fee-2*slip-tp[k]
   price_stop=np.int64(a[f])+stop[k]
   event,rawcause=first_crossing(amax,amin,size,f+1,right,price_stop,price_target)
   cause=0 if rawcause==1 else (1 if rawcause==0 else -1)
  ex=-1;net=0;code=-1
  if event>=0:
   ex=event;code=cause
  elif end>=len(t) or gix<=end or (end>f and t[end]-t[end-1]>15000):
   code=3
   ex=gix-1 if gix<len(t) else len(t)-1
  else:
   code=2;ex=end
  if ex<f:raise ValueError('INVALID_CAUSAL_EXIT_ORDINAL')
  if code!=3:
   net=(np.int64(b[ex])-a[f]-fee-2*slip) if s==0 else (np.int64(b[f])-a[ex]-fee-2*slip)
   last_exit_ms=t[ex]
  else:
   # A conservative HOLD on the quote hiatus; NOT a dealer execution proof.
   last_exit_ms=(t[gix]+300000) if gix<len(t) else t[-1]
  result[w,0]=si[k];result[w,1]=f;result[w,2]=ex;result[w,3]=code;result[w,4]=s;result[w,5]=hor[k];result[w,6]=net;w+=1
 return result[:w]

def source_replay(t,b,a,si,side,h,tp,stop,gaps,src,slip=0,limit_tree=None):
 if limit_tree is None:tree=build_tree(b,a)
 else:tree=limit_tree
 target=t[si]+DELAY_MS
 fi=np.searchsorted(t,target,side='left').astype(np.int32)
 valid=fi<len(t);safe=np.minimum(fi,len(t)-1)
 valid&=(t[safe]-target<=FILL_STALE_MS)&(t[safe]>t[si])
 cap=8000 if src=='DUKASCOPY_RAW' else (4000 if src=='MT5_BROKER_EXPORT' else -1)
 valid&=(a[safe]>=b[safe])&((a[safe].astype(np.int64)-b[safe])<=cap)
 fi[~valid]=-1
 return replay_positions(t,b,a,si,fi,side,h,tp,stop,*tree,gaps,slip,FEE_RAW)

def source_report(src,mon,cycle,t,results,ep,ref):
 """Full UTC quarter/hour/day calendar, including no-reference periods.
 Period metrics from *completed actual quote-index positions* only; censored
 remains UNKNOWN and is never scored as a win.
 """
 years=2026; qs=ep.copy();n=len(ep)
 qcount=np.zeros(n,np.int32);qtarget=np.zeros(n,np.int32);qstop=np.zeros(n,np.int32);qtimeout=np.zeros(n,np.int32);qcensor=np.zeros(n,np.int32);qunfilled=np.zeros(n,np.int32);qpnl=np.zeros(n,np.int64)
 if len(results):
  f=results[:,1];sig=results[:,0];idx=np.where(f>=0,f,sig)
  key=t[idx]//QUARTER_MS*QUARTER_MS
  ix=np.searchsorted(qs,key);ok=(ix<n)&(qs[np.minimum(ix,n-1)]==key)
  for code,target in [(1,qtarget),(0,qstop),(2,qtimeout),(3,qcensor),(4,qunfilled)]:
   mask=ok&(results[:,3]==code);target[:]=np.bincount(ix[mask],minlength=n)
  completed=ok&np.isin(results[:,3],np.array([0,1,2],np.int64))
  qcount[:]=np.bincount(ix[completed],minlength=n)
  qpnl[:]=np.bincount(ix[completed],weights=results[completed,6],minlength=n).astype(np.int64)
 if n%96:raise RuntimeError('EXPECTED_WHOLE_UTC_DAYS')
 def fold(a,k):return np.add.reduceat(a,np.arange(0,n,k))
 groups={}
 for typ,k in [('quarter',1),('hour',4),('day',96),('month',n)]:
  rc=fold(ref,k);vol=fold(qcount,k);wins=fold(qtarget,k);loss=fold(qstop,k);tout=fold(qtimeout,k);cens=fold(qcensor,k);unfill=fold(qunfilled,k);nraw=fold(qpnl,k)
  correct=np.divide(wins,vol,out=np.zeros(len(vol),np.float64),where=vol>0)
  active=rc>0;joint=active&(vol>=rc)&(correct>=.8)
  keytimes=pd.to_datetime(ep[::k],unit='ms',utc=True).strftime('%Y-%m-%dT%H:%M:%SZ')
  frame=pd.DataFrame({'source':src,'month':mon,'cycle':cycle,'utc_'+typ:keytimes,'R9_SYNTH_reference':rc,'completed_filled':vol,'target_first':wins,'stop_first':loss,'timeout':tout,'censored':cens,'unfilled':unfill,'completed_precision':np.where(vol>0,correct,np.nan),'source_net_quote_raw':nraw,'r9_count_met':active&(vol>=rc),'atleast_80pct_target_correct':active&(vol>0)&(correct>=.8),'joint_correct_count_met':joint,'R9_reference_active':active})
  groups[typ]=frame
 return groups

def run(src,mon,cycles=(1,2,3),outroot=BASE/'h1v2_vnext'/'results'):
 if src not in SRC or mon not in MONTHS:raise ValueError('INVALID_SOURCE_MONTH')
 began=time.perf_counter();ep,ref=quota(mon);t,b,a=load_month(src,mon);si,gaps,ages=first_seconds(t,b,a,src)
 feature=prefix_features(t,b,a,si,ages)
 # Freeze feature array entirely before the next replay: no future label or original R9 reference is ever passed to policy().
 tree=build_tree(b,a)
 summaries=[]
 work=outroot/src/mon;work.mkdir(parents=True,exist_ok=True)
 for cyc in cycles:
  side,hor,tp,stop,score=policy(feature,src,cyc)
  result=source_replay(t,b,a,si,side,hor,tp,stop,gaps,src=src,limit_tree=tree)
  group=source_report(src,mon,cyc,t,result,ep,ref)
  paths={}
  for key,g in group.items():
   path=work/f'VNEXT_C{cyc}_{src}_{mon}_FULL_UTC_{key.upper()}.csv';g.to_csv(path,index=False);paths[path.name]={'bytes':path.stat().st_size,'sha256':sha(path),'rows':len(g)}
  trace=work/f'VNEXT_C{cyc}_{src}_{mon}_FULL_SOURCE_SELECTED_TRADE_ORDINALS.npz'
  np.savez_compressed(trace,source_quote_signal_ordinal=result[:,0],source_quote_fill_ordinal=result[:,1],source_quote_exit_ordinal=result[:,2],class_code=result[:,3],side_buy0_sell1=result[:,4],intended_horizon_ms=result[:,5],source_realized_net_raw=result[:,6])
  paths[trace.name]={'bytes':trace.stat().st_size,'sha256':sha(trace),'rows':len(result)}
  qs=group['quarter'];hs=group['hour'];day=group['day'];one=group['month'].iloc[0]
  counters=np.bincount(np.maximum(result[:,3],0),minlength=5)
  rec={'source':src,'mon':mon,'cycle':cyc,'contract':'exact-first-observed-bidask+100ms+1000ms_stale+strict_oneposition+15s_gap_censor+300s_rewarm','raw_original_SHA':SHA[src][mon],
       'quote_rows':len(t),'source_first_1s_eligible_after_300s_warmup':len(si),'asof_entry_nonWAIT':int(np.count_nonzero(side>=0)),
       'completed_total':int(one.completed_filled),'original_R9_SYNTH_month_ref':int(ref.sum()),'correct_target':int(one.target_first),
       'stops':int(one.stop_first),'timeouts':int(one.timeout),'censored':int(one.censored),'unfilled':int(one.unfilled),
       'completed_precision':float(one.completed_precision) if np.isfinite(one.completed_precision) else None,'net_quote_raw_sum':int(one.source_net_quote_raw),
       'active_quarters':int(qs.R9_reference_active.sum()),'quarter_count_met':int(qs.r9_count_met.sum()),'quarter_accuracy_80':int(qs.atleast_80pct_target_correct.sum()),'quarter_joint':int(qs.joint_correct_count_met.sum()),
       'active_hours':int(hs.R9_reference_active.sum()),'hour_count_met':int(hs.r9_count_met.sum()),'hour_accuracy_80':int(hs.atleast_80pct_target_correct.sum()),'hour_joint':int(hs.joint_correct_count_met.sum()),
       'active_days':int(day.R9_reference_active.sum()),'day_count_met':int(day.r9_count_met.sum()),'day_accuracy_80':int(day.atleast_80pct_target_correct.sum()),'day_joint':int(day.joint_correct_count_met.sum()),
       'all_zero_reference_buckets_retained':True,'not_a_real_broker_fill':True,'research_in_sample_exposed':True,'no_original_EA_modification':True,'paths':paths}
  record=work/f'VNEXT_C{cyc}_{src}_{mon}_RESEARCH_RECEIPT.json';record.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n');summaries.append(rec)
  print(json.dumps({k:v for k,v in rec.items() if k in ('source','mon','cycle','quote_rows','completed_total','original_R9_SYNTH_month_ref','correct_target','stops','timeouts','censored','completed_precision','net_quote_raw_sum','hour_joint','quarter_joint','day_joint')}),flush=True)
 index=work/f'VNEXT_{src}_{mon}_THREE_CYCLES_INDEX.json';index.write_text(json.dumps({'cases':summaries,'seconds':time.perf_counter()-began},indent=2,allow_nan=False)+'\n')
 return summaries

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=SRC,required=True);ap.add_argument('--month',choices=MONTHS,required=True);ap.add_argument('--cycles',nargs='+',type=int,default=(1,2,3));x=ap.parse_args();run(x.source,x.month,cycles=tuple(x.cycles))
if __name__=='__main__':main()
