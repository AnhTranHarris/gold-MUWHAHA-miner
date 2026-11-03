"""Rebuild exact R9 SYNTH quarter-hour entry reference from ORIGINAL daily GZ.
No quota guesses: raw ENTRY_BUY/ENTRY_SELL event rows, immutable daily index.
UTC conversion follows original R11S3 source clock correction assumptions, and
must reproduce EVERY pinned R11S4 UTC hourly reference before certification.
The source log time conversion is a historical alignment assumption, not a
verified independent broker TimeTradeServer offset authority.
"""
from __future__ import annotations
import csv,datetime as dt,hashlib,json,gzip
from collections import Counter,defaultdict
from pathlib import Path
from r12_tp_oracle import write_csv,sha
ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r12/results'
OFFSET={'01':-2,'02':-2,'06':-3,'07':-3}
MONTH_KEYS={'01':'2026_01','02':'2026_02','06':'2026_06','07':'2026_07'}

def extract(mon):
 OUT.mkdir(parents=True,exist_ok=True)
 idx=list(csv.DictReader(open(ROOT/'R9_SYNTH_TICK_DRIVE_INDEX.csv',newline='',encoding='utf-8')))
 inputs=[q for q in idx if q['month']==MONTH_KEYS[mon]]
 assert len(inputs)>=20
 date_month=f'2026-{mon}'
 counts=Counter();hour=Counter();ev=[];checks=[]
 for r in inputs:
  p=ROOT/r['file_name']
  if not p.exists():raise FileNotFoundError(f'missing original indexed {r["file_name"]}')
  assert p.stat().st_size==int(r['size_bytes']),(p,'size vs index')
  s=sha(p);n=0;entries=0
  with gzip.open(p,'rt',encoding='utf-8',newline='') as f:
   rd=csv.DictReader(f)
   assert rd.fieldnames is not None and 'event' in rd.fieldnames and 'time_msc' in rd.fieldnames
   for v in rd:
    n+=1
    if v['event'] not in ('ENTRY_BUY','ENTRY_SELL'):continue
    entries+=1
    ms=int(v['time_msc']) + OFFSET[mon]*3600000
    if dt.datetime.fromtimestamp(ms/1000,dt.timezone.utc).strftime('%Y-%m')!=date_month:continue
    qo=ms//900000;ho=ms//3600000;counts[qo]+=1;hour[ho]+=1
    ev.append({'month':date_month,'utc_entry_ms':ms,'utc_hour':dt.datetime.fromtimestamp(ho*3600,dt.timezone.utc).strftime('%Y-%m-%dT%H:00:00Z'),
       'utc_quarter':dt.datetime.fromtimestamp(qo*900,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
       'trade_direction':v['event'],'original_server_time_msc':v['time_msc'],
       'original_source_day':r['date_utc'],'original_source_day_sha256':s})
  checks.append({'date':r['date_utc'],'file':p.name,'drive_id':r['drive_file_id'],'gzip_sha256':s,
                 'gz_bytes':p.stat().st_size,'total_quote_rows':n,'ENTRY_event_rows':entries})
 # Month boundary corrected UTC tails can arise from the NEXT SERVER MONTH first
 # day (June->July, Jan->Feb); scan only that first day for target UTC month.
 # The daily R9 index is server-clock labeled, so missing this step creates
 # inaccurate end-of-month 15-minute cells and hourly totals.
 next_mon=str(int(mon)+1).zfill(2)
 for r in idx:
  if r['month']!=f'2026_{next_mon}':continue
  if r!=next((q for q in idx if q['month']==f'2026_{next_mon}'),None):continue
  p=ROOT/r['file_name']
  if not p.exists():
   checks.append({'boundary_next_month_expected':p.name,'status':'MISSING_AND_ORIGINAL_HOUR_PARITY_WILL_FAIL_IF_RELEVANT'});continue
  assert p.stat().st_size==int(r['size_bytes'])
  s=sha(p);n=0;entry_n=0;included=0
  with gzip.open(p,'rt',encoding='utf-8',newline='') as f:
   for v in csv.DictReader(f):
    n+=1
    if v['event'] not in ('ENTRY_BUY','ENTRY_SELL'):continue
    entry_n+=1
    ms=int(v['time_msc'])+OFFSET[mon]*3600000
    if dt.datetime.fromtimestamp(ms/1000,dt.timezone.utc).strftime('%Y-%m')!=date_month:continue
    included+=1;qo=ms//900000;ho=ms//3600000;counts[qo]+=1;hour[ho]+=1
    ev.append({'month':date_month,'utc_entry_ms':ms,'utc_hour':dt.datetime.fromtimestamp(ho*3600,dt.timezone.utc).strftime('%Y-%m-%dT%H:00:00Z'),
      'utc_quarter':dt.datetime.fromtimestamp(qo*900,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
      'trade_direction':v['event'],'original_server_time_msc':v['time_msc'],'original_source_day':r['date_utc'],'original_source_day_sha256':s})
  checks.append({'boundary_next_month':r['date_utc'],'file':p.name,'gzip_sha256':s,'gz_bytes':p.stat().st_size,
                 'total_quote_rows':n,'ENTRY_event_rows':entry_n,'included_in_prior_UTC_month':included})
 # Original S4 reference source is authoritative and is read-only.
 src=ROOT/'h1v2_r12/results'/f'R12_{mon}_ALL_UTC_HOURS.csv'
 hh=list(csv.DictReader(open(src,newline='',encoding='utf-8')))
 expected={q['utc_hour']:int(q['r9_synth_hour_reference']) for q in hh}
 actual={dt.datetime.fromtimestamp(k*3600,dt.timezone.utc).strftime('%Y-%m-%dT%H:00:00Z'):v for k,v in hour.items()}
 mismatches=[{'hour':k,'s4_reference':v,'source_tick_recomputed':actual.get(k,0)} for k,v in expected.items() if actual.get(k,0)!=v]
 if mismatches:
  p=OUT/f'R12_{mon}_SYNTH_HOUR_MISMATCH.csv';write_csv(p,mismatches,list(mismatches[0]))
  raise ValueError(f'R9_SYNTH_HOUR_SOURCE_PARITY_FAILED {mon} {len(mismatches)} mismatch first {mismatches[:10]}')
 quarter_rows=list(csv.DictReader(open(OUT/f'R12_{mon}_ALL_UTC_QUARTERS.csv',newline='',encoding='utf-8')))
 for q in quarter_rows:
  ts=int(dt.datetime.strptime(q['utc_quarter'],'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp()*1000)
  ref=int(counts.get(ts//900000,0));sel=int(q['R12_first_TP_global_maxcount_quarter_selected']);cap=int(q['R12_first_TP_isolated_quarter_upper'])
  q['R9_SYNTH_exact_15min_reference']=ref
  q['R12_first_TP_quarter_100pct_reference_met']=int(sel>=ref) if ref else ''
  q['R12_first_TP_quarter_source_impossible']=int(cap<ref) if ref else ''
  q['R12_first_TP_quarter_deficit']=max(0,ref-sel) if ref else 0
 qwrite=OUT/f'R12_{mon}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv';write_csv(qwrite,quarter_rows,list(quarter_rows[0]))
 ev.sort(key=lambda x:x['utc_entry_ms'])
 p=OUT/f'R12_{mon}_ORIGINAL_R9_SYNTH_ALL_ENTRY_EVENTS_CLOCKALIGNED_UTC.csv'
 write_csv(p,ev,list(ev[0]))
 r={ 'month':date_month,'original_server_to_UTC_shift_hours':OFFSET[mon],
    'exact_R9_SYNTH_UTC_month_entry_count':len(ev),
    'exact_source_hourly_parity_all_hours':True,'source_hourly_mismatches':0,
    'original_month_quarter_count':len(quarter_rows),'original_quarters_with_positive_synth_ref':sum(int(q['R9_SYNTH_exact_15min_reference'])>0 for q in quarter_rows),
    'R12_quarters_meeting_100pct_R9_SYNTH':sum(int(q['R12_first_TP_quarter_100pct_reference_met']) for q in quarter_rows if q['R12_first_TP_quarter_100pct_reference_met']!=''),
    'R12_quarters_source_infeasible_first_TP':sum(int(q['R12_first_TP_quarter_source_impossible']) for q in quarter_rows if q['R12_first_TP_quarter_source_impossible']!=''),
    'exact_daily_source_index':checks,
    'full_original_R9_SYNTH_UTC_event_count_per_quarter_is_not_guessed':True,
    'FUTURE_ORACLE_NOT_FORECAST':True,
    'files_SHA256':{x.name:sha(x) for x in [qwrite,p]}}
 j=OUT/f'R12_{mon}_SYNTH_QUARTER_FULL_SOURCE_RECEIPT.json';j.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k!='exact_daily_source_index'},indent=2),flush=True)
 return r

if __name__=='__main__':
 import argparse
 q=argparse.ArgumentParser();q.add_argument('--month',required=True,choices=OFFSET);args=q.parse_args();extract(args.month)
