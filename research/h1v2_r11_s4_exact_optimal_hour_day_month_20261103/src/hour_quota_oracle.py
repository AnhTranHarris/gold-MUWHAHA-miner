"""R11S4, strictly future-privileged, beam-search hour/day/month 30-second scheduler.

Independently process each complete 2026 Jan/Feb/Jun/Jul immutable R11-S1 label
archive. No original label/exit/holding change. All feature labels are FUTURE.
This is not a causal student or real trading model. Source R9 SYNTH clock-aligned
UTC hourly quotas come exclusively from immutable R11S3 2880-row CSV.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, io, json, pathlib, zipfile, time, os
from dataclasses import dataclass
import numpy as np
import pandas as pd
from numba import njit

ROOT=pathlib.Path('/mnt/data'); HERE=ROOT/'r11_s4'; S3=ROOT/'r11_s3'
MONTHS=('01','02','06','07'); MS_HOUR=3600000; RESERVE_MS=30000
SOURCE_SHAS={'01':'97d98454751f0037581cc706260a60f7bc8085e5ae3b92ca719474b719041dee',
 '02':'ab014ab2ef6512b5870fcdc50f0828c33f8b3a09547d886225ad7915037e27dc',
 '06':'4b46b337d84a2ab16be63c61edea9e98160d9a288b6ae14ddebe79ae484a1194',
 '07':'2352e60f7f8c374d533ae3c91aac6def25adb47696ecb0728065c34d025f1ce5'}

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def load_month(m):
 p=next(ROOT.glob(f'R11S_{m}_FULLMONTH_*.zip'))
 assert sha_file(p)==SOURCE_SHAS[m],('ZIP_SOURCE_DRIFT',m)
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  f=next(n for n in z.namelist() if n.endswith('EXACT_SURVIVAL_LABELS.npz'))
  payload=z.read(f)
  manifest=json.loads(z.read('SURVIVAL_COMPLETE_SOURCE_MANIFEST.json'))
  # source member hash must appear in immutable original complete manifest
  assert sha_bytes(payload) in json.dumps(manifest),('ARCHIVED_MEMBER_SHA_DRIFT',m)
  with np.load(io.BytesIO(payload),allow_pickle=False) as ar:
   tick=ar['source_tick_ordinal'].copy();t=ar['entry_utc_ms'].copy()
   b=ar['h15_BUY_survives_and_favorable'] & ar['h30_BUY_survives_no_adverse'] & ar['h30_coverage']
   s=ar['h15_SELL_survives_and_favorable'] & ar['h30_SELL_survives_no_adverse'] & ar['h30_coverage']
   mb=ar['h30_BUY_safety_margin_raw'];ms=ar['h30_SELL_safety_margin_raw']
 assert len(t)>0 and np.all(t[1:]>=t[:-1]) and np.count_nonzero(b&s)==0
 valid=b|s;rows=np.flatnonzero(valid)
 return dict(m=m,t=t[valid],tick=tick[valid],row=rows,side=np.where(b[valid],1,-1).astype(np.int8),margin=np.where(b[valid],mb[valid],ms[valid]).astype(np.int32),
 original_candidate_count=len(t),good_event_count=len(rows),archive_sha=SOURCE_SHAS[m],original_labels_sha=sha_bytes(payload))

@njit(cache=True)
def greedy_from_start(t,next_idx,start,end):
 out=np.empty(160,np.int64);k=0;j=start
 while j<end:
  if k>=160:raise RuntimeError('max gap scheduling physical bound exceeded')
  out[k]=j;k+=1;j=next_idx[j]
 return out[:k]

@njit(cache=True)
def greedy_all(t,next_idx):
 out=np.empty(len(t),np.int64);k=0;j=0
 while j<len(t):
  out[k]=j;k+=1;j=next_idx[j]
 return out[:k]

@njit(cache=True)
def greedy_day_upper(t,next_idx,begin,end):
 # Full local UTC date, ignore incoming boundary reservation: optimistic capacity.
 out=np.empty(3000,np.int64);k=0;j=begin
 while j<end:
  if k>=3000:raise RuntimeError('day capacity exceeds 3000 physical trades')
  out[k]=j;k+=1;j=next_idx[j]
 return out[:k]

@dataclass(slots=True)
class Node:
 prev:object
 idxs:object
 count:int
 last:int
 total:int
 hours:int
 days:int
 day_count:int
 safety:int
 hour_num:int


def hour_decisions(t, next_idx, begin, end, state, hour_ref, end_ms):
 # find first strictly available candidate, as exact one-position reservation.
 first=np.searchsorted(t, state.last+RESERVE_MS,side='right')
 first=max(begin,first)
 if first>=end:return np.empty(0,np.int64), [0]
 greedy=greedy_from_start(t,next_idx,first,end);K=len(greedy)
 options={0,K,max(0,K-1),max(0,K-2),max(0,K-3),max(0,K-4),min(K,hour_ref),min(K,max(0,hour_ref-1)),min(K,hour_ref+1),min(K,hour_ref+2)}
 # Add boundary-safe prefix explicitly; this can free the next hour without full loss.
 boundary=np.searchsorted(t[greedy],end_ms-RESERVE_MS,side='left')
 options.add(int(boundary))
 if hour_ref>0 and K>=hour_ref:options.add(hour_ref)
 return greedy, sorted(options)


def generate_month(m, beam_width=160):
 tic=time.time();data=load_month(m);t=data['t'];n=len(t)
 next_idx=np.searchsorted(t,t+RESERVE_MS,side='right')
 table=pd.read_csv(S3/'ALL_2880_UTC_HOURLY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv')
 table=table[table.month==f'2026-{m}'].copy().reset_index(drop=True)
 assert len(table) in (672,720,744) and table.utc_hour_start.is_unique
 epoch=pd.to_datetime(table.utc_hour_start,utc=True).astype('int64').to_numpy()//10**6
 hourref=table['R9_SYNTH_reference'].to_numpy(np.int32)
 assert int(hourref.sum()) in (27980,33523,31758,24324)
 hours_count=len(epoch);end_ms=epoch+MS_HOUR
 starts=np.searchsorted(t,epoch,side='left');ends=np.searchsorted(t,end_ms,side='left')
 hour_to_day=np.arange(hours_count)//24
 assert hours_count%24==0
 dayref=np.add.reduceat(hourref,np.arange(0,hours_count,24))
 baseline=greedy_all(t,next_idx)
 assert len(baseline)=={'01':35652,'02':33640,'06':40296,'07':35813}[m],('ORIGINAL_GLOBAL_TEACHER_DRIFT',m,len(baseline))
 # Keep incremental Pareto beam, with end-of-hour occupancy state, hour passes,
 # full day passes, net total and current day progress. All emitted nodes are source-exact.
 beam=[Node(prev=None,idxs=np.empty(0,np.int64),count=0,last=-2**61,total=0,hours=0,days=0,day_count=0,safety=0,hour_num=-1)]
 peak=0
 for h in range(hours_count):
  ref=int(hourref[h]);dayidx=int(hour_to_day[h]);dayend=(h%24==23)
  candidates=[]
  for state in beam:
   greedy,options=hour_decisions(t,next_idx,int(starts[h]),int(ends[h]),state,ref,int(end_ms[h]))
   for k in options:
    ix=greedy[:k]
    last=int(t[ix[-1]]) if k else state.last
    daycount=state.day_count+k
    dhit=int(daycount>=int(dayref[dayidx])) if dayend and int(dayref[dayidx])>0 else 0
    # compress old last timestamp into single no-occupancy state, but keep exact original
    # within prev Node history and derive next eligibility through compressed value.
    compressed=max(last,int(end_ms[h]-RESERVE_MS-1))
    node=Node(prev=state,idxs=ix,count=k,last=compressed,total=state.total+k,
       hours=state.hours+(int(k>=ref) if ref>0 else 0),days=state.days+dhit,
       day_count=(0 if dayend else daycount),safety=state.safety+(int(data['margin'][ix].sum()) if k else 0),hour_num=h)
    candidates.append(node)
  # Diversity preserving: retain best path for near-identical output quote-occupancy
  # AND capped progress-to-day-need. Top pool retains competing count/hour priorities.
  candidates.sort(key=lambda u:(u.hours,u.days,u.total,u.safety),reverse=True)
  states={};selected=[]
  for c in candidates:
   key=(min(max(0,c.last-int(end_ms[h]-RESERVE_MS)),RESERVE_MS)//250,
        min(c.day_count//25,6) if not dayend else 0)
   if states.get(key,0)>=4:continue
   states[key]=states.get(key,0)+1;selected.append(c)
   if len(selected)>=beam_width:break
  beam=selected;peak=max(peak,len(beam))
  if h%24==23:print(f'PROGRESS {m} UTC_DAY {(h+1)//24}/{hours_count//24} STATES={len(beam)} HOURS={beam[0].hours} DAYS={beam[0].days} ENTRIES={beam[0].total}',flush=True)
 # Prefer valid monthly total if possible; then maximize hourly, daily, total and safety.
 floor=int(hourref.sum())
 good=[c for c in beam if c.total>=floor]
 finalpool=good or beam
 best=max(finalpool,key=lambda u:(u.hours,u.days,u.total,u.safety))
 # Reconstruct all 100% future-known positions by selected original quote ordinal.
 path=[];u=best
 while u and u.hour_num>=0:
  path.append((u.hour_num,u.idxs.copy(),u.count))
  u=u.prev
 path.reverse();assert len(path)==hours_count
 chosen=np.concatenate([ix for _,ix,_ in path])
 assert len(chosen)==best.total and len(np.unique(chosen))==len(chosen)
 assert np.all(t[chosen[1:]]>t[chosen[:-1]]+RESERVE_MS)
 ch=pd.to_datetime(t[chosen],unit='ms',utc=True)
 chh=(t[chosen]//MS_HOUR)*MS_HOUR
 hc=pd.Series(chh).value_counts();hour_selected=np.array([int(hc.get(v,0)) for v in epoch],np.int32)
 assert sum(hour_selected)==len(chosen)
 assert np.array_equal(hour_selected,np.array([k for _,_,k in path],np.int32))
 assert sum((hour_selected>=hourref)&(hourref>0))==best.hours
 dsel=np.add.reduceat(hour_selected,np.arange(0,hours_count,24));dpass=(dsel>=dayref)&(dayref>0)
 independent_day_upper=np.array([len(greedy_day_upper(t,next_idx,int(starts[d*24]),int(ends[d*24+23]))) for d in range(len(dayref))],np.int32)
 assert np.all(dsel<=independent_day_upper)
 independent_day_possible=((independent_day_upper>=dayref)&(dayref>0))
 assert int(dpass.sum())==best.days
 basehour=np.bincount(np.searchsorted(epoch,t[baseline]//MS_HOUR*MS_HOUR),minlength=hours_count)
 # Context recorded exactly, even inactive reference days and hours.
 hours=[]
 for h in range(hours_count):
  r=table.iloc[h];hours.append(dict(month=f'2026-{m}',utc_hour=r.utc_hour_start,utc_day=r.utc_day,hour_utc=int(r.hour_utc),
   R9_SYNTH_UTC=int(hourref[h]),R11S4_CONTROL_EARLIEST_GREEDY_MONTH_MAXCOUNT=int(basehour[h]),
   R11S1_FROZEN_GLOBAL_DP_SOURCE_HOURLY_COUNT=int(r.R11_strict_15fav_30surv_original_global_hindsight_selected),
   R11S3_INDEPENDENT_HOUR_INTERIOR_MAX=int(r.R11_strict_30s_hour_interior_constructive_MAX),
   R11S3_INDEPENDENT_HOUR_CROSSING_UPPER=int(r.R11_strict_30s_hour_crossing_optimistic_UPPER),
   R11S4_HOUR_QUOTA_BEAM_ENTRIES=int(hour_selected[h]),R11S4_HOUR_QUOTA_MET=(int(hour_selected[h]>=hourref[h]) if hourref[h]>0 else None),
   hour_mathematically_impossible=int(hourref[h]>r.R11_strict_30s_hour_crossing_optimistic_UPPER),
   absolute_gap_to_quota=int(hour_selected[h]-hourref[h]) if hourref[h]>0 else None,
   R11S4_HINDSIGHT_ENTRY_GOOD15_SURVIVE30=int(hour_selected[h]),
   R11S4_HINDSIGHT_STRICT_PRECISION=1.0 if hour_selected[h]>0 else None,
   contract='FUTURE_PRIVILEGED_EXACT_30SEC_RESERVATION_NOT_A_PREDICTIVE_MODEL'))
 days=[]
 for d in range(len(dayref)):
  a=d*24;days.append(dict(month=f'2026-{m}',utc_day=table.utc_day.iloc[a],R9_SYNTH_UTC=int(dayref[d]),
  source_hour_coverage=24,R11S4_HINDSIGHT_ENTRIES=int(dsel[d]),R11S4_STRICT_GOOD15_SURVIVE30=int(dsel[d]),
  R11S4_R9_DAY_QUOTA_PASS=(int(dsel[d]>=dayref[d]) if dayref[d]>0 else None),
  source_day_active=int(dayref[d]>0),R11S4_INDEPENDENT_DAY_OPTIMISTIC_UPPER=int(independent_day_upper[d]),
  R11S4_DAY_PROVEN_IMPOSSIBLE=int(dayref[d]>independent_day_upper[d]),number_active_hour_quotas_passed=int(sum((hour_selected[a:a+24]>=hourref[a:a+24])&(hourref[a:a+24]>0))),
  number_active_hour_quotas_impossible=int(sum(hourref[a:a+24]>table.R11_strict_30s_hour_crossing_optimistic_UPPER.to_numpy()[a:a+24]))))
 out=HERE/f'month_{m}';out.mkdir(parents=True,exist_ok=True)
 pd.DataFrame(hours).to_csv(out/f'R11S4_{m}_ALL_UTC_HOURS.csv',index=False)
 pd.DataFrame(days).to_csv(out/f'R11S4_{m}_ALL_UTC_DAYS.csv',index=False)
 # Exact selected ordinal array and CSV trace, not flattened statistics.
 np.savez_compressed(out/f'R11S4_{m}_FULL_SELECTED_SOURCE_TRACE.npz',source_candidate_row=data['row'][chosen],source_tick_ordinal=data['tick'][chosen],
   entry_utc_ms=t[chosen],side=data['side'][chosen],entry_side_margin_raw=data['margin'][chosen],full15_favorable_and_full30_survival=np.ones(len(chosen),bool),reservation_ms=np.full(len(chosen),RESERVE_MS,np.int32))
 with open(out/f'R11S4_{m}_FULL_SELECTED_SOURCE_TRACE.csv','w',newline='') as f:
  writer=csv.writer(f);writer.writerow(('month','source_candidate_row','source_tick_ordinal','entry_utc_ms','entry_UTC_hour','side','safety_margin_raw','strict15fav30surv'))
  for i in chosen:writer.writerow((m,int(data['row'][i]),int(data['tick'][i]),int(t[i]),dt.datetime.fromtimestamp(t[i]//1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:00:00Z'),int(data['side'][i]),int(data['margin'][i]),1))
 result={'month':f'2026-{m}','source_archived_zip_sha256':data['archive_sha'],'source_full_labels_sha256':data['original_labels_sha'],
  'all_original_v5_gap_candidates':data['original_candidate_count'],'strict_good15_and_survive30_candidate_timestamps':data['good_event_count'],
  'both_sides_good_per_timestamp':0,'original_maxcount_hindsight_positions':len(baseline),
  'new_hour_target_beam_positions':len(chosen),'R9_SYNTH_clock_corrected_month_total':floor,
  'monthly_full_R9_SYNTH_quota_met':bool(len(chosen)>=floor),'month_difference_to_exact_R9_SYNTH':len(chosen)-floor,
  'R9_SYNTH_active_hours':int((hourref>0).sum()),'hourly_quota_passed':int(best.hours),
  'hourly_quota_failed':int((hourref>0).sum()-best.hours),'R11S3_hours_mathematically_impossible':int(sum(hourref>table.R11_strict_30s_hour_crossing_optimistic_UPPER.to_numpy())),
  'R11S3_genuine_frozen_month_global_DP_hour_quota_passed':int(sum((table.R11_strict_15fav_30surv_original_global_hindsight_selected.to_numpy()>=hourref)&(hourref>0))),
  'R11S4_earliest_greedy_original_maxcount_hour_quota_passed':int(sum((basehour>=hourref)&(hourref>0))),
  'hourly_quota_optimistic_upper_possible':int(sum((hourref<=table.R11_strict_30s_hour_crossing_optimistic_UPPER.to_numpy())&(hourref>0))),
  'R9_SYNTH_active_days':int((dayref>0).sum()),'daily_volume_quota_passed':int(dpass.sum()),'daily_volume_quota_failed':int((dayref>0).sum()-dpass.sum()),
  'daily_quota_optimistic_upper_possible':int(independent_day_possible.sum()),
  'daily_quota_proven_impossible':int(((dayref>0)&(~independent_day_possible)).sum()),
  'strict_selected_correct15_and_survive30':int(len(chosen)),'strict_selected_class_precision':1.0 if len(chosen) else None,
  'optimizer':'DETERMINISTIC_FUTURE_PRIVILEGED_250MS_QUOTE_SIDE_HOUR_PRIORITY_BEAM_SEARCH_NOT_EXACT_MULTIQUOTA_OPTIMAL',
  'beam_width':beam_width,'max_beam_states':peak,'primary_objective':'maximize number of source R9 SYNTH-active UTC hours meeting exact hourly count',
  'secondary_objective':'maximize active UTC days meeting exact daily count','third_objective':'maximize total 30s source-exact future-eligible selected positions',
  'exception':'if no beam state reaches exact monthly R9 SYNTH quota, choose highest hour/day coverage state, disclose failure',
  'reservation_ms':30000,'favorable_deadline_ms':15000,'adverse_threshold_raw':-100,'quote_gap_ms':15000,
  'economic_profit_not_objective':True,'holding_exit_mechanisms_unchanged':True,'runtime_prediction_accuracy_claim':False,
  'limitations':['future-known teacher is intentionally in sample, not a fitted as-of agent','beam search is a heuristic; independent hourly upper bound comes from frozen R11S3, not a proof of global simultaneous attainability','strict 30sec single-position reservation is imposed across UTC hour/day boundaries','monthly clock-aligned SYNTH dates not broker MT5 live account certification','original 36 trained same-month student outcomes unchanged and all failed joint hourly 80percent plus volume'],
  'elapsed_seconds':round(time.time()-tic,3)}
 files=sorted(p for p in out.iterdir() if p.is_file())
 result['artifacts']={p.name:{'sha256':sha_file(p),'bytes':p.stat().st_size} for p in files}
 (out/f'R11S4_{m}_EXACT_COMPLETE_RESULT.json').write_text(json.dumps(result,indent=2))
 print('DONE',json.dumps({k:result[k] for k in ['month','new_hour_target_beam_positions','hourly_quota_passed','hourly_quota_optimistic_upper_possible','R11S3_genuine_frozen_month_global_DP_hour_quota_passed','daily_volume_quota_passed','monthly_full_R9_SYNTH_quota_met','elapsed_seconds']}),flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--month',choices=MONTHS,required=True);p.add_argument('--beam',type=int,default=160);arg=p.parse_args()
 generate_month(arg.month,arg.beam)
