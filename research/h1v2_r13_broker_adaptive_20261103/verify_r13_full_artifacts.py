#!/usr/bin/env python3
"""Independent complete-source-ordinal verification for ALL R13 persisted traces.

Does not create an entry model or infer account PnL. All original source sha,
quarter/hour totals, every future selected trade, all 135 +27 scenario arrays,
and 540+108 quarter rows are rejoined to actual source quote ordinals.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import r13_crossbroker_horizon_lanes as r


def read(path):return list(csv.DictReader(path.open(newline='',encoding='utf8')))

def main():
 root=r.OUT
 fixed=read(root/'R13_ALL_45_SOURCE_LANE_HORIZON_RESULTS.csv')
 fq=read(root/'R13_ALL_180_SOURCE_QUARTER_LANE_HORIZON_RESULTS.csv')
 stress=read(root/'R13_ALL_135_NEW_LANE_LATENCY_SLIPPAGE_SCENARIOS.csv')
 sq=read(root/'R13_ALL_540_QUARTER_DELAY_FRICTION_SCENARIOS.csv')
 dynstress=read(root/'R13_ALL_27_ASOF_DYNAMIC_HORIZON_DELAY_SCENARIOS.csv')
 dynq=read(root/'R13_ALL_108_ASOF_DYNAMIC_HORIZON_DELAY_QUARTERS.csv')
 assert [len(x) for x in (fixed,fq,stress,sq,dynstress,dynq)]==[45,180,135,540,27,108]
 source_receipts=[];verified_fixed_trades=0;verified_scenario_actions=0;verified_dynamic_trades=0
 for source in r.EXPECTED:
  t,b,a,pin=r.load_source(source)
  with np.load(root/f'R13_{source}_ALL_ASOF_CANDIDATES_AND_SEPARATE_HORIZON_LABELS.npz',allow_pickle=False) as z:
   ix=z['source_quote_ordinal'];tix=z['entry_utc_ms'];eb=z['entry_bid_raw'];ea=z['entry_ask_raw'];flags=z['asof_clock_bits']
   assert np.array_equal(t[ix],tix) and np.array_equal(b[ix],eb) and np.array_equal(a[ix],ea)
   assert np.all(np.diff(ix)>0) and not np.any((a[ix]-b[ix])>4000)
   assert len(ix)==len(np.unique(tix))
   for h in r.HORIZONS:
    g=z[f'h{h}_future_good_BUY'];s=z[f'h{h}_future_good_SELL']
    assert not np.any(g&s)
  full=read(root/f'R13_{source}_ALL_FUTURE_SELECTED_TRADE_SOURCE_ORDINALS.csv')
  by=defaultdict(list)
  for row in full:
   by[(row['lane'],row['favorable_horizon_ms'])].append(row)
   i=int(row['entry_raw_tick_ordinal']);j=int(row['exit_raw_tick_ordinal'])
   assert i<j and t[i]==int(row['entry_ms_UTC']) and t[j]==int(row['exit_ms_UTC'])
   side=int(row['side_BUY_1_SELL_minus1']);value=int(row['net_proxy_price_raw_0p001'])
   net=b[j]-a[i]-20 if side==1 else b[i]-a[j]-20
   assert value==net>=100
   assert t[j]>t[i] and t[j]<=t[i]+int(row['favorable_horizon_ms'])
   verified_fixed_trades+=1
  for info in fixed:
   if info['source']!=source:continue
   entries=by[(info['lane'],info['first_favorable_horizon_ms'])]
   assert len(entries)==int(info['future_selected_nonoverlap_firstTP'])
   for old,new in zip(entries[:-1],entries[1:]):
    assert int(new['entry_ms_UTC'])>int(old['exit_ms_UTC'])
   for quarter in [q for q in fq if q['source']==source and q['lane']==info['lane'] and q['horizon_ms']==info['first_favorable_horizon_ms']]:
    start=int(__import__('datetime').datetime.strptime(quarter['quarter_UTC'],'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=__import__('datetime').timezone.utc).timestamp()*1000)
    count=sum(start<=int(x['entry_ms_UTC'])<start+900000 for x in entries)
    assert count==int(quarter['future_selected_nonoverlap_count'])
  for rec in [a for a in stress if a['source']==source]:
   name=f"R13_{source}_{rec['lane']}_lag{rec['latency_ms']}_slip{rec['per_leg_slippage_raw_0p001']}_ALL_FROZEN_SIGNALS_FULL_QUOTE_ORDINAL_OUTCOMES.npz"
   with np.load(root/name,allow_pickle=False) as z:
    sig=z['source_quote_signal_ix'];f=z['fill_quote_ix'];ex=z['first_good_exit_quote_ix'];status=z['outcome_code'];nets=z['strict_good_executable_net_after_nominal_fee_raw'];side=z['source_signal_utc_ms']
    assert len(sig)==int(rec['frozen_future_selected_signals'])
    assert np.array_equal(t[sig],side)
    m={1:'strict_good_delayed_quotes',0:'completed_failure',-3:'source_censored',-1:'quote_or_spread_reject',-2:'occupied_skip'}
    for code,key in m.items(): assert np.count_nonzero(status==code)==int(rec[key])
    good=np.flatnonzero(status==1)
    for k in good:
     assert f[k]>=0 and ex[k]>f[k]
     assert t[ex[k]]>t[f[k]] and t[ex[k]]<=t[f[k]]+15000
     assert int(nets[k])>=100
    verified_scenario_actions+=len(sig)
    parts=[q for q in sq if q['source']==source and q['lane']==rec['lane'] and q['latency_ms']==rec['latency_ms'] and q['per_leg_slippage_raw_0p001']==rec['per_leg_slippage_raw_0p001']]
    assert len(parts)==4
    assert sum(int(q['strict_good_filled_at_UTC_quarter']) for q in parts)==len(good)
    assert sum(int(q['completed_bad_filled_at_UTC_quarter']) for q in parts)==int((status==0).sum())
  drows=read(root/f'R13_{source}_ADAPTIVE_ASOF_HORIZON_V1_ALL_TRADE_ORDINALS.csv')
  for i,row in enumerate(drows):
   j=int(row['entry_source_quote_ordinal']);k=int(row['exit_source_quote_ordinal'])
   assert t[j]==int(row['entry_UTC_ms']) and t[k]==int(row['exit_UTC_ms'])
   assert row['satisfies_original_first15_safe_full30']=='True'
   assert t[k]>t[j]
   if i:assert t[j]>int(drows[i-1]['exit_UTC_ms'])
   verified_dynamic_trades+=1
  for rec in [z for z in dynstress if z['source']==source]:
   name=f"R13_{source}_DYNAMIC_HORIZON_STRESS_lag{rec['lag_ms']}_slip{rec['per_leg_slip_raw']}_ALL_ORDINALS.npz"
   with np.load(root/name,allow_pickle=False) as z:
    sig=z['signal_source_quote_ordinal'];sta=z['delayed_strict_outcome'];f=z['delayed_fill_quote_ordinal']
    assert len(sig)==int(rec['source_future_oracle_initial_qualified'])
    assert np.count_nonzero(sta==1)==int(rec['good_delayed_fill_strict15'])
    assert np.count_nonzero(sta==0)==int(rec['bad_delayed_fill_strict15'])
    assert len(sta)==sum(int(rec[x]) for x in ['good_delayed_fill_strict15','bad_delayed_fill_strict15','source_censored','quote_spread_rejected','position_busy_skip'])
   qs=[q for q in dynq if q['source']==source and q['lag_ms']==rec['lag_ms'] and q['per_leg_slip_raw']==rec['per_leg_slip_raw']]
   assert len(qs)==4
   assert sum(int(x['good_completed']) for x in qs)==int(rec['good_delayed_fill_strict15'])
  source_receipts.append({'source':source,'source_original_sha256':pin,'source_halo_quotes':len(t),
    'asof_candidate_ordinal_rows':len(ix),'all_fixed_source_trade_trace_rows':len(full),'all_dynamic_source_trade_trace_rows':len(drows),
    'source_scenario_count':45,'dynamic_scenario_count':9,'all_ordinal_joins_and_bucket_sums':True})
 final={'source_data_validated':source_receipts,'fixed_hour_rows':len(fixed),'fixed_quarter_rows':len(fq),
  'delayed_scenario_rows':len(stress),'delayed_quarter_rows':len(sq),'adaptive_delayed_scenario_rows':len(dynstress),
  'adaptive_delayed_quarter_rows':len(dynq),'selected_fixed_trade_ordinal_full_records_checked':verified_fixed_trades,
  'selected_dynamic_trade_ordinal_full_records_checked':verified_dynamic_trades,
  'original_135_scenarios_all_source_signals_reconciled':verified_scenario_actions,
  'source_sha_and_full_quote_ordinal_checks':'ALL_PASS',
  'research_not_a_prospective_model_or_live_fill':True}
 path=root/'R13_FULL_SOURCE_INDEPENDENT_TRACE_REVERIFICATION.json'
 path.write_text(json.dumps(final,indent=2,allow_nan=False)+'\n')
 print(json.dumps(final,indent=2))
 return final
if __name__=='__main__':main()
