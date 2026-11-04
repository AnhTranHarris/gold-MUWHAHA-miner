"""R24 full original raw quote month into source-exact as-of learner rows.

Run independently per broker-month, preserving atomic source receipts. No posthoc
R9 quotas in admission / feature tensor, only independent reporting.
"""
from __future__ import annotations
import argparse,gc,hashlib,json,time,sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r24_firstpass_engine as x


def run(source,month,decision_ms=1000,entry_lag_ms=100):
 start=time.monotonic();mon=f'{int(month):02d}'
 dest=x.R24/'results'/source/mon;dest.mkdir(exist_ok=True,parents=True)
 output=dest/f'R24_{source}_{mon}_{decision_ms}MS'
 import hashlib
 src=x.source_file(source,mon)
 rawsha=hashlib.file_digest(open(src,'rb'),'sha256').hexdigest()
 if rawsha!=x.source_pin(source,mon):raise ValueError('SOURCE_SHA_PIN_MISMATCH')
 t,b,a=x.raw_month(source,mon,verify=False)
 cand,gaps=x.candidates(t,b,a,decision_ms=decision_ms,cap=8000 if source=='DUKASCOPY_RAW' else 4000)
 # Monthly original broker source files are SERVER-month; preserved UTC
 # benchmark must discard leading previous-UTC-month timestamps. June is
 # corrected by original SHA-pinned July source tail, not interpolation.
 from datetime import datetime,timezone
 begin=int(datetime(2026,int(mon),1,tzinfo=timezone.utc).timestamp()*1000)
 end=int(datetime(2026, int(mon)+1 if int(mon)<12 else 1,1,tzinfo=timezone.utc).timestamp()*1000)
 cand=cand[(t[cand]>=begin)&(t[cand]<end)]
 fills=x.fill_after(t,b,a,cand,lag=entry_lag_ms,fillcap=8000 if source=='DUKASCOPY_RAW' else 4000)
 features=x.extract_features(t,b,a,cand,gaps,source)
 labels,event_ix,valid=x.generate_labels(t,b,a,cand,fills)
 assert features.shape==(len(cand),len(x.FEATURE_NAMES))
 assert labels.shape==(len(cand),2,3) and np.isfinite(features).all()
 # Every source sample has a true UTC timestamp; raw source original quote ordinal pinned.
 np.save(str(output)+'_features.npy',features,allow_pickle=False)
 np.save(str(output)+'_signal_utc_ms.npy',t[cand],allow_pickle=False)
 np.save(str(output)+'_source_quote_ordinal.npy',cand,allow_pickle=False)
 np.save(str(output)+'_fill_source_quote_ordinal.npy',fills,allow_pickle=False)
 np.save(str(output)+'_labels_2SIDE_3HORIZON.npy',labels,allow_pickle=False)
 np.save(str(output)+'_first_event_source_quote_ordinal.npy',event_ix,allow_pickle=False)
 # reference source hour and quarter identities (never used as learner features)
 qtime,qref=x.calendar_reference(mon)
 ci=np.searchsorted(qtime,t[cand]//900000*900000)
 valid_q=(ci<len(qtime))& (qtime[np.minimum(ci,len(qtime)-1)]==t[cand]//900000*900000)
 if not valid_q.all():raise RuntimeError('QUOTE_OUTSIDE_SOURCE_REFERENCED_MONTH')
 counts=np.bincount(ci,minlength=len(qref))
 g15=np.bincount(ci,weights=np.any(labels[:,:,0]==1,axis=1),minlength=len(qref))
 g30=np.bincount(ci,weights=np.any(labels[:,:,1]==1,axis=1),minlength=len(qref))
 g60=np.bincount(ci,weights=np.any(labels[:,:,2]==1,axis=1),minlength=len(qref))
 import csv
 with (dest/f'R24_{source}_{mon}_ALL_R9_SOURCE_QUARTER_RAW_CANDIDATE_AND_TP_COVERAGE.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['source','month','utc_quarter','original_R9_SYNTH_exact_quarter_reference','asof_observed_decision_candidates','any_side_future_target_before_stop_15s','any_side_future_target_before_stop_30s','any_side_future_target_before_stop_60s','future_label_not_decision'])
  for q in range(len(qref)):
   w.writerow([source,mon,datetime.fromtimestamp(int(qtime[q])/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),int(qref[q]),int(counts[q]),int(g15[q]),int(g30[q]),int(g60[q]),True])
 # exact partial row category counts retained incl right censor and unfilled
 bins={}
 for side,sd in enumerate(('BUY','SELL')):
  for h,sec in enumerate((15,30,60)):
   bins[f'{sd}_{sec}S']={name:int((labels[:,side,h]==k).sum()) for k,name in enumerate(x.CLASS_NAMES)}
 result={'status':'COMPLETE_ONE_BROKER_ONE_SOURCE_MONTH_FULL_RAW_TICK_PASS','date_utc':datetime.now(timezone.utc).isoformat(),
   'source':source,'month':mon,'raw_source':src.name,'source_sha256':rawsha,'source_bytes':src.stat().st_size,
   'raw_quote_rows':len(t),'initial_1sec_first_observed_tick_decision_clock_ms':decision_ms,
   'nominal_first_observed_fill_latency_ms':entry_lag_ms,'source_eligible_asof_decisions_after_v5_300s_warmup_and_spread':len(cand),
   'real_quotes_lagged_fill_attempts_successful':int(valid.sum()),'feature_schema_names':x.FEATURE_NAMES,
   'head3_x_label_cause_counts':bins,'original_R9_SYNTH_exact_source_month_target':int(qref.sum()),
   'source_active_hour_count':int((qref.reshape(-1,4).sum(axis=1)>0).sum()),'source_active_quarter_count':int((qref>0).sum()),
   'source_hour_total':len(qref)//4,'source_quarter_total':len(qref),
   'labelling_computes_targets_from_future_quotes_BUT_asof_features_past_only':True,
   'no_trained_policy_in_this_phase':True,'no_mt5_calendar_events_available':True,
   'nominal_sessions_informational_only':True,'historical_market_actual_broker_permission_UNKNOWN':True,
   'no_real_broker_execution_or_cash_PNL':True,'seconds':round(time.monotonic()-start,3)}
 # SHA of every derived output and atomic commit last
 result['outputs']={p.name:{'size':p.stat().st_size,'sha256':hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()}
  for p in sorted(dest.glob(f'R24_{source}_{mon}*')) if p.is_file() and not p.name.endswith('receipt.json')}
 (dest/f'R24_{source}_{mon}_SOURCE_PREPARATION_ATOMIC_receipt.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('feature_schema_names','head3_x_label_cause_counts','outputs')},indent=2),flush=True)
 return result

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',choices=x.SOURCE_NAMES,required=True);a.add_argument('--month',choices=('01','02','06','07'),required=True);a.add_argument('--decision-ms',type=int,default=1000)
 args=a.parse_args();run(args.source,args.month,decision_ms=args.decision_ms)
