import os,sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from entry_contract import candidate_legacy, candidate_v5, reconcile, candidate_quotes

def test_after_30sec_gap_v5_rewarm_legacy_retains():
 t=np.arange(0,600001,250,dtype=np.int64)
 t[t>=300000]+=30000
 b=np.full(len(t),100.,np.float64)
 a=b+.2
 orig=candidate_legacy(t,b,a)
 new=candidate_v5(t,b,a)
 assert len(orig)>len(new)
 assert np.array_equal(new,np.intersect1d(new,orig))
 # after the 30s drought, v5 rejects freshly observed data until a new 300s epoch
 gap_ix=int(np.flatnonzero(np.diff(t)>15000)[0]+1)
 assert gap_ix in orig and gap_ix not in new

def test_original_gap_equality_is_inclusive():
 t=np.array([0,300000,600000,900000],dtype=np.int64)
 b=np.full(len(t),100.);a=b+.2
 assert candidate_legacy(t,b,a).size==0
 # explicitly reconstructed v5 contract also resets for gaps this long
 assert candidate_v5(t,b,a).size==0

def test_intraslot_future_price_cannot_change_first_observed_quote_admission():
 t=np.array([0,300000,300001,300002,300250,300251],np.int64)
 b=np.full(len(t),100.)
 a=b+.2
 orig=candidate_legacy(t,b,a)
 a2=a.copy();a2[2]=1000.;a2[3]=1000.
 assert np.array_equal(orig,candidate_legacy(t,b,a2))

def test_reconcile_fails_closed_on_impossible_teacher_ordinal():
 t=np.array([0,300000,300250,300500],np.int64)
 b=np.full(len(t),100.);a=b+.2
 code=np.zeros((1,2),dtype=np.int8)
 val=np.zeros((1,2),dtype=np.float32)
 exitix=np.zeros((1,2),dtype=np.int64)
 with pytest.raises(ValueError,match='not source exact'):
  reconcile(t,b,a,np.array([3],dtype=np.int64),code,val,exitix)

def test_empty_input():
 z=np.array([],np.int64)
 assert candidate_quotes(z,z.astype(float),z.astype(float)).size==0
