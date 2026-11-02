import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from path_config import artifact_stem
from raw_repaired_features import candidate_indices_250ms
from full_250ms_universe import replay_candidate_pairs

def test_domain_stem_is_source_agnostic():
    assert artifact_stem('coinexx','01','2026-01-06')=='coinexx_01_2026-01-06'
    assert artifact_stem('dukascopy','01','2026-01-06')=='dukascopy_01_2026-01-06'

def test_candidate_and_teacher_core_do_not_depend_on_source_name():
    t=np.arange(0,31000,250,dtype=np.int64);b=100-np.arange(len(t))*.002;a=b+.2;idx=candidate_indices_250ms(t,b,a,warmup_ms=0,max_spread=1.5)[:1]
    net,good,*_=replay_candidate_pairs(t,b,a,idx)
    assert idx.tolist()==[0] and np.isfinite(net).all() and net[0,1]>0 and net[0,0]<0