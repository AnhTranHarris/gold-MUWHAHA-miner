"""Freeze entire four-month H1V2 R11 future-privileged objective traces.

Never silently omit a failed variant or archived outcome. No predictor training.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile,math
from pathlib import Path
import numpy as np
from fullmonth_oracle_optimization import EXPERIMENTS
from entry_contract import PINNED,SYNTH

ROOT=Path('/mnt/data/h1v2_r11_lab')
EXPECTED_ORIGINAL={
 '01':'1ab88d87409f81bf0966fcb21eabff17b47663962be66de29bf98b8d33eb3b49',
 '02':'521e9244fa42360d429317df22049208d1538f985e5823551116a2fe7a8069eb',
 '06':'54b1a4300b0b9a3aabb28bb016041c947eb29908cad4d6b6083c0bafcffef138',
 '07':'1e941322b0198110b62289f0baf6228aa17f80de7b391121ce43a74e1d397644',
}

def sha(f):
 with Path(f).open('rb') as x:return hashlib.file_digest(x,'sha256').hexdigest()

def freeze(mon):
 loc=ROOT/'optimization'/f'month_{mon}'
 teacher=ROOT/'rebuilt_teacher'/f'h1v2_dukascopy_{mon}_oracle_labels.npz'
 compressed=ROOT/'rebuilt_teacher'/f'h1v2_dukascopy_{mon}_oracle_labels_lossless.npz'
 assert sha(teacher)==EXPECTED_ORIGINAL[mon]
 with np.load(compressed,allow_pickle=False) as c,np.load(teacher,allow_pickle=False) as o:
  assert c.files==o.files
  for key in c.files: assert np.array_equal(c[key],o[key],equal_nan=True), key
 records={};paths=[]
 for spec in EXPERIMENTS:
  p=loc/f'{spec.id}_COMPLETE_RECEIPT.json'
  if not p.exists():raise ValueError('missing whole month experiment '+str(p))
  r=json.loads(p.read_text());assert r['id']==spec.id
  for fname in [r['all_positions_trace'],r['full_daily_record'],r['full_weekly_record']]:
   fp=loc/fname
   if not fp.exists():raise ValueError('missing full data '+fname)
   paths.append(fp)
  assert sha(loc/r['all_positions_trace'])==r['all_positions_trace_sha256']
  with np.load(loc/r['all_positions_trace'],allow_pickle=False) as z:
   cnt=len(z['side']);assert cnt==r['strict_known_successful_selected']
   ix=z['source_raw_entry_tick'];out=z['source_raw_exit_tick']
   assert np.all(out>ix) and (len(ix)<2 or np.all(ix[1:]>out[:-1]))
   assert np.all(z['research_net_after_incremental_cost']>0)
   assert np.all((z['side']==1)|(z['side']==-1))
  with (loc/r['full_daily_record']).open() as f:daily=json.load(f)['cells']
  with (loc/r['full_weekly_record']).open() as f:weekly=json.load(f)['cells']
  assert sum(int(x['positions']) for x in daily)==cnt
  assert sum(int(x['positions']) for x in weekly)==cnt
  assert sum(int(x['strict_first15_seconds']) for x in daily)==sum(int(x['strict_first15_seconds']) for x in weekly)
  records[spec.id]={**r,'calendar_validation':{
       'active_utc_days':len(daily),'active_iso_weeks':len(weekly),
       'number_days_below_80pct_first15':sum(int(x['strict_first15_rate']<.80) for x in daily),
       'number_weeks_below_80pct_first15':sum(int(x['strict_first15_rate']<.80) for x in weekly),
       'min_daily_first15':min((x['strict_first15_rate'] for x in daily),default=None),
       'min_weekly_first15':min((x['strict_first15_rate'] for x in weekly),default=None),
       'days_zero_positions_not_quantified':True}}
  paths.append(p)
 for p in sorted(loc.glob('R11_FULL_MONTH_EXPERIMENT_STAGE_*.json')):paths.append(p)
 report={
  'month':mon,
  'original_raw_sha256':PINNED[mon],
  'verified_original_exact_full_teacher_labels_sha256':EXPECTED_ORIGINAL[mon],
  'lossless_compressed_full_labels_sha256':sha(compressed),
  'lossless_compressed_full_labels_bytes':compressed.stat().st_size,
  'original_uncompressed_full_teacher_bytes':teacher.stat().st_size,
  'all_variant_ids':[x.id for x in EXPERIMENTS],
  'source_r9_synth':SYNTH[mon],
  'r9v2_85pct_month_floor':math.ceil(.85*SYNTH[mon]),
  'all_computed_from_complete_original_250ms_population':True,
  'source_model':'H1V2 R11 full raw/month; original 30s oracle, alternative future-privileged interval schedules',
  'unqualified_asof_student':'NO_FULL_MONTH_TRAINED_HAZARD_OR_CALIBRATED_PREDICTIVE_POLICY',
  'experiments':records,
 }
 merged=loc/f'R11_{mon}_ALL_11_EXPERIMENTS_COMPLETE_RECEIPT.json'
 merged.write_text(json.dumps(report,indent=2));paths.append(merged)
 archive=ROOT/f'R11_{mon}_FULL_MONTH_11_OBJECTIVES_EXACT_TRACES_AND_CALENDARS_20261103.zip'
 manifest={f.name:{'size':f.stat().st_size,'sha256':sha(f)} for f in paths}
 manifest_file=loc/f'R11_{mon}_COMPLETE_INTERNAL_SHA256_MANIFEST.json'
 manifest_file.write_text(json.dumps({'month':mon,'files':manifest,'complete_objectives':len(EXPERIMENTS)},indent=2));paths.append(manifest_file)
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for fp in paths:z.write(fp,arcname=fp.name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  assert set(z.namelist())==set(f.name for f in paths)
 assert len(EXPERIMENTS)==11
 return {'month':mon,'raw_SHA256':PINNED[mon], 'archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_SHA256':sha(archive), 'member_files':len(paths),'full_original_teacher_labels_SHA256':sha(teacher),'full_lossless_teacher_labels_SHA256':sha(compressed),'all_hindsight_variants':{x.id: {'positions':records[x.id]['strict_known_successful_selected'],'net':records[x.id]['simulated_research_net_after_incremental_cost'],'first15':records[x.id]['first15s_strict_rate'],'day80fails':records[x.id]['calendar_validation']['number_days_below_80pct_first15'],'week80fails':records[x.id]['calendar_validation']['number_weeks_below_80pct_first15']} for x in EXPERIMENTS}}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=['01','02','06','07']);a=p.parse_args()
 print(json.dumps(freeze(a.month),indent=2))
