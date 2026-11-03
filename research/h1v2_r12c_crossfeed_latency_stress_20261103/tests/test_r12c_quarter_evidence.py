"""Full source V2 month-quarter receipt regression, skipped if source archive not present."""
import csv, json
from pathlib import Path
import numpy as np
import pytest

R=Path('/mnt/data/h1v2_r12c/results_quarter_v2')

def data():
 p=R/'R12C_Q_ALL_216_QUARTER_SOURCE_EXACT_LATENCY_AND_PRECISION.csv'
 if not p.exists():pytest.skip('source full replay receipts not available on this runner')
 return list(csv.DictReader(p.open(newline='')))

def test_all_216_reconciled_and_54_scenarios():
 rows=data();assert len(rows)==216
 assert len(set((r['source'],r['latency_ms'],r['entry_exit_extra_slippage_each_raw_0p001']) for r in rows))==54
 assert all(len([x for x in rows if x['source']==r['source'] and x['latency_ms']==r['latency_ms'] and x['entry_exit_extra_slippage_each_raw_0p001']==r['entry_exit_extra_slippage_each_raw_0p001']])==4 for r in rows)

def test_original_104_quarter_source_ref_never_hour_divide():
 rows=data()
 for source in set(x['source'] for x in rows):
  vals=[int(r['original_R9_SYNTH_source_15m_reference']) for r in rows if r['source']==source and r['latency_ms']=='0' and r['entry_exit_extra_slippage_each_raw_0p001']=='0']
  assert vals==[28,27,25,24] and sum(vals)==104

def test_no_fake_quarter_success_from_missing_completed_fills():
 for r in data():
  g=int(r['good_delayed_execution_fills_in_quarter']);bad=int(r['completed_bad_delayed_execution_fills_in_quarter']);target=int(r['original_R9_SYNTH_source_15m_reference'])
  joint=int(r['joint_15min_80precision_and_100pct_count'])
  assert joint==int(g>=target and (g+bad)>0 and g/(g+bad)>=.80)
  if not g+bad:assert r['strict_precision_completed_fills_in_quarter']==''

def test_all_54_trace_families_exact_source_ordinal_and_outcome_accounting():
 rows=data();p=list(R.glob('R12C_Q_FULL_SOURCE*.npz'));assert len(p)==54
 for f in p:
  with np.load(f,allow_pickle=False) as z:
   o=z['outcome_code'];sig=z['signal_quote_ordinals'];fill=z['delayed_fill_quote_ordinals']
   assert len(o)==len(sig)==len(fill)
   assert np.all(sig[1:]>sig[:-1]);assert np.all(np.isin(o,[-3,-2,-1,0,1]))
   assert np.all(fill[o==-2]<0)

def test_per_source_54_scenarios_must_match_pinned_v1():
 data()
 a=list(csv.DictReader((R/'R12C_Q_ALL_54_HOURLY_FULL_STRESS_RECONCILED.csv').open(newline='')))
 b=list(csv.DictReader(Path('/mnt/data/h1v2_r12c/results/R12C_ALL_54_SOURCE_LATENCY_SLIPPAGE_SCENARIOS.csv').open(newline='')))
 assert len(a)==len(b)==54
 ix={(x['source'],x['latency_nominal_ms'],x['entry_and_exit_each_slip_raw_usd_0p001']):x for x in b}
 for r in a:
  old=ix[(r['source'],r['lag'],r['slip_each_0p001'])]
  assert int(r['good_delayed_fill_total'])==int(old['good_first15_and_safe_full30_at_delayed_quote'])
  assert int(r['quarter_good_sum'])==int(r['good_delayed_fill_total'])
