from pathlib import Path
import numpy as np
from r34_eightcell_source_audit import load,stats,select_on_calibration
ROOT=Path(__file__).parent

def test_original_eight_cells_and_aggregate():
 d=load(ROOT)
 assert len(d)==8
 assert sum(int((x['frozen_r24_veto']&(x['original_truth']!=0)).sum()) for x in d.values())==814995
 assert sum(int((x['frozen_r24_veto']&(x['original_truth']==0)).sum()) for x in d.values())==9999

def test_dukascopy_t15_is_always_below_required_90pct():
 d=load(ROOT)
 for month in ('01','02','06','07'):
  x=d[('DUKASCOPY',month)];r=stats(x,x['frozen_r24_veto'])
  assert not r['90pct_bad_rejection_feasible_t15']
  assert r['bad_rejection_fraction']<=r['eligible_bad_fraction']

def test_threshold_calibration_uses_only_declared_prior_months():
 d=load(ROOT)
 q=select_on_calibration(d,('01','02'),'COINEXX')
 t=d[('COINEXX','07')].copy();t['original_truth']=np.zeros_like(t['original_truth'])
 # Mutating late July labels without touching the Jan/Feb FIT cells cannot change the frozen cutoff.
 e=dict(d);e[('COINEXX','07')]=t
 assert q==select_on_calibration(e,('01','02'),'COINEXX')
