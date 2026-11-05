"""True source quote-ordinal causal action replay, full UTC month/day/hour/quarter.
All benchmark quota joins happen AFTER actual policy decisions and replay.
"""
from __future__ import annotations
import csv,hashlib,json,zipfile,sys,os
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from source import source_month, source_candidates,sample_features,PINS
from r26_mechanisms import choose_actions,NAME

ROOT=Path('/mnt/data')
R=ROOT/'r26'
R23=ROOT/'R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip'
FEE=20;FILL_LAG=100;MAX_LATE=1000;QUOTE_GAP=15000


def calendar(mon):
 with zipfile.ZipFile(R23) as z:
  path=f'results/R23_DUKASCOPY_RAW_{mon}_COMPLETE_QUARTERS.csv'
  with z.open(path) as fi:d=pd.read_csv(fi,low_memory=False)
 sub=d[d.scenario=='A1_TP050_STOP100_H60_CAP4000_Q8'].copy()
 q=np.array(pd.to_datetime(sub.utc_quarter,utc=True).astype('int64')//1000000,dtype=np.int64)
 refs=sub.original_R9_SYNTH_reference.to_numpy(np.int32)
 expect={'01':(2976,27980),'02':(2688,33523),'06':(2880,31758),'07':(2976,24324)}[mon]
 assert len(q)==expect[0] and int(refs.sum())==expect[1]
 assert len(np.unique(q))==len(q) and np.all(np.diff(q)==900000)
 return q,refs


@njit(cache=False)
def replay_quotes(ts,bid,ask,signal_idx,first_fill,signal_side,net_tp,stop_distance,horizon_ms,max_start_ms):
 """One position across all UTC boundaries. First actual quote fill after lag.
 NO future information used for side or static stop/target/horizon selection.
 First crossing checked after each actual source ordinal. A source observation
 drought >15s makes dealer exit unknown; position quarantined 300s after next
 observed quote. NO fabricated exit quote/cash payoff on censored positions.
 Entry unfilled: no position taken and can try next observed signal.
 1 TARGET; 0 STOP; 2 TIMEOUT; 3 CENSORED; 4 UNFILLED.
 """
 n=len(signal_idx)
 out=np.empty((n,11),np.int64);k=0;last_exit_ms=-9223372036854775000
 for j in range(n):
  si=signal_idx[j]
  if ts[si]>=max_start_ms:break
  if ts[si]<=last_exit_ms:continue
  s=signal_side[j]
  if s==0:continue
  fi=first_fill[j]
  if fi<0:
   out[k,0]=si;out[k,1]=-1;out[k,2]=-1;out[k,3]=s;out[k,4]=4
   out[k,5]=0;out[k,6]=net_tp[j];out[k,7]=stop_distance[j]
   out[k,8]=horizon_ms[j];out[k,9]=-2147483647;out[k,10]=-1
   k+=1;continue
  # Quote cap / first actual +100ms are computed prior to this function;
  # source time remains true quote ordinal. One position from first actual fill.
  time_exit=ts[fi]+horizon_ms[j]
  stop=stop_distance[j];tp=net_tp[j]
  buy=(s==1)
  low=int(bid[fi])-stop
  high=int(ask[fi])+stop
  target_hi=int(ask[fi])+FEE+tp
  target_lo=int(bid[fi])-FEE-tp
  ix=fi+1;status=3;exit_ix=-1;net=-2147483647
  while ix<len(ts):
   if ts[ix]-ts[ix-1]>QUOTE_GAP:
    # No assumed execution during unobserved drought; broker position UNKNOWN.
    # Cannot reenter until source has restarted for >=300s; no cash PnL.
    status=3;exit_ix=ix;last_exit_ms=ts[ix]+300000;break
   # Scientific F02 repair: a quote strictly AFTER the predeclared H
   # cannot be relabelled in-horizon TP/STOP (first observed time exit).
   # GAP is checked first; exact t == H remains a legal in-horizon hit.
   if ts[ix]>time_exit:
    status=2;exit_ix=ix;last_exit_ms=ts[ix]
    net=(int(bid[ix])-int(ask[fi])-FEE) if buy else (int(bid[fi])-int(ask[ix])-FEE)
    break
   if buy:
    if int(bid[ix])<=low:status=0
    elif int(bid[ix])>=target_hi:status=1
   else:
    if int(ask[ix])>=high:status=0
    elif int(ask[ix])<=target_lo:status=1
   if status==0 or status==1:
    exit_ix=ix;last_exit_ms=ts[ix]
    net=(int(bid[ix])-int(ask[fi])-FEE) if buy else (int(bid[fi])-int(ask[ix])-FEE)
    break
   if ts[ix]>=time_exit:
    status=2;exit_ix=ix;last_exit_ms=ts[ix]
    net=(int(bid[ix])-int(ask[fi])-FEE) if buy else (int(bid[fi])-int(ask[ix])-FEE)
    break
   ix+=1
  if exit_ix<0:
   status=3;last_exit_ms=ts[-1]
  out[k,0]=si;out[k,1]=fi;out[k,2]=exit_ix;out[k,3]=s;out[k,4]=status
  out[k,5]=ts[fi];out[k,6]=tp;out[k,7]=stop
  out[k,8]=horizon_ms[j];out[k,9]=net;out[k,10]=int(ask[fi])-int(bid[fi])
  k+=1
 return out[:k]


def fills(t,b,a,ids,cap=4000):
 delay=t[ids]+FILL_LAG
 f=np.searchsorted(t,delay,side='left').astype(np.int32)
 good=f<len(t)
 safe=np.minimum(f,len(t)-1)
 good&=(t[safe]-delay<=MAX_LATE)&(t[safe]>=delay)&(a[safe]>=b[safe])&(a[safe]-b[safe]<=cap)
 return np.where(good,f,-1).astype(np.int32)


def classify_and_save(m,source,i,t,b,a,q,ref,signal_idx,actions,firstfill,out):
 root=R/'results'/source/m/NAME[i]
 root.mkdir(parents=True,exist_ok=True)
 file_sha=lambda p:hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
 monthstart=int(q[0]);monthend=int(q[-1]+900000)
 st=out[:,4];valid=out[:,1]>=0;known=valid&(st!=3)&(st!=4)
 fillout=out[valid,5];ind=(fillout//900000-q[0]//900000).astype(np.int64)
 assert np.all((ind>=0)&(ind<len(ref)))
 def count(mask):
  return np.bincount(ind[mask[valid]],minlength=len(ref)).astype(np.int32)
 filled=count(valid); # counts selected real quote fills including censored
 good=count(st==1);bad=count(st==0);timeout=count(st==2);censor=count(st==3)
 completed=good+bad+timeout
 # source successful trade strict target-first; unknown has no claim.
 accuracy=np.divide(good,completed,out=np.zeros(len(ref),np.float64),where=completed>0)
 pct_correct80=(accuracy>=.8)&(completed>0)
 qpassvol=(ref>0)&(completed>=ref)
 qpass=(qpassvol)&pct_correct80
 # use observed quote-price net only for known actual exits
 net=np.zeros(len(ref),np.int64)
 for c,x in zip(ind[known[valid]],out[known,9]):net[c]+=int(x)
 # Original calendar includes zero-R9 period, so source positions may be real.
 data=[]
 start=datetime.fromtimestamp(monthstart/1000,timezone.utc)
 for scope,rows_per in [('QUARTER',1),('HOUR',4),('DAY',96)]:
  assert len(ref)%rows_per==0
  shape=(-1,rows_per)
  r=ref.reshape(shape).sum(axis=1)
  ff=filled.reshape(shape).sum(axis=1)
  cc=completed.reshape(shape).sum(axis=1)
  gg=good.reshape(shape).sum(axis=1)
  bb=bad.reshape(shape).sum(axis=1)
  tt=timeout.reshape(shape).sum(axis=1)
  xx=censor.reshape(shape).sum(axis=1)
  nn=net.reshape(shape).sum(axis=1)
  p=np.divide(gg,cc,out=np.zeros(len(r),np.float64),where=cc>0)
  vol=(r>0)&(cc>=r)
  prec=(r>0)&(cc>0)&(p>=.8)
  joint=vol&prec
  path=root/f'R26_{source}_{m}_{NAME[i]}_ALL_{len(r)}_UTC_{scope}_SOURCE_OUTCOMES.csv'
  with path.open('w',newline='') as fh:
   w=csv.writer(fh)
   w.writerow(['source','month','policy','UTC_period_start','original_R9_SYNTH_UTC_reference','actually_filled','completed_eligible_excluding_gap_and_unfilled','TARGET_FIRST','STOP_FIRST','TIMEOUT','GAP_CENSORED','completed_strict_first_target_fraction','known_net_quoted_price_raw_NOT_ACCOUNT_CASH','source_reference_active','original_quota_count_pass','strict_80pct_precision_pass','joint_80pct_AND_original_R9_quota_pass','not_broker_dealer_fill'])
   for k in range(len(r)):
    date=pd.to_datetime(int(q[k*rows_per]),unit='ms',utc=True).isoformat()
    w.writerow([source,f'2026-{m}',NAME[i],date,int(r[k]),int(ff[k]),int(cc[k]),int(gg[k]),int(bb[k]),int(tt[k]),int(xx[k]),float(p[k]) if cc[k] else '',int(nn[k]),int(r[k]>0),int(vol[k]) if r[k] else '',int(prec[k]) if r[k] else '',int(joint[k]) if r[k] else '',True])
  data.append((scope,path,int((r>0).sum()),int(vol.sum()),int(prec.sum()),int(joint.sum()),int(r.sum()),int(cc.sum()),int(gg.sum()),int(nn.sum())))
 tr=root/f'R26_{source}_{m}_{NAME[i]}_ALL_ACCEPTED_AND_UNFILLED_EXACT_SOURCE_QUOTE_ORDINALS.npz'
 np.savez_compressed(tr,signal_ordinal=out[:,0],fill_ordinal=out[:,1],exit_ordinal=out[:,2],buy1_sellminus1=out[:,3].astype(np.int8),outcome_code_1TARGET_0STOP_2TIMEOUT_3UNKNOWN_4UNFILLED=out[:,4].astype(np.int8),fill_utc_ms=out[:,5],target_net_raw=out[:,6].astype(np.int32),stop_adverse_from_open_liq_raw=out[:,7].astype(np.int32),horizon_ms=out[:,8].astype(np.int32),known_net_quote_raw_unknown_minus2147483647=out[:,9],fill_source_spread_raw=out[:,10].astype(np.int32))
 bad_out=out[:,4]
 receipt={
  'source':source,'month':m,'source_raw_sha256':PINS[(source,m)],'policy':NAME[i],
  'root_calendar_utc_quarters':len(ref),'root_calendar_utc_hours':len(ref)//4,'root_calendar_utc_days':len(ref)//96,
  'original_R9_SYNTH_corrected_month_reference':int(ref.sum()),
  'preselected_first_per_second_asof_candidates':len(signal_idx),
  'policy_asof_proposals':int(np.count_nonzero(actions.side[i])),
  'replay_attempts_including_unfilled':len(out),
  'true_actual_quote_fills':int(valid.sum()),'TARGET_FIRST':int((bad_out==1).sum()),
  'STOP_FIRST':int((bad_out==0).sum()),'TIMEOUT':int((bad_out==2).sum()),
  'GAP_CENSORED_UNKNOWN_PNL':int((bad_out==3).sum()),'UNFILLED':int((bad_out==4).sum()),
  'known_quote_price_net_raw_excluding_censored':int(out[known,9].sum()),
  'model_is_deterministic_asof_not_fitted':True,'R9_quota_used_only_after_replay':True,
  'broker_Coinexx_actual_dealer_fill_verified':False,'historical_news_verified':False,
  'strict_quarters':{'active':data[0][2],'volume':data[0][3],'precision':data[0][4],'joint':data[0][5]},
  'strict_hours':{'active':data[1][2],'volume':data[1][3],'precision':data[1][4],'joint':data[1][5]},
  'strict_days':{'active':data[2][2],'volume':data[2][3],'precision':data[2][4],'joint':data[2][5]},
  'full_original_month_completed_count_quota_met':bool(len(out[known])>=ref.sum()),
  'full_original_month_target_fraction':(int((bad_out==1).sum())/max(int(known.sum()),1)),
  'files':{p.name:{'sha256':file_sha(p),'bytes':p.stat().st_size} for p in [*(d[1] for d in data),tr]}
 }
 path=root/f'R26_{source}_{m}_{NAME[i]}_SOURCE_SHA_AND_SCIENCE_RECEIPT.json'
 path.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt


def run(source,mon,verify_sha=True,only_policy=None):
 t,b,a=source_month(source,mon,verify_sha=verify_sha)
 q,ref=calendar(mon)
 ix=source_candidates(t,b,a,mon,source)
 f=sample_features(t,b,a,ix)
 actions=choose_actions(f,source)
 firstfill=fills(t,b,a,ix)
 reports=[]
 for i in (range(len(NAME)) if only_policy is None else [int(only_policy)]):
  output=replay_quotes(t,b,a,ix,firstfill,actions.side[i],actions.net_target[i],actions.stop_dist[i],actions.horizon_ms[i],int(q[-1]+900000))
  result=classify_and_save(mon,source,i,t,b,a,q,ref,ix,actions,firstfill,output)
  reports.append(result)
  print('CASE_EXACT',json.dumps({k:result[k] for k in ['source','month','policy','true_actual_quote_fills','TARGET_FIRST','STOP_FIRST','TIMEOUT','GAP_CENSORED_UNKNOWN_PNL','known_quote_price_net_raw_excluding_censored','strict_quarters','strict_hours','strict_days']}),flush=True)
 return reports

if __name__=='__main__':
 if len(sys.argv) not in (3,4):raise SystemExit('python r26_replay.py DUKASCOPY_RAW 01 [optional_policy_index_0to5]')
 run(sys.argv[1],sys.argv[2],only_policy=(int(sys.argv[3]) if len(sys.argv)==4 else None))
