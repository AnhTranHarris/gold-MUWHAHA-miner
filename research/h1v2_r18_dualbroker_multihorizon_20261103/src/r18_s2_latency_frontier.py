"""R18-S2: source-exact two-broker delayed-firstTP hindsight frontier.

This new *retrospective* study freezes R18 zero-delay future-selected source
signal ordinals and sides, independently evaluates their first observed quote
at signal+100/500ms with full bid/ask transaction friction, and repacks ONLY
future-known successful delayed intervals. The repacking is future-privileged;
100% correctness of selected actions is a tautology, NOT a predictor.

Unlike R18-S1, no trial is suppressed by a different trial's busy state while
labelling. This permits a scientifically explicit optimistic interval packing
of the FROZEN R18 selected-signal subuniverse. Because it excludes unselected
as-of source quotes, this is NOT a universal achievable upper bound.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys, time
from pathlib import Path
import numpy as np
from numba import njit
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen,GOOD,STOP,TIMEOUT,REJECT,CENSOR
LAGS=(100,500)
SLIPS=(0,20)
CAPS=(1500,2500,4000)
FEE=20;TARGET=100;ADVERSE=100;HORIZON=60000;GAP=15000

@njit(cache=False)
def independent_delayed_firsttouch(t,b,a,signals,side,fills,slip):
 """Per-source-signal independent first passage, no position busy arbitration.

 First observed fill >= signal+lag is precomputed in wrapper; -1 is reject.
 Intentionally returns STOP/TIMEOUT realized quote economics and CENSOR unknown.
 """
 n=len(signals)
 state=np.full(n,REJECT,np.int8);exitord=np.full(n,-1,np.int32)
 net=np.full(n,-2147483647,np.int32)
 for k in range(n):
  f=int(fills[k]);si=int(side[k]);
  if f<0:continue
  buy=si==1
  paid=(int(a[f])+slip) if buy else (int(b[f])-slip)
  opening=int(b[f]) if buy else int(a[f])
  prev=t[f];resolved=False
  for j in range(f+1,len(t)):
   if t[j]==t[f]:continue
   if t[j]-prev>GAP:
    state[k]=CENSOR;resolved=True;break
   prev=t[j]
   liq=int(b[j])-slip if buy else int(a[j])+slip
   value=(liq-paid)*si-FEE
   if t[j]>t[f]+HORIZON:
    state[k]=TIMEOUT;exitord[k]=j;net[k]=value;resolved=True;break
   if (buy and b[j]<=opening-ADVERSE) or (not buy and a[j]>=opening+ADVERSE):
    state[k]=STOP;exitord[k]=j;net[k]=value;resolved=True;break
   if value>=TARGET:
    state[k]=GOOD;exitord[k]=j;net[k]=value;resolved=True;break
  if not resolved:state[k]=CENSOR
 return state,exitord,net

@njit(cache=False)
def _pack_sorted(starts,ends,order):
 out=np.empty(len(order),np.int32);n=0
 last=np.int64(-9223372036854775807)
 for z in range(len(order)):
  k=order[z]
  if starts[k]>last:
   out[n]=k;n+=1;last=ends[k]
 return out[:n]

def pack_future_good(t,fills,exitord,valid):
 k=np.flatnonzero(valid)
 if len(k)==0:return np.empty(0,np.int32)
 starts=t[fills[k]];ends=t[exitord[k]]
 assert np.all(ends>starts)
 # Earliest-completion interval packing gives exact max cardinality for
 # this closed, offline-filtered event set, NOT interval+quota economics.
 order=np.lexsort((k,starts,ends)).astype(np.int64)
 chosen=_pack_sorted(starts,ends,order)
 return k[chosen]

def run_source_month(source,mon):
 started=time.monotonic();t,b,a,signal,side,_,provenance=get_frozen(source,mon)
 original_refs=r18.refs_for_month(mon,Path('/mnt/data'))
 qkeys=original_refs['qkeys'];qref=original_refs['qref'];href=original_refs['href']
 start=int(qkeys[0]*900000);end=int((qkeys[-1]+1)*900000)
 assert len(signal)>0 and np.all(np.diff(t[signal])>0)
 monthtag=f'R18_S2_{source}_{mon}'
 out=HERE/'results_r18_S2_LATENCY_FRONTIER';out.mkdir(exist_ok=True)
 scenarios=[];qrows=[];hrows=[];traces={};refactive=int((qref>0).sum())
 for lag in LAGS:
  fill=np.searchsorted(t,t[signal]+lag,side='left').astype(np.int32)
  valid=(fill<len(t));fi=fill.clip(0,len(t)-1)
  valid&=(fi>signal)&(t[fi]>t[signal])
  valid&=(t[fi]-(t[signal]+lag)<=1000)
  # Stop source-end cash net inference; honor original source-month UTC
  # calendar and separately record actual delayed fills after source end.
  valid&=(t[fi]>=start)&(t[fi]<end)
  spread=(a[fi].astype(np.int64)-b[fi].astype(np.int64))
  valid&=(spread>=0)&(spread<=4000)
  fills=np.where(valid,fi,-1).astype(np.int32)
  for slip in SLIPS:
   state,exitord,net=independent_delayed_firsttouch(t,b,a,signal,side,fills,slip)
   succeeded=(state==GOOD)
   assert np.all(net[succeeded]>=TARGET) and np.all(exitord[succeeded]>fills[succeeded])
   for cap in CAPS:
    accepted=(fills>=0)&(spread<=cap)
    qual=succeeded&accepted
    chosen=pack_future_good(t,fills,exitord,qual)
    if len(chosen)>1:
     assert np.all(t[fills[chosen[1:]]]>t[exitord[chosen[:-1]]]),'PACK_OVERLAP'
    offsets=(t[fills[chosen]]//900000-qkeys[0]).astype(np.int64)
    assert np.all((offsets>=0)&(offsets<len(qref)))
    qcount=np.bincount(offsets,minlength=len(qref)).astype(np.int32)
    hcount=qcount.reshape(-1,4).sum(axis=1)
    qmatch=(qref>0)&(qcount>=qref);hmatch=(href>0)&(hcount>=href)
    name=f'lag{lag}_slip{slip}_cap{cap}'
    scenarios.append({'source':source,'month':mon,'scenario':name,'nominal_delay_ms':lag,
      'extra_slip_quoted_price_raw_per_leg':slip,'current_actual_fill_spread_cap_raw':cap,
      'R18_frozen_original_source_signals':len(signal),
      'independent_hindsight_source_delayed_good':int(qual.sum()),
      'independent_hindsight_source_delay_completed_bad':int(((state==STOP)|(state==TIMEOUT)).sum()),
      'source_signal_rejected_or_censored':int((~accepted).sum()+int(((state==CENSOR)&accepted).sum())),
      'repacked_onepos_future_known_winners':len(chosen),
      'repacked_15min_quotas_met':int(qmatch.sum()),'active_15min_quota_ref':refactive,
      'repacked_hourly_quotas_met':int(hmatch.sum()),'active_hourly_ref':int((href>0).sum()),
      'original_R9_SYNTH_ref_trades':int(qref.sum()),
      'selected_future_target_net_quote_price_units_0p001':int(net[chosen].astype(np.int64).sum()),
      'selected_historical_100pct_good_is_future_selection_tautology':True,
      'subuniverse_ONLY_original_R18_zero_latency_selected_signals':True,
      'cannot_claim_any_out_of_sample_accuracy_or_live_broker_fills':True})
    for z,ref in enumerate(qref):
     qrows.append({'source':source,'month':mon,'scenario':name,
       'quarter_UTC':original_refs['rows'][z]['utc_quarter'],
       'R9_SYNTH_ref':int(ref),'repacked_future_good':int(qcount[z]),
       'source_delta_slots':int(qcount[z]-ref),'quota_met':int(qmatch[z]) if ref else '',
       'future_selected':True})
    for z,ref in enumerate(href):
     hrows.append({'source':source,'month':mon,'scenario':name,
       'hour_UTC':original_refs['rows'][4*z]['utc_hour'],
       'R9_SYNTH_ref':int(ref),'repacked_future_good':int(hcount[z]),
       'source_delta_slots':int(hcount[z]-ref),'quota_met':int(hmatch[z]) if ref else '',
       'future_selected':True})
    traces[name+'_source_signal_idx']=signal[chosen]
    traces[name+'_side_future_informed']=side[chosen]
    traces[name+'_actual_quote_fill_idx']=fills[chosen]
    traces[name+'_first_observed_target_exit_idx']=exitord[chosen]
    traces[name+'_nominal_net_raw']=net[chosen]
    print(source,mon,name,'future-good',int(qual.sum()),'repacked',len(chosen),
          'Q',int(qmatch.sum()),'/',refactive,
          'H',int(hmatch.sum()),'/',int((href>0).sum()),flush=True)
 def outputcsv(p,rows):
  with p.open('w',newline='',encoding='utf8') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 p=out/(monthtag+'_12_RESEARCH_SCENARIO_ROWS.csv')
 q=out/(monthtag+'_ALL_UTC_15MIN_12_SCENARIOS.csv')
 h=out/(monthtag+'_ALL_UTC_HOURS_12_SCENARIOS.csv')
 z=out/(monthtag+'_COMPLETE_REPACKED_SOURCE_SIGNAL_QUOTE_ORDINALS.npz')
 outputcsv(p,scenarios);outputcsv(q,qrows);outputcsv(h,hrows)
 np.savez_compressed(z,**traces)
 rec={'classification':'FUTURE_SELECTED_DELAY_AWARE_REPACK_SOURCE_SELECTED_SUBUNIVERSE_ONLY_NOT_DEPLOYABLE',
  'source':source,'month':mon,'original_src_sha':r18.PINS[source][mon],
  'r18_month_original_ORACLE_signals':len(signal),'historical_clock':provenance,
  'source_UTC_reference_sha256':original_refs['sha256'],
  'all_scenarios':scenarios,
  'source_is_ONLY_r18_zero_latency_future_selected_ordinal_universe':True,
  'cannot_prove_global_impossibility_from_subset':True,
  'must_not_predict_or_trade_future_membership':True,
  'no_actual_broker_fill_or_account_currency_pnl':True,
  'outputs':{x.name:{'bytes':x.stat().st_size,'sha256':r18.sha(x)} for x in (p,q,h,z)},
  'elapsed_wall_seconds':round(time.monotonic()-started,2)}
 recp=out/(monthtag+'_SOURCE_AND_OUTPUT_SHA_RECEIPT.json');recp.write_text(json.dumps(rec,indent=2)+'\n')
 return rec
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=tuple(r18.PINS),required=True)
 ap.add_argument('--month',choices=tuple(r18.OFFSETS),required=True)
 args=ap.parse_args();x=run_source_month(args.source,args.month)
 print('COMPLETE',x['source'],x['month'],'scenarios',len(x['all_scenarios']),flush=True)
