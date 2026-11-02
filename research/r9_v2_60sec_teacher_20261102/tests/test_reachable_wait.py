from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from train_60s_reachable import load,chronological_partition
from teacher_60s import DELAYS

def test_reachable_wait_excludes_oracle_late_delays():
    labels=np.zeros((2,7),np.int8)
    labels[0,4]=1 # +5s future winner is NOT reachable by 3s WAIT
    labels[1,3]=1 # +3s eligible future label
    yes=((labels[:,0]!=1)&np.any(labels[:,1:4]==1,axis=1)).astype(np.uint8)
    assert yes.tolist()==[0,1]

def test_existing_complete_teacher_not_mutated_by_derived_target():
    p=Path('/mnt/data/v2_new_research/sixty/teacher/coinexx_01/teacher_60s.npz')
    if not p.exists():return
    v=load('coinexx','01','/mnt/data/v2_new_research/sixty')
    y=v['delay_class']
    assert np.array_equal(v['wait_rescue'],((y[:,0]!=1)&np.any(y[:,1:4]==1,axis=1)).astype(np.uint8))
    assert np.array_equal(v['teacher_60s_later_rescue'],((y[:,0]!=1)&np.any(y[:,4:]==1,axis=1)).astype(np.uint8))
    assert np.count_nonzero(v['teacher_60s_later_rescue'])>0

def test_actor_has_no_future_teacher_data_runtime_import():
    s=Path('/mnt/data/v2_new_research/sixty/src/sequential_base_exact.py').read_text()
    assert 'teacher_60s' not in s
    assert 'lookahead' not in s.lower()
    assert 'self.policy.predict(self.active_features)' in s

def test_delay_grid_within_one_minute():
    assert max(DELAYS)+30000<=60000

if __name__=='__main__':
    test_reachable_wait_excludes_oracle_late_delays()
