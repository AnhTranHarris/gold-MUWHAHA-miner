"""Direct compatibility against original preserved H1V2 research code.

These are synthetic deterministic fixtures only. They do not replace full-month
raw-byte SHA verification and full historical oracle parity in R11 runner.
"""
import numpy as np
from h1v2_teacher import candidate_250ms,schedule_oracle
from r11_entry_admission import candidate_mask,H1V2_ORIGINAL
from r11_future_frontier import optimize,FrontierConfig

def test_R11_H1V2_candidate_generation_matches_original_executable():
    t=np.r_[np.arange(0,310000,5000,dtype=np.int64),330001,330001,630010,930020]
    b=np.ones(len(t),np.float64)*100
    a=b+.2;a[-2]=102
    want=candidate_250ms(t,b,a,max_spread=1.50,warmup_ms=300000,gap_reset_ms=300000)
    got=np.flatnonzero(candidate_mask(t,b,a,H1V2_ORIGINAL))
    np.testing.assert_array_equal(got,want)

def test_R11_count_objective_matches_original_hindsight_DP_on_strict_fixture():
    entries=np.array([0,2,4,8,12],np.int64)
    code=np.array([[1,0],[1,0],[1,0],[0,1],[1,0]],np.int8)
    net=np.array([[.9,np.nan],[.2,np.nan],[.2,np.nan],[np.nan,.3],[.4,np.nan]],np.float32)
    exit_idx=np.array([[4,-1],[3,-1],[5,-1],[-1,10],[15,-1]],np.int64)
    first_ms=np.where(code==1,1500,-1).astype(np.int64)
    exit_ms=np.where(code==1,2000,-1).astype(np.int64)
    original_rows,original_side,orig=schedule_oracle(entries,code,net,exit_idx)
    new_rows,new_side,new=optimize(entries,code,net,exit_idx,first_ms,exit_ms,
                                config=FrontierConfig(objective="count"))
    np.testing.assert_array_equal(new_rows,original_rows)
    np.testing.assert_array_equal(new_side,original_side)
    assert new["trades"]==orig["trades"]
    assert abs(new["original_research_net"]-orig["sum_net"])<1e-3
