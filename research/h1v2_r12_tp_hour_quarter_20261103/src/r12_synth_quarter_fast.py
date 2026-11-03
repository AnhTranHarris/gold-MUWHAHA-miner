"""R12 resume-safe FAST exact R9 SYNTH daily-entry scanner and 15-min aggregator.
No source file modification. Original daily gzip CRC, file size, SHA are pinned.

Use quoted CSV header once; event is the final unquoted source logger column.
Only ENTRY_BUY and ENTRY_SELL events are emitted. Other rows are counted, not
misclassified as trade entries. Daily atomic receipts prevent timeout losses.
The prior slow DictReader research script is an immutable control.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,gzip,hashlib,json,os
from collections import Counter
from pathlib import Path
from r12_tp_oracle import sha,write_csv

ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r12/results';ATOM=ROOT/'h1v2_r12/atomic_r9_synth'
OFF={'01':-2,'02':-2,'06':-3,'07':-3}

def _atomic_write(path:Path, data:bytes):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+'.write_in_progress')
 tmp.write_bytes(data);os.replace(tmp,path)

def scan_day(row):
 file=ROOT/row['file_name'];target=ATOM/(file.name+'.entry_receipt.json')
 assert file.is_file(),('MISSING_SOURCE',file)
 assert file.stat().st_size==int(row['size_bytes']),('SOURCE_FILE_SIZE_DRIFT',file)
 digest=sha(file)
 if target.exists():
  j=json.loads(target.read_text())
  if j['source_sha256']==digest and j['gzip_bytes']==file.stat().st_size and j['source_file_drive_id']==row['drive_file_id']:
   return j
  raise ValueError('STALE_OR_CORRUPT_ATOMIC_CACHE '+str(target))
 n=0;ev=[];first=None;last=None
 with gzip.open(file,'rb') as f:
  head=f.readline().rstrip(b'\r\n').decode('utf-8').split(',')
  assert head[1]=='time_msc' and head[-1]=='event' and len(head)==31,(file,head)
  for line in f:
   n+=1
   kind=line.rsplit(b',',1)[-1].strip()
   if kind not in (b'ENTRY_BUY',b'ENTRY_SELL'):continue
   timestamp=int(line.split(b',',2)[1]);evt=kind.decode('ascii')
   if first is None:first=timestamp
   last=timestamp
   ev.append([timestamp,evt])
 assert n>0 and first is not None,('NO_ENTRIES_UNEXPECTED',file)
 data={'source_date_index':row['date_utc'],'source_file_name':file.name,'source_file_drive_id':row['drive_file_id'],
       'source_sha256':digest,'gzip_bytes':file.stat().st_size,'all_raw_source_rows':n,
       'entry_events':ev,'entry_event_count':len(ev),'first_original_server_ms':first,'last_original_server_ms':last,
       'original_source_immutable':True}
 _atomic_write(target,(json.dumps(data,ensure_ascii=True,separators=(',',':'))+'\n').encode('utf8'))
 return data

def rebuild(month):
 OUT.mkdir(parents=True,exist_ok=True)
 index=list(csv.DictReader(open(ROOT/'R9_SYNTH_TICK_DRIVE_INDEX.csv',newline='',encoding='utf8')))
 selected=[r for r in index if r['month']==f'2026_{month}']
 assert len(selected)>=20
 following=f'2026_{int(month)+1:02d}'
 first_next=next((r for r in index if r['month']==following),None)
 if first_next:selected.append(first_next)
 checks=[];ev=[];ht=Counter();qt=Counter();wanted=f'2026-{month}'
 for idx,row in enumerate(selected):
  source=scan_day(row)
  checks.append({k:v for k,v in source.items() if k!='entry_events'})
  for serverms,kind in source['entry_events']:
   ms=int(serverms)+OFF[month]*3600000
   if dt.datetime.fromtimestamp(ms/1000,dt.timezone.utc).strftime('%Y-%m')!=wanted:continue
   h=ms//3600000;q=ms//900000;ht[h]+=1;qt[q]+=1
   ev.append({'month':wanted,'utc_entry_ms':ms,'utc_hour':dt.datetime.fromtimestamp(h*3600,dt.timezone.utc).strftime('%Y-%m-%dT%H:00:00Z'),
        'utc_quarter':dt.datetime.fromtimestamp(q*900,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
        'trade_direction':kind,'original_server_time_msc':serverms,'original_source_day':row['date_utc'],
        'original_source_day_sha256':source['source_sha256']})
  print(month,'daily_atomic',idx+1,'/',len(selected),row['date_utc'],source['entry_event_count'],'original entry rows',flush=True)
 hours=list(csv.DictReader(open(OUT/f'R12_{month}_ALL_UTC_HOURS.csv',newline='',encoding='utf8')))
 mismatches=[]
 for r in hours:
  utc=int(dt.datetime.strptime(r['utc_hour'],'%Y-%m-%dT%H:00:00Z').replace(tzinfo=dt.timezone.utc).timestamp())
  z=int(ht.get(utc//3600,0));ref=int(r['r9_synth_hour_reference'])
  if z!=ref:mismatches.append({'hour':r['utc_hour'],'source_count':z,'original_S4_hourly_reference':ref})
 if mismatches:
  p=OUT/f'R12_{month}_FAST_HOUR_PARITY_FAILURE.csv';write_csv(p,mismatches,list(mismatches[0]));raise AssertionError(f'{len(mismatches)} original R9 SYNTH hourly mismatches {mismatches[:6]}')
 quarters=list(csv.DictReader(open(OUT/f'R12_{month}_ALL_UTC_QUARTERS.csv',newline='',encoding='utf8')))
 for r in quarters:
  utc=int(dt.datetime.strptime(r['utc_quarter'],'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp())
  ref=int(qt.get(utc//900,0));selected=int(r['R12_first_TP_global_maxcount_quarter_selected']);upper=int(r['R12_first_TP_isolated_quarter_upper'])
  r['R9_SYNTH_exact_15min_reference']=ref
  r['R12_first_TP_quarter_100pct_reference_met']=int(selected>=ref) if ref else ''
  r['R12_first_TP_quarter_source_impossible']=int(upper<ref) if ref else ''
  r['R12_first_TP_quarter_deficit']=max(0,ref-selected) if ref else 0
 ev.sort(key=lambda x:x['utc_entry_ms'])
 qpath=OUT/f'R12_{month}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv';write_csv(qpath,quarters,list(quarters[0]))
 epath=OUT/f'R12_{month}_ORIGINAL_R9_SYNTH_ALL_ENTRY_EVENTS_CLOCKALIGNED_UTC.csv';write_csv(epath,ev,list(ev[0]))
 result={'month':wanted,'server_UTC_hour_offset':OFF[month],'exact_R9_SYNTH_UTC_month_entry_count':len(ev),
         'exact_source_hourly_parity_all_hours':True,'source_hourly_mismatches':0,
         'UTC_hour_count':len(hours),'UTC_quarter_count':len(quarters),
         'source_active_quarters':sum(int(q['R9_SYNTH_exact_15min_reference'])>0 for q in quarters),
         'R12_quarters_meeting_100pct_R9_SYNTH':sum(int(q['R12_first_TP_quarter_100pct_reference_met']) for q in quarters if q['R12_first_TP_quarter_100pct_reference_met']!=''),
         'R12_quarters_source_infeasible_first_TP':sum(int(q['R12_first_TP_quarter_source_impossible']) for q in quarters if q['R12_first_TP_quarter_source_impossible']!=''),
         'atomic_original_daily_receipts':checks,
         'all_S1_strict_labels_are_offline_future_known':True,
         'source_original_index_Google_Sheet':'https://docs.google.com/spreadsheets/d/1VIx7mDN-sHBj2kQ5-JueV4V-sIHnFhPadOYClgLG_I8/edit',
         'files_SHA256':{p.name:sha(p) for p in [qpath,epath]}}
 jsonpath=OUT/f'R12_{month}_SYNTH_QUARTER_FULL_SOURCE_RECEIPT_FAST.json'
 _atomic_write(jsonpath,(json.dumps(result,indent=2)+'\n').encode())
 print(json.dumps({k:v for k,v in result.items() if k!='atomic_original_daily_receipts'},indent=2),flush=True)
 return result

if __name__=='__main__':
 x=argparse.ArgumentParser();x.add_argument('--month',choices=OFF,required=True);a=x.parse_args();rebuild(a.month)
