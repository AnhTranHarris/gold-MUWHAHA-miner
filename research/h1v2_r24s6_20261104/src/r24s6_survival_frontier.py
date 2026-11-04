"""R24S6 add-only original-quote initial holding-time survivability diagnostics.

Separate independent evidence classes:
A. position remains without a liquidation-side adverse stop until its first observed
   exit quote >= requested minimum holding horizon (15/30/60s);
B. within first H seconds, observed price reaches original nominal +$0.10 after fee
   and (A) remains true. This is stricter than original R24 first TARGET then exit;
C. hindsight any-good-side fixed-H single-position cardinality upper (not a policy);
D. real past-only bid/ask-movement BUY/SELL side policies, admitting ALL their
   candidate signals before knowing future outcome and retaining all failures.
No future label is permitted in the as-of side or in input candidate eligibility.
Each varied stop is a NEW risk contract; not original R9 or deployed EA.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0, '/mnt/data/h1v2_r24_asof/source')
import r24_firstpass_engine as e
ROOT=Path('/mnt/data/h1v2_r24s6')
FEE=20;TP=100;GAP=15000;Q=900000
HOLDS=(15,30,60);STOPS=(100,250,500,1000,2000)

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

@njit(cache=False)
def query_extrema(size, ibmax,ibmin,iamax,iamin,l,r):
 maxbid=-2147483647;minbid=2147483647;maxask=-2147483647;minask=2147483647
 l+=size;r+=size
 while l<r:
  if l&1:
   maxbid=max(maxbid,ibmax[l]);minbid=min(minbid,ibmin[l]);maxask=max(maxask,iamax[l]);minask=min(minask,iamin[l]);l+=1
  if r&1:
   r-=1;maxbid=max(maxbid,ibmax[r]);minbid=min(minbid,ibmin[r]);maxask=max(maxask,iamax[r]);minask=min(minask,iamin[r])
  l//=2;r//=2
 return minbid,maxbid,minask,maxask

@njit(cache=False)
def evaluated_horizon(t,b,a,fi,end,cover,side_shadow,stop_values,sz,bmax,bmin,amax,amin):
 n=len(fi);K=len(stop_values)
 fillvalid=np.zeros(n,np.bool_);safe=np.zeros((K,n,2),np.bool_);strict_tp=np.zeros((K,n,2),np.bool_)
 shadow_success=np.zeros((K,n),np.bool_);shadow_strict=np.zeros((K,n),np.bool_)
 for i in range(n):
  if not cover[i]:continue
  f=fi[i];j=end[i]
  if f<0 or j<=f or j>=len(t):continue
  mb,xb,ma,xa=query_extrema(sz,bmax,bmin,amax,amin,f+1,j+1)
  # Target extrema must occur before the requested horizon, not at a later exit tick.
  tb,ub,ta,va=query_extrema(sz,bmax,bmin,amax,amin,f+1,j)
  fillvalid[i]=True
  bp=(ub>=int(a[f])+FEE+TP)
  sp=(ta<=int(b[f])-FEE-TP)
  for k in range(K):
   st=stop_values[k]
   bs=mb>int(b[f])-st
   ss=xa<int(a[f])+st
   safe[k,i,0]=bs;safe[k,i,1]=ss
   strict_tp[k,i,0]=bs and bp;strict_tp[k,i,1]=ss and sp
   si=side_shadow[i]
   if si==1:
    shadow_success[k,i]=bs;shadow_strict[k,i]=bs and bp
   elif si==-1:
    shadow_success[k,i]=ss;shadow_strict[k,i]=ss and sp
 return fillvalid,safe,strict_tp,shadow_success,shadow_strict

@njit(cache=False)
def fixed_hold_earliest(tfill,eligible,h):
 """Exact maximum cardinality under identical reservation H; prefix sorted fills."""
 sel=np.zeros(len(tfill),np.bool_);last=np.int64(-9223372036854775807)
 for i in range(len(tfill)):
  if eligible[i] and tfill[i]>last:
   sel[i]=True;last=tfill[i]+h
 return sel

def csvwrite(path,rows):
 if not rows:raise ValueError('NO_ROWS')
 with open(path,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run(source,mon):
 start=time.monotonic();out=ROOT/'results'/source/mon;out.mkdir(parents=True,exist_ok=True)
 pin=e.source_pin(source,mon)
 t,b,a=e.raw_month(source,mon,verify=True)
 stem=e.R24/'results'/source/mon/f'R24_{source}_{mon}_1000MS'
 signal=np.load(str(stem)+'_source_quote_ordinal.npy',mmap_mode='r')
 fills=np.load(str(stem)+'_fill_source_quote_ordinal.npy',mmap_mode='r')
 feats=np.load(str(stem)+'_features.npy',mmap_mode='r')
 receipt=json.loads((e.R24/'results'/source/mon/f'R24_{source}_{mon}_SOURCE_PREPARATION_ATOMIC_receipt.json').read_text())
 assert receipt['source_sha256']==pin and receipt['source_eligible_asof_decisions_after_v5_300s_warmup_and_spread']==len(signal)
 assert feats.shape==(len(signal),len(e.FEATURE_NAMES))
 # Side shadow uses ONLY past quote-prefix derived movement, never future labels.
 ix={x:i for i,x in enumerate(e.FEATURE_NAMES)}
 B3=np.asarray(feats[:,ix['bid_move_3s']],np.float64);A3=np.asarray(feats[:,ix['ask_move_3s']],np.float64)
 shadow=np.where((B3>0)&(A3>0),1,np.where((B3<0)&(A3<0),-1,0)).astype(np.int8)
 # Ensure full-prep quote ordinals, true delayed fills and 1-sec clock remain immutable.
 assert np.all((fills<0)|((fills>=signal)&(fills<len(t))))
 sz,bmax,bmin,amax,amin=e.build_tree(b,a)
 tm=t[np.maximum(fills,0)]
 gaps=np.r_[0,np.cumsum(np.diff(t)>GAP,dtype=np.int64)]
 qtime,qref=e.calendar_reference(mon)
 qstart=int(qtime[0]);qlen=len(qref)
 monend=int(qtime[-1])+Q
 full=[];qrows=[];hrows=[];drows=[]
 for horizon in HOLDS:
  H=horizon*1000
  end=np.searchsorted(t,tm+H,side='left').astype(np.int32)
  valid=(fills>=0)&(end<len(t))
  ec=np.minimum(end,len(t)-1)
  fi=np.maximum(fills,0)
  valid&=(t[ec]-(tm+H)<=GAP)&(gaps[ec]==gaps[fi])
  valid&=(tm>=qstart)&(tm<monend)
  ok,safe,tp,ss,stp=evaluated_horizon(t,b,a,fills,ec,valid,shadow,np.asarray(STOPS,np.int32),sz,bmax,bmin,amax,amin)
  qidx=((tm-qstart)//Q).astype(np.int32)
  asofbin=(fills>=0)&(qidx>=0)&(qidx<qlen)
  oraclebin=ok&asofbin
  qsafe=np.asarray(qidx)
  spread=np.asarray(feats[:,ix['spread_raw']],np.float32)
  rel=(spread<=.8*np.asarray(feats[:,ix['spread_ema300s']],np.float32))&(np.asarray(feats[:,ix['spread_ema15s']],np.float32)<=np.asarray(feats[:,ix['spread_ema300s']],np.float32))
  for si,st in enumerate(STOPS):
   for mode,mask in [('ORACLE_ANY_SURVIVE_FULL_H',np.any(safe[si],axis=1)&oraclebin),
                     ('ORACLE_ANY_SURVIVE_AND_TARGET',np.any(tp[si],axis=1)&oraclebin),
                     ('ASOF_SIGN3S_ALL', (shadow!=0)&asofbin),
                     ('ASOF_SIGN3S_RELIEF', (shadow!=0)&asofbin&rel)]:
    # Legal trade schedules use actual lagged fill quote and same fixed-H occupancy.
    chosen=fixed_hold_earliest(tm,mask,H)
    # Oracle side may look into future; as-of policy picks side only from prefix.
    oracle=mode.startswith('ORACLE')
    picked_side=np.where(np.any(safe[si],axis=1) if mode=='ORACLE_ANY_SURVIVE_FULL_H' else np.any(tp[si],axis=1),np.where(safe[si,:,0] if mode=='ORACLE_ANY_SURVIVE_FULL_H' else tp[si,:,0],1,-1),1) if oracle else shadow
    correct_safe=np.where(picked_side==1,safe[si,:,0],safe[si,:,1])&ok
    correct_tp=np.where(picked_side==1,tp[si,:,0],tp[si,:,1])&ok
    qc=np.bincount(qsafe[chosen],minlength=qlen)
    qgood=np.bincount(qsafe[chosen&correct_safe],minlength=qlen)
    qtarget=np.bincount(qsafe[chosen&correct_tp],minlength=qlen)
    qcensored=np.bincount(qsafe[chosen&~ok],minlength=qlen)
    completed=int(chosen.sum()-qcensored.sum())
    accuracy=None if completed==0 else float(correct_safe[chosen].sum()/completed)
    target_accuracy=None if completed==0 else float(correct_tp[chosen].sum()/completed)

    qmet=((qref>0)&(qc>=qref)).astype(np.uint8)
    hqc=qc.reshape(-1,4).sum(axis=1);href=qref.reshape(-1,4).sum(axis=1)
    hgood=qgood.reshape(-1,4).sum(axis=1);htarget=qtarget.reshape(-1,4).sum(axis=1)
    dqc=qc.reshape(-1,96).sum(axis=1);dref=qref.reshape(-1,96).sum(axis=1)
    dgood=qgood.reshape(-1,96).sum(axis=1);dtarget=qtarget.reshape(-1,96).sum(axis=1)

    row={'source':source,'month':mon,'label_class':mode,'min_hold_sec':horizon,'new_liquidation_adverse_stop_raw':st,
      'risk_contract_differs_from_R9_R11_R24':True,'oracle_future_label_mode':oracle,
      'entry_clock_1000ms_source_ordinal':True,'entry_latency_100ms_first_observed_quote':True,
      'source_SHA256':pin,'observed_source_quotes':len(t),'original_r9_month_reference':int(qref.sum()),
      'candidate_signals':len(signal),'valid_full_horizon_covered_fills':int(ok.sum()),
      'candidate_current_asof_admissible_count':int(mask.sum()),
      'completed_filled_positions':completed,'correct_survived_initial_full_H':int(correct_safe[chosen].sum()),
      'correct_survived_and_target_by_H':int(correct_tp[chosen].sum()),
      'right_censored_unknown':int(qcensored.sum()),
      'correct_initial_survival_fraction_completed':accuracy,'correct_initial_survival_and_target_fraction_completed':target_accuracy,
      'calendar_quarters_target_count_met':int(((qref>0)&(qtarget>=qref)).sum()),
      'calendar_hours_target_count_met':int(((href>0)&(htarget>=href)).sum()),
      'calendar_quarters_joint80_initial_survival_and_fill_volume':int(((qref>0)&(qc>=qref)&(qgood/np.maximum(qc-qcensored,1)>=.8)).sum()),
      'max_independent_onepos_fixed_hold_fullmonth':int(chosen.sum()),
      'active_R9_quarters':int((qref>0).sum()),'quarter_exact_volume_met':int(qmet.sum()),
      'active_R9_hours':int((href>0).sum()),'hour_exact_volume_met':int(((href>0)&(hqc>=href)).sum()),
      'active_R9_days':int((dref>0).sum()),'day_exact_volume_met':int(((dref>0)&(dqc>=dref)).sum()),
      'source_quarter_deficit_slots':int(np.maximum(qref-qc,0).sum()),
      'source_quarter_correct_target_deficit_slots':int(np.maximum(qref-qtarget,0).sum()),
      'future_quality_is_NOT_asof_predictor':True,'no_historical_news_events':True}
    full.append(row)
    keys=[datetime.fromtimestamp(int(ms)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') for ms in qtime]
    for i,k in enumerate(keys):qrows.append({'label_class':mode,'min_hold_sec':horizon,'new_stop_raw':st,'utc_quarter':k,'r9_SYNTH_reference':int(qref[i]),'selected_entries':int(qc[i]),'selected_correct_hold':int(qgood[i]),'selected_correct_target_and_hold':int(qtarget[i]),'censored':int(qcensored[i]),'capacity_meets_ref':int(qc[i]>=qref[i]) if qref[i] else '', 'source':source,'month':mon})
    for i,k in enumerate(keys[::4]):hrows.append({'label_class':mode,'min_hold_sec':horizon,'new_stop_raw':st,'utc_hour':k,'r9_SYNTH_reference':int(href[i]),'selected_entries':int(hqc[i]),'selected_correct_hold':int(hgood[i]),'selected_correct_target_and_hold':int(htarget[i]),'capacity_meets_ref':int(hqc[i]>=href[i]) if href[i] else '', 'source':source,'month':mon})
    for i,k in enumerate(keys[::96]):drows.append({'label_class':mode,'min_hold_sec':horizon,'new_stop_raw':st,'utc_day':k[:10],'r9_SYNTH_reference':int(dref[i]),'selected_entries':int(dqc[i]),'selected_correct_hold':int(dgood[i]),'selected_correct_target_and_hold':int(dtarget[i]),'capacity_meets_ref':int(dqc[i]>=dref[i]) if dref[i] else '', 'source':source,'month':mon})
    # Preserve selected source ordinal and exit-book occupancy, including future privilege flag.
    np.savez_compressed(out/f'S6_{source}_{mon}_H{horizon}_STOP{st}_{mode}_FULL_SELECTED_SOURCE_ORDINALS.npz',
       selected_signal_source_ordinal=np.asarray(signal[chosen],np.int32),
       selected_actual_fill_source_ordinal=np.asarray(fills[chosen],np.int32),
       selected_fill_utc_ms=tm[chosen],selected_fixed_exit_utc_ms=tm[chosen]+H,
       selected_preentry_past3s_observed_sign=shadow[chosen],
       selected_actual_buy1_sell_minus1=picked_side[chosen].astype(np.int8),
       selected_full_horizon_covered=ok[chosen],
       selected_actual_side_full_horizon_survived=correct_safe[chosen],
       selected_actual_side_full_horizon_survived_and_target=correct_tp[chosen],
       hindsight_any_side_survive_at_horizon=np.asarray(np.any(safe[si],axis=1)[chosen]),
       hindsight_any_side_survive_plus_target_at_horizon=np.asarray(np.any(tp[si],axis=1)[chosen]))
  print('R24S6_COMPLETE_HORIZON',source,mon,horizon,flush=True)
 csvwrite(out/f'S6_{source}_{mon}_ALL_60_SCENARIOS.csv',full)
 csvwrite(out/f'S6_{source}_{mon}_ALL_60_CALENDAR_QUARTERS.csv',qrows)
 csvwrite(out/f'S6_{source}_{mon}_ALL_60_CALENDAR_HOURS.csv',hrows)
 csvwrite(out/f'S6_{source}_{mon}_ALL_60_CALENDAR_DAYS.csv',drows)
 manifest={'research_class':'R24S6_UNABRIDGED_INITIAL_MINIMUM_HOLD_SOURCE_EXACT_HINDSIGHT_AND_PREFIX_SHADOW',
  'source':source,'month':mon,'raw_SHA':pin,'reference_R9_count':int(qref.sum()),
  'original_source_preparation_receipt':receipt['status'],'experiment_scenarios':len(full),
  'calendar_records':{'quarter':len(qrows),'hour':len(hrows),'day':len(drows)},
  'no_calendar_news_verified':True,'historically_exposed_in_sample':True,
  'future_survival_labels_NOT_causal_policy':True,'holding_time_not_profit_target_window':True,
  'complete_negative_source_ordinal_preservation':'R24 original two sided labels unchanged; ASOF_SIGN3S schedules select prefix-only and include all STOP/non-target/censored outcomes; ORACLE selects future-surviving candidates and is never a causal policy.',
  'research_performance_no_cash_PNL':True,'elapsed_seconds':time.monotonic()-start,
  'complete_output_file_digests':{q.name:{'sha256':sha(q),'bytes':q.stat().st_size} for q in sorted(out.iterdir()) if q.is_file() and q.name.startswith(f'S6_{source}_{mon}') and not q.name.endswith('MANIFEST.json')}}
 (out/f'S6_{source}_{mon}_FULL_SHA_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('R24S6_SOURCE_MONTH_PASS',source,mon,'len=',len(full),'elapsed=',manifest['elapsed_seconds'],flush=True)
 return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=e.SOURCE_NAMES,required=True);p.add_argument('--month',choices=('01','02','06','07'),required=True)
 opt=p.parse_args();run(opt.source,opt.month)
