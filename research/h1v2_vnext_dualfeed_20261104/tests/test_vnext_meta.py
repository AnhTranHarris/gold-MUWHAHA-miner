"""Deterministic C4 forward-only split and receipt invariants (no raw PnL claims)."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from vnext_meta import (chronological_splits,BINS,TRAIN_END_DAY,CAL_START_DAY,CAL_END_DAY,TEST_START_DAY)

def test_phases_purged_by_real_utc_days_and_never_overlap():
 # Synthetic quote ordinals are exactly one per UTC day, with no fabricated labels.
 begin=np.datetime64('2026-01-01T00:00:00','ms').astype('int64')
 t=begin+np.arange(31,dtype=np.int64)*86_400_000
 trace=np.zeros((31,7),np.int64);trace[:,0]=np.arange(31);trace[:,3]=np.where(np.arange(31)%3==0,1,0)
 train,cal,test,day=chronological_splits(t,trace,'01')
 assert train.sum()==9 and cal.sum()==9 and test.sum()==11
 assert not np.any(train&cal) and not np.any(train&test) and not np.any(cal&test)
 assert day[9]==10 and not (train[9] or cal[9] or test[9])
 assert day[19]==20 and not (train[19] or cal[19] or test[19])

def test_phase_censored_and_unfilled_not_used_as_target_labels():
 begin=np.datetime64('2026-02-01T00:00:00','ms').astype('int64')
 t=begin+np.arange(28,dtype=np.int64)*86_400_000
 trace=np.zeros((28,7),np.int64);trace[:,0]=np.arange(28);trace[:,3]=1;trace[0,3]=3;trace[11,3]=4;trace[22,3]=3
 tr,ca,te,_=chronological_splits(t,trace,'02')
 assert tr.sum()==8 and ca.sum()==8 and te.sum()==7
 assert not tr[0] and not ca[11] and not te[22]

def test_predeclared_risk_gates_not_optimized_on_test_outcomes():
 assert BINS==(('M00_P55',.55,False),('M01_P65',.65,False),('M02_P75',.75,False),('M03_P55_NETPOS',.55,True))
 assert TRAIN_END_DAY==9 and CAL_START_DAY==11 and CAL_END_DAY==19 and TEST_START_DAY==21

def test_all_original_c4_source_month_receipts_preserved_when_present():
 root=Path('/mnt/data/h1v2_vnext/meta')
 if not root.exists():pytest.skip('full original authenticated C4 results not mounted')
 paths=sorted(root.glob('*/*/C4_*_ATOMIC_RECEIPT.json'))
 if len(paths)<8:pytest.skip('still in research, eight source-month cases not complete')
 assert len(paths)==8
 for p in paths:
  j=json.loads(p.read_text());assert len(j['four_frozen_gates'])==4
  assert all(x['test_hour_joint']==0 for x in j['four_frozen_gates'])
  assert all(x['is_conservative_subset_of_preexecuted_C3'] and not x['test_hour_joint'] for x in j['four_frozen_gates'])
  assert j['not_a_blind_OOS'] and j['no_original_EA_modifications']
