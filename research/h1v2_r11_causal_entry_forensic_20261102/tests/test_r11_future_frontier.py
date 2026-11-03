import numpy as np
import pytest
from r11_future_frontier import optimize,FrontierConfig

def _toy():
    ix=np.array([0,2,4],dtype=np.int64)
    code=np.array([[1,0],[1,0],[1,0]],dtype=np.int8)
    pnl=np.array([[.9,np.nan],[.2,np.nan],[.2,np.nan]],dtype=np.float64)
    end=np.array([[4,-1],[3,-1],[5,-1]],np.int64)
    first=np.array([[1000,-1],[1000,-1],[1000,-1]],np.int64)
    elapsed=np.array([[20000,-1],[1000,-1],[1000,-1]],np.int64)
    return ix,code,pnl,end,first,elapsed

def test_count_maximizes_nonoverlap_not_individual_profit():
    row,side,r=optimize(*_toy())
    assert row.tolist()==[1,2] and side.tolist()==[1,1]
    assert r["trades"]==2 and abs(r["original_research_net"]-.4)<1e-9

def test_net_objective_is_distinct_from_max_count():
    row,side,r=optimize(*_toy(),config=FrontierConfig(objective="net"))
    assert row.tolist()==[0] and abs(r["repriced_net"]-.9)<1e-9

def test_occupancy_cost_makes_slow_hindsight_trade_less_attractive():
    cfg=FrontierConfig(objective="occupancy",occupation_penalty_per_ms=.00003)
    rows,side,rec=optimize(*_toy(),config=cfg)
    assert rows.tolist()==[1,2]
    assert rec["occupancy_adjusted_objective"]>0

def test_incremental_fees_and_original_eligibility_are_separate():
    ix,code,pnl,end,first,elapsed=_toy()
    rows,side,rec=optimize(ix,code,pnl,end,first,elapsed,
        eligible=np.array([True,False,True]),
        config=FrontierConfig(objective="count",incremental_cost=.1))
    assert rows.tolist()==[0] and rec["strict_good_eligible_action_count"]==2
    assert abs(rec["repriced_net"]-.8)<1e-9

def test_fail_closed_unknown_or_censored_outcomes():
    ix,code,pnl,end,first,elapsed=_toy()
    code[:]=0;end[:]=-1;pnl[:]=np.nan
    rows,side,r=optimize(ix,code,pnl,end,first,elapsed)
    assert len(rows)==0 and r["trades"]==0

def test_wrong_eligibility_shape_fails_closed():
    with pytest.raises(ValueError):
        optimize(*_toy(),eligible=np.array([True]))
