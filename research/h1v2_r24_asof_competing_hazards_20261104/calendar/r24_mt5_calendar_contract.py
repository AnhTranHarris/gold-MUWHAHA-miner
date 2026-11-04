"""R24 MT5 calendar source validation, offline as-of safety, broker hours.

The MQL exporter emits TRADE-SERVER-TIME; no historical timezone guessed.
A retroactive economic-calendar download is not a point-in-time tape.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
from pathlib import Path
import csv,hashlib,json

class CalendarSourceUnavailable(ValueError):pass

REQUIRED_SOURCE_STATUS={
 'research_contract':'R24_PRESERVATION_ONLY_NOT_EXECUTABLE_TRADING_POLICY',
 'historical_schedule_asof_revisions':'UNKNOWN_PROVIDER_DB_CAN_BE_RETROSPECTIVE',
}

def read_kv_tsv(p):
 with Path(p).open(newline='',encoding='utf-8-sig') as fh:
  rd=csv.DictReader(fh,delimiter='\t')
  if rd.fieldnames!=['key','value']:raise CalendarSourceUnavailable('NOT_STATUS_HEADER')
  rows=list(rd)
  if len(rows)!=len({r['key'] for r in rows}):raise CalendarSourceUnavailable('DUPLICATE_STATUS_FIELDS')
  return {r['key']:r['value'] for r in rows}

def read_server_time(s):
 try:return datetime.strptime(s,'%Y.%m.%d %H:%M:%S')
 except ValueError:raise CalendarSourceUnavailable('BAD_MT5_SERVER_TIMESTAMP '+s)

def normalize_economic_calendar(status_file,events_file,offset_segments_file,decision_time_data_provenance=None):
 """Return separate RETROSPECTIVE research events, never predictive as-of features.

The historical UTC offset segments MUST be supplied externally and supported by
original broker offset evidence; an MQL5 current TimeGMT reading is insufficient.
Missing source or unproved offset fail closed (rather than labeling no-news).
"""
 status=read_kv_tsv(status_file)
 for k,v in REQUIRED_SOURCE_STATUS.items():
  if status.get(k)!=v:raise CalendarSourceUnavailable('STATUS_SOURCE_CONTRACT_MISMATCH_'+k)
 if status.get('calendar_export_status')!='COMPLETE_RETROSPECTIVE_METADATA_UNVERIFIED_POINT_IN_TIME':
  raise CalendarSourceUnavailable('MT5_PROVIDER_NOT_COMPLETE')
 with Path(offset_segments_file).open(newline='',encoding='utf8') as f:
  segments=list(csv.DictReader(f,delimiter='\t'))
 if not segments:raise CalendarSourceUnavailable('MISSING_HISTORICAL_OFFSET_EVIDENCE')
 seg=[]
 for x in segments:
  if x.get('evidence_sha256') is None or len(x['evidence_sha256'])!=64:raise CalendarSourceUnavailable('MISSING_OFFSET_PROVENANCE_SHA')
  start=read_server_time(x['start_server']);end=read_server_time(x['end_server']);offset=int(x['utc_offset_seconds'])
  if end<=start or abs(offset)>14*3600:raise CalendarSourceUnavailable('BAD_BROKER_OFFSET')
  seg.append((start,end,offset,x['evidence_sha256']))
 seg.sort()
 for p,n in zip(seg,seg[1:]):
  if n[0]<p[1]:raise CalendarSourceUnavailable('OFFSET_OVERLAP')
 with Path(events_file).open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f,delimiter='\t'))
 required={'currency_filter','calendar_value_id','event_id','server_scheduled_time','event_importance','event_time_mode','event_name'}
 if not rows:raise CalendarSourceUnavailable('NO_PROVIDER_EVENTS_IS_NOT_VERIFIED_ZERO_NEWS')
 if not required.issubset(set(rows[0])):raise CalendarSourceUnavailable('EVENT_SCHEMA_UNRECOGNIZED')
 result=[];seen=set();unmappable=[]
 for row in rows:
  if row['event_importance'] not in ('CALENDAR_IMPORTANCE_MODERATE','CALENDAR_IMPORTANCE_HIGH'):continue
  if row['event_time_mode']!='CALENDAR_TIMEMODE_DATETIME':continue
  server=read_server_time(row['server_scheduled_time'])
  hits=[s for s in seg if s[0]<=server<s[1]]
  if len(hits)!=1:
   unmappable.append(row['calendar_value_id']);continue
  key=(row['calendar_value_id'],row['event_id'],server)
  if key in seen:continue
  seen.add(key)
  utc=(server-timedelta(seconds=hits[0][2])).replace(tzinfo=timezone.utc)
  result.append({'calendar_value_id':row['calendar_value_id'],'event_id':row['event_id'],
   'scheduled_utc':utc.isoformat(),'importance':row['event_importance'],
   'currency':row['currency_filter'],'event_name':row['event_name'],
   'historically_knowable_at_decision':'UNKNOWN_REQUIRES_POINT_IN_TIME_CALENDAR_SNAPSHOT',
   'model_asof_news_feature_admissible':False,'server_offset_evidence_sha256':hits[0][3]})
 if unmappable:raise CalendarSourceUnavailable('SOME_SERVER_EVENTS_HAVE_NO_SOURCE_VERIFIED_OFFSET '+str(len(unmappable)))
 if not result:raise CalendarSourceUnavailable('NO_MEDIUM_HIGH_EXACT_TIME_EVENTS')
 return result

def calendar_quarter_diagnostic(events,quarter_start_ms):
 """Retrospective research-only events in ±60m; NOT a model feature.
    Return UNKNOWN when no provider data rather than counting zero events.
 """
 if events is None:return {'impact_state':'UNKNOWN_UNVERIFIED_MT5_EXPORT','event_count':None}
 qt=datetime.fromtimestamp(quarter_start_ms/1000,timezone.utc)
 matches=[v for v in events if abs((datetime.fromisoformat(v['scheduled_utc'])-qt).total_seconds())<=3600]
 return {'impact_state':'HISTORICAL_RETROSPECTIVE_UNVERIFIED_POINT_IN_TIME',
  'retrospective_medium_high_event_count':len(matches),
  'no_causal_asof_impact_inference_from_retro_schedules':True}
