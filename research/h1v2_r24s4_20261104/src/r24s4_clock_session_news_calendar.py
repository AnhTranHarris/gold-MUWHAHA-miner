"""Full original 2026 H1V2 month/day/hour/quarter UTC research calendar.

The USD economic-event state is UNKNOWN until a point-in-time or verified
retrospective MT5/ForexFactory release schedule with contemporaneous UTC offset
and source provenance is provided; it is NOT equal to zero medium/high events.
An observed quote is not evidence that a prop firm, broker or strategy permits an
entry. No known 2026 historical news events are invented.
"""
from __future__ import annotations
import csv, hashlib, json, sys, argparse
from pathlib import Path
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import numpy as np
sys.path[:0]=['/mnt/data/h1v2_r24_asof/source','/mnt/data/h1v2_r24_asof/calendar']
import r24_firstpass_engine as r

ROOT=Path('/mnt/data/h1v2_r24s4_entry_specialists')
CITIES={'SYDNEY':'Australia/Sydney','TOKYO':'Asia/Tokyo','LONDON':'Europe/London','NEW_YORK':'America/New_York'}
WINDOWS={'SYDNEY':(9,17),'TOKYO':(9,18),'LONDON':(8,17),'NEW_YORK':(8,17)}
UNKNOWN='UNKNOWN_NEEDS_VERIFIED_HISTORICAL_PROVIDER_EXPORT'

def session_at(instant):
 if instant.tzinfo is None or instant.utcoffset()!=timedelta(0):raise ValueError('UTC_OFFSET_AWARE_REQUIRED')
 result={}
 for k,tz in CITIES.items():
  local=instant.astimezone(ZoneInfo(tz));a,b=WINDOWS[k]
  result[k+'_nominal_hours']=int(a<=local.hour<b and local.weekday()<5)
  result[k+'_local_clock']=local.strftime('%Y-%m-%d %H:%M:%S%z')
 result['SYDNEY_LONDON_nominal_overlap']=int(bool(result['SYDNEY_nominal_hours'] and result['LONDON_nominal_hours']))
 result['LONDON_NY_nominal_overlap']=int(bool(result['LONDON_nominal_hours'] and result['NEW_YORK_nominal_hours']))
 return result

def run(source,mon):
 p=r.R24/'results'/source/mon/f'R24_{source}_{mon}_1000MS'
 if not Path(str(p)+'_features.npy').exists():raise RuntimeError('NO_VERIFIED_ASOF_SOURCE')
 t=np.load(str(p)+'_signal_utc_ms.npy',mmap_mode='r')
 F=np.load(str(p)+'_fill_source_quote_ordinal.npy',mmap_mode='r')
 X=np.load(str(p)+'_features.npy',mmap_mode='r')
 q,ref=r.calendar_reference(mon);n=len(q)
 qi=(t//900000-q[0]//900000).astype(np.int64)
 if np.any((qi<0)|(qi>=n)):raise ValueError('SOURCE_MONTH_CLOCK_DRIFT')
 source_dec=np.bincount(qi,minlength=n).astype(np.int64)
 successful=np.bincount(qi[F>=0],minlength=n).astype(np.int64)
 spread=X[:,r.FEATURE_NAMES.index('spread_raw')]
 median=np.full(n,np.nan,np.float64)
 # Candidate volume per quarter is small enough to keep sorted streaming percentiles bounded.
 ix=np.r_[0,np.flatnonzero(np.diff(qi)>0)+1,len(qi)]
 for a,b in zip(ix[:-1],ix[1:]):
  median[qi[a]]=float(np.median(spread[a:b]))
 out=ROOT/'results'/source/mon
 out.mkdir(exist_ok=True,parents=True)
 qrows=[]
 for i,t0 in enumerate(q):
  stamp=datetime.fromtimestamp(int(t0)/1000,timezone.utc)
  active=int(source_dec[i]>0)
  qrows.append({'source':source,'month':mon,'utc_start':stamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
     'date_utc':stamp.strftime('%Y-%m-%d'),'iso_week':stamp.isocalendar().week,'weekday_utc':stamp.weekday(),
     'utc_hour':stamp.hour,'utc_quarter_in_hour':stamp.minute//15,
     'r9_SYNTH_original_quarter_target':int(ref[i]),
     'source_first_observed_1sec_decisions':int(source_dec[i]),
     'source_actual_100ms_fillable_attempts':int(successful[i]),
     'source_median_eligible_decision_spread_USD':median[i]/1000. if np.isfinite(median[i]) else None,
     'has_fresh_300s_eligible_source_decision':bool(active),
     'actual_broker_order_permission':UNKNOWN,
     'actual_prop_firm_operating_permission':UNKNOWN,
     'USD_medium_high_verified_calendar_event_count':None,
     'USD_medium_high_calendar_provenance':UNKNOWN,
     'ForexFactory_event_vintage_verified':False,
     'MT5_online_calendar_export_verified':False,
     'historical_actual_release_pre_news_model_feature_admissible':False,
     **session_at(stamp)})
 head=list(qrows[0]);qpath=out/f'R24S4_{source}_{mon}_COMPLETE_ORIGINAL_UTC_15MIN_SESSION_AND_NEWS_STATUS.csv'
 with qpath.open('w',newline='',encoding='utf8') as file:
  wr=csv.DictWriter(file,fieldnames=head);wr.writeheader();wr.writerows(qrows)
 aggregates=[]
 for stride,suffix in [(4,'HOURS'),(96,'DAYS')]:
  rows=[]
  for i in range(0,n,stride):
   a=qrows[i:i+stride]
   rows.append({'source':source,'month':mon,'utc_start':a[0]['utc_start'],
   'r9_SYNTH_original_reference':sum(z['r9_SYNTH_original_quarter_target'] for z in a),
   'source_first_observed_1sec_decisions':sum(z['source_first_observed_1sec_decisions'] for z in a),
   'source_actual_100ms_fillable_attempts':sum(z['source_actual_100ms_fillable_attempts'] for z in a),
   'actual_broker_order_permission':UNKNOWN,'actual_prop_firm_operating_permission':UNKNOWN,
   'USD_medium_high_verified_calendar_event_count':None,'USD_medium_high_calendar_provenance':UNKNOWN,
   'session_status':'NOMINAL_IANA_CLOCK_ONLY_NO_ORDER_PERMISSION_CERTIFICATION'})
  path=out/f'R24S4_{source}_{mon}_COMPLETE_ORIGINAL_UTC_{suffix}_CLOCK_AND_NEWS_STATUS.csv'
  with path.open('w',newline='',encoding='utf8') as file:
   wr=csv.DictWriter(file,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
  aggregates.append(path)
 def sha(p):
  with open(p,'rb') as file:return hashlib.file_digest(file,'sha256').hexdigest()
 rec={'status':'COMPLETE_RETROSPECTIVE_SOURCE_CLOCK_NO_HISTORICAL_EVENT_EXPORT',
  'source':source,'month':mon,'r9_source_quote_reference':int(ref.sum()),
  'exact_15min_rows':n,'exact_hour_rows':n//4,'exact_daily_rows':n//96,
  'eligible_observed_quote_decisions':int(source_dec.sum()),'actually_observed_fillable_actions':int(successful.sum()),
  'historical_mt5_news_available':False,'historical_forexfactory_news_verified':False,
  'permitted_broker_and_prop_hours':'UNKNOWN','not_event_impact_research_proof':True,
  'outputs':{v.name:sha(v) for v in [qpath,*aggregates]}}
 outp=out/f'R24S4_{source}_{mon}_COMPLETE_CALENDAR_AND_UNKNOWN_NEWS_RECEIPT.json'
 outp.write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps({k:v for k,v in rec.items() if k!='outputs'},indent=2),flush=True)
 return rec

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',choices=r.SOURCE_NAMES,required=True);a.add_argument('--month',choices=('01','02','06','07'),required=True);args=a.parse_args();run(args.source,args.month)
