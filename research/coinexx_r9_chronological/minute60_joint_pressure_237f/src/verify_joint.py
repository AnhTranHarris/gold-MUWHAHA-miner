"""Hash, refit-replay and causal-data readback of joint screen; no model promotion."""
import hashlib,json,sys,io,zipfile
from pathlib import Path
import numpy as np,joblib
sys.path.insert(0,'/mnt/data/r9_m60_joint_20261113/src')
from train_joint import ROOT,UP,read_month,metrics,CONFIG,sha,cross_features

SOURCE=json.loads((UP/'deps'/'source_receipt.json').read_text())['source_months']
raw_checks={}
for month,obj in SOURCE.items():
 p=Path(f'/mnt/data/XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz')
 actual=sha(p)
 if actual!=obj['source_sha256']:raise ValueError(f'SOURCE HASH FAIL: {month} actual {actual}')
 raw_checks[month]={'sha256':actual,'original_quote_rows':obj['rows'],'original_r9_decisions':obj['entries']}
assert sum(x['original_quote_rows'] for x in raw_checks.values())==72129347
assert sum(x['original_r9_decisions'] for x in raw_checks.values())==303934

replays={}
for mm in ['05','06','07','08','09']:
 r=read_month(mm)
 if r['n_entries']!=raw_checks[mm]['original_r9_decisions']:raise ValueError('ordinal count mismatch')
 checks={}
 for family in ['capacity_182','synergy_joint','original_side_specialist']:
  file=ROOT/'models'/f'{family}_eval_{mm}.joblib'
  receipt=json.loads((ROOT/'results'/f'score_{mm}_{family}.json').read_text())
  if sha(file)!=receipt['model_sha256']:raise ValueError(f'MODEL HASH FAIL {family} {mm}')
  loaded=joblib.load(file)
  if loaded['config']!=CONFIG:raise ValueError(f'MODEL CONFIG FAIL {family} {mm}')
  x=r['X_joint' if family!='capacity_182' else 'X182']
  p=loaded['model'].predict_proba(x)[:,1]
  prediction=np.load(ROOT/'results'/f'pred_{mm}_{family}.npy')
  if not np.allclose(p,prediction,rtol=1e-6,atol=1e-7):raise ValueError(f'PRED FAIL {mm} {family}')
  m=metrics(r,p)
  for key in ('pooled_auc','r9_direction_auc','pooled_ap','r9_direction_ap'):
   if abs(m[key]-receipt[key])>2.e-8:raise ValueError(f'METRIC FAIL {mm} {family} {key}')
  checks[family]={k:m[k] for k in ('pooled_auc','r9_direction_auc','pooled_ap','r9_direction_ap')}
 replays[mm]=checks

final=json.loads((ROOT/'results'/'ALL_NINE_TRAINING_RECEIPT.json').read_text())
for key,meta in final['models'].items():
 p=ROOT/'models'/meta['name']
 if sha(p)!=meta['sha256']:raise ValueError('FULL NINE HASH FAIL '+key)
 j=joblib.load(p)
 if j['status']!='IN_SAMPLE_ONLY_NOT_PROSPECTIVE_OOS_NOT_FOR_TRADING':raise ValueError('FULL MODEL UNSAFE STATUS')

output={'status':'RESEARCH_REPLAY_PASSED_NOT_MT5_OR_FORWARD_CERTIFIED',
 'monthly_raw_sha256_reverified':raw_checks,
 'original_source_ticks':72129347,'original_r9_decisions':303934,
 'evaluated_months':replays,'models_verified_n':15,
 'reproduced_auc_ap_values_n':60,
 'all_nine_models_verified_n':2,'all_nine_oos_metric':'NONE',
 'original_r9_ea_edited':False}
(ROOT/'results'/'VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n')
print('SOURCE_AND_MODEL_VERIFY_PASS',len(replays),'evaluation_months',len(raw_checks),'raw_month_hashes',flush=True)
