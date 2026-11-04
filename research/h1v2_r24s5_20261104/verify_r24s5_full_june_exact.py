"""Independently reconstruct all R24S5 60-policy full-month original source ordinals and UTC periods.

NO trust in summary receipts alone; read every NPZ trade and original truth arrays,
reaggregate quote fill time into original UTC quarter/hour/day, and compare
all 2880/720/30 source period rows in each of sixty cases.
"""
from __future__ import annotations
import csv,json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
sys.path[:0]=['/mnt/data/h1v2_r24_asof/source']
import r24_firstpass_engine as e
root=Path('/mnt/data/h1v2_r24s5/results/DUKASCOPY_RAW/06')
prep=e.R24/'results/DUKASCOPY_RAW/06/R24_DUKASCOPY_RAW_06_1000MS'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for c in iter(lambda:f.read(4<<20),b''):h.update(c)
 return h.hexdigest()

orig=np.load(str(prep)+'_source_quote_ordinal.npy',mmap_mode='r')
t=np.load(str(prep)+'_signal_utc_ms.npy',mmap_mode='r')
truth=np.load(str(prep)+'_labels_2SIDE_3HORIZON.npy',mmap_mode='r')
ft=np.load(str(prep)+'_actual_fill_utc_ms.npy',mmap_mode='r')
et=np.load(str(prep)+'_first_barrier_2SIDE_utc_ms.npy',mmap_mode='r')
to=np.load(str(prep)+'_true_timeout_first_observed_utc_ms.npy',mmap_mode='r')
qr,qref=e.calendar_reference('06')
assert len(qref)==2880 and qref.sum()==31758
allq=sorted(root.glob('R24S5_DUKASCOPY_RAW_06_P*_COMPLETE_QUARTERS.csv'))
assert len(allq)==60, f'EXPECTED60:{len(allq)}'
errors=[]; checks=0;cases=[];details=[]
for qpath in allq:
 name=qpath.name;case=name.split('R24S5_DUKASCOPY_RAW_06_')[1].split('_COMPLETE_QUARTERS.csv')[0]
 prefix=f'R24S5_DUKASCOPY_RAW_06_{case}'
 rec=json.loads((root/f'{prefix}_ATOMIC_RECEIPT.json').read_text())
 for f in rec['outputs']:
  p=root/f['file'];checks+=1
  if not p.is_file() or sha(p)!=f['sha256']:errors.append((case,'CHUNK_SHA',p.name))
 with np.load(root/f'{prefix}_ALL_SELECTED_SOURCE_ORDINALS_GOOD_BAD_TIMEOUT_CENSORED.npz',allow_pickle=False) as z:
  ix=z['source_quote_ordinal'];signal=z['signal_utc_ms'];side=z['action_side_buy1_sellminus1']
  hi=z['horizon_index'];code=z['outcome_code'];f=z['actual_first_observed_fill_utc_ms'];ex=z['first_event_exit_utc_ms'];pred=z['asof_predicted_pTARGET']
  checks+=1
  i=np.searchsorted(orig,ix)
  if np.any(i>=len(orig)) or not np.array_equal(orig[i],ix):errors.append((case,'SOURCE_ORDINAL_NOT_IN_PREFIX'))
  if not np.array_equal(t[i],signal) or not np.array_equal(ft[i],f):errors.append((case,'SOURCE_TIME_OR_DELAY'))
  if len(f)>1 and np.any(f[1:]<=ex[:-1]):errors.append((case,'ONE_POSITION_CONFLICT'))
  s=(side==-1).astype('int64')
  if not np.array_equal(truth[i,s,hi],code):errors.append((case,'QUOTED_GROUND_TRUTH_MISMATCH'))
  if not np.all(np.isfinite(pred)):errors.append((case,'NONFINITE_SCORE'))
  if np.any((code==0)|(code==1)) and not np.array_equal(ex[(code==0)|(code==1)],et[i[(code==0)|(code==1)],s[(code==0)|(code==1)]]):errors.append((case,'EXIT_QUOTE_TIME_MISMATCH'))
  bincount=(f//900000-qr[0]//900000).astype(np.int64)
  if np.any(bincount<0) or np.any(bincount>=len(qref)):errors.append((case,'OUTSIDE_MONTH'))
  qcounts={k:np.bincount(bincount[code==k],minlength=len(qref)) for k in [0,1,2,3]}
  qtotal=np.bincount(bincount,minlength=len(qref))
 with qpath.open(newline='') as sfile:qr0=list(csv.DictReader(sfile))
 with (root/f'{prefix}_COMPLETE_HOURS.csv').open(newline='') as sfile:hr0=list(csv.DictReader(sfile))
 with (root/f'{prefix}_COMPLETE_DAYS.csv').open(newline='') as sfile:dr0=list(csv.DictReader(sfile))
 checks+=4
 if len(qr0)!=2880 or len(hr0)!=720 or len(dr0)!=30:errors.append((case,'PERIOD_COVERAGE_LENGTH'))
 valmap={'asof_fills':qtotal,'TARGET_first_correct':qcounts[1],
  'STOP_first_wrong':qcounts[0],'TIMEOUT_initially_survived_without_target':qcounts[2],
  'QUOTE_CENSORED_unknown':qcounts[3]}
 for key,values in valmap.items():
  checks+=3
  qv=np.asarray([int(x[key]) for x in qr0]);hv=np.asarray([int(x[key]) for x in hr0]);dv=np.asarray([int(x[key]) for x in dr0]);
  if not np.array_equal(qv,values):errors.append((case,'Q_'+key))
  if not np.array_equal(hv,values.reshape(-1,4).sum(axis=1)):errors.append((case,'H_'+key))
  if not np.array_equal(dv,values.reshape(-1,96).sum(axis=1)):errors.append((case,'D_'+key))
 if not np.array_equal(np.asarray([int(x['r9_SYNTH_original_ref']) for x in qr0]),qref):errors.append((case,'R9_EXACT_QUARTER_BENCHMARK'))
 if not np.array_equal(np.asarray([int(x['r9_SYNTH_original_ref']) for x in hr0]),qref.reshape(-1,4).sum(axis=1)):errors.append((case,'R9_EXACT_HOUR_BENCHMARK'))
 if not np.array_equal(np.asarray([int(x['r9_SYNTH_original_ref']) for x in dr0]),qref.reshape(-1,96).sum(axis=1)):errors.append((case,'R9_EXACT_DAY_BENCHMARK'))
 checks+=3
 row=rec['metrics'];cases.append(row)
 if row['source_month_fills']!=int(qtotal.sum()) or row['TARGET_first_correct']!=int(qcounts[1].sum()):errors.append((case,'AGGREGATE_TOTALS'))
 details.append({'case':case,'selected_positions':len(code),'STOP_first':int(qcounts[0].sum()),
  'TARGET_first':int(qcounts[1].sum()),'TIMEOUT':int(qcounts[2].sum()),'CENSORED':int(qcounts[3].sum()),
  'active_hour_correct_and80':int(row['hours_joint80_target_and_quota']),
  'active_quarter_correct_and80':int(row['quarters_joint80_target_and_quota'])})
 checks+=1
best=sorted(cases,key=lambda x:(x['quarters_joint80_target_and_quota'],x['hours_joint80_target_and_quota'],x['quarters_target_count_met'],x['TARGET_first_correct'],-x['STOP_first_wrong']),reverse=True)[0]
summary={'status':'PASS' if not errors else 'FAIL','independently_reaggregated_original_source_and_model_selected_60_cases':len(cases),
 'source_raw_pin':e.source_pin('DUKASCOPY_RAW','06'),'source_month_ref':int(qref.sum()),
 'checks':checks,'failed':len(errors),'failures':errors,
 'full_day_hour_quarter_rows':{'days':len(cases)*30,'hours':len(cases)*720,'quarters':len(cases)*2880},
 'best_lexicographic_case':best,'all_cases':details,
 'proof_type':'REPLAY_TRACES_VS_ORIGINAL_INDEPENDENT_SOURCE_LABELS_AND_SOURCE_CLOCKS; does not independently recompute all raw ticks first-passage labels',
 'not_blind_OOS':True,'not_live_broker_fill_or_R9_actual_exit_PnL':True}
out=Path('/mnt/data/h1v2_r24s5/R24S5_JUNE_60CASE_INDEPENDENT_FULL_SOURCE_VERIFICATION.json')
out.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('all_cases','best_lexicographic_case','failures')},indent=2))
if errors:print('FAILURES',errors[:30]);raise RuntimeError('SOURCE_REPLAY_VERIFICATION_FAILED')
