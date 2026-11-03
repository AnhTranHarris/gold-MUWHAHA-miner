"""R12 independent, read-only strict-entry / executable first-TP exit hindsight experiment.

Inputs are SHA-verified frozen R11S1 15/30 labels and raw Dukascopy quotes.
Original label: favorable >=+$0.10 net by 15s, no -$0.10 opening-liq
movement at any time through a FULL source-verified 30s after entry.
New DISTINCT occupancy: first quote crossing nominal TP +$0.10 net, 1 pos.
This is a hindsight ORACLE: future labels and future TP timestamps are USED
for selection and cannot become as-of decision features.

Source references: original R11S1 entry_survivability.py, R11S4 hour_quota_oracle.py.
Original H1V2, R9 v2, R11S1/S2/S3/S4/S5 are immutable and untouched.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,os,time,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from numba import njit

SRC=Path('/mnt/data'); OUT=Path('/mnt/data/h1v2_r12/results')
MONTHS=('01','02','06','07')
RAW_SHA={'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
 '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
 '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}
S1_ZIP_SHA={'01':'97d98454751f0037581cc706260a60f7bc8085e5ae3b92ca719474b719041dee',
 '02':'ab014ab2ef6512b5870fcdc50f0828c33f8b3a09547d886225ad7915037e27dc',
 '06':'4b46b337d84a2ab16be63c61edea9e98160d9a288b6ae14ddebe79ae484a1194',
 '07':'2352e60f7f8c374d533ae3c91aac6def25adb47696ecb0728065c34d025f1ce5'}
EXPECTED={'01':(9135062,4012834,666023,35652),'02':(7538339,3076349,548356,33640),
 '06':(8201406,4173378,768043,40296),'07':(7415841,4038891,610185,35813)}
FAV_RAW=120; FEE_RAW=20; TP_HORIZON=15000

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def write_csv(p,rows,fields):
 with open(p,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='raise');w.writeheader();w.writerows(rows)

def load_labels(mon):
 zpath=next(iter(sorted(SRC.glob(f'R11S_{mon}_FULLMONTH_FIXED15_30_SURVIVAL_FULLPOP_LABELS_CALENDARS_SOURCE_20261103.zip'))),None)
 if zpath is None:raise FileNotFoundError(mon)
 assert sha(zpath)==S1_ZIP_SHA[mon],('source ZIP SHA mismatch',mon)
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None,('source ZIP CRC failure',mon)
  name=next(n for n in z.namelist() if n.endswith('_ALL_V5_CANDIDATE_H15_H30_EXACT_SURVIVAL_LABELS.npz'))
  blob=z.read(name)
  manifest=json.loads(z.read('SURVIVAL_COMPLETE_SOURCE_MANIFEST.json'))
  assert hashlib.sha256(blob).hexdigest() in json.dumps(manifest),('unmanifested label bytes',mon)
 with np.load(io.BytesIO(blob),allow_pickle=False) as v:
  required=('source_tick_ordinal','entry_utc_ms','entry_bid_raw','entry_ask_raw','h15_BUY_survives_and_favorable',
            'h15_SELL_survives_and_favorable','h30_BUY_survives_no_adverse',
            'h30_SELL_survives_no_adverse','h30_coverage')
  d={k:v[k].copy() for k in required}
 assert len(d['entry_utc_ms'])==EXPECTED[mon][1]
 valid_buy=d['h15_BUY_survives_and_favorable'] & d['h30_BUY_survives_no_adverse'] & d['h30_coverage']
 valid_sell=d['h15_SELL_survives_and_favorable'] & d['h30_SELL_survives_no_adverse'] & d['h30_coverage']
 assert not np.any(valid_buy & valid_sell),('two side good',mon)
 valid=valid_buy|valid_sell
 assert np.count_nonzero(valid)==EXPECTED[mon][2],('strict candidate cardinality mismatch',mon)
 ix=d['source_tick_ordinal'][valid].copy()
 t=d['entry_utc_ms'][valid].copy()
 bid=d['entry_bid_raw'][valid].copy();ask=d['entry_ask_raw'][valid].copy()
 side=np.where(valid_buy[valid],1,-1).astype(np.int8)
 assert np.all(np.diff(t)>=0) and np.all(np.diff(ix)>0)
 return {'ix':ix,'t':t,'bid':bid,'ask':ask,'side':side,'labels_sha256':hashlib.sha256(blob).hexdigest(),
         'zip_sha256':S1_ZIP_SHA[mon]}

def read_raw(mon):
 import pandas as pd
 p=SRC/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 assert sha(p)==RAW_SHA[mon],('RAW SOURCE SHA mismatch',mon)
 a=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
               dtype={'timestamp_ms_utc':np.int64,'bid_raw':np.int32,'ask_raw':np.int32})
 t=a['timestamp_ms_utc'].to_numpy(copy=True);b=a['bid_raw'].to_numpy(copy=True);ask=a['ask_raw'].to_numpy(copy=True)
 assert len(t)==EXPECTED[mon][0] and np.all(t[1:]>=t[:-1]) and np.all(b<=ask)
 return t,b,ask

@njit(cache=True)
def quote_tp_first(t,b,a,ix,entry_a,entry_b,side,horizon=TP_HORIZON,thr=FAV_RAW):
 """Use strictly later-ms source quote; exact event ordinal and observed executable side."""
 n=len(ix); end_ix=np.full(n,-1,np.int64); exit_ms=np.full(n,-1,np.int64)
 for k in range(n):
  i=ix[k]; start=t[i]; stop=start+horizon
  j=i+1
  if side[k]==1:
   target=entry_a[k]+thr
   while j<len(t) and t[j]<=stop:
    if t[j]>start and b[j]>=target:
     end_ix[k]=j;exit_ms[k]=t[j];break
    j+=1
  else:
   target=entry_b[k]-thr
   while j<len(t) and t[j]<=stop:
    if t[j]>start and a[j]<=target:
     end_ix[k]=j;exit_ms[k]=t[j];break
    j+=1
 return end_ix,exit_ms

def earliest_finish_schedule(start_ms,end_ms):
 """Exact maximal cardinality of arbitrary known [entry, first TP] intervals;
 lex sort by exit then entry; strictly later entry after last exit.
 """
 assert len(start_ms)==len(end_ms) and (end_ms>start_ms).all()
 order=np.lexsort((start_ms,end_ms));ends=end_ms[order];starts=start_ms[order]
 out=np.empty(len(order),np.int64);n=0;last=-2**62
 for k in range(len(order)):
  if starts[k]>last:
   out[n]=order[k];n+=1;last=ends[k]
 return out[:n]

def greedy_equal_ms(start_ms,reserve=30000):
 order=np.argsort(start_ms,kind='stable');out=[];last=-2**62
 for k in order:
  if start_ms[k]>last+reserve:
   out.append(k);last=start_ms[k]
 return np.asarray(out,dtype=np.int64)

def local_optimal_capacity(t0,t1,quarter_start,quarter_ms=900000):
 """Per quarter optimistic upper, ignore prior quarter incoming position conflicts.
 Reuses globally known (strict only) intervals from exact source."""
 buckets=(t0-quarter_start)//quarter_ms
 n=(int((t0.max()-quarter_start)//quarter_ms)+1) if len(t0) else 0
 results=np.zeros(n,np.int32)
 for q in range(n):
  ids=np.flatnonzero(buckets==q)
  if not len(ids):continue
  sel=earliest_finish_schedule(t0[ids],t1[ids]);results[q]=len(sel)
 return results

def hour_key(ts):return datetime.fromtimestamp(int(ts)//3600000*3600,tz=timezone.utc).strftime('%Y-%m-%dT%H:00:00Z')
def quarter_key(ts):return datetime.fromtimestamp(int(ts)//900000*900,tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z')

def load_original_hour(mon):
 zpath=SRC/'R11S4_ALL_FOUR_COMPLETE_HOUR_DAY_MONTH_STRICT_15FAV_30SURV_HINDSIGHT_20261103.zip'
 with zipfile.ZipFile(zpath) as z:
  xs=list(csv.DictReader(io.StringIO(z.read(f'month_{mon}/R11S4_{mon}_ALL_UTC_HOURS.csv').decode())))
 assert len(xs) in (672,720,744)
 return {r['utc_hour']:{'R9_SYNTH_UTC':int(r['R9_SYNTH_UTC']),
                         'R11S4_30SEC_SELECTED':int(r['R11S4_HOUR_QUOTA_BEAM_ENTRIES']),
                         'R11S3_30SEC_UPPER':int(r['R11S3_INDEPENDENT_HOUR_CROSSING_UPPER'])} for r in xs}

def main(mon):
 start_clock=time.time();OUT.mkdir(exist_ok=True,parents=True)
 label=load_labels(mon);rawt,b,a=read_raw(mon)
 ix=label['ix'];T=label['t'];side=label['side'];entry_b=label['bid'];entry_a=label['ask']
 assert np.array_equal(rawt[ix],T) and np.array_equal(b[ix],entry_b) and np.array_equal(a[ix],entry_a),('SOURCE_ORDINAL_OR_PRICE_DRIFT',mon)
 exits,exitms=quote_tp_first(rawt,b,a,ix,entry_a,entry_b,side)
 assert np.all(exits>=0),('S1 strict positive first15 contradiction',mon,np.count_nonzero(exits<0))
 assert np.all(exitms>T) and np.all(exitms<=T+TP_HORIZON)
 liq=np.where(side>0,b[exits],a[exits]).astype(np.int64)
 pnl=((liq-np.where(side>0,entry_a,entry_b))*side-FEE_RAW).astype(np.int64)
 assert np.all(pnl>=100),(mon,'TP executable nominal net below $0.10')
 duration=exitms-T
 g=earliest_finish_schedule(T,exitms)
 assert np.all(T[g[1:]]>exitms[g[:-1]]),(mon,'selected overlaps')
 # Baseline strict 30s global max COUNT independent control from original frozen labels.
 # We do NOT compare to original S4 beam per-hour scheduling directly as objectives differ.
 refs=load_original_hour(mon)
 n_quarters=(len(refs)*4);quarterkeys=sorted(refs)
 observed={}
 selected_utc_hour={}
 for idx in g:
  hh=hour_key(T[idx]);qq=quarter_key(T[idx]);selected_utc_hour[hh]=selected_utc_hour.get(hh,0)+1
  observed[qq]=observed.get(qq,0)+1
 # exact within-hour independent optimistic maximum and quarter optimistic maximum under TP occupancy.
 h_bucket=T//3600000; q_bucket=T//900000
 hour_upp={};q_upp={};hr_candidates={};q_candidates={}
 def capacity(codes,upp,cands):
  cuts=np.flatnonzero(np.diff(codes))+1
  offsets=np.r_[0,cuts,len(codes)]
  for s,e in zip(offsets[:-1],offsets[1:]):
   bucket=int(codes[s]);cands[bucket]=int(e-s)
   upp[bucket]=len(earliest_finish_schedule(T[s:e],exitms[s:e]))
 capacity(h_bucket,hour_upp,hr_candidates);capacity(q_bucket,q_upp,q_candidates)
 quarters=[];hours=[]
 for h in quarterkeys:
  base=refs[h];ht=int(datetime.strptime(h,'%Y-%m-%dT%H:00:00Z').replace(tzinfo=timezone.utc).timestamp()*1000)
  ref=base['R9_SYNTH_UTC'];got=selected_utc_hour.get(h,0);upper=hour_upp.get(ht//3600000,0)
  hours.append({'month':'2026-'+mon,'utc_hour':h,'r9_synth_hour_reference':ref,
   'R11S4_original_30s_selected':base['R11S4_30SEC_SELECTED'],'R11S3_original_30s_hourly_upper':base['R11S3_30SEC_UPPER'],
   'R12_first_TP_global_maxcount_hourly_selected':got,'R12_first_TP_isolated_hour_upper':upper,
   'R12_first_TP_hour_candidates':hr_candidates.get(ht//3600000,0),
   'original_hour_active':int(ref>0),'R12_hourly_reference_met':int(got>=ref) if ref else '',
   'R12_hourly_unattainable_with_same_first_TP_interval_set':int(upper<ref) if ref else ''})
  for d in range(4):
   qt=ht+d*900000;qq=quarter_key(qt)
   quarters.append({'month':'2026-'+mon,'utc_quarter':qq,'utc_hour':h,'quarter_ordinal_in_hour':d,
     'R9_SYNTH_exact_15min_reference':'UNVERIFIED_PENDING_TICK_SOURCE',
     'R11S4_original_30s_selected_in_quarter':'PENDING_ORIGINAL_SELECTED_TRACE_RECONCILIATION',
     'R12_first_TP_global_maxcount_quarter_selected':observed.get(qq,0),
     'R12_first_TP_isolated_quarter_upper':q_upp.get(qt//900000,0),
     'R12_first_TP_candidate_count_in_quarter':q_candidates.get(qt//900000,0)})
 # Export EVERY selected quote-ordinal and entrance/exit. NO aggregation-only evidence.
 paths=[]
 result=[]
 for idx in g:
  result.append({'month':'2026-'+mon,'entry_utc_ms':int(T[idx]),'entry_utc_hour':hour_key(T[idx]),'entry_utc_quarter':quarter_key(T[idx]),
   'entry_tick_ordinal':int(ix[idx]),'exit_utc_ms':int(exitms[idx]),'exit_tick_ordinal':int(exits[idx]),
   'side':int(side[idx]),'entry_ask_raw':int(entry_a[idx]),'entry_bid_raw':int(entry_b[idx]),
   'exit_liquidation_raw':int(liq[idx]),'nominal_net_raw_after_fee':int(pnl[idx]),
   'hold_ms':int(duration[idx]),'full_30sec_no_adverse_after_entry_verified_by_original_S1':True,
   'not_a_causal_entry_model':True})
 for name,rows in [(f'R12_{mon}_ALL_UTC_HOURS.csv',hours),(f'R12_{mon}_ALL_UTC_QUARTERS.csv',quarters),
                  (f'R12_{mon}_ALL_EXECUTABLE_FIRSTTP_SELECTED_SOURCE_QUOTE_TRACES.csv',result)]:
  p=OUT/name;write_csv(p,rows,list(rows[0]));paths.append(p)
 summary={'month':mon,'source_raw_sha256':RAW_SHA[mon],'labels_archive_sha256':label['zip_sha256'],
  'full_original_label_npz_sha256':label['labels_sha256'],'raw_rows':len(rawt),'v5_candidates':EXPECTED[mon][1],
  'strict15fav30surv_candidates':len(T),'selected_first_TP_maxcount_global':len(g),
  'old_S4_global_30s_selected':EXPECTED[mon][3],
  'hour_UTC_rows':len(hours),'quarter_UTC_rows':len(quarters),
  'hour_100pct_reference_met':sum(int(h['R12_hourly_reference_met']) for h in hours if h['original_hour_active']),
  'hour_100pct_reference_unattainable_first_TP':sum(h['R12_hourly_unattainable_with_same_first_TP_interval_set'] for h in hours if h['original_hour_active']),
  'original_active_hours':sum(h['original_hour_active'] for h in hours),
  'total_R9_SYNTH_UTC_hour_reference':sum(h['r9_synth_hour_reference'] for h in hours),
  'total_R12_first_TP_selected_over_reference_active_and_inactive':len(g),
  'min_nominal_net_raw':int(pnl[g].min()),'median_nominal_net_raw':float(np.median(pnl[g])),
  'median_holding_ms':float(np.median(duration[g])),'mean_holding_ms':float(np.mean(duration[g])),
  'p90_holding_ms':float(np.percentile(duration[g],90)),
  'model_classification':'FUTURE_SELECTED_ORACLE_NOT_CAUSAL',
  'changed_occupancy_contract':'FIRST_EXECUTABLE_SOURCE_QUOTE_TP_0.10_NET_AND_ORIGINAL_30S_STRICT_ENTRY_LABEL',
  'commission_fee_nominal_raw':FEE_RAW,'broker_fill_slippage_latency':'UNMODELED',
  'R9_SYNTH_15min_references':'UNVERIFIED',
  'elapsed_seconds':round(time.time()-start_clock,2)}
 p=OUT/f'R12_{mon}_FULL_RESEARCH_RECEIPT.json';p.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');paths.append(p)
 summary['SHA256_ALL_OUTPUTS']={p.name:sha(p) for p in paths}
 (OUT/f'R12_{mon}_OUTPUT_HASHES.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
 print(json.dumps(summary,indent=2),flush=True)
 return summary

if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--month',required=True,choices=MONTHS);a=q.parse_args();main(a.month)
