"""R13 source-specific delayed execution counterfactual for new broker lanes.

A FUTURE-SELECTED source-native signal is frozen before delaying the entry;
never reselect optimal entry after delay. Actual fill modeled as NEXT observed
source quote at/after latency, never fabricated midpoint. The admissible
spread cap is source-lane-specific and makes WIDE_4USD a diagnostic changed
policy, *not* original <=1.50 runtime. Slippage applied to BOTH legs, nominal
$0.02 quoted-price fee. First favorable >=+$0.10 net by 15s; full30 zero
-$0.10 opening-liquidation adverse. Failure/censor occupies full30, success
releases position at observed first target. Requires one position at a time.
No claim of true fill, profitable P&L or prospective predictive accuracy.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,str(Path(__file__).parent))
import r13_crossbroker_horizon_lanes as r13

@njit(cache=True)
def stressed_frozen_signal(t,b,a,signals,side,lag_ms,slip_raw,maxspread_raw,max_age_ms=1000):
 n=len(t);m=len(signals)
 outcome=np.full(m,-9,np.int8);fill_ix=np.full(m,-1,np.int64)
 exit_ix=np.full(m,-1,np.int64); realized_good_net=np.full(m,-2147483647,np.int32)
 busyuntil=-2**62
 for k in range(m):
  i=signals[k];now=t[i];s=side[k]
  if now<=busyuntil:
   outcome[k]=-2;continue
  # Initial received signal can only be submitted AT OR AFTER it is observed.
  target=now+lag_ms
  f=i
  if lag_ms>0:
   left=i+1;right=n
   while left<right:
    mid=(left+right)//2
    if t[mid]<target:left=mid+1
    else:right=mid
   f=left
  if f>=n or t[f]-target>max_age_ms or t[f]>=r13.T1:
   outcome[k]=-1;continue
  spread=a[f]-b[f]
  if spread<0 or spread>maxspread_raw:
   outcome[k]=-1;continue
  fill_ix[k]=f
  entry=(a[f]+slip_raw) if s>0 else (b[f]-slip_raw)
  opening_liq=b[f] if s>0 else a[f]
  first_good=-1;lastinside=t[f];prior=t[f];observed=False
  minliq=9223372036854775807;maxliq=-9223372036854775807
  stale=False;coverage=False;h15=t[f]+15000;h30=t[f]+30000
  for j in range(f+1,n):
   if t[j]==t[f]:continue
   if t[j]>h30:
    if t[j]-lastinside<=15000:coverage=True
    break
   if t[j]-prior>15000:stale=True
   observed=True;lastinside=t[j];prior=t[j]
   liq=b[j] if s>0 else a[j]
   if liq<minliq:minliq=liq
   if liq>maxliq:maxliq=liq
   if first_good<0 and t[j]<=h15:
    close=b[j]-slip_raw if s>0 else a[j]+slip_raw
    net=s*(close-entry)-20
    if net>=100:
     first_good=j;realized_good_net[k]=net
  if lastinside==h30:coverage=True
  if not observed or not coverage or stale:
   outcome[k]=-3;busyuntil=h30;continue
  safe=(minliq>opening_liq-100) if s>0 else (maxliq<opening_liq+100)
  if first_good>=0 and safe:
   outcome[k]=1;exit_ix[k]=first_good;busyuntil=t[first_good]
  else:
   outcome[k]=0;busyuntil=h30
 return outcome,fill_ix,exit_ix,realized_good_net


def execute():
 out=r13.OUT
 rows=[];quarter_rows=[];allsha={};source_receipts=[]
 for name in r13.EXPECTED:
  t,b,a,pin=r13.load_source(name)
  source_receipts.append({'name':name,'source_sha256':pin,'source_quote_halo_n':len(t)})
  p=out/f'R13_{name}_ALL_FUTURE_SELECTED_TRADE_SOURCE_ORDINALS.csv'
  orig=list(csv.DictReader(p.open(newline='')))
  for lane in ['BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000','BROKER_CONTRACTION','DIRECTIONAL_MICROPATH']:
   sub=[x for x in orig if x['lane']==lane and x['favorable_horizon_ms']=='15000']
   sig=np.array([int(r['entry_raw_tick_ordinal']) for r in sub],dtype=np.int64)
   side=np.array([int(r['side_BUY_1_SELL_minus1']) for r in sub],dtype=np.int8)
   assert len(sig)>0
   assert np.all(np.diff(t[sig])>0)
   assert all(str(int(t[sig[k]]))==sub[k]['entry_ms_UTC'] for k in range(len(sig)))
   cap=1500 if lane in ['BASE_250_1500','DENSE_1500'] else 4000
   for lag in (0,100,500):
    for slip in (0,20,50):
     outcome,fill,ex,net=stressed_frozen_signal(t,b,a,sig,side,lag,slip,cap)
     if lag==0 and slip==0:
      assert int(np.count_nonzero(outcome==1))==len(sig),f'BASE_SIGNAL_PARITY_FAIL {name} {lane} {len(sig)} {np.unique(outcome,return_counts=True)}'
     positive=(outcome==1).sum();failed=(outcome==0).sum()
     denominator=positive+failed
     acc=(float(positive/denominator) if denominator else None)
     r={'source':name,'lane':lane,'latency_ms':lag,'per_leg_slippage_raw_0p001':slip,
      'roundtrip_slippage_price_usd':2*slip/1000,'fill_spread_limit_USD':cap/1000,
      'frozen_future_selected_signals':len(sig),'strict_good_delayed_quotes':int(positive),
      'completed_failure':int(failed),'source_censored':int((outcome==-3).sum()),
      'quote_or_spread_reject':int((outcome==-1).sum()),'occupied_skip':int((outcome==-2).sum()),
      'completed_strict_accuracy':acc,'strict_good_count_meets_original_104':bool(positive>=104),
      'joint_accuracy_80_and_104':bool(acc is not None and acc>=.8 and positive>=104),
      'future_known_signal_not_real_model':True,'unmodeled_failed_trade_exit_economics':True}
     rows.append(r)
     for q in range(4):
      qs=r13.T0+q*900000;qt=qs+900000
      # Reference quarters are source UTC 06:00, 06:15, 06:30, 06:45.
      # Count a delayed entry by ACTUAL observed fill time, not the signal time.
      actualfill=(fill>=0)&(t[np.maximum(fill,0)]>=qs)&(t[np.maximum(fill,0)]<qt)
      goodq=int(np.count_nonzero(actualfill&(outcome==1)))
      badq=int(np.count_nonzero(actualfill&(outcome==0)))
      cenq=int(np.count_nonzero(actualfill&(outcome==-3)))
      cq=goodq+badq
      quota=(28,27,25,24)[q]
      quarter_rows.append({
       'source':name,'lane':lane,'latency_ms':lag,'per_leg_slippage_raw_0p001':slip,
       'filled_entry_UTC_quarter':__import__('datetime').datetime.fromtimestamp(qs/1000,__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
       'original_R9_SYNTH_quarter_ref':quota,
       'strict_good_filled_at_UTC_quarter':goodq,
       'completed_bad_filled_at_UTC_quarter':badq,
       'right_censored_filled_at_UTC_quarter':cenq,
       'accuracy_completed':None if not cq else goodq/cq,
       'good_count_quarter_meets_reference':bool(goodq>=quota),
       'joint_reference_and_80pct':bool(goodq>=quota and cq and goodq/cq>=.8),
       'future_selected_scenario_only':True})
     stem=f'R13_{name}_{lane}_lag{lag}_slip{slip}'
     tracep=out/(stem+'_ALL_FROZEN_SIGNALS_FULL_QUOTE_ORDINAL_OUTCOMES.npz')
     np.savez_compressed(tracep,source_quote_signal_ix=sig,source_signal_utc_ms=t[sig],
       original_hindsight_side=side,fill_quote_ix=fill,first_good_exit_quote_ix=ex,
       outcome_code=outcome,strict_good_executable_net_after_nominal_fee_raw=net)
     allsha[tracep.name]={'sha256':r13.sha(tracep),'bytes':tracep.stat().st_size}
  print(json.dumps({'source':name,'stress_scenarios':45}),flush=True)
 a=out/'R13_ALL_135_NEW_LANE_LATENCY_SLIPPAGE_SCENARIOS.csv'
 r13.write_csv(a,rows)
 qcsv=out/'R13_ALL_540_QUARTER_DELAY_FRICTION_SCENARIOS.csv';r13.write_csv(qcsv,quarter_rows)
 assert len(quarter_rows)==len(rows)*4
 receipt={'source_receipts':source_receipts,'scenarios':len(rows),'individual_complete_trace_files':len(allsha),
  'strict_correct_means_SOURCE_FUTURE_SELECTED_FIRST15_FAVORABLE_SAFE_FULL30':True,
  'research_status':'DELAY_COUNTERFACTUAL_FROM_FUTURE_PRIVILEGED_FROZEN_SIGNAL_NO_DEPLOYMENT',
  'maxspread_4p00_lane_is_an_UNAPPROVED_CHANGED_GATE':True,
  'no_failed_trade_net_or_account_PNL_claim':True,'source_quote_ordinal_trace_sha256':allsha}
 r=(out/'R13_135_EXACT_STRESS_TRACE_SHA_RECEIPT.json');r.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt
if __name__=='__main__':execute()
