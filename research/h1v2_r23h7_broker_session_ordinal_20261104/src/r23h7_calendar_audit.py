"""Read-only R23H24 original full-day/hour/quarter calendar augmentation.

Reads ALL 8 source-months of frozen E00 H15 causal replay, appends exact IANA
nominal regional daytime clocks and fail-closed economic/prop permission states.
NEVER changes outcome, R9 quota, broker fill, selected ordinal or original file.
"""
from __future__ import annotations
import csv,hashlib,json,sys,os
from datetime import datetime,timezone
from pathlib import Path
from collections import defaultdict
import numpy as np
from r23h7_clock_news import clock_features,CLOCK_NAMES
BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).resolve()
SOURCE=('DUKASCOPY_RAW','MT5_BROKER_EXPORT');MONTH=('01','02','06','07')
KINDS=('QUARTER','HOUR','DAY')

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write_clock(source,month,kind,outroot):
 p=BASE/'evaluated'/source/month/f'E00_VOLUME_FIRST_H15_{kind}_FULL_UNABRIDGED.csv'
 if not p.is_file():raise FileNotFoundError(str(p))
 with p.open('r',newline='',encoding='utf8') as h:rows=list(csv.DictReader(h))
 expected={'01':(2976,744,31),'02':(2688,672,28),'06':(2880,720,30),'07':(2976,744,31)}[month][KINDS.index(kind)]
 if len(rows)!=expected:raise AssertionError(('MISSING_UTC_BUCKETS',p,len(rows),expected))
 utc=[]; seen=set()
 for row in rows:
  label=row['utc_'+kind.lower()]
  dt=datetime.fromisoformat(label)
  if dt.tzinfo is None and kind!='DAY':raise ValueError('MISSING_EXPLICIT_UTC_OFFSET')
  if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
  if dt.utcoffset().total_seconds()!=0:raise ValueError('NOT_UTC_BUCKET')
  ts=int(dt.timestamp()*1000)
  if ts in seen:raise AssertionError('DUPLICATED_UTC_BUCKET')
  seen.add(ts);utc.append(ts)
 if np.any(np.diff(utc)<=0):raise AssertionError('NOT_SORTED_UTC')
 if kind=='QUARTER' and np.any(np.diff(utc)!=900000):raise AssertionError('MISSING_QUARTER')
 if kind=='HOUR' and np.any(np.diff(utc)!=3600000):raise AssertionError('MISSING_HOUR')
 if kind=='DAY' and np.any(np.diff(utc)!=86400000):raise AssertionError('MISSING_DAY')
 if kind=='DAY':
  # Exact UTC day features are descriptive proxy-hours, never a realized trader gate.
  hours=np.array([int(ts+j*3600000) for ts in utc for j in range(24)],np.int64)
  x=clock_features(hours).reshape(len(rows),24,len(CLOCK_NAMES))
  columns=['nominal_sydney_proxy_utc_hours','nominal_tokyo_proxy_utc_hours',
           'nominal_london_proxy_utc_hours','nominal_newyork_proxy_utc_hours']
  for i,row in enumerate(rows):
   for j,col in enumerate(columns):row[col]=int(x[i,:,4+j].sum())
 else:
  x=clock_features(np.array(utc,np.int64))
  columns=list(CLOCK_NAMES)
  for i,row in enumerate(rows):
   for j,col in enumerate(columns):row[col]=float(x[i,j])
 for row in rows:
  row.update({'clock_contract':'IANA_NOMINAL_REGION_PROXIES_ONLY',
     'broker_symbol_trading_permission':'UNKNOWN_UNVERIFIED_HISTORICAL_SERVER_SESSION',
     'prop_firm_trading_permission':'UNKNOWN_OWNER_CONTRACT_NOT_SUPPLIED',
     'mt5_medium_high_news_state':'UNKNOWN_NO_HISTORIC_ASOF_SNAPSHOT',
     'forexfactory_medium_high_news_state':'UNKNOWN_NO_HISTORIC_ASOF_SNAPSHOT',
     'forexfactory_scheduled_release_retrospective':'NOT_INGESTED'})
 dest=outroot/source/month/f'R23H7_{source}_{month}_{kind}_COMPLETE_CLOCK_RESEARCH.csv'
 dest.parent.mkdir(exist_ok=True,parents=True)
 tmp=dest.with_suffix('.tmp')
 with tmp.open('w',newline='',encoding='utf8') as h:
  writer=csv.DictWriter(h,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 os.replace(tmp,dest)
 input_sum=sum(int(r['R9_SYNTH_original_exact_UTC_reference']) for r in rows)
 filled_sum=sum(int(r['filled']) for r in rows)
 return {'source':source,'month':month,'kind':kind,'rows':len(rows),'original_sha256':sha(p),
         'original_path':str(p.relative_to(BASE)),'output_sha256':sha(dest),
         'output_path':str(dest),'R9_SYNTH_original_exact_UTC_reference_sum':input_sum,
         'original_causal_filled_sum':filled_sum,'source_rows_preserved':True,
         'no_events_or_permission_fabricated':True}

def run(outroot):
 outroot=Path(outroot);receipts=[]
 for source in SOURCE:
  for month in MONTH:
   for kind in KINDS:receipts.append(write_clock(source,month,kind,outroot))
    # Per-source-month full calendar arithmetic is independently cross checked.
 for s in SOURCE:
  for m in MONTH:
   group=[r for r in receipts if r['source']==s and r['month']==m]
   for field in ('R9_SYNTH_original_exact_UTC_reference_sum','original_causal_filled_sum'):
    if len({r[field] for r in group})!=1:raise AssertionError(('ROLLUP_MISMATCH',s,m,field,[r[field] for r in group]))
 expected={'01':27980,'02':33523,'06':31758,'07':24324}
 for r in receipts:
  assert r['R9_SYNTH_original_exact_UTC_reference_sum']==expected[r['month']]
 assert len(receipts)==24
 meta={'status':'R23H7_0007_READONLY_EIGHT_SOURCE_COMPLETE_CALENDAR_CLOCK_AUDIT',
  'rows_by_kind':{k:sum(r['rows'] for r in receipts if r['kind']==k) for k in KINDS},
  'source_months':8,'original_files_preserved':24,'outputs':receipts,
  'no_market_open_or_prop_permission_proof':True,'no_mql5_terminal_news_snapshot':True,
  'all_reference_counts_exact':True,'no_new_causal_trade_policy_result':True}
 p=outroot/'R23H7_ALL_EIGHT_SOURCE_MONTHS_24_OUTPUT_SHA_MANIFEST.json'
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(meta,indent=2)+'\n');os.replace(tmp,p)
 return meta
if __name__=='__main__':
 result=run(Path(__file__).resolve().parents[1]/'results'/'clock_audit')
 print(json.dumps({'status':result['status'],'rows_by_kind':result['rows_by_kind'],
                   'sha_manifest':str(Path(__file__).resolve().parents[1]/'results'/'clock_audit'/'R23H7_ALL_EIGHT_SOURCE_MONTHS_24_OUTPUT_SHA_MANIFEST.json')},indent=2))
