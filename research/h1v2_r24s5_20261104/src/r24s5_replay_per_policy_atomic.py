"""Append-only independent 60-policy 15m/hour/day R24S4 June source replay.

Each policy is a separate replay of the SAME completed S4 in-sample model output;
no oracle future-selected side enters entry scoring. Full original Bid/Ask target,
stop, timeout, right-censor outcomes are evaluated after selecting BUY/SELL/WAIT.

Store each exact selected source quote ordinal (and losing outcomes), calendar
period and SHA-256 under an atomic case-specific receipt. Never delete a prior
failed case or substitute volume for correctness. Distinct from full EA PnL.
"""
from __future__ import annotations
import argparse,sys,hashlib,json,csv,os,itertools
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
sys.path[:0]=['/mnt/data/h1v2_r24_asof/source','/mnt/data/h1v2_r24s4_entry_specialists/src']
import r24_firstpass_engine as e
from r24_predict_replay_V2_highthroughput import replay_one_position
import r24s4_broker_hazard_specialist as sp

LAB=Path('/mnt/data/h1v2_r24s5')
PARAMS=tuple(itertools.product((.06,.12,.20,.35,.50),(.65,.85,.99),(0.,.15),(0.,.07)))

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(4<<20),b''):h.update(chunk)
 return h.hexdigest()

def writecsv(path,rows):
 if not rows:raise ValueError('NO_ROWS')
 tmp=Path(str(path)+'.TMP')
 with tmp.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 os.replace(tmp,path)

def run(source,mon,max_cases=10):
 p=sp.inputpaths(source,mon);sd=Path('/mnt/data/h1v2_r24s4_entry_specialists/results')/source/mon
 out=LAB/'results'/source/mon;out.mkdir(parents=True,exist_ok=True)
 Ppath=sd/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_HAZARD_PROBABILITIES.npy'
 Wpath=sd/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_WAIT_PROBABILITIES.npy'
 greceipt=sd/f'R24S5_{source}_{mon}_RESUMABLE_INFERENCE_ATOMIC_FINAL_RECEIPT.json'
 gr=json.loads(greceipt.read_text());
 if gr['probability_file_sha']!=sha(Ppath) or gr['WAIT_probability_sha']!=sha(Wpath):raise RuntimeError('MODEL_INFERENCE_DRIFT')
 if sha(e.source_file(source,mon))!=e.source_pin(source,mon):raise RuntimeError('SOURCE_RAW_SHA_DRIFT')
 paths={'labels':str(p)+'_labels_2SIDE_3HORIZON.npy',
   'signal':str(p)+'_signal_utc_ms.npy','ordinal':str(p)+'_source_quote_ordinal.npy',
   'fill':str(p)+'_actual_fill_utc_ms.npy','event':str(p)+'_first_barrier_2SIDE_utc_ms.npy',
   'timeout':str(p)+'_true_timeout_first_observed_utc_ms.npy'}
 stamp={'source':source,'month':mon,'raw_sha':e.source_pin(source,mon),'model_score_sha':sha(Ppath),
  'wait_score_sha':sha(Wpath),'source_arrays_sha':{k:sha(f) for k,f in paths.items()},
  'accepted_policy_contract':'R24S4_5CAUSE_WAIT10_FIRST_OBSERVED_100MS_ONE_POSITION'}
 P=np.load(Ppath,mmap_mode='r');W=np.load(Wpath,mmap_mode='r')
 labels=np.load(paths['labels'],mmap_mode='r');tim=np.load(paths['signal'],mmap_mode='r')
 ords=np.load(paths['ordinal'],mmap_mode='r');fill=np.load(paths['fill'],mmap_mode='r')
 event=np.load(paths['event'],mmap_mode='r');timeout=np.load(paths['timeout'],mmap_mode='r')
 qr,qref=e.calendar_reference(mon);qfirst=int(qr[0]//900000);nq=len(qref)
 assert len(qref)=={'01':2976,'02':2688,'06':2880,'07':2976}[mon]
 assert np.all(np.diff(qr)==900000)
 assert qref.sum()=={'01':27980,'02':33523,'06':31758,'07':24324}[mon]
 href=qref.reshape(-1,4).sum(axis=1);dref=qref.reshape(-1,96).sum(axis=1)
 qkeys=[datetime.fromtimestamp(int(t)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') for t in qr]
 completed=0
 for tp,risk,wp,hp in PARAMS:
  case=f'P{tp:.2f}_STOP{risk:.2f}_WAIT{wp:.2f}_H{hp:.2f}'
  caseprefix=f'R24S5_{source}_{mon}_{case}'
  receipt=out/f'{caseprefix}_ATOMIC_RECEIPT.json'
  if receipt.is_file():
   old=json.loads(receipt.read_text())
   if old['stamp']!=stamp:raise RuntimeError('CASE_CHECKPOINT_STAMP_DRIFT '+case)
   for item in old['outputs']:
    q=out/item['file']
    if not q.is_file() or sha(q)!=item['sha256']:raise RuntimeError('CASE_ARCHIVE_HASH_DRIFT '+str(q))
   continue
  res=replay_one_position(P,W,labels,tim,fill,event,timeout,qfirst,nq,tp,risk,wp,hp)
  f,g,stop,to,ce=res[:5]
  if np.any(f!=(g+stop+to+ce)):raise RuntimeError('CAUSE_PARTITION_MISMATCH')
  if np.any(f<0):raise RuntimeError('NEGATIVE_FILLED')
  ids,sides,hindices,causes,proba,fillt,exitt=res[5:]
  if len(ids)!=int(f.sum()) or len(ids)>1 and np.any(np.diff(ids)<=0):raise RuntimeError('SELECTED_ORDINAL_OR_COUNTS')
  if len(fillt)>1 and np.any(fillt[1:]<=exitt[:-1]):raise RuntimeError('ONE_POSITION_CONFLICT')
  if len(ids) and (np.any(ords[ids]<0) or np.any(fillt<tim[ids]+100)):raise RuntimeError('SOURCE_DELAY_FILL_NOT_EXECUTABLE')
  if len(ids) and np.any(labels[ids,(sides!=1).astype(np.int64),hindices]!=causes):
   raise RuntimeError('POST_ACTION_TRUTH_MISMATCH')
  trace=out/f'{caseprefix}_ALL_SELECTED_SOURCE_ORDINALS_GOOD_BAD_TIMEOUT_CENSORED.npz'
  # Write atomically, including even 0-volume cases with empty arrays.
  tr_tmp=Path(str(trace)+'.TMP.npz')
  np.savez_compressed(tr_tmp,source_quote_ordinal=ords[ids],signal_utc_ms=tim[ids],
    action_side_buy1_sellminus1=sides,horizon_index=hindices,outcome_code=causes,
    asof_predicted_pTARGET=proba,actual_first_observed_fill_utc_ms=fillt,first_event_exit_utc_ms=exitt)
  os.replace(tr_tmp,trace)
  def periods(ref,step,keys):
   rows=[]
   for j,rv in enumerate(ref):
    l=j*step;r=l+step
    F=int(f[l:r].sum());G=int(g[l:r].sum());S=int(stop[l:r].sum());T=int(to[l:r].sum());C=int(ce[l:r].sum())
    completed=G+S+T;v=int(rv);acc=G/completed if completed else None
    rows.append({'case':case,'source':source,'month':mon,'utc_start':keys[j],
       'r9_SYNTH_original_ref':v,'asof_fills':F,'TARGET_first_correct':G,'STOP_first_wrong':S,
       'TIMEOUT_initially_survived_without_target':T,'QUOTE_CENSORED_unknown':C,
       'completed_correctness_target_fraction':acc,
       'source_count_quota_met':int(F>=v) if v else '',
       'correct_trade_count_quota_met':int(G>=v) if v else '',
       'joint_80pct_TARGET_and_R9_filled_quota':int(F>=v and acc is not None and acc>=.8) if v else '',
       'joint_80pct_TARGET_and_R9_correct_quota':int(G>=v and acc is not None and acc>=.8) if v else '',
       'initial_noSTOP_first_fraction':(G+T)/completed if completed else None,
       'news_and_prop_permission':'UNKNOWN_UNVERIFIED',
       'source_month_IN_SAMPLE':True})
   return rows
  qs=periods(qref,1,qkeys);hs=periods(href,4,qkeys[::4]);ds=periods(dref,96,qkeys[::96])
  for label,rows in [('QUARTERS',qs),('HOURS',hs),('DAYS',ds)]:
   assert sum(r['asof_fills'] for r in rows)==int(f.sum())
   assert sum(r['TARGET_first_correct'] for r in rows)==int(g.sum())
   assert sum(r['STOP_first_wrong'] for r in rows)==int(stop.sum())
  files=[trace]
  for label,rows in [('QUARTERS',qs),('HOURS',hs),('DAYS',ds)]:
   path=out/f'{caseprefix}_COMPLETE_{label}.csv';writecsv(path,rows);files.append(path)
  den=int(g.sum()+stop.sum()+to.sum());caserow={'case':case,'source':source,'month':mon,
    'model_probability_threshold':tp,'stop_probability_cap':risk,'WAIT_penalty':wp,'horizon_penalty':hp,
    'r9_SYNTH_original_month_count':int(qref.sum()),'source_month_fills':int(f.sum()),
    'TARGET_first_correct':int(g.sum()),'STOP_first_wrong':int(stop.sum()),'TIMEOUT':int(to.sum()),
    'CENSORED_unknown':int(ce.sum()),'TARGET_first_fraction':int(g.sum())/den if den else None,
    'initial_noSTOP_first_fraction':int(g.sum()+to.sum())/den if den else None,
    'R9_active_hours':int((href>0).sum()),'R9_active_15min':int((qref>0).sum()),
    'quarters_target_count_met':sum(r['correct_trade_count_quota_met']==1 for r in qs),
    'quarters_joint80_target_and_quota':sum(r['joint_80pct_TARGET_and_R9_correct_quota']==1 for r in qs),
    'hours_target_count_met':sum(r['correct_trade_count_quota_met']==1 for r in hs),
    'hours_joint80_target_and_quota':sum(r['joint_80pct_TARGET_and_R9_correct_quota']==1 for r in hs),
    'days_joint80_target_and_quota':sum(r['joint_80pct_TARGET_and_R9_correct_quota']==1 for r in ds),
    'in_sample_not_blind_OOS':True,'not_deployable':True}
  rec={'status':'COMPLETE_INDIVIDUAL_CASE_SOURCE_EXACT','stamp':stamp,'case':case,
    'metrics':caserow,'outputs':[{'file':z.name,'bytes':z.stat().st_size,'sha256':sha(z)} for z in files]}
  tmp=Path(str(receipt)+'.TMP');tmp.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n');os.replace(tmp,receipt)
  completed+=1
  print('R24S5_ATOMIC_FULL_REPLAY_CASE',source,mon,case,'COMPLETE',completed,flush=True)
  if completed>=max_cases:break
 count=len(list(out.glob('R24S5_*_ATOMIC_RECEIPT.json')))
 if count==len(PARAMS):
  receipts=[];qfull=[];hfull=[];dfull=[]
  for tp,risk,wp,hp in PARAMS:
   case=f'P{tp:.2f}_STOP{risk:.2f}_WAIT{wp:.2f}_H{hp:.2f}'
   prefix=f'R24S5_{source}_{mon}_{case}'
   rec=json.loads((out/f'{prefix}_ATOMIC_RECEIPT.json').read_text())
   if rec['stamp']!=stamp:raise RuntimeError('FINAL_RECEIPT_SOURCE_DRIFT')
   receipts.append(rec['metrics'])
   for label,dest in [('QUARTERS',qfull),('HOURS',hfull),('DAYS',dfull)]:
    with (out/f'{prefix}_COMPLETE_{label}.csv').open(newline='') as f:dest.extend(csv.DictReader(f))
  assert len(qfull)==60*len(qref) and len(hfull)==60*len(href) and len(dfull)==60*len(dref)
  paths=[]
  for nm,rows in [('MONTH_CASES',receipts),('QUARTERS',qfull),('HOURS',hfull),('DAYS',dfull)]:
   pp=out/f'R24S5_{source}_{mon}_ALL_60_CASES_COMPLETE_{nm}.csv';writecsv(pp,rows);paths.append(pp)
  best=sorted(receipts,key=lambda x:(x['quarters_joint80_target_and_quota'],x['hours_joint80_target_and_quota'],x['quarters_target_count_met'],x['TARGET_first_correct'],-x['STOP_first_wrong']),reverse=True)[0]
  final={'status':'ALL_60_SOURCE_EXACT_IN_SAMPLE_HAZARD_SPECIALIST_REPLAYS_COMPLETE',
   'source':source,'month':mon,'inputs':stamp,'cases':60,'quarter_rows':len(qfull),'hour_rows':len(hfull),'day_rows':len(dfull),
   'best_policy_lexicographic_only':best,
   'case_receipt_count':60,'all_selected_wrong_and_correct_ordinals_retained':True,
   'no_verified_historical_news_or_prop_eligibility':True,'in_sample_only_no_OOS_or_real_fill':True,
   'outputs':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in paths}}
  (out/f'R24S5_{source}_{mon}_ALL60_FINAL_SOURCE_AND_CALENDAR_RECEIPT.json').write_text(json.dumps(final,indent=2)+'\n')
  print('R24S5_FULL_60_COMPLETED',json.dumps({k:v for k,v in final.items() if k not in ('inputs','outputs')},allow_nan=False),flush=True)
 else:print('R24S5_PARTIAL',source,mon,count,'/',len(PARAMS),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',default='DUKASCOPY_RAW');ap.add_argument('--month',default='06');ap.add_argument('--max-cases',type=int,default=10)
 a=ap.parse_args();run(a.source,a.month,a.max_cases)
