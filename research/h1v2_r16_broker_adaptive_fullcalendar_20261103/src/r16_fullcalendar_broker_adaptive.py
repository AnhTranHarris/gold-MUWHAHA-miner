"""R16 additive source-exact broker-adaptive H1V2 hindsight capacity research.

All candidate admission is strictly past/now observed Bid+Ask. All GOOD and
first-TP exit labels are future privileged (offline only). Strict S1 target:
+0.10 executable nominal net in <=15s, adverse opening liquidation price
excursion NEVER reaches -0.10 through full 30s; reject quote-gap censorship.

Source feeds cannot substitute for one another: this runner is Dukascopy only.
Widened <=$4 price spread is UNAPPROVED experimental changed admission and
must NEVER replace original <=$1.50, original R9 EA, or trained policy.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,sys,time,zipfile
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from numba import njit

ROOT=Path('/mnt/data')
LAB=ROOT/'h1v2_r16_broker_adaptive'
R13=ROOT/'h1v2_r13_broker_adaptive/src'
R12=ROOT/'h1v2_r12/source'
sys.path[:0]=[str(R13),str(R12)]
import r13_crossbroker_horizon_lanes as ancestor
import r12_tp_oracle as tp
RAW_PINS=tp.RAW_SHA
UPSTREAM_R13_SHA256='e90da8141639428d173d7587d44f251748130e690c1f5f754594727ba691ed7e'
UPSTREAM_R12_SHA256='83d5622167ae517a12ecca6b7388e46b65d549a44be271c6f4d410e7e4bff1be'
S1_HELPER_PIN=ancestor.PINNED_HELPER
REF_QUARTERS=ROOT/'R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv'
REF_HOURS=ROOT/'R12DQ_COMPLETE_ALL_2880_SOURCE_HOURS_S4_R12_R12DQ.csv'
W=60000; STEP_QUARTER=900000;STEP_HOUR=3600000
LANES=('BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000','BROKER_CONTRACTION',
       'DIRECTIONAL_MICROPATH','WATCH60_COOL_1500','WATCH60_COOL_2500',
       'BUDGETED_MULTI_REGIME','FULL_WIDE_DENSE_DIAGNOSTIC')

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

@njit(cache=False)
def watch_prefix(t,b,a,ix,flags,short_ema,long_ema):
 """Two as-of watches, only actual observed confirmations, no backdating.

 Watch 0: wide $2-$4, later spread <=1.50 and <=70% seed.
 Watch 1: wide $2.8-$4, later <=2.50 and <=80% seed with
              as-of EMA15 <= EMA300.
 All candidate ordinals at unique milliseconds, as observed. Reset after
 quote drought >15s. Position management is SEPARATE from watch state.
 """
 n=len(ix); w0=np.zeros(n,np.bool_);w1=np.zeros(n,np.bool_)
 starts=np.zeros(2,np.int64);ok=np.zeros(2,np.int64)
 expired=np.zeros(2,np.int64);reset=np.zeros(2,np.int64)
 born=np.zeros(2,np.int64);spread0=np.zeros(2,np.int32)
 active=np.zeros(2,np.bool_)
 # Detect quote drought even when all quotations around the gap were
 # excluded from the candidate universe by spread/epoch admission.
 gap_pref=np.zeros(len(t),np.int32)
 for j in range(1,len(t)):
  gap_pref[j]=gap_pref[j-1]+(1 if t[j]-t[j-1]>15000 else 0)
 prev_raw_ix=-1
 for k in range(n):
  i=ix[k];ti=t[i];s=a[i]-b[i]
  if prev_raw_ix>=0 and gap_pref[i]>gap_pref[prev_raw_ix]:
   for w in range(2):
    if active[w]:active[w]=False;reset[w]+=1
  for w in range(2):
   if active[w] and ti-born[w]>W:
    active[w]=False;expired[w]+=1
   if active[w] and 250<=ti-born[w]<=W:
    passed=(s<=1500 and s*10<=spread0[w]*7) if w==0 else (
       s<=2500 and s*10<=spread0[w]*8 and short_ema[i]<=long_ema[i])
    if passed:
     if w==0:w0[k]=True
     else:w1[k]=True
     active[w]=False;ok[w]+=1
   # New watch only begins after a new actually observed first250 quote.
   if not active[w] and (int(flags[k])&1)!=0:
    trigger=(2000<=s<=4000) if w==0 else (2800<=s<=4000)
    if trigger:active[w]=True;born[w]=ti;spread0[w]=s;starts[w]+=1
  prev_raw_ix=i
 return w0,w1,starts,ok,expired,reset

@njit(cache=False)
def interval_greedy(starts,ends):
 """Input pre-sorted by finish (and then entry), strict position nonoverlap."""
 take=np.empty(len(starts),np.int64);last=np.int64(-9223372036854775807);n=0
 for j in range(len(starts)):
  if starts[j]>last:take[n]=j;n+=1;last=ends[j]
 return take[:n]

def schedule(starts,ends):
 if len(starts)==0:return np.empty(0,np.int64)
 if not np.all(ends>starts):raise AssertionError('ZERO_LENGTH_INTERVAL')
 order=np.lexsort((np.arange(len(starts)),starts,ends))
 selected=interval_greedy(starts[order],ends[order])
 return order[selected]

def quarter_counts(source_starts,source_ends,all_qkeys,compute_isolated=True):
 # Selected events are globally scheduled; original quarter source count is
 # never invented by dividing source hourly targets by four.
 qidx=np.searchsorted(all_qkeys,source_starts//STEP_QUARTER)
 counts=np.bincount(qidx,minlength=len(all_qkeys))[:len(all_qkeys)]
 return counts

def read_refs(mon):
 with REF_QUARTERS.open(newline='',encoding='utf8') as f:
  rows=[r for r in csv.DictReader(f) if r['month']=='2026-'+mon]
 with REF_HOURS.open(newline='',encoding='utf8') as f:
  hr=[r for r in csv.DictReader(f) if r['month']=='2026-'+mon]
 n={'01':2976,'02':2688,'06':2880,'07':2976}[mon]
 if len(rows)!=n or len(hr)!=n//4:raise RuntimeError('INCOMPLETE_ORIGINAL_QUOTA_CALENDAR')
 start=np.asarray([int(datetime.strptime(x['utc_quarter'],'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=timezone.utc).timestamp()*1000)//STEP_QUARTER for x in rows],dtype=np.int64)
 if not np.array_equal(np.diff(start),np.ones(len(start)-1,dtype=np.int64)):
  raise RuntimeError('NONCONTIGUOUS_ORIGINAL_QUARTER')
 ref=np.asarray([int(r['original_R9_SYNTH_15min_reference']) for r in rows],np.int32)
 if int(ref.sum())!={'01':27980,'02':33523,'06':31758,'07':24324}[mon]:raise RuntimeError('ORIGINAL_15M_QUOTA_HASH_DOMAIN_INCONSISTENCY')
 original_hour=np.asarray([int(x['orig_R9']) for x in hr],np.int32)
 if not np.array_equal(ref.reshape(-1,4).sum(axis=1),original_hour):raise RuntimeError('QUARTER_HOURLY_PARITY')
 return rows,hr,start,ref,original_hour

def csv_rows(path,rows):
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run_month(mon,verify_baseline=True):
 tic=time.monotonic();OUT=LAB/'results';OUT.mkdir(exist_ok=True,parents=True)
 if sha(R13/'r13_crossbroker_horizon_lanes.py')!=UPSTREAM_R13_SHA256 or sha(R12/'r12_tp_oracle.py')!=UPSTREAM_R12_SHA256:
  raise RuntimeError('PARENT_MODULE_SHA_DRIFT')
 raw_path=ROOT/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 pin=RAW_PINS[mon]
 if sha(raw_path)!=pin:raise RuntimeError('IMMUTABLE_RAW_SHA_DRIFT '+mon)
 t,b,a=tp.read_raw(mon)
 refs,hours,qkeys,qrefs,href=read_refs(mon)
 ix,flags,e300,e15,mb3,ma3=ancestor.prefix_candidates(t,b,a)
 if len(ix)==0:raise RuntimeError('ZERO_ASOF_CANDIDATES')
 lanes=ancestor.lane_membership(ix,flags,b,a,e300,e15,mb3,ma3)
 watch0,watch1,started,confirmed,expired,reset=watch_prefix(t,b,a,ix,flags,e15,e300)
 s=a[ix].astype(np.int64)-b[ix].astype(np.int64)
 coher=np.sign(mb3[ix])==np.sign(ma3[ix])
 motion=np.minimum(np.abs(mb3[ix]),np.abs(ma3[ix])).astype(np.int64)
 lanes.update({
  'WATCH60_COOL_1500':watch0,
  'WATCH60_COOL_2500':watch1,
  'BUDGETED_MULTI_REGIME':lanes['DENSE_1500']|(
     (s>1500)&(s<=4000)&(e15[ix]<=e300[ix])&coher&(motion>=s+120)),
  'FULL_WIDE_DENSE_DIAGNOSTIC':s<=4000,
 })
 if tuple(lanes)!=LANES:raise RuntimeError('LANE_ORDER_MUTATED')
 mn15,mx15,na15,xa15,_,_,cov15=ancestor.frozen_extrema(t,b,a,ix,15000)
 mn30,mx30,na30,xa30,_,_,cov30=ancestor.frozen_extrema(t,b,a,ix,30000)
 gB=(mx15.astype(np.int64)>=a[ix].astype(np.int64)+120)&(mn30.astype(np.int64)>b[ix].astype(np.int64)-100)&cov15&cov30
 gS=(na15.astype(np.int64)<=b[ix].astype(np.int64)-120)&(xa30.astype(np.int64)<a[ix].astype(np.int64)+100)&cov15&cov30
 if np.any(gB&gS):raise RuntimeError('FUTURE_GOOD_BOTH_SIDES_CONTRACT_IMPOSSIBLE')
 good=gB|gS
 # Source previous frozen R11S1 original strict-good at ORIGINAL first250.
 original=tp.load_labels(mon)
 orig_ix=ix[lanes['BASE_250_1500']&good]
 if verify_baseline:
  if not np.array_equal(orig_ix,original['ix']):raise RuntimeError('IMMUTABLE_S1_GOOD_ORDINAL_PARITY_MISMATCH')
  if not np.array_equal(np.where(gB[lanes['BASE_250_1500']&good],1,-1).astype(np.int8),original['side']):
   raise RuntimeError('ORIGINAL_S1_SIDE_PARITY_MISMATCH')
 goodix=ix[good]; gtime=t[goodix];gside=np.where(gB[good],1,-1).astype(np.int8)
 # EXACT first-TP quote exit for the newly permitted widened-spread candidates.
 ex,et=tp.quote_tp_first(t,b,a,goodix,a[goodix],b[goodix],gside)
 if np.any(ex<0) or np.any(et<=gtime) or np.any(et>gtime+15000):raise RuntimeError('SOURCE_TP_EXACT')
 result_net=np.where(gside==1,b[ex]-a[goodix],b[goodix]-a[ex]).astype(np.int64)-20
 if np.any(result_net<100):raise RuntimeError('EXIT_PRICE_GEOMETRY')
 # ALL strict future good source quote ordinals, not only post-selected traces;
 # this is source audit, not an as-of model output.
 gp={k:v[good] for k,v in lanes.items()}
 npz=OUT/f'R16_{mon}_ALL_SOURCE_ORIGINAL_AND_EXPANDED_QUOTE_GOOD_FIRSTTP.npz'
 np.savez_compressed(npz,source_ordinal=goodix,entry_utc_ms=gtime,
  entry_bid_raw=b[goodix],entry_ask_raw=a[goodix],side_buy1_sellminus1=gside,
  first_tp_exit_raw_ordinal=ex,first_tp_exit_utc_ms=et,nominal_net_raw=result_net,
  past_spread_ema15=e15[goodix],past_spread_ema300=e300[goodix],
  past_bid3s_move_raw=mb3[goodix],past_ask3s_move_raw=ma3[goodix],
  **{'lane_'+name:val for name,val in gp.items()})
 per_quarter=[];per_hour=[];one_q=len(qkeys);refactive=int(np.count_nonzero(qrefs))
 outcomes={}; chosen_orig={}
 for name in LANES:
  chosen=np.flatnonzero(gp[name]);sel=schedule(gtime[chosen],et[chosen]);ids=chosen[sel]
  if len(ids)>1 and np.any(gtime[ids[1:]]<=et[ids[:-1]]):raise RuntimeError('ONE_POSITION_CONFLICT')
  counts=np.bincount((gtime[ids]//STEP_QUARTER-qkeys[0]).astype(np.int64),minlength=one_q)
  good_counts=np.bincount((gtime[chosen]//STEP_QUARTER-qkeys[0]).astype(np.int64),minlength=one_q)
  if np.any(gtime[ids]//STEP_QUARTER<qkeys[0]) or np.any(gtime[ids]//STEP_QUARTER>qkeys[-1]):
   raise RuntimeError('BEYOND_ORIGINAL_QUARTER_CALENDAR')
  # Independent quarter optimistic upper: schedule quote intervals starting in
  # each quarter independently. Crucially NEVER treat global total as proof.
  boundaries=np.searchsorted(gtime[chosen]//STEP_QUARTER,qkeys)
  limits=np.r_[boundaries[1:],len(chosen)]
  upper=np.zeros(one_q,np.int32)
  for q,(j0,j1) in enumerate(zip(boundaries,limits)):
   if j1>j0:
    loc=chosen[j0:j1];upper[q]=len(schedule(gtime[loc],et[loc]))
  if np.any(counts>upper):raise RuntimeError('GLOBAL_SELECTION_EXCEEDS_ISOLATED_UPPER')
  failed=(qrefs>0)&(upper<qrefs);meets=(qrefs>0)&(counts>=qrefs)
  result={'month':'2026-'+mon,'lane':name,'candidate_admitted_before_future_label':int(lanes[name].sum()),
          'future_good_candidates':int(len(chosen)),'selected_one_position_firsttp':int(len(ids)),
          'R9_active_15m_quarters':refactive,'15m_quotas_met':int(meets.sum()),
          '15m_source_isolated_impossible':int(failed.sum()),
          '15m_attainable_but_unmet_under_global_maxcount':int(((qrefs>0)&~meets&~failed).sum()),
          'active_hour_quotas_met':int(np.sum((href>0)&(counts.reshape(-1,4).sum(axis=1)>=href))),
          'active_hour_original_R9_quotas':int(np.count_nonzero(href)),
          'source_is_DUKASCOPY_ONLY':True,'future_known_side_and_outcome':True,
          'widened_spread_unapproved':bool(name not in ('BASE_250_1500','DENSE_1500','WATCH60_COOL_1500'))}
  outcomes[name]=result
  # Every record, including zero-active quotas, retains all fields.
  for q,row in enumerate(refs):
   per_quarter.append({'month':'2026-'+mon,'utc_quarter':row['utc_quarter'],'utc_hour':row['utc_hour'],
     'lane':name,'original_R9_SYNTH_15min_reference':int(qrefs[q]),'source_asof_future_good_candidate_count':int(good_counts[q]),
     'future_selected_one_position_firsttp':int(counts[q]),'isolated_quarter_upper':int(upper[q]),
     'quota_met':int(meets[q]) if qrefs[q] else '',
     'source_contract_infeasible':int(failed[q]) if qrefs[q] else '',
     'future_privileged_hindsight_NOT_REAL_TRADING':True})
  for h,row in enumerate(hours):
   selcnt=int(sum(counts[h*4:h*4+4]));refh=int(href[h]);
   per_hour.append({'month':'2026-'+mon,'utc_hour':row['utc_hour'],'lane':name,
    'original_R9_SYNTH_hourly_reference':refh,'future_selected_count':selcnt,
    'four_quarters_reaching_quota':int(sum(meets[h*4:h*4+4])),
    'hour_reference_reached':int(selcnt>=refh) if refh else '',
    'future_privileged_hindsight_NOT_REAL_TRADING':True})
  # Lossless full selected quote-ordinal row material for independent source check.
  chosen_orig[name]=ids
 traces=OUT/f'R16_{mon}_ALL_LANE_SELECTED_ENTRY_EXIT_ORDINALS.npz'
 np.savez_compressed(traces,**{f'{name}_good_ordinal_index':ids for name,ids in chosen_orig.items()})
 outq=OUT/f'R16_{mon}_ALL_15MIN_LANE_CALENDAR.csv';outh=OUT/f'R16_{mon}_ALL_HOURLY_LANE_CALENDAR.csv';
 csv_rows(outq,per_quarter);csv_rows(outh,per_hour)
 manifest={'month':mon,'verified_original_raw_SHA256':pin,'quote_rows':len(t),
  'upstream_R11S1_source_SHA256':S1_HELPER_PIN,'original_R11S1_eligible_good_events':len(original['ix']),
  'R13_prefix_source_relpath':'research/h1v2_r13_broker_adaptive_20261103/src/r13_crossbroker_horizon_lanes.py',
  'R9_source_quarter_reference_file_sha256':sha(REF_QUARTERS),
  'R9_source_hour_reference_file_sha256':sha(REF_HOURS),
  'source_strict_15fav30noadverse_all_brokers_target_only':'source_favorable_true_bidask_net+0.10 and full30 no-adverse; source fixed $0.02 fee',
  'watch_60_only_PRE_ENTRY_observed':'True; new trades never backdated to watch initiation',
  'FUTURE_INFORMATION_IS_ORACLE_ONLY':True,'ON_POLICY_MODEL_OR_LIVE_CERTIFICATION':False,
  'future_good_candidate_count_all_max4':int(good.sum()),
  'asof_candidate_total_max4':len(ix),'watch_started':started.tolist(),
  'watch_confirmed':confirmed.tolist(),'watch_expired':expired.tolist(),'watch_quote_gap_reset':reset.tolist(),
  'fully_evaluated_variants':outcomes,
  'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (npz,traces,outq,outh)},
  'seconds':round(time.monotonic()-tic,3)}
 output=OUT/f'R16_{mon}_EXACT_COMPLETE_EXECUTION.json'
 output.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n',encoding='utf8')
 return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=['01','02','06','07']);p.add_argument('--skip-original-parity',action='store_true')
 args=p.parse_args()
 print(json.dumps(run_month(args.month,not args.skip_original_parity),indent=2,allow_nan=False),flush=True)
