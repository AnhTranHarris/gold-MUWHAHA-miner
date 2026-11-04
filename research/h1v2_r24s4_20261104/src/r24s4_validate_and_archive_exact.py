"""R24S4 source-exact archive/reconciliation of ALL 60 per-source/month outcomes.

No partial receipt success. Independently audits all original quarter/hour/day rows,
all selected filled ordinal labels, class code totals and source SHA. Splits into
four 15-case shard ZIPs so huge research has durable atomic restart slices.
Does not rerun the original raw first-passage over 8M quotes; source SHA parity
and original R24 raw-label preparation are separate preconditions.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime,timezone
ROOT=Path('/mnt/data/h1v2_r24s4_entry_specialists'); R24=Path('/mnt/data/h1v2_r24_asof')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def run(src,mon):
 out=ROOT/'results'/src/mon; manifest=json.loads((out/f'R24S4_{src}_{mon}_FULL_60_CASES_ATOMIC_RECEIPT.json').read_text())
 assert manifest['status']=='R24S4_FULL_60_IN_SAMPLE_SOURCE_REPLAY_ATOMIC_COMPLETE'
 case_csv=out/f'R24S4_{src}_{mon}_ALL_60_HAZARD_POLICY_MONTH_CASES.csv'
 cases=pd.read_csv(case_csv); assert len(cases)==60 and cases.case.is_unique
 q=pd.read_csv(out/f'R24S4_{src}_{mon}_ALL_60_CASES_COMPLETE_QUARTERS.csv');h=pd.read_csv(out/f'R24S4_{src}_{mon}_ALL_60_CASES_COMPLETE_HOURS.csv');d=pd.read_csv(out/f'R24S4_{src}_{mon}_ALL_60_CASES_COMPLETE_DAYS.csv')
 n_q={'01':2976,'02':2688,'06':2880,'07':2976}[mon];n_h=n_q//4;n_d=n_q//96
 assert len(q)==60*n_q and len(h)==60*n_h and len(d)==60*n_d
 # Original UTC monthly R9 quota calendar from immutable R23 archived values.
 import sys
 sys.path[:0]=['/mnt/data/h1v2_r24_asof/source']
 import r24_firstpass_engine as orig
 originalq, originalref=orig.calendar_reference(mon)
 originalkeys=pd.to_datetime(originalq,unit='ms',utc=True).strftime('%Y-%m-%dT%H:%M:%SZ')
 checks=[];checks.append('60_POLICY_ROWS_and_60X_FULL_CALENDAR_SHAPES')
 for case in cases.itertuples():
  name=case.case
  qs=q[q.case==name];hs=h[h.case==name];ds=d[d.case==name]
  assert len(qs)==n_q and len(hs)==n_h and len(ds)==n_d
  assert list(qs.utc_start)==list(originalkeys)
  assert np.array_equal(qs.r9_SYNTH_original_ref.to_numpy(np.int32),originalref)
  assert np.array_equal(hs.r9_SYNTH_original_ref.to_numpy(np.int32),originalref.reshape(-1,4).sum(axis=1))
  assert np.array_equal(ds.r9_SYNTH_original_ref.to_numpy(np.int32),originalref.reshape(-1,96).sum(axis=1))
  path=out/f'R24S4_{src}_{mon}_{name}_ALL_SELECTIONS_POSITIVE_AND_NEGATIVE.npz'
  assert path.exists() and path.stat().st_size>100
  with np.load(path,allow_pickle=False) as data:
   a={key:np.asarray(data[key]) for key in data.files}
  n=len(a['signal_row']);assert n==int(case.source_month_fills)
  assert all(len(v)==n for v in a.values())
  assert np.array_equal(np.unique(a['observed_cause'],return_counts=True)[0],np.unique(a['observed_cause']))
  assert set(np.unique(a['observed_cause'])).issubset({0,1,2,3})
  assert int(np.sum(a['observed_cause']==1))==case.TARGET_first_correct
  assert int(np.sum(a['observed_cause']==0))==case.STOP_first_wrong
  assert int(np.sum(a['observed_cause']==2))==case.TIMEOUT
  assert int(np.sum(a['observed_cause']==3))==case.CENSORED_unknown
  assert np.all(a['actual_fill_ms']>=0)
  assert np.all(a['actual_exit_ms']>=a['actual_fill_ms'])
  assert not np.any(np.diff(a['signal_row'])<=0)
  # Complete buckets by observed real fill, preserving boundary shifts.
  qi=(a['actual_fill_ms']//900000)-(int(originalq[0])//900000)
  assert not np.any((qi<0)|(qi>=n_q))
  for code,col in [(-1,'asof_fills'),(0,'STOP_first_wrong'),(1,'TARGET_first_correct'),(2,'TIMEOUT_initially_survived_without_target'),(3,'QUOTE_CENSORED_unknown')]:
   hit=np.ones(n,bool) if code==-1 else a['observed_cause']==code
   cnt=np.bincount(qi[hit].astype(np.int64),minlength=n_q)
   assert np.array_equal(cnt,qs[col].to_numpy(np.int64)),f'QUARTER_CLASS_MISMATCH {name} {col}'
  for col in ['asof_fills','STOP_first_wrong','TARGET_first_correct','TIMEOUT_initially_survived_without_target','QUOTE_CENSORED_unknown']:
   vals=qs[col].to_numpy(np.int64)
   assert np.array_equal(vals.reshape(-1,4).sum(axis=1),hs[col].to_numpy(np.int64)),f'HOUR_CLASS_MISMATCH {name} {col}'
   assert np.array_equal(vals.reshape(-1,96).sum(axis=1),ds[col].to_numpy(np.int64)),f'DAY_CLASS_MISMATCH {name} {col}'
  checks.extend([name+' FULL_SOURCE_ORDINAL_CLASS_COUNT',name+' ALL_MONTH_QUARTERS',name+' ALL_HOURS',name+' ALL_DAYS'])
 # Re-check original input digest + new generated trained model SHA and final frozen scores.
 source_path=orig.source_file(src,mon)
 assert sha(source_path)==orig.source_pin(src,mon)==manifest['raw_sha']
 fit=json.loads((out/f'R24S4_{src}_{mon}_FULL_INFERENCE_ATOMIC_RECEIPT.json').read_text())
 for fn,meta in fit['outputs'].items():
  path=out/fn
  assert path.stat().st_size==meta['bytes'] and sha(path)==meta['sha256'],fn
 checks.append('SOURCE_RAW_SHA_AND_EVERY_FITTED_MODEL_SCORE_SHA')
 core=[p for p in out.glob('R24S4_*') if p.is_file() and p.suffix!='.npz']
 core.extend([ROOT/'src/r24s4_broker_hazard_specialist.py', ROOT/'src/r24s4_validate_and_archive_exact.py',ROOT/'tests/test_r24s4_early_entry_contracts.py',ROOT/'R24S4_FAILURES_CORRECTIONS_APPEND_ONLY.txt'])
 outputdir=ROOT/'archives';outputdir.mkdir(exist_ok=True)
 rec={'status':'COMPLETE_INDEPENDENT_CALENDAR_AND_SELECTED_QUOTE_ORDINAL_AUDIT',
      'source':src,'month':mon,'checked_policy_cases':60,'quarter_rows':len(q),'hour_rows':len(h),'day_rows':len(d),
      'selected_traces_count':60,'raw_source_sha256':manifest['raw_sha'],
      'checks_passed':len(checks),'checks_failed':0,'checks_lossless':checks,
      'raw_first_passage_recomputed_independently_on_every_quote':False,
      'source_r24_full_quote_label_sha_guarded_by_original_receipt':True,
      'no_future_selected_trade_used_as_inference_feature':True,
      'no_profitability_or_80pct_approval':True,'cases':[{'case':r.case,'filled':int(r.source_month_fills),'correct':int(r.TARGET_first_correct),'wrong_stop':int(r.STOP_first_wrong)} for r in cases.itertuples()]}
 reppath=out/f'R24S4_{src}_{mon}_INDEPENDENT_COMPLETE_SOURCE_60CASE_AUDIT.json';reppath.write_text(json.dumps(rec,indent=2)+'\n')
 core.append(reppath)
 corezip=outputdir/f'R24S4_{src}_{mon}_CORE_MODEL_CALENDARS_AND_FULL_VERIFIER.zip'
 with zipfile.ZipFile(corezip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for p in sorted(set(core)):z.write(p,arcname=p.name)
 arc=[corezip];idx={'core':corezip.name,'parts':[],'source':src,'month':mon}
 for i in range(0,60,15):
  names=cases.case.to_list()[i:i+15]
  shard=outputdir/f'R24S4_{src}_{mon}_COMPLETE_SELECTED_TRADE_ORDINALS_{i:02d}_{i+14:02d}.zip'
  with zipfile.ZipFile(shard,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
   for n0 in names:
    file=out/f'R24S4_{src}_{mon}_{n0}_ALL_SELECTIONS_POSITIVE_AND_NEGATIVE.npz';z.write(file,arcname=file.name)
  arc.append(shard);idx['parts'].append({'file':shard.name,'cases':names})
 for p in arc:
  with zipfile.ZipFile(p) as z:
   if z.testzip()!=None:raise ValueError('ZIP_CRC_FAIL '+p.name)
 idx['archives']={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in arc}
 idxp=outputdir/f'R24S4_{src}_{mon}_FULL_ARCHIVE_SHA_AND_MEMBER_INDEX.json';idxp.write_text(json.dumps(idx,indent=2)+'\n')
 print(json.dumps({'source':src,'month':mon,'cases':60,'checks_passed':len(checks),'archives':idx['archives']},indent=2),flush=True)
 return idx

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,choices=['DUKASCOPY_RAW','MT5_BROKER_EXPORT']);p.add_argument('--month',required=True,choices=['01','02','06','07']);a=p.parse_args()
 run(a.source,a.month)
