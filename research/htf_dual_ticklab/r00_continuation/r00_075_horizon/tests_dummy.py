from pathlib import Path
import numpy as np

def test_exact_registered_native_30s_outcome_archive():
 root=Path(__file__).resolve().parents[1]
 p=root/'r00_075_horizon/results/OUTCOME_INDEX_coinexx_02_h30.npz'
 with np.load(p) as z:
  assert len(z['quote_index'])==len(z['future_quote_index'])==len(z['correct'])
  assert (z['future_quote_index'][z['known']]>=z['quote_index'][z['known']]).all()
