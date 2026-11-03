"""R12D-XF: exact R9 SYNTH vs Dukascopy hourly spread-pressure SOURCE AUDIT.

Reads raw independently SHA-verified R9 SYNTH test-logger quote rows; preserves
all duplicate timestamps and also a distinct-ms diagnostic separately. These
are separate broker/feed domains; this is NOT an execution signal or price
conversion, never relaxes original H1V2 spread/fee/strict adverse requirements.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
R=Path('/mnt/data/h1v2_r12/results');ROOT=Path('/mnt/data')
HOURS=('2026-01-30T18:00:00Z','2026-02-02T01:00:00Z','2026-02-02T04:00:00Z','2026-02-02T05:00:00Z',
       '2026-02-02T06:00:00Z','2026-02-02T07:00:00Z','2026-02-02T08:00:00Z','2026-02-02T09:00:00Z',
       '2026-02-05T03:00:00Z','2026-02-06T01:00:00Z')


def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def report():
 source_rows=list(csv.DictReader((ROOT/'H1V2_ALL_246_HOURLY_IMPOSSIBILITY_WITNESSES_FULL_20261103.csv').open(newline='',encoding='utf8')))
 duk={x['utc_hour']:x for x in source_rows}
 missing=set(HOURS)-set(duk);assert not missing,missing
 periods={int(datetime.strptime(h,'%Y-%m-%dT%H:00:00Z').replace(tzinfo=timezone.utc).timestamp()*1000)//3600000:h for h in HOURS}
 hours=defaultdict(list); file_records=[]
 files=('R9_SYNTH_2026-01-30_ticks.csv.gz','R9_SYNTH_2026-02-02_ticks.csv.gz',
        'R9_SYNTH_2026-02-05_ticks.csv.gz','R9_SYNTH_2026-02-06_ticks.csv.gz')
 for name in files:
  p=ROOT/name;receiptp=ROOT/'h1v2_r12/atomic_r9_synth'/(name+'.entry_receipt.json')
  rec=json.loads(receiptp.read_text()); source_sha=sha(p)
  assert source_sha==rec['source_sha256'] and p.stat().st_size==rec['gzip_bytes'],name
  n=0;parsed=0
  with gzip.open(p,'rt',encoding='utf8',errors='strict',newline='') as f:
   read=csv.reader(f);hdr=next(read)
   assert (len(hdr)==31 and hdr[1]=='time_msc' and hdr[3]=='bid' and hdr[4]=='ask' and hdr[9]=='spread' and hdr[30]=='event')
   for row in read:
    n+=1
    if len(row)!=len(hdr):raise ValueError((name,n,'invalid tick record'))
    if row[0]!='SYNTH':raise ValueError((name,n,'unexpected source run label'))
    source_ms=int(row[1]);utc_ms=source_ms-2*3600000
    label=periods.get(utc_ms//3600000)
    if label is None:continue
    # Exact source storage has USD 0.01 quote precision and displayed points;
    # compare both independent reported spread sources within 1 USD cent.
    sprice=int(round((float(row[4])-float(row[3]))*1000))
    spoints=int(round(float(row[9])*10))
    if abs(sprice-spoints)>10:raise ValueError((name,row[1],'points disagreement',sprice,spoints))
    hours[label].append((source_ms,sprice,row[30],row[3],row[4]))
    parsed+=1
  assert n==rec['all_raw_source_rows'],(name,n,rec['all_raw_source_rows'])
  file_records.append({'source_file_name':name,'original_ID':rec.get('source_file_drive_id'),
                       'source_sha256':source_sha,'rows':n,'rows_in_selected_UTC_hours':parsed})
 def sums(arr):
  if not arr:return {}
  ss=sorted(x[1] for x in arr)
  return {'quote_event_rows':len(ss),'median_spread_raw_0p001USD':float(statistics.median(ss)),
          'p90_spread_raw_0p001USD':int(ss[min(len(ss)-1,int(.9*(len(ss)-1)))]),
          'pct_spread_above_1p50_USD':sum(x>1500 for x in ss)/len(ss),
          'event_ENTRY_BUY_or_ENTRY_SELL_count':sum(x[2] in ('ENTRY_BUY','ENTRY_SELL') for x in arr)}
 out=[]
 for h in HOURS:
  vals=hours[h];other=duk[h]
  distinct={}
  for tick in vals:distinct.setdefault(tick[0],tick)  # earliest source logger row per ms
  a=sums(vals);b=sums(list(distinct.values()))
  out.append({'utc_hour':h,'r9_SYNTH_original_entry_count':int(other['R9_SYNTH_UTC']),
     'dukascopy_raw_observed_quote_rows':int(float(other['raw_quotes'])),
     'dukascopy_raw_median_spread_0p001USD':float(other['raw_median_spread']),
     'dukascopy_pct_spread_gt_1p50':float(other['raw_pct_spread_gt1500']),
     'H1V2_original_first250_SAFE30_FAV15_count':int(float(other['strict_candidate_count'])),
     'H1V2_30sec_isolated_hour_capacity':int(float(other['R11S3_INDEPENDENT_HOUR_CROSSING_UPPER'])),
     'SYNTH_original_server_UTC_shift_hours':-2,
     'SYNTH_logger_raw_rows':a.get('quote_event_rows',0),
     'SYNTH_logger_median_spread_0p001USD':a.get('median_spread_raw_0p001USD'),
     'SYNTH_logger_pct_gt_1p50':a.get('pct_spread_above_1p50_USD'),
     'SYNTH_logger_ENTRY_events_in_hour':a.get('event_ENTRY_BUY_or_ENTRY_SELL_count'),
     'SYNTH_logger_first_per_ms_rows':b.get('quote_event_rows',0),
     'SYNTH_first_per_ms_median_spread_0p001USD':b.get('median_spread_raw_0p001USD'),
     'SYNTH_first_per_ms_pct_gt_1p50':b.get('pct_spread_above_1p50_USD'),
     'hypothesis_note':'source domain quotes only; no fill equivalence or same-source profitability inferred'})
 path=R/'R12D_XF_ALL_TEN_SOURCE_COUNT_STARVED_HOURS_R9_SYNTH_VS_DUKAS_SPREAD.csv'
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 receipt={'research':'R12D_XF_SOURCE_INDEPENDENT_DUKASCOPY_VS_R9_SYNTH_TESTER_SPREAD_DIAGNOSTIC',
  'source_10_h1v2_count_starved_hours':HOURS,'original_R9_source_files':file_records,
  'source_data_rows':out,'output_sha256':sha(path),
  'R9_SYNTH_QUOTE_LOGGER_CANNOT_INFER_TRUE_BROKER_FILL':True,
  'R11_ORIGINAL_S1_STILL_FROZEN':True,'any_altered_admission_spread_or_research_fee':False}
 p=R/'R12D_XF_TEN_HOUR_CROSSFEED_SOURCE_AUDIT_RECEIPT.json';p.write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'output':str(path),'SHA':sha(path),'rows':out,'file_sources':file_records},indent=2))
 return out
if __name__=='__main__':report()
