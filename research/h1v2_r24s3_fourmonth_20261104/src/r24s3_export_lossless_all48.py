"""Lossless 48-policy, full-month/UTC-day/hour/quarter R24S3 evidence.

Re-evaluates frozen as-of LightGBM BUY/SELL/WAIT outputs against immutable
future-labelled exact quote paths, preserving ALL losing selected positions.
No R9 source quota or future label ever enters inference. Written artifacts are
fully model/feature/raw SHA-bound and independently recomputed before accepting.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r24_asof/source')
import r24_firstpass_engine as r
from r24_predict_replay_V2_highthroughput import replay_one_position
LAB=Path('/mnt/data/h1v2_r24_s3')


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def atomic_json(path,record):
 p=Path(path);p.parent.mkdir(exist_ok=True,parents=True)
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');os.replace(tmp,p)

def write_csv_gz(path,rows,header):
 p=Path(path);tmp=Path(str(p)+'.temporary')
 with gzip.open(tmp,'wt',newline='',encoding='utf8',compresslevel=4) as f:
  w=csv.DictWriter(f,fieldnames=header);w.writeheader();w.writerows(rows)
 os.replace(tmp,p)

def scenario_parameters():
 return [(p,s,w,h) for p in (.08,.12,.16,.20) for s in (.90,.99) for w in (0.,.12) for h in (0.,.04,.08)]

def verify_upstream(src,mon,source_dir):
 raw=r.source_file(src,mon);sha_raw=sha(raw)
 if sha_raw!=r.source_pin(src,mon):raise RuntimeError('ORIGINAL_SOURCE_RAW_SHA_DRIFT')
 inp=source_dir/f'R24_{src}_{mon}_1000MS_features.npy'
 model=r.R24/'models'/mon/'R24_FROZEN_BROKER_CONDITIONED_MULTISCALE_FIRSTPASS_5_CAUSE_LGBM.txt'
 wait=r.R24/'models'/mon/'R24_FROZEN_OPPORTUNITY_WAIT10S_LGBM.txt'
 marker=source_dir/f'R24_{src}_{mon}_FROZEN_ASOF_INFERENCE_ATOMIC_COMPLETION.json'
 if not marker.exists():raise RuntimeError('ATOMIC_INFERENCE_COMPLETION_MISSING')
 m=json.loads(marker.read_text())
 P=source_dir/f'R24_{src}_{mon}_FROZEN_ASOF_FIVE_CAUSE_PROBABILITIES.npy'
 W=source_dir/f'R24_{src}_{mon}_FROZEN_ASOF_WAIT10S_PROBABILITY.npy'
 for k,actual in [('source_sha',sha_raw),('hazard_model_sha',sha(model)),('wait_model_sha',sha(wait)),('probabilities_sha',sha(P)),('wait_probabilities_sha',sha(W))]:
  if m.get(k)!=actual:raise RuntimeError('PREDICTION_MEMBER_DRIFT_'+k)
 # For all replays, the first two source tensors are independent inputs.
 return {'raw':sha_raw,'model':sha(model),'wait_model':sha(wait),'features':sha(inp),'predict':sha(P),'wait':sha(W)}

def run(src,mon):
 root=r.R24/'results'/src/mon
 pin=verify_upstream(src,mon,root)
 prefix=f'R24_{src}_{mon}_1000MS'
 X=np.load(root/(prefix+'_features.npy'),mmap_mode='r',allow_pickle=False)
 sig=np.load(root/(prefix+'_signal_utc_ms.npy'),mmap_mode='r',allow_pickle=False)
 rawidx=np.load(root/(prefix+'_source_quote_ordinal.npy'),mmap_mode='r',allow_pickle=False)
 fillidx=np.load(root/(prefix+'_fill_source_quote_ordinal.npy'),mmap_mode='r',allow_pickle=False)
 fill=np.load(root/(prefix+'_actual_fill_utc_ms.npy'),mmap_mode='r',allow_pickle=False)
 event=np.load(root/(prefix+'_first_barrier_2SIDE_utc_ms.npy'),mmap_mode='r',allow_pickle=False)
 timeout=np.load(root/(prefix+'_true_timeout_first_observed_utc_ms.npy'),mmap_mode='r',allow_pickle=False)
 truth=np.load(root/(prefix+'_labels_2SIDE_3HORIZON.npy'),mmap_mode='r',allow_pickle=False)
 P=np.load(root/f'R24_{src}_{mon}_FROZEN_ASOF_FIVE_CAUSE_PROBABILITIES.npy',mmap_mode='r',allow_pickle=False)
 W=np.load(root/f'R24_{src}_{mon}_FROZEN_ASOF_WAIT10S_PROBABILITY.npy',mmap_mode='r',allow_pickle=False)
 n=len(sig)
 if not(all(len(x)==n for x in (X,rawidx,fillidx,fill,event,timeout,truth,P,W))) or P.shape!=(n,2,3,5):raise AssertionError('ALL_INPUTS_SHAPE_NOT_EQUAL')
 qt,qref=r.calendar_reference(mon);qfirst=int(qt[0]//900000)
 if int(qref.sum())!={'01':27980,'02':33523,'06':31758,'07':24324}[mon]:raise RuntimeError('SOURCE_R9_CLOCK_REFERENCE_NOT_EXACT')
 nquarters=len(qref);nhours=nquarters//4;ndays=nquarters//96
 qtext=[datetime.fromtimestamp(int(x)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') for x in qt]
 dest=LAB/'lossless_all48'/src/mon;dest.mkdir(parents=True,exist_ok=True)
 receipt={'source':src,'month':mon,'original_R9_QUARTER_CALENDAR_EXACT':True,'source_pins':pin,'n_candidates':n,
          'complete_calendar_sizes':{'quarters':nquarters,'hours':nhours,'days':ndays},'variants':[],'causal_only_source_prefix_inputs':True,
          'labels_only_used_after_decision_for_replay_and_scoring':True,'nondeployment_insample_exposed':True}
 allrows=[];monthcases=[]
 for num,(p,s,w,h) in enumerate(scenario_parameters()):
  code=f'V{num:02d}';pr=replay_one_position(P,W,truth,sig,fill,event,timeout,qfirst,nquarters,p,s,w,h)
  fc,tp,stop,to,cen=pr[:5]
  ids,sides,hbins,status,probs,fm,ex=pr[5:]
  if len(ids)!=int(fc.sum()) or int(fc.sum())!=int(tp.sum()+stop.sum()+to.sum()+cen.sum()):raise AssertionError('TOTAL_SELECTED_OUTCOME_PARITY')
  if len(ids) and (np.any(np.diff(fm)<0) or not np.array_equal(status,truth[ids,np.where(sides==1,0,1),hbins])):raise AssertionError('SELECTED_ORIGINAL_BARRIER_LABEL_MISMATCH')
  if len(ids)>1 and np.any(fm[1:]<=ex[:-1]):raise AssertionError('ONE_POSITION_OVERLAP')
  if len(ids) and (not np.array_equal(fm,fill[ids]) or np.any(fm<sig[ids]+100) or np.any(ex<fm)):
   raise AssertionError('ACTUAL_QUOTE_FILL_OR_EVENT_CLOCK_DRIFT')
  bq=(fm//900000-qfirst).astype(np.int64)
  if len(ids) and (np.any(bq<0)|np.any(bq>=nquarters)):raise RuntimeError('FILLED_OUTSIDE_MONTH')
  for status_code,arr in ((1,tp),(0,stop),(2,to),(3,cen)):
   z=np.flatnonzero(status==status_code)
   if not np.array_equal(np.bincount(bq[z],minlength=nquarters),arr):raise AssertionError('INDEPENDENT_QUARTER_CAUSE_RECOUNT_FAIL')
  qsum={k:v for k,v in [('fills',fc),('TP',tp),('STOP',stop),('TIMEOUT',to),('CENSOR',cen)]}
  for scale,width in [('QUARTER',1),('HOUR',4),('DAY',96)]:
   nums={k:v.reshape(-1,width).sum(axis=1) for k,v in qsum.items()}
   qtarget=qref.reshape(-1,width).sum(axis=1)
   for i in range(len(qtarget)):
    nonc=int(nums['TP'][i]+nums['STOP'][i]+nums['TIMEOUT'][i]);correct=int(nums['TP'][i]);original=int(qtarget[i]);filled=int(nums['fills'][i])
    row={'source':src,'month':mon,'variant':code,'min_target_p':p,'max_pstop':s,'wait_penalty':w,'horizon_penalty':h,
         'resolution':scale,'utc_start':qtext[width*i], 'R9_SYNTH_UTC_REFERENCE':original,
         'filled':filled,'target_first':correct,'stop_first':int(nums['STOP'][i]),'timeout':int(nums['TIMEOUT'][i]),'right_censored':int(nums['CENSOR'][i]),
         'accuracy_completed':(correct/nonc if nonc else ''),
         'pass_filled_volume':(int(filled>=original) if original else ''),
         'pass_correct_volume':(int(correct>=original) if original else ''),
         'joint_correct_volume_and_80_accuracy':(int(correct>=original and nonc>0 and correct/nonc>=.8) if original else ''),
         'exposed_in_sample_causal_signal':True,'source_label_used_only_after_admission':True}
    allrows.append(row)
  zpath=dest/f'R24S3_{src}_{mon}_{code}_ALL_SELECTED_CORRECT_WRONG_ORIGINAL_ORDINALS.npz'
  if zpath.exists():raise RuntimeError('DO_NOT_OVERWRITE_SAVED_VARIANT')
  temp=zpath.with_name(zpath.name+'.TEMP.npz')
  np.savez_compressed(temp,source_signal_candidate_index=ids,
   source_original_quote_ordinal=rawidx[ids],source_signal_utc_ms=sig[ids],
   source_fill_quote_ordinal=fillidx[ids],actual_observed_fill_utc_ms=fm,
   side_buy1_sellminus1=sides,selected_horizon_0_15_1_30_2_60=hbins,
   correct_target1_stop0_timeout2_censor3=status,one_position_occupied_until_utc_ms=ex,
   asof_model_target_p_at_decision=probs)
  os.replace(temp,zpath)
  manifest={'variant':code,'n_selected':len(ids),'target_first':int(tp.sum()),'stop_first':int(stop.sum()),'timeout':int(to.sum()),
            'censored':int(cen.sum()),'original_src_and_model_pins':pin,'selected_member_sha256':sha(zpath),
            'all_UTC_quarters':nquarters,'all_UTC_hours':nhours,'all_UTC_days':ndays}
  atomic_json(dest/f'R24S3_{src}_{mon}_{code}_ATOMIC_SHA_RECEIPT.json',manifest)
  receipt['variants'].append(manifest)
  monthcases.append({'source':src,'month':mon,'variant':code,'p':p,'stop_cap':s,'wait_penalty':w,'horizon_penalty':h,
                     'selected':len(ids),'correct':int(tp.sum()),'incorrect_stop':int(stop.sum()),'timeout':int(to.sum()),
                     'censored':int(cen.sum()),'accuracy_completed':float(tp.sum()/(tp.sum()+stop.sum()+to.sum())) if int(tp.sum()+stop.sum()+to.sum()) else None,
                     'independent_selected_file_sha256':manifest['selected_member_sha256']})
  if num%8==0:print('ALL48_ATOMIC_CASE',src,mon,code,'filled',len(ids),'correct',int(tp.sum()),flush=True)
 header=list(allrows[0]);cases=list(monthcases[0]);z=dest/f'R24S3_{src}_{mon}_ALL_48_FULL_QUARTER_HOUR_DAY_CALENDARS.csv.gz'
 write_csv_gz(z,allrows,header)
 file2=dest/f'R24S3_{src}_{mon}_ALL_48_TRIALS_FULL_MONTH.csv.gz'
 write_csv_gz(file2,monthcases,cases)
 receipt['rows_full_calendar']=len(allrows);receipt['calendar_sha256']=sha(z);receipt['monthcases_sha256']=sha(file2);
 if len(allrows)!=48*(nquarters+nhours+ndays):raise AssertionError('REQUIRED_COMPLETE_CALENDAR_ROW_COUNT')
 receipt['status']='ALL_48_ATOMIC_RECEIPTS_COMPLETE';atomic_json(dest/f'R24S3_{src}_{mon}_ALL_48_INDEPENDENT_SOURCE_CALENDAR_SHA_RECEIPT.json',receipt)
 print('ALL48_FULL_CALENDAR_COMPLETE',src,mon,'row_count',len(allrows),'selected_files',len(receipt['variants']),flush=True)
 return receipt

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',choices=r.SOURCE_NAMES,required=True);a.add_argument('--month',choices=['01','02','06','07'],required=True);x=a.parse_args();run(x.source,x.month)
