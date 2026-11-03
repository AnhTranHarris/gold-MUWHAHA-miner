"""Full artifact retention for one month R11 fitted causal student negative experiment.

Never lose scores or negative on-policy selections when the local runtime expires.
Stores source-exact model weights, every candidate probability, all selected
source-ordinal position traces and complete daily/weekly receipts, with hashes.
The full graph matrix is regenerable from source raw and archived code/pins;
its 70-feature, complete-month exact SHA256 is retained in the manifest.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile,pathlib
import numpy as np
from entry_contract import MONTHS
from preserve_month import ROOT,sha
from evaluate_fullmonth_student import POLICIES,FRACTIONS

POLICY_NAMES=[x[0] for x in POLICIES]+[f'DIAGNOSTIC_TOP{int(f*100):02d}PCT_FITMONTH_IN_SAMPLE_NO_ECONOMIC_GATES' for f in FRACTIONS]

def preserve(month):
 if month not in MONTHS:raise ValueError(month)
 modeldir=ROOT/'models'; replaydir=ROOT/'student_replay'/f'month_{month}'
 graphdir=ROOT/'graph';paths=[];meta={'month':month,'model_status':'FIT_EACH_SIDE_WHOLE_MONTH_IN_SAMPLE_NOT_PREDICTIVE_QUALIFICATION','model_weights':{},'source_feature':{},'score_archives':{},'replay_artifacts':{},'policy_names':POLICY_NAMES}
 graphrec=graphdir/f'R11_CAUSAL_GRAPH_V5_{month}_RECEIPT.json'
 orig=json.loads(graphrec.read_text());paths.append(graphrec)
 graphfile=graphdir/f'R11_CAUSAL_GRAPH_V5_{month}.npy'
 if sha(graphfile)!=orig['matrix_sha256']:raise ValueError('graph changed')
 meta['source_feature']={'sha256':orig['matrix_sha256'],'rows':orig['r11_v5_250ms_complete_candidates'],'features':orig['feature_count'],'original_npy_bytes':orig['matrix_size_bytes'],
 'source_graph_not_embedded_1GB':'Restorable from raw source SHA + exact saved graph code; output SHA required for replay'}
 for side in ('BUY','SELL'):
  recp=modeldir/f'R11_{month}_{side}_ALLPOP_IN_SAMPLE_FIT_RECEIPT.json';r=json.loads(recp.read_text())
  model=modeldir/r['model_file'];probs=modeldir/r['full_probability_file']
  if sha(model)!=r['model_sha256'] or sha(probs)!=r['full_probability_file_sha256'] or r['causal_feature_sha256']!=orig['matrix_sha256']:
   raise ValueError('student model/source/probability artifact mutated')
  p=np.load(probs,mmap_mode='r')
  if p.shape!=(orig['r11_v5_250ms_complete_candidates'],3):raise ValueError('source probability count mismatch')
  dst=modeldir/f'R11_{month}_{side}_FULL_ELIGIBLE_CANDIDATE_PROBS_LOSSLESS.npz'
  np.savez_compressed(dst,probabilities=np.asarray(p),
                      source_month=np.asarray([month]),
                      source_graph_sha256=np.asarray([orig['matrix_sha256']]),
                      frozen_fit_model_sha256=np.asarray([r['model_sha256']]))
  with np.load(dst,allow_pickle=False) as z:
   if not np.array_equal(z['probabilities'],p):raise ValueError('score compression changed full values')
  paths.extend([recp,model,dst])
  meta['model_weights'][side]={'file':model.name,'SHA256':r['model_sha256'],'train_rows_valid':r['included_supervised_rows'],'censored_excluded':r['excluded_source_end_censored'],'training_brier':r['in_sample_multiclass_brier_on_valid_exits'],'training_logloss':r['in_sample_log_loss_on_valid_exits']}
  meta['score_archives'][side]={'archive':dst.name,'archive_SHA256':sha(dst),'bytes':dst.stat().st_size,'array_shape':list(p.shape),'original_uncompressed_score_sha256':r['full_probability_file_sha256']}
 resultfile=replaydir/f'R11_{month}_FULLMONTH_STUDENT_IN_SAMPLE_ALLPOLICIES.json'
 result=json.loads(resultfile.read_text());paths.append(resultfile)
 if set(result['experiments'])!=set(POLICY_NAMES):raise ValueError('one or more experimental policies missing')
 for name in POLICY_NAMES:
  record=result['experiments'][name]
  for suffix in ('COMPLETE_RECEIPT.json','FULL_SELECTED_TRADES.npz','EXACT_UTC_DAY_HOLDOUT_NOTE.json','EXACT_ISO_WEEK_HOLDOUT_NOTE.json'):
   file=replaydir/f'{name}_{suffix}'
   if not file.exists():raise ValueError('full policy file missing '+str(file))
   paths.append(file)
  f=replaydir/record['exact_trace_file']
  if sha(f)!=record['exact_trace_sha256']:raise ValueError('selected trace mismatch')
  with np.load(f,allow_pickle=False) as z:
   assert len(z['code'])==record['trades']
   assert len(z['code'])==record['strict_good']+record['wrong']+record['neutral']
  cal=json.loads((replaydir/record['complete_utc_day_file']).read_text())
  assert sum(x['real_selected_source_entries'] for x in cal['cells'])==record['trades']
  meta['replay_artifacts'][name]={'trades':record['trades'],'strict_precision':record['strict_precision'],
       'modeled_net':record['modeled_net_original_fees'],'selected_trace_sha256':record['exact_trace_sha256']}
 dst=ROOT/f'R11_{month}_FULL_POPULATION_CAUSAL_STUDENT_TRAINING_AND_REPLAY_20261103.zip'
 metafile=replaydir/f'R11_{month}_SOURCE_EXACT_ALL_STUDENT_ARTIFACTS_MANIFEST.json'
 members={f.name:{'size':f.stat().st_size,'sha256':sha(f)} for f in paths}
 metafile.write_text(json.dumps({'complete':meta,'contents':members},indent=2));paths.append(metafile)
 with zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as f:
  for p in paths:f.write(p,p.name)
 with zipfile.ZipFile(dst) as f:
  if f.testzip() is not None:raise ValueError('ZIP CRC failed')
  if len(f.namelist())!=len(paths):raise ValueError('ZIP member count drift')
 return {'month':month,'archive':str(dst),'archive_bytes':dst.stat().st_size,'archive_sha256':sha(dst),'member_count':len(paths),
         'complete_source_population':orig['r11_v5_250ms_complete_candidates'],'graph_sha256':orig['matrix_sha256'],
         'model_weights':meta['model_weights'],'score_archives':meta['score_archives'],
         'policy_replay_outcomes':meta['replay_artifacts'],
         'scientific_boundary':'IN_SAMPLE_FULL_MONTH_STUDENT_NEGATIVE_EXPERIMENT; NOT A NEAR PERFECT CAUSAL PREDICTOR'}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--month',required=True,choices=MONTHS);x=ap.parse_args()
 print(json.dumps(preserve(x.month),indent=2),flush=True)
