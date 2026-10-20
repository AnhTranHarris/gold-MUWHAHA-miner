#!/usr/bin/env python3
"""Regression and causal prefix tests for research-only R00-054 FILTER09."""
import json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from run_filter09 import episodic,make_lifecycles,calc_thresholds,data

def test_lifecycle_prefix():
 t,s,y,X,_=data('coinexx','02');th=json.loads((R/'JAN_ONLY_EPISODE_THRESHOLDS_coinexx.json').read_text())
 n=4000
 life,flags=make_lifecycles(t[:n],X[:n],th)
 shorter,short_flags=make_lifecycles(t[:(n//2)],X[:(n//2)],th)
 assert np.array_equal(flags[:n//2],short_flags)
 assert np.allclose(life[:n//2],shorter,rtol=0,atol=0)
 for st in range(5):
  assert np.all((flags[:,st]==0)|(flags[:,st]==1))
 return int(n)

def test_outcome_maturity():
 t,s,y,X,_=data('coinexx','02');n=3000;t=t[:n];labels=(y[:n]==0).astype('int8')
 index=500;delta_ms=32001
 lo=np.searchsorted(t,t-120000,side='left');eligible=np.searchsorted(t,t-delta_ms,side='right')
 def pastscores(yy):
  cs=np.r_[0,np.cumsum(yy,dtype=np.int64)];den=eligible-lo
  return np.where(den>=3,(cs[eligible]-cs[lo]+2)/(den+4),.5)
 baseline=pastscores(labels);fake=labels.copy();fake[index]=1-fake[index];after=pastscores(fake)
 assert np.array_equal(baseline[t<t[index]+delta_ms],after[t<t[index]+delta_ms])
 assert np.any(baseline!=after)
 return int(index)

def test_archived_predictions_reproducible():
 for b in ['coinexx','dukascopy']:
  frozen=json.loads((R/f'FEB_FROZEN_POLICY_{b}.json').read_text())
  for m in ['06','07']:
   with np.load(R/f'FROZEN_DECISIONS_{b}_{m}.npz') as x:
    truth=x['label'];keep=x['keep'].astype(bool);r=x['risk'];flag=np.column_stack([x[f'{n}_state'] for n in 'NOSRM'])
    selected=frozen['selected'];expected=~((r>selected['threshold'])&(flag.sum(axis=1)>=2))
    assert np.array_equal(keep,expected),f'{b}-{m}: archived mask mismatch'
   receipt=json.loads((R/f'TRANSFER_{b}_{m}.json').read_text())
   assert int((truth[keep]==0).sum())==receipt['correct']
 return True
if __name__=='__main__':
 print('PREFIX_TEST',test_lifecycle_prefix())
 print('MATURED_FEEDBACK',test_outcome_maturity())
 print('ARCHIVE_DECISION_MATCH',test_archived_predictions_reproducible())
 print('ALL_FILTER09_TESTS_PASS')
