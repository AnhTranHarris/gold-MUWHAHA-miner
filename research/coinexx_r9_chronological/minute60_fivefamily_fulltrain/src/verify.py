"""Source manifest and independent serialized-model evaluation replay."""
import sys,json,hashlib,time
from pathlib import Path
import numpy as np,joblib
sys.path.insert(0,'/mnt/data/r9_m60_training_20261113')
from run_train import read_month,area_metrics,predict_hazard,ROOT,OUT

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024*4),b''):h.update(b)
 return h.hexdigest()

receipt=json.loads(__import__('zipfile').ZipFile('/mnt/data/R9_M60_2026_JanSep_FullUniverse_All303934_AsOf_FeatureCache_20261113.zip').read('source_receipt.json'))
source=[]
for k in range(1,10):
 mm=f'{k:02}';p=Path(f'/mnt/data/XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz')
 h=sha(p);expected=receipt['source_months'][mm]['source_sha256'];assert h==expected,(mm,h,expected)
 source.append({'month':mm,'sha256':h,'bytes':p.stat().st_size,'source_rows':receipt['source_months'][mm]['rows'],'entries':receipt['source_months'][mm]['entries']})
print('RAW_SOURCE_HASHES_MATCH',len(source),flush=True)
replay=[]
for ix in range(5,10):
 mm=f'{ix:02}';r=read_month(mm)
 old=json.loads((OUT/f'fold_{mm}.json').read_text())
 for name,prefix in [('expanded_hazard','hazard'),('direct_5sec','direct')]:
  p=OUT/'models'/f'{prefix}_test_{mm}_shadow.joblib'
  h=sha(p);assert h==old['models'][name]['model_sha256']
  d=joblib.load(p)['model']
  pred=predict_hazard(d,r['X'])[5000]['p_fav'] if prefix=='hazard' else d.predict_proba(r['X'])[:,1]
  vals=area_metrics(r,pred)
  for metric in ('pooled_auc5','r9_direction_auc5','average_precision5'):
   diff=abs(vals[metric]-old['models'][name][metric]);assert diff<1.e-12,(mm,name,metric,diff)
  replay.append({'month':mm,'name':name,'model_sha256':h,'pooled_auc5':vals['pooled_auc5'],'r9_direction_auc5':vals['r9_direction_auc5']})
 print('REPLAY_OK',mm,flush=True)
full=json.loads((OUT/'all_nine_training_receipt.json').read_text())
for name,meta in full['models'].items():
 p=OUT/'models'/meta['path'];assert sha(p)==meta['sha256']
 m=joblib.load(p);assert m['feature_count']==155 and m['status'].startswith('IN_SAMPLE')
assert sum(x['entries'] for x in source)==303934
out={'source_sha_matches':source,'replayed_evaluations':replay,'full_nine_models':full['models'],
     'baseline_source':'R9 M60 full-universe frozen records, including archived first-passage labels',
     'source_immutability':True,'test_months_previously_exposed':True,'live_compilation_not_performed':True}
(OUT/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('REPLAY_COMPLETE',len(replay),'saved models and 2 full-fit artifacts verified',flush=True)

m=joblib.load(OUT/'models'/'direct_all_JanSep_IS_ONLY.joblib')['model']
gain=m.booster_.feature_importance('gain')
groups={'R9 and earlier M60':(0,39),'event-time nested trend':(39,85),'QRB/QAF quote flow':(85,116),
        'CUSUM':(116,120),'signed quote intensity':(120,139),
        'Brownian first passage':(139,150),'action/geometry metadata':(150,155)}
importance={k:{'gain_share':float(gain[a:b].sum()/gain.sum()),'features':b-a} for k,(a,b) in groups.items()}
(OUT/'feature_importance_diagnostic.json').write_text(json.dumps({'note':'LightGBM correlated-feature gain attribution is not causal incremental information',
  'groups':importance},indent=2)+'\n')
print('GAIN_SHARES',importance,flush=True)
