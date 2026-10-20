#!/usr/bin/env python3
"""Versioned additive FILTER08 receipt and per-bin scoreboard for four-month overfit.
Never blends two brokers as a single executable account. Never rewrites original files.
"""
import csv, gzip, hashlib, io, json, math, zipfile
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
ROOT=Path('/mnt/data');D=ROOT/'R00_054_FILTER08_FOUR_MONTH_DISCOVERY';R=ROOT/'R00_054_VALIDATION/continuation_results'
BR=('coinexx','dukascopy');MONTHS=('01','02','06','07')
BASE={}; data=[]
for b in BR:
 for m in MONTHS:
  p=D/f'RESULT_{b}_{m}.json'
  if not p.exists():raise SystemExit(f'RESEARCH INCOMPLETE: {p.name} not found')
  x=json.loads(p.read_text());s=x['selected'];BASE[b,m]=x
  with np.load(D/f'FITTED_CLASSIFIER_SCORES_{b}_{m}.npz',allow_pickle=False) as o:
   assert len(o['t'])==x['n_original'] and np.all(np.diff(o['t'])>=0)
   assert int((o['truth_class']==0).sum())==x['n_correct']
   assert int((o['kept']&(o['truth_class']==0)).sum())==s['correct']
   data.append((b,m,o['t'].copy(),o['truth_class'].copy(),o['kept'].copy()))
print('EIGHT_APPROVED_BROKER_MONTH_INPUTS_RECONCILED',flush=True)
reference={}
with gzip.open(R/'R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz','rt',newline='') as f:
 for r in csv.DictReader(f):
  k=(r['broker'],int(r['hour_key'])); reference[k]=int(r['r9_synth_completed_trades'])
bybroker={}; tables=[]
for b in BR:
 t=np.concatenate([q[2] for q in data if q[0]==b]);y=np.concatenate([q[3] for q in data if q[0]==b]);keep=np.concatenate([q[4] for q in data if q[0]==b])
 h=t//3600000
 u,inv=np.unique(h,return_inverse=True)
 ng=np.bincount(inv,weights=(keep&(y==0)).astype(np.uint8)); ns=np.bincount(inv,weights=keep.astype(np.uint8));nb=np.bincount(inv,weights=((~keep)&(y!=0)).astype(np.uint8))
 got={int(k):(int(ns[i]),int(ng[i]),int(nb[i])) for i,k in enumerate(u)}
 # Every reference UTC hour in the FOUR requested calendar months, including zero-candidate hours.
 candidate_hours=[k[1] for k,v in reference.items() if k[0]==b and v>0 and datetime.fromtimestamp(k[1]*3600,tz=timezone.utc).month in (1,2,6,7) and datetime.fromtimestamp(k[1]*3600,tz=timezone.utc).year==2026]
 month_hour=[]
 for hour in sorted(set(candidate_hours)|{a for a in got if datetime.fromtimestamp(a*3600,tz=timezone.utc).month in (1,2,6,7)}):
  ts=datetime.fromtimestamp(hour*3600,timezone.utc);n,c,bad=got.get(hour,(0,0,0)); ref=reference.get((b,hour),0)
  need=math.ceil(ref*.9) if ref>0 else 0
  row={'broker':b,'utc_hour':ts.isoformat(),'date':ts.strftime('%Y-%m-%d'),'iso_week':f'{ts.isocalendar().year}-W{ts.isocalendar().week:02}','month':ts.strftime('%Y-%m'),'r9_reference':ref,'required_correct_90pct':need,'filter_emitted':n,'filter_correct':c,'incorrect_rejected':bad,'hour_pass':int(ref>0 and c>=need),'r9_eligible':int(ref>0),'hour_has_no_signals':int(ref>0 and n==0)}
  month_hour.append(row);tables.append(row)
 bybroker[b]={'original_signals':sum(BASE[b,m]['n_original'] for m in MONTHS),'original_correct':sum(BASE[b,m]['n_correct'] for m in MONTHS),'filtered_signals':int(keep.sum()),'filtered_correct':int((keep&(y==0)).sum()), 'wrong_rejected':int(((~keep)&(y!=0)).sum()), 'rate':float((keep&(y==0)).sum()/max(1,keep.sum()))}
print('CONTIGUOUS_UTC_HOURLY_ROWS',len(tables),flush=True)
with gzip.open(D/'FOUR_MONTH_CONTIGUOUS_UTC_HOURLY.csv.gz','wt',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(tables[0]));w.writeheader();w.writerows(tables)
rollups=[]
for level,key in [('hour','utc_hour'),('day','date'),('iso_week','iso_week'),('month','month')]:
 for broker in BR:
  by={}
  for h in tables:
   if h['broker']!=broker:continue
   k=h[key];v=by.setdefault(k,{'r9_reference':0,'filter_emitted':0,'filter_correct':0,'incorrect_rejected':0,'eligible_hours':0,'passing_hours':0,'uncovered_hours':0})
   for name in ('r9_reference','filter_emitted','filter_correct','incorrect_rejected'):v[name]+=h[name]
   v['eligible_hours']+=h['r9_eligible'];v['passing_hours']+=h['hour_pass'];v['uncovered_hours']+=h['hour_has_no_signals']
  for k,v in by.items():
   ref=v['r9_reference'];need=math.ceil(.9*ref) if ref else 0
   rollups.append({'broker':broker,'level':level,'utc_key':k,**v,'required_correct_90pct':need,'pass':int(ref>0 and v['filter_correct']>=need),'precision':v['filter_correct']/max(1,v['filter_emitted'])})
with (D/'FOUR_MONTH_HOUR_DAY_WEEK_MONTH_R9_QUOTAS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rollups[0]));w.writeheader();w.writerows(rollups)
feat_rows=[]
for b in BR:
 for m in MONTHS:
  with (D/f'FEATURE_GAINS_{b}_{m}.csv').open() as f:
   items=list(csv.DictReader(f))
  total=sum(float(x['gain']) for x in items)
  for x in items:
   name=x['feature'];i=int(x['rank']);gain=float(x['gain']);
   if name.startswith('orig_') or name.startswith('side_orig_'):family='PRIMARY_M1_M5_M15_H1_GEOMETRY_AND_RETURNS'
   elif name.startswith('matured_'):family='MATURED_SHADOW_PRIOR_OUTCOMES'
   elif name.startswith('expert_') or name.startswith('side_expert_'):family='ORIGINAL_LIFECYCLE_EXPERT_STATES'
   elif name.startswith('hour_') or name.startswith('dow_') or name.startswith('session_'):family='SESSION_CYCLIC_REGIME'
   elif name=='side':family='SIDE_ONLY'
   else:family='ORDERED_BID_ASK_QUOTE_RESPONSES'
   feat_rows.append({'broker':b,'month':m,'rank':i,'feature':name,'family':family,'fit_gain_fraction':gain/max(total,1)})
with (D/'ALL_MONTHS_FEATURE_IMPORTANCE_FACETS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(feat_rows[0]));w.writeheader();w.writerows(feat_rows)
summary={'scope':'R00-054 FILTER08 four-month January February June July, two distinct quote feeds','research_status':'SAME_MONTH_OVERFIT_NON_DEPLOYABLE','results':[BASE[b,m] for b in BR for m in MONTHS], 'broker_aggregate':bybroker,'r9_quota_rollups':{},'feature_groups':{},'predeclared_global_filter':False,'blind_test':False}
for b in BR:
 summary['r9_quota_rollups'][b]={}
 for level in ('hour','day','iso_week','month'):
  vals=[r for r in rollups if r['broker']==b and r['level']==level and r['r9_reference']>0]
  summary['r9_quota_rollups'][b][level]={'passing':sum(r['pass'] for r in vals),'eligible':len(vals),'missed_keys':[r['utc_key'] for r in vals if not r['pass']][:50]}
 weights={}
 for x in feat_rows:
  if x['broker']==b:weights[x['family']]=weights.get(x['family'],0)+x['fit_gain_fraction']/4
 summary['feature_groups'][b]=weights
(D/'FOUR_MONTH_RESEARCH_VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
manifest=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.name not in ('FILE_SHA256_MANIFEST.json', 'RUN_ALL.log'):
  with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  manifest.append({'name':p.name,'sha256':h,'size_bytes':p.stat().st_size})
(D/'FILE_SHA256_MANIFEST.json').write_text(json.dumps({'sha256_manifest':manifest},indent=2)+'\n')
out=ROOT/'R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 z.write(ROOT/'R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT.py','FILTER08/run_four_month_70pct_overfit.py')
 for p in sorted(D.iterdir()):
  if p.is_file() and p.name not in ('RUN_ALL.log',):z.write(p,arcname='FILTER08/'+p.name)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for x in manifest:
  binary=z.read('FILTER08/'+x['name']);assert len(binary)==x['size_bytes'] and hashlib.sha256(binary).hexdigest()==x['sha256']
with out.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
print('DONE',json.dumps({'path':str(out),'sha256':sha,'bytes':out.stat().st_size,'broker_aggregate':bybroker,'r9':summary['r9_quota_rollups']}),flush=True)
