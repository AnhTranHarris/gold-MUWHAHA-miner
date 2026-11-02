import sys,json,unittest,math
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101')
sys.path.insert(0,str(ROOT/'src'))
from acceptance_gate import acceptance
class ResearchIntegrity(unittest.TestCase):
 def test_all_eight_exact_quote_matches(self):
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    x=json.loads((ROOT/'checkpoints'/f'{src}_{m}_feature_receipt.json').read_text())
    self.assertEqual(x['rows'],x['exact_price_timestamp_matched']);self.assertEqual(0,x['mismatch_count'])
 def test_hindsight_cannot_leak_into_runtime_X(self):
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    meta=json.loads((ROOT/'checkpoints'/f'{src}_{m}_mmap.json').read_text())
    self.assertEqual(89,len(meta['features']))
    self.assertFalse(any(('future' in x or 'teacher' in x or 'label' in x or 'net' in x or 'exit' in x) for x in meta['features']))
 def test_monthly_real_trade_counts_stable(self):
  truth=json.loads((ROOT/'results/full_ledger_truth.json').read_text())
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    df=truth[f'{src}_{m}'];v=json.loads((ROOT/'checkpoints'/f'{src}_{m}_feature_receipt.json').read_text())
    self.assertEqual(df['trades'],v['rows'])
 def test_all_eight_ordered_labels_refine_close_only(self):
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    r=json.loads((ROOT/'checkpoints'/f'{src}_{m}_ordered_barrier_receipt.json').read_text())
    orig=json.loads((ROOT/'checkpoints'/f'{src}_{m}_feature_receipt.json').read_text())
    self.assertEqual(r['rows'],orig['rows'])
    self.assertLessEqual(r['ordered_good'],orig['labeled_win'])
 def test_all_ordered_chronological_calibrations_fail_contract(self):
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    r=json.loads((ROOT/'results'/f'{src}_{m}_ordered_firstpass_chronological.json').read_text())
    self.assertFalse(any(c['meets80'] and c['positive_expectancy'] for c in r['NP_variants']))
 def test_gate_does_not_pass_empty_periods(self):
  x={'selected':23783,'30s_win_count':23783,'daily_passes':3,'daily_total':4,'weekly_passes':4,'weekly_total':4,'profit_net':123.}
  self.assertFalse(acceptance('coinexx','01',x)['APPROVED'])
 def test_gate_does_not_pass_low_volume_even_perfect_accuracy(self):
  x={'selected':10,'30s_win_count':10,'daily_passes':2,'daily_total':2,'weekly_passes':2,'weekly_total':2,'profit_net':1.}
  self.assertFalse(acceptance('coinexx','01',x)['APPROVED'])
 def test_gate_passes_only_full_contract(self):
  x={'selected':23783,'30s_win_count':19027,'daily_passes':10,'daily_total':10,'weekly_passes':4,'weekly_total':4,'profit_net':2.}
  self.assertTrue(acceptance('coinexx','01',x)['APPROVED'])
 def test_all_chronological_policies_rejected(self):
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    r=json.loads((ROOT/'results'/f'{src}_{m}_chronological.json').read_text())
    self.assertFalse(any(c['meets80'] and c['positive_expectancy'] for c in r['NP_variants']))
 def test_heldout_score_not_80_pct(self):
  for src in ('coinexx','dukascopy'):
   for m in ('01','02','06','07'):
    r=json.loads((ROOT/'results'/f'{src}_{m}_heldout_volume_ranking.json').read_text())
    self.assertLess(r['score_rank_topK_survival_rate'],.8)
if __name__=='__main__': unittest.main()
