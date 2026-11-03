"""R16 full-calendar observed-quote delayed-fill stress: no runtime predictor.

Each signal was selected BY hindsight under current quotes; do not reinterpret
stress accuracy as an as-of trading strategy. Replays frozen selected entry
ordinals, never replaces failed entries by later hindsight-selected winners.
Positions suppressed while occupied, no synthetic midprice fills. A completed
non-GOOD trade occupies full 30s; failed-trade realized R9 P&L is NOT scored.
"""
from __future__ import annotations
import argparse,csv,json,sys,time
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data/h1v2_r16_broker_adaptive/src')
import r16_fullcalendar_broker_adaptive as r16
ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r16_broker_adaptive/results'
STRESSED=('BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000','BUDGETED_MULTI_REGIME','FULL_WIDE_DENSE_DIAGNOSTIC','WATCH60_COOL_1500','WATCH60_COOL_2500')
SCENARIOS=((0,0),(100,0),(100,20),(500,0),(500,20))

@njit(cache=False)
def freeze_delayed_oneposition(t,b,a,sig,side,lag,slip,cap):
 n=len(sig)
 outcome=np.full(n,-9,np.int8);fills=np.full(n,-1,np.int64);exits=np.full(n,-1,np.int64)
 netgood=np.full(n,-2147483647,np.int32);last_busy=np.int64(-9223372036854775807)
 for k in range(n):
  i=sig[k];now=t[i];si=side[k]
  if now<=last_busy:outcome[k]=-2;continue
  target=now+lag
  f=i
  if lag>0:
   left=i+1;right=len(t)
   while left<right:
    mid=(left+right)//2
    if t[mid]<target:left=mid+1
    else:right=mid
   f=left
  if f>=len(t) or t[f]-target>1000:outcome[k]=-1;continue
  sp=a[f]-b[f]
  if sp<0 or sp>cap:outcome[k]=-1;continue
  fills[k]=f
  first=-1;last_inside=t[f];prev=t[f];inside=0;stale=False
  lo=9223372036854775807;hi=-9223372036854775807
  paid=(a[f]+slip) if si==1 else (b[f]-slip)
  liq0=b[f] if si==1 else a[f]
  horizon15=t[f]+15000;horizon30=t[f]+30000
  j=f+1
  while j<len(t) and t[j]<=horizon30:
   if t[j]==t[f]:j+=1;continue
   if t[j]-prev>15000:stale=True
   prev=t[j];last_inside=t[j];inside+=1
   liq=b[j] if si==1 else a[j]
   if liq<lo:lo=liq
   if liq>hi:hi=liq
   if first<0 and t[j]<=horizon15:
    liquidation=(b[j]-slip) if si==1 else (a[j]+slip)
    net=(liquidation-paid)*si-20
    if net>=100:first=j;netgood[k]=net
   j+=1
  # Require at least one post-horizon quote with no >15s unobserved
  # quote drought straddling the horizon. This is not an actual broker fill.
  endcoverage=(j<len(t) and t[j]-last_inside<=15000 and t[-1]>=horizon30)
  if inside==0 or stale or not endcoverage or horizon30<t[f]:
   outcome[k]=-3;last_busy=horizon30;continue
  safe=(lo>liq0-100) if si==1 else (hi<liq0+100)
  if first>=0 and safe:
   outcome[k]=1;exits[k]=first;last_busy=t[first]
  else:
   outcome[k]=0;last_busy=horizon30
 return outcome,fills,exits,netgood

def run_month(mon):
 t0=time.monotonic();t,b,a=r16.tp.read_raw(mon)
 qs,hrs,qkeys,qref,href=r16.read_refs(mon)
 good_path=OUT/f'R16_{mon}_ALL_SOURCE_ORIGINAL_AND_EXPANDED_QUOTE_GOOD_FIRSTTP.npz'
 selected_path=OUT/f'R16_{mon}_ALL_LANE_SELECTED_ENTRY_EXIT_ORDINALS.npz'
 with np.load(good_path,allow_pickle=False) as g:
  orig_ix=g['source_ordinal'].copy();origside=g['side_buy1_sellminus1'].copy()
  ori_t=g['entry_utc_ms'].copy()
 with np.load(selected_path,allow_pickle=False) as x:
  lanes={name:x[f'{name}_good_ordinal_index'].copy() for name in STRESSED}
 outcomes=[];quarters=[];allpins={}
 for lane,idx in lanes.items():
  si=orig_ix[idx];sides=origside[idx]
  if len(si)>1 and not np.all(np.diff(t[si])>0):raise RuntimeError('SIGNAL_SELECTION_NOT_CHRONOLOGICAL')
  # Extended spread acceptance must not be conflated with original runtime.
  cap=1500 if lane in ('BASE_250_1500','DENSE_1500','WATCH60_COOL_1500') else 4000
  for lag,slip in SCENARIOS:
   status,fills,exits,net=freeze_delayed_oneposition(t,b,a,si,sides,lag,slip,cap)
   n1=int((status==1).sum());n0=int((status==0).sum());rej=int((status==-1).sum());busy=int((status==-2).sum());cen=int((status==-3).sum())
   if n1+n0+rej+busy+cen!=len(si):raise RuntimeError('UNRECONCILED_FROZEN_SIGNAL_OUTCOMES')
   if (lag,slip)==(0,0) and (n1!=len(si) or np.any(fills!=si)):
    raise RuntimeError('ORIGINAL_GOOD_QUOTE_ORDINAL_STRESS_BASELINE_MISMATCH '+mon+' '+lane)
   good_q=np.zeros(len(qkeys),np.int32);bad_q=np.zeros(len(qkeys),np.int32)
   cens_q=np.zeros(len(qkeys),np.int32);reject_signal_q=np.zeros(len(qkeys),np.int32);busy_signal_q=np.zeros(len(qkeys),np.int32)
   for stat,v in ((1,good_q),(0,bad_q),(-3,cens_q)):
    hits=np.flatnonzero(status==stat)
    if len(hits):
     bucket=(t[fills[hits]]//900000-qkeys[0]).astype(np.int64)
     if np.any(bucket<0) or np.any(bucket>=len(qkeys)):raise RuntimeError('FILLED_OUT_OF_SOURCE_MONTH')
     v[:]=np.bincount(bucket,minlength=len(qkeys))
   for stat,v in ((-1,reject_signal_q),(-2,busy_signal_q)):
    hits=np.flatnonzero(status==stat)
    if len(hits):
     bucket=(t[si[hits]]//900000-qkeys[0]).astype(np.int64)
     v[:]=np.bincount(bucket,minlength=len(qkeys))
   if (sum(map(np.sum,(good_q,bad_q,cens_q,reject_signal_q,busy_signal_q))))!=len(si):
    raise RuntimeError('QUARTER_LATENCY_ATTRIBUTION_MISMATCH')
   qmet=0;hmet=0
   for q,row in enumerate(qs):
    cnt=int(good_q[q]+bad_q[q]);trueacc=good_q[q]/cnt if cnt else None
    target=int(qref[q]);meet=int(cnt>=target and trueacc is not None and trueacc>=.8) if target else ''
    if meet!='':qmet+=int(meet)
    quarters.append({'month':'2026-'+mon,'lane':lane,'latency_ms':lag,'slippage_per_leg_raw':slip,
      'original_UTC_quarter':row['utc_quarter'],'R9_SYNTH_original_quarter_reference':target,
      'actual_fill_UTC_quarter_STRICT_GOOD':int(good_q[q]),'actual_fill_UTC_quarter_COMPLETED_FAILED':int(bad_q[q]),
      'actual_fill_UTC_quarter_CENSORED':int(cens_q[q]),'source_signal_quarter_REJECT':int(reject_signal_q[q]),
      'source_signal_quarter_OCCUPIED_SKIP':int(busy_signal_q[q]),
      'completed_accuracy':trueacc,'joint_quarter_volume_and_80pct':meet,
      'quota_honest_all_filled_positions':int(cnt+cens_q[q]>=target) if target else '',
      'outcome_future_privileged_selected_original_only':True})
   for h in range(len(href)):
    true=int(good_q[h*4:h*4+4].sum());false=int(bad_q[h*4:h*4+4].sum())
    if int(href[h]) and true+false>=int(href[h]) and true+false and true/(true+false)>=.8:hmet+=1
   outcome_path=OUT/f'R16_{mon}_{lane}_lag{lag}_slip{slip}_FULL_FROZEN_TICK_OUTCOME.npz'
   np.savez_compressed(outcome_path,source_signal_tick_ordinal=si,source_signal_side=sides,
     original_signal_utc_ms=t[si],actual_fill_tick_ordinal=fills,first_good_exit_tick_ordinal=exits,
     outcome_code_good1_bad0_rejectminus1_busym2_censm3=status,good_net_raw_price_unit_0p001=net)
   allpins[outcome_path.name]={'bytes':outcome_path.stat().st_size,'sha256':r16.sha(outcome_path)}
   denom=n1+n0
   outcomes.append({'month':'2026-'+mon,'lane':lane,'lag_ms':lag,'per_leg_slippage_raw':slip,
    'signal_count_offline_future_selected':len(si),'GOOD':n1,'completed_BAD':n0,
    'source_CENSORED':cen,'quote_or_spread_REJECT':rej,'single_position_busy_SKIP':busy,
    'completed_accuracy':None if not denom else n1/denom,
    'conservative_completed_plus_censored_accuracy':None if not denom+cen else n1/(denom+cen),
    'quarter_joint_volume_and_80pct':qmet,'hour_joint_volume_and_80pct':hmet,
    'original_active_15m_quarters':int((qref>0).sum()),'original_active_hours':int((href>0).sum()),
    'unmodeled_failed_position_realized_cash_pnl':True,
    'FUTURE_SELECTED_NOT_CAUSAL':True,'BROKER_REAL_FILLS_NOT_VERIFIED':True})
  print(mon,lane,'latency scen',len(SCENARIOS),flush=True)
 outcsv=OUT/f'R16_{mon}_ALL_35_DELAY_FRICTION_SCENARIOS.csv'
 qcsv=OUT/f'R16_{mon}_ALL_15MIN_DELAYS_STRESS_CALENDAR.csv'
 r16.csv_rows(outcsv,outcomes);r16.csv_rows(qcsv,quarters)
 result={'month':mon,'status':'COMPLETE_FUTURE_SELECTED_FROZEN_SIGNAL_LATENCY_STRESS_NONDEPLOYABLE',
   'original_raw_source_SHA':r16.RAW_PINS[mon],'scenarios':len(outcomes),'quarters':len(quarters),
   'model_hindsight_selection':True,'R9_30SEC_FAILED_EXIT_ACCOUNT_PNL_NOT_COMPUTED':True,
   'source_files':{p.name:{'bytes':p.stat().st_size,'sha256':r16.sha(p)} for p in (outcsv,qcsv)},
   'all_full_35_signal_outcome_npz_hashes':allpins,'results_all_35_scenarios':outcomes,
   'seconds':round(time.monotonic()-t0,3)}
 p=OUT/f'R16_{mon}_FULL_DELAY_EXECUTION_RECEIPT.json';p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--month',choices=['01','02','06','07'],required=True);m=p.parse_args().month
 r=run_month(m);print(json.dumps({'month':m,'scenarios':r['scenarios'],'quarters':r['quarters'],'elapsed':r['seconds']}),flush=True)
