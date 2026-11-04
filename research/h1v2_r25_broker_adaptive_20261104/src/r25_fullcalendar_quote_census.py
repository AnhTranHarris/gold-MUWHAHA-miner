"""R25 FULL 120-UTC-DAY x 2-feed original tick-state geometry census.

This is NOT a trading backtest: it audits raw quote counts, spread distribution,
as-of +300s fresh first source quote per 1s clock, and original source-exact
R9 SYNTH 15-minute/hour/day quota side by side for ALL periods, including zero-
reference buckets.  No future price or outcome is required to count signals.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,time
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from r25_broker_adaptive import ROOT,SOURCES,MONTHS,verify_gzip,r24

OUT=ROOT/'h1v2_r25'/'artifacts'/'full_calendar_quote_census'
OUT.mkdir(parents=True,exist_ok=True)

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write(path,rows):
 with path.open('w',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def run(source,mon):
 start=time.monotonic()
 pins=json.loads((ROOT/'h1v2_r25/artifacts/raw_source_sha256.json').read_text())
 cert=verify_gzip(source,mon,pins)
 t,b,a=r24.raw_month(source,mon,verify=False)
 qt,qr=r24.calendar_reference(mon)
 month_end=int(qt[-1])+900000
 qt_count=len(qt)
 if qt_count not in (2688,2880,2976):raise RuntimeError('BAD_R9_CALENDAR')
 spread=(a.astype(np.int64)-b.astype(np.int64))
 valid=(t>=qt[0])&(t<month_end)
 ix=np.flatnonzero(valid)
 if len(ix)==0:raise RuntimeError('NO_QUOTE_IN_ORIGINAL_MONTH')
 cid=((t[ix]-qt[0])//900000).astype(np.int32)
 all_quote=np.bincount(cid,minlength=qt_count)
 cnt15=np.bincount(cid,weights=(spread[ix]<=1500),minlength=qt_count).astype(np.int64)
 cnt40=np.bincount(cid,weights=(spread[ix]<=4000),minlength=qt_count).astype(np.int64)
 cnt60=np.bincount(cid,weights=(spread[ix]<=6000),minlength=qt_count).astype(np.int64)
 cnt80=np.bincount(cid,weights=(spread[ix]<=8000),minlength=qt_count).astype(np.int64)
 signal,gapstarts=r24.candidates(t,b,a,decision_ms=1000,cap=8000)
 signal=signal[(t[signal]>=qt[0])&(t[signal]<month_end)]
 sq=((t[signal]-qt[0])//900000).astype(np.int32)
 ss=spread[signal]
 s15=np.bincount(sq,weights=(ss<=1500),minlength=qt_count).astype(np.int32)
 s40=np.bincount(sq,weights=(ss<=4000),minlength=qt_count).astype(np.int32)
 s60=np.bincount(sq,weights=(ss<=6000),minlength=qt_count).astype(np.int32)
 s80=np.bincount(sq,weights=(ss<=8000),minlength=qt_count).astype(np.int32)
 lo=np.searchsorted(t,qt,side='left')
 hi=np.searchsorted(t,qt+900000,side='left')
 gaps=np.flatnonzero(np.diff(t)>15000).astype(np.int32)+1
 gq=((t[gaps]-qt[0])//900000).astype(np.int64)
 gq=gq[(gq>=0)&(gq<qt_count)]
 qg=np.bincount(gq,minlength=qt_count).astype(np.int32)
 qrows=[]
 for k in range(qt_count):
  st=int(lo[k]);en=int(hi[k]);n=int(all_quote[k]);
  if n!=en-st:raise AssertionError('QUOTE_QUARTER_RECONCILIATION_'+str(k))
  spr=spread[st:en]
  m=float(np.median(spr)) if n else None
  pp90=float(np.percentile(spr,90)) if n else None
  first=int(t[st]-qt[k]) if n else None
  last=int(qt[k]+900000-t[en-1]) if n else None
  qrows.append(dict(source=source,month='2026-'+mon,utc_quarter=datetime.fromtimestamp(int(qt[k]/1000),timezone.utc).isoformat(),
       original_R9_SYNTH_quarter_reference=int(qr[k]),r9_quarter_active=int(qr[k]>0),
       observed_source_bidask_quotes=n,source_quote_first_offset_ms=first,source_quote_last_to_end_ms=last,
       source_spread_median_raw=m,source_spread_p90_raw=pp90,
       source_spread_under_1500_raw_quotes=int(cnt15[k]),source_spread_under_4000_raw_quotes=int(cnt40[k]),
       source_spread_under_6000_raw_quotes=int(cnt60[k]),source_spread_under_8000_raw_quotes=int(cnt80[k]),
       source_asof_first_1s_300s_epoch_spread1500=int(s15[k]),
       source_asof_first_1s_300s_epoch_spread4000=int(s40[k]),
       source_asof_first_1s_300s_epoch_spread6000=int(s60[k]),
       source_asof_first_1s_300s_epoch_spread8000=int(s80[k]),
       source_gap_over15s_reacquisition_starts=int(qg[k]),
       note='PURE_SOURCE_STATE_COUNTS_NOT_TRADE_FILLS_OR_CORRECT_TRADES'))
 hrows=[]
 for h in range(qt_count//4):
  qs=qrows[h*4:h*4+4];d={'source':source,'month':'2026-'+mon,'utc_hour':qs[0]['utc_quarter'],
       'original_R9_SYNTH_hour_reference':sum(x['original_R9_SYNTH_quarter_reference'] for x in qs),
       'active_reference_quarters':sum(x['r9_quarter_active'] for x in qs)}
  for field in ('observed_source_bidask_quotes','source_asof_first_1s_300s_epoch_spread1500','source_asof_first_1s_300s_epoch_spread4000',
                'source_asof_first_1s_300s_epoch_spread6000','source_asof_first_1s_300s_epoch_spread8000','source_gap_over15s_reacquisition_starts'):
   d[field]=sum(x[field] for x in qs)
  hrows.append(d)
 drows=[]
 for day in range(qt_count//96):
  hrs=hrows[day*24:day*24+24]
  d={'source':source,'month':'2026-'+mon,'utc_day':hrs[0]['utc_hour'][:10],
     'original_R9_SYNTH_day_reference':sum(x['original_R9_SYNTH_hour_reference'] for x in hrs),
     'active_reference_hours':sum(x['original_R9_SYNTH_hour_reference']>0 for x in hrs)}
  for field in ('observed_source_bidask_quotes','source_asof_first_1s_300s_epoch_spread1500','source_asof_first_1s_300s_epoch_spread4000',
                'source_asof_first_1s_300s_epoch_spread6000','source_asof_first_1s_300s_epoch_spread8000','source_gap_over15s_reacquisition_starts'):
   d[field]=sum(x[field] for x in hrs)
  drows.append(d)
 qfile=OUT/f'R25_{source}_{mon}_ALL_{qt_count}_SOURCE_QUARTER_GEOMETRY.csv'
 hfile=OUT/f'R25_{source}_{mon}_ALL_{len(hrows)}_SOURCE_HOURLY_GEOMETRY.csv'
 dfile=OUT/f'R25_{source}_{mon}_ALL_{len(drows)}_SOURCE_DAILY_GEOMETRY.csv'
 write(qfile,qrows);write(hfile,hrows);write(dfile,drows)
 if sum(x['original_R9_SYNTH_hour_reference'] for x in hrows)!=int(qr.sum()):raise AssertionError('REF_DRIFT_H')
 if sum(x['original_R9_SYNTH_day_reference'] for x in drows)!=int(qr.sum()):raise AssertionError('REF_DRIFT_D')
 if sum(x['observed_source_bidask_quotes'] for x in drows)!=len(ix):raise AssertionError('SOURCE_QUOTE_MONTH_DRIFT')
 summary={'source':source,'month':'2026-'+mon,'days':len(drows),'hours':len(hrows),'quarters':len(qrows),
          'active_quarters':int(np.count_nonzero(qr)),'active_hours':sum(r['original_R9_SYNTH_hour_reference']>0 for r in hrows),
          'original_R9_SYNTH_reference':int(qr.sum()),'original_source_quote_sha':cert['sha256'],
          'observed_raw_month_quotes':len(ix),'source_eligible_1s_signals_spread1500':int(sum(s15)),
          'source_eligible_1s_signals_spread4000':int(sum(s40)),
          'source_eligible_1s_signals_spread6000':int(sum(s60)),
          'source_eligible_1s_signals_spread8000':int(sum(s80)),
          '15s_quote_gap_restarts':int(sum(qg)),
          'median_spread_of_month_raw':float(np.median(spread[ix])),
          'median_spread_of_month_quoted_USD':float(np.median(spread[ix])/1000),
          'not_actual_broker_execution':True,'no_future_path_labels':True,
          'does_not_measure_accuracy_or_profits':True,'elapsed_seconds':round(time.monotonic()-start,3),
          'artifacts':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in (qfile,hfile,dfile)}}
 out=OUT/f'R25_{source}_{mon}_SOURCE_HOURLY_QUARTER_DAY_RECEIPT.json'
 out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
 print(json.dumps(summary),flush=True)
 return summary

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,choices=SOURCES);ap.add_argument('--month',required=True,choices=MONTHS)
 args=ap.parse_args();run(args.source,args.month)
