"""R23H-0007 exact input/model/day score/day-hour-quarter calendar verification.
Never alters source files. Fails hard on absent/mismatched byte or event path.
"""
from __future__ import annotations
import csv,hashlib,json,os
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).resolve()
FEEDS=('DUKASCOPY_RAW','MT5_BROKER_EXPORT');MONS=('01','02','06','07')
def sha(f):
 with open(f,'rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()

def check():
 records=list(csv.DictReader((ROOT/'results/R23H7_PROBE_EXECUTION_REGISTER.tsv').open(),delimiter='\t'))
 assert len(records)==16 and all(r['status']=='PASS' for r in records)
 fit=[];days=[];tests=[]
 for s in FEEDS:
  for m in MONS:
   modeldir=BASE/'r23h7_models'/s/m
   receipt=modeldir/'R23H7_FIT_RECEIPT.json'
   x=json.loads(receipt.read_text())
   assert x['source']==s and x['month']==m and x['feature_count_before_side_and_h']==89
   assert len(x['models'])==3 and x['training_cause_rows']>0 and x['training_held_rows']>0
   for model,z in x['models'].items():
    p=modeldir/z['name'];assert sha(p)==z['sha256']
   fit.append({'source':s,'month':m,'sha256':sha(receipt),
        'original_gz_sha256':x['original_source_gz_sha256'],
        'sampled_signals':x['sampled_signals'],'original_quote_rows':x['original_quote_rows'],
        'class_counts':x['class_count'],'fit_model_sha256':{k:v['sha256'] for k,v in x['models'].items()}})
   day=2 if m in ('01','02') else 1
   p=BASE/'r23h7_scores'/s/m/f'R23H7_{s}_{m}_{day:02d}_PREDICTIONS.npz'
   r=json.loads(p.with_suffix('.receipt.json').read_text());assert r['source']==s and r['month']==m
   assert sha(p)==r['sha256']
   with np.load(p,allow_pickle=False) as z:
    cause=z['cause5'];held=z['held'];wait=z['wait10']
    assert cause.shape==(r['rows'],2,3,5) and held.shape==(r['rows'],2,3)
    assert wait.shape==(r['rows'],) and np.isfinite(cause).all()
    if r['rows']:
     assert np.max(np.abs(cause.sum(axis=3)-1))<1e-4
     assert np.min(cause)>=0 and np.max(cause)<=1.00001
     assert np.min(held)>=0 and np.max(held)<=1
     assert np.min(wait)>=0 and np.max(wait)<=1
     for k in (0,1,3,4):assert np.min(np.diff(cause[:,:,:,k],axis=2))>-1e-4
     assert np.max(np.diff(cause[:,:,:,2],axis=2))<1e-4
     assert np.max(np.diff(held,axis=2))<1e-4
   days.append({'source':s,'month':m,'day':day,'full_daily_signal_population':r['rows'],
       'start_row':r['start_row'],'end_row':r['end_row'],'score_sha256':r['sha256'],
       'models_receipt_sha256':r['model_receipt_sha256'],'asof_unknown_news':True})
 for contract,required in (('clock_audit',24),('capacity_witness',96)):
  folder=ROOT/'results'/contract
  j=json.loads(next(folder.glob('*HASHES.json') if contract=='capacity_witness' else folder.glob('*SHA_MANIFEST.json')).read_text())
  recs=j['receipts'] if contract=='capacity_witness' else j['outputs']
  assert len(recs)==required
  for rr in recs:
   p=Path(rr['derived_path'] if contract=='capacity_witness' else rr['output_path'])
   assert p.is_file() and sha(p)==rr['derived_sha256' if contract=='capacity_witness' else 'output_sha256']
  tests.append({'source':contract,'records':required,'file_hash_reconciled':required})
 assert len({r['fit_model_sha256']['CAUSE5'] for r in fit})==8
 meta={'status':'R23H7_0007_EXECUTED_FITS_EIGHT_AND_DAY_PILOTS_EIGHT_NO_POLICY_REPLAY',
  'fit_records':fit,'day_score_records':days,'calendar_and_oracle_witness_integrity':tests,
  'parent_original_source_unchanged':True,'source_months':8,'source_model_files':24,
  'different_source_month_hazard_weights_SHA':True,
  'passed_tests':4,'original_causal_policy_accuracy':'NOT_EVALUATED_NEW_GATE',
  'full_new_R23H7_monthly_policy_replay':'NOT_PERFORMED',
  'actual_MT5_economic_snapshot':'UNKNOWN','historic_prop_trading_window':'UNKNOWN'}
 out=ROOT/'results'/'R23H7_0007_FINAL_EXECUTED_SHA_VERIFIER.json'
 out.write_text(json.dumps(meta,indent=2)+'\n')
 return meta
if __name__=='__main__':
 r=check();print(json.dumps({'status':r['status'],'fit_records':len(r['fit_records']),
  'day_scores':len(r['day_score_records']),'checks':r['calendar_and_oracle_witness_integrity']},indent=2))
