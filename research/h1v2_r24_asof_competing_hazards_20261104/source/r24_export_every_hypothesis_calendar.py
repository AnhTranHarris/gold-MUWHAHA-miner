"""Lossless R24V2 all-48 full month/day/hour/15min & selected quote ordinal recorder.

Source-exact real observations; original R9 SYNTH calendar, never interpolated.
Separate from V1 and V2 primary results. This is IN-SAMPLE, not deployment.
No inference score uses a future label or an R9 quota; labels enter replay only.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,sys,time
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import r24_firstpass_engine as e
from r24_predict_replay_V2_highthroughput import replay_one_position


def write_scope(file,ref,qstart,filled,target,stop,timeout,censor,source,month,scope,cfg):
 ref=np.asarray(ref);filled=np.asarray(filled);target=np.asarray(target);stop=np.asarray(stop);timeout=np.asarray(timeout);censor=np.asarray(censor)
 qn=int(900000 if scope=='QUARTER' else 3600000 if scope=='HOUR' else 86400000)
 for i,r in enumerate(ref):
  d=int(target[i]+stop[i]+timeout[i]);acc=target[i]/d if d else ''
  ts=datetime.fromtimestamp((qstart+i*qn)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
  file.writerow([source,month,cfg,scope,ts,int(r),int(filled[i]),int(target[i]),int(stop[i]),int(timeout[i]),int(censor[i]),acc,int(filled[i]>=r) if r else '',int(target[i]>=r) if r else '',int(target[i]>=r and acc!='' and acc>=.8) if r else ''])


def record(src,mon):
 start=time.monotonic();base=e.R24/'results'/src/mon;pfx=base/f'R24_{src}_{mon}_1000MS'
 inf=base/f'R24_{src}_{mon}_FROZEN_ASOF_INFERENCE_ATOMIC_COMPLETION.json'
 if not inf.exists():raise RuntimeError('FROZEN_HAZARD_MISSING_COMPLETION_MARKER')
 receipt=json.loads(inf.read_text());proba=base/f'R24_{src}_{mon}_FROZEN_ASOF_FIVE_CAUSE_PROBABILITIES.npy';wait=base/f'R24_{src}_{mon}_FROZEN_ASOF_WAIT10S_PROBABILITY.npy'
 if receipt['probabilities_sha']!=e.sha(proba) or receipt['wait_probabilities_sha']!=e.sha(wait):raise ValueError('FROZEN_SCORE_DRIFT')
 P=np.load(proba,mmap_mode='r');W=np.load(wait,mmap_mode='r')
 T=np.load(str(pfx)+'_signal_utc_ms.npy',mmap_mode='r');F=np.load(str(pfx)+'_actual_fill_utc_ms.npy',mmap_mode='r')
 E=np.load(str(pfx)+'_first_barrier_2SIDE_utc_ms.npy',mmap_mode='r');TO=np.load(str(pfx)+'_true_timeout_first_observed_utc_ms.npy',mmap_mode='r')
 labels=np.load(str(pfx)+'_labels_2SIDE_3HORIZON.npy',mmap_mode='r');ordinals=np.load(str(pfx)+'_source_quote_ordinal.npy',mmap_mode='r')
 if len(P)!=len(T) or len(labels)!=len(T) or len(ordinals)!=len(T):raise ValueError('INCOMPLETE_SOURCE_CANDIDATE_POPULATION')
 qr,qref=e.calendar_reference(mon);nq=len(qref);qfirst=int(qr[0]//900000)
 allref={'QUARTER':qref,'HOUR':qref.reshape(-1,4).sum(axis=1),'DAY':qref.reshape(-1,96).sum(axis=1)}
 rawcsv=base/f'R24_V2_{src}_{mon}_ALL_48_VARIANTS_EVERY_MONTH_DAY_HOUR_15MIN.csv.gz'
 cohorts=base/f'R24_V2_{src}_{mon}_ALL_48_ORIGINAL_SOURCE_ENTRY_AND_EXIT_ORDINALS.npz'
 header=['source','month','variant_id','scope','utc_period_start','R9_SYNTH_reference','asof_all_filled','asof_target_first','asof_stop_first','asof_timeout','asof_censored','completed_target_first_precision','filled_quota_met','target_first_quota_met','joint_80pct_correct_quota_met']
 variants=[];save={}
 with gzip.open(rawcsv,'wt',newline='',encoding='utf8',compresslevel=6) as f:
  w=csv.writer(f);w.writerow(header)
  case=0
  for threshold in (0.08,0.12,0.16,0.20):
   for stopmax in (0.90,0.99):
    for wait_penalty in (0.0,0.12):
     for horizon_penalty in (0.0,0.04,0.08):
      z=replay_one_position(P,W,labels,T,F,E,TO,qfirst,nq,threshold,stopmax,wait_penalty,horizon_penalty)
      f0,g,s,t,c=z[:5];idx,side,horizon,outcome,score,actualfill,exit0=z[5:]
      if not (np.sum(f0)==len(idx)==np.count_nonzero(outcome>=0)):raise RuntimeError('SELECTED_ORDINAL_TO_FILLED_RECONCILE')
      if not np.all(np.diff(T[idx])>0):raise RuntimeError('NONINCREASING_SOURCE_ORDINAL')
      if not np.array_equal(np.bincount(actualfill//900000-qfirst,minlength=nq),f0):raise RuntimeError('FILLED_QUARTER_RECONCILE')
      variants.append({'variant':case,'minp':threshold,'maxstop':stopmax,'wait_penalty':wait_penalty,'horizon_penalty':horizon_penalty,'filled':len(idx),'target_first':int(np.sum(g)),'stop_first':int(np.sum(s)),'timeout':int(np.sum(t)),'censored':int(np.sum(c))})
      for scope,span in (('QUARTER',1),('HOUR',4),('DAY',96)):
       def agg(z):return z if span==1 else z.reshape(-1,span).sum(axis=1)
       write_scope(w,allref[scope],int(qr[0]),agg(f0),agg(g),agg(s),agg(t),agg(c),src,mon,scope,case)
      pref=f'V{case:02d}_';save[pref+'observed_signal_row']=idx;save[pref+'raw_source_quote_ordinal']=ordinals[idx];save[pref+'side']=side;save[pref+'horizon_bin']=horizon;save[pref+'outcome']=outcome;save[pref+'target_probability']=score;save[pref+'actual_fill_time_utc_ms']=actualfill;save[pref+'source_firstpass_exit_time_utc_ms']=exit0
      case+=1
      if case%8==0:print('ALL_POLICY_CHRONOLOGICAL_ROWS_WRITTEN',src,mon,case,'of 48',flush=True)
 if case!=48:raise RuntimeError('CASE_CARDINALITY')
 np.savez_compressed(cohorts,**save)
 models=e.R24/'models'/mon
 o={'status':'COMPLETE_LOSSLESS_ALL_48_FULL_CALENDARS_ALL_SELECTED_ORDINALS_IN_SAMPLE_ONLY','source':src,'month':mon,'source_raw_sha':e.source_pin(src,mon),'frozen_model_sha':e.sha(models/'R24_FROZEN_BROKER_CONDITIONED_MULTISCALE_FIRSTPASS_5_CAUSE_LGBM.txt'),'source_candidates':len(T),'variants':variants,'R9_reference_total':int(qref.sum()),'calendar_rows_per_variant':nq+nq//4+nq//96,'all_48_selected_source_actions_retained':True,'frozen_inference_sha':receipt['probabilities_sha'],'output_files':{x.name:{'size':x.stat().st_size,'sha256':e.sha(x)} for x in (rawcsv,cohorts)},'elapsed_seconds':round(time.monotonic()-start,3)}
 (base/f'R24_V2_{src}_{mon}_ALL_48_UNABRIDGED_INDEPENDENT_RECONCILIATION_RECEIPT.json').write_text(json.dumps(o,indent=2)+'\n')
 print('COMPLETE_ALL_POLICY_CALENDAR',json.dumps({'source':src,'mon':mon,'nvariants':len(variants),'source_candidates':len(T),'all_calendar_csv_bytes':rawcsv.stat().st_size,'all_48_ordinal_bytes':cohorts.stat().st_size,'seconds':o['elapsed_seconds']},indent=2),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=e.SOURCE_NAMES,required=True);p.add_argument('--month',choices=('01','02','06','07'),required=True);a=p.parse_args();record(a.source,a.month)
