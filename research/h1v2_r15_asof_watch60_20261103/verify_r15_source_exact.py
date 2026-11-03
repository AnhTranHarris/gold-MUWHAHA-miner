"""Independent source-ordinal/quote net and all 84/336/189/756 R15 row audit.
No fitting, no execution or live claims. Failure is fatal and logged.
"""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import r15_asof_watch60 as r15


def rows(name):
 with (ROOT/'results'/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def verify():
 h=rows('R15_ALL_84_SOURCE_LANE_HORIZON_HOURS.csv')
 q=rows('R15_ALL_336_SOURCE_LANE_HORIZON_QUARTERS.csv')
 tr=rows('R15_ALL_FUTURE_SELECTED_ORIGINAL_SOURCE_ORDINALS.csv')
 stress=rows('R15_ALL_189_ORIGINAL_STRICT_LATENCY_STRESS.csv')
 stressq=rows('R15_ALL_756_ORIGINAL_STRICT_LATENCY_QUARTERS.csv')
 assert(len(h),len(q),len(stress),len(stressq))==(84,336,189,756)
 assert len({(x['source'],x['lane'],x['forward_favorable_horizon_ms']) for x in h})==84
 assert len({(x['source'],x['lane'],x['forward_favorable_horizon_ms'],x['quarter_UTC_start']) for x in q})==336
 assert len({(x['source'],x['lane'],x['lag_ms'],x['slippage_raw_per_leg']) for x in stress})==189
 assert len({(x['source'],x['lane'],x['lag_ms'],x['slippage_raw_per_leg'],x['quarter_UTC']) for x in stressq})==756
 orig=dict(zip(('R9_REAL_MT5_TESTER','R9_SYNTH_MT5_TESTER','DUKASCOPY_RAW'),(705,1853,6)))
 wide=dict(zip(('R9_REAL_MT5_TESTER','R9_SYNTH_MT5_TESTER','DUKASCOPY_RAW'),(765,1853,347)))
 quotes={}
 trace_verify=0;pop_verify=0
 for source,pin in r15.r13.EXPECTED.items():
  t,b,a,check=r15.load_source(source)
  assert pin[1]==check
  quotes[source]=(t,b,a)
  z=ROOT/'results'/f'R15_{source}_ALL_ASOF_CANDIDATES_ALL_LANES_AND_SEPARATE_STRICT_LABELS.npz'
  with np.load(z,allow_pickle=False) as v:
   ix=v['source_quote_ix'];tn=v['source_utc_ms'];bid=v['quote_bid_raw'];ask=v['quote_ask_raw']
   assert len(tn)==len(ix) and np.array_equal(t[ix],tn)
   assert np.array_equal(b[ix],bid) and np.array_equal(a[ix],ask)
   assert v['lane_bits'].shape==(len(ix),len(r15.LANES))
   assert tuple(v['lane_names'].tolist())==r15.LANES
   assert not np.any(v['original_strict15_buy'] & v['original_strict15_sell'])
   assert np.all(v['original_strict15_buy']<=v['complete30'])
   assert np.all(v['original_strict15_sell']<=v['complete30'])
   assert np.all(v['strict60_buy']<=v['complete60'])
   assert np.all(v['strict60_sell']<=v['complete60'])
   pop_verify+=len(ix)
  control=next(x for x in h if x['source']==source and x['lane']=='BASE_250_1500' and x['forward_favorable_horizon_ms']=='15000')
  assert int(control['future_selected_exact_firstTP_onepos_count'])==orig[source]
  control2=next(x for x in h if x['source']==source and x['lane']=='R13_WIDE_REQUOTE_4000' and x['forward_favorable_horizon_ms']=='15000')
  assert int(control2['future_selected_exact_firstTP_onepos_count'])==wide[source]
  for lane in r15.LANES:
   for horizon in r15.FAV_HORIZONS:
    z=[x for x in tr if x['source']==source and x['lane']==lane and int(x['horizon_ms'])==horizon]
    claim=next(x for x in h if x['source']==source and x['lane']==lane and int(x['forward_favorable_horizon_ms'])==horizon)
    assert len(z)==int(claim['future_selected_exact_firstTP_onepos_count'])
    # Each schedule is independently one-position on original source observed quote ordinals.
    z.sort(key=lambda x:int(x['signal_utc_ms']))
    last=-2**62
    orig_good=0
    for x in z:
     i=int(x['entry_source_quote_ordinal']);j=int(x['exit_source_quote_ordinal'])
     side=int(x['BUY_1_SELL_minus1_FUTURE_KNOWN']);net=int(x['net_after_nominal_fee_raw'])
     assert side in (-1,1) and 0<=i<j<len(t)
     assert int(x['signal_utc_ms'])==int(t[i]) and int(x['exit_utc_ms'])==int(t[j])
     assert t[i]>last and t[j]>t[i] and t[j]<=t[i]+horizon
     assert int(x['entry_bid_raw'])==int(b[i]) and int(x['entry_ask_raw'])==int(a[i])
     assert int(x['exit_bid_raw'])==int(b[j]) and int(x['exit_ask_raw'])==int(a[j])
     assert net==(b[j]-a[i]-20 if side>0 else b[i]-a[j]-20)
     assert net>=100 and int(x['spread_raw'])==int(a[i]-b[i])
     assert x['asof_observed_entry_not_watch_trigger']=='True'
     orig_good+=int(x['original_strict15_full30'])
     if horizon==15000:assert x['original_strict15_full30']=='1'
     last=t[j]
    assert orig_good==int(claim['original_15s_correct_among_future_selected'])
    assert int(claim['future_selected_exact_firstTP_onepos_count'])>=0
    rq=[x for x in q if x['source']==source and x['lane']==lane and int(x['forward_favorable_horizon_ms'])==horizon]
    assert len(rq)==4
    assert sum(int(x['global_future_selected_in_quarter']) for x in rq)==len(z)
    assert sum(int(x['original_strict15_selected_in_this_quarter']) for x in rq)==orig_good
    assert [int(x['original_R9_SYNTH_reference_quarter']) for x in rq]==list(r15.REFERENCE)
    trace_verify+=len(z)
 for x in stress:
  source=x['source'];lane=x['lane'];lag=int(x['lag_ms']);slip=int(x['slippage_raw_per_leg'])
  assert lag in (0,100,500) and slip in (0,20,50)
  with np.load(ROOT/'results'/f'R15_{source}_{lane}_lag{lag}_slip{slip}_ALL_FROZEN_SOURCE_ORDINALS.npz',allow_pickle=False) as v:
   code=v['outcome_code'];ix=v['original_source_signal_ix'];f=v['fill_source_ix'];ex=v['firstTP_exit_source_ix'];n=v['net_reachable_raw']
   t,b,a=quotes[source]
   assert len(code)==len(ix)==int(x['future_known_original_strict_signals'])
   assert int((code==1).sum())==int(x['strict_good_after_delay'])
   assert int((code==0).sum())==int(x['strict_completed_failure_after_delay'])
   assert int((code==-3).sum())==int(x['right_censored_after_delay'])
   assert int((code==-1).sum())==int(x['spread_or_quote_reject'])
   assert int((code==-2).sum())==int(x['busy_position_skip'])
   assert set(np.unique(code)).issubset({1,0,-1,-2,-3})
   assert np.all(ex[code==1]>=0) and np.all(n[code==1]>=100)
   assert not (code==1).sum() or np.all(t[ex[code==1]]>t[f[code==1]])
   for z in np.flatnonzero(code==1):
    s=int(v['future_known_side'][z]);i=int(f[z]);j=int(ex[z]);p=int(n[z]);
    assert p== (b[j]-slip-a[i]-slip-20 if s==1 else b[i]-slip-a[j]-slip-20)
 qs={'sources':list(quotes),'raw_three_verified_sha':True,'full_source_asof_candidate_rows_read':pop_verify,
  'all_alternative_selected_source_quote_paths_revalidated':trace_verify,
  'hour_rows':len(h),'quarter_rows':len(q),'latency_scenarios':len(stress),'latency_quarters':len(stressq),
  'R13_original_15s_base_selected_counts':orig,'R13_original_15s_wide_selected_counts':wide,
  'all_original_15s_side_labels_verified_via_source':True,'all_selected_one_position_and_actual_bid_ask_net_checked':True,
  'source_research_only_not_execution_or_realtime_prediction':True}
 (ROOT/'results/R15_INDEPENDENT_QUOTE_ORDINAL_VERIFICATION.json').write_text(json.dumps(qs,indent=2,allow_nan=False)+'\n')
 print(json.dumps(qs,indent=2));return qs
if __name__=='__main__':verify()
