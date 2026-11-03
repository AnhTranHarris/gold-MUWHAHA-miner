"""Regression assertions on all four actual 2026 R11S/R11S2 full-source exports.
These assert source provenance and mechanical aggregation, NOT profitable alpha.
"""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
MONTHS={'2026-01':(744,27980,480,50),'2026-02':(672,33523,458,151),
        '2026-06':(720,31758,497,27),'2026-07':(744,24324,482,18)}
def read(name):
 with (ROOT/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def test_complete_hour_calendar_and_corrected_synth_month():
 a=read('ALL_2880_UTC_HOURLY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv')
 assert len(a)==2880
 for m,(n,ref,active,bad) in MONTHS.items():
  z=[x for x in a if x['month']==m]
  assert len(z)==n
  assert len(set(x['utc_hour_start'] for x in z))==n
  assert sum(int(x['R9_SYNTH_reference']) for x in z)==ref
  assert sum(int(x['R9_SYNTH_reference_active']) for x in z)==active
  assert sum(int(x['R11_impossible_even_independent_hour_crossing']) for x in z)==bad
  assert all(int(x['R11_strict_30s_hour_interior_constructive_MAX'])<=int(x['R11_strict_30s_hour_crossing_optimistic_UPPER']) for x in z)

def test_complete_day_calendar_and_parity_with_hourly():
 a=read('ALL_120_UTC_DAILY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv')
 b=read('ALL_2880_UTC_HOURLY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv')
 assert len(a)==120
 for r in a:
  z=[x for x in b if x['utc_day']==r['utc_day']]
  assert len(z)==24
  assert sum(int(x['R9_SYNTH_reference']) for x in z)==int(r['R9_SYNTH_reference'])
  assert sum(int(x['R11_strict_15fav_30surv_original_global_hindsight_selected']) for x in z)==int(r['strict_15fav30surv_global_hindsight'])

def test_fitted_student_all_36_policy_hourly_and_day_counts():
 a=read('ALL_25920_UTC_HOURLY_STUDENT_REPLAY_36_POLICIES.csv')
 b=read('ALL_1080_UTC_DAILY_STUDENT_REPLAY_36_POLICIES.csv')
 assert len(a)==25920 and len(b)==1080
 for x in a:
  total=int(x['R11S2_model_trades_30s_nooverlap'])
  counts=sum(int(x[f]) for f in ['R11S2_model_STRICT_15fav30surv','R11S2_model_ADVERSE30','R11S2_model_NEUTRAL','R11S2_model_CENSORED'])
  assert total==counts
 for x in b:
  z=[y for y in a if y['utc_hour_start'].startswith(x['utc_day']) and y['fraction']==x['fraction']]
  assert len(z)==24
  assert sum(int(y['R11S2_model_trades_30s_nooverlap']) for y in z)==int(x['R11S2_model_trades'])

def test_no_in_sample_student_meets_joint_hourly_contract():
 a=read('ALL_25920_UTC_HOURLY_STUDENT_REPLAY_36_POLICIES.csv')
 assert sum(x['joint_hour_reference_and_strict80']=='1' for x in a)==0

def test_full_data_deficit_witnesses_not_suppressed():
 witnesses=json.loads((ROOT/'ALL_PROVEN_30SEC_HOURLY_IMPOSSIBILITY_WITNESSES.json').read_text())
 assert len(witnesses)==246
 for x in witnesses:
  assert x['reference']>x['max_possible_with_original_strict_horizon']
  assert x['unavoidable_deficit']==x['reference']-x['max_possible_with_original_strict_horizon']

def test_hash_index_all_four_clock_version():
 v=json.loads((ROOT/'EXECUTION_VERIFICATION_INDEX.json').read_text())
 assert v['calendar_hours']==2880 and v['calendar_days']==120
 assert v['student_policies']==36 and v['student_policy_hour_rows']==25920
 assert all(x['all_model_traces_rechecked'] for x in json.loads((ROOT/'ALL_SOURCE_EXACT_EXECUTION_PARITY_CHECKS.json').read_text()))
