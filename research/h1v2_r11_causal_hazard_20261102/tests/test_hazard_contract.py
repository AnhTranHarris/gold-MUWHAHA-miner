import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from hazard_contract import first_passage_risk_sets,finite_outcome_group_stats

def test_competing_favorable_and_adverse_with_distinct_exposures():
 c=np.array([[1,-1],[0,1]],np.int8)
 first=np.array([[249,250],[ -1,1000]],np.int32)
 exitms=np.array([[500,600],[100,2000]],np.int32)
 end=np.array([[4,4],[2,4]],np.int64)
 net=np.array([[.3,-.7],[.01,.3]])
 z=first_passage_risk_sets(c,first,exitms,end,net)
 assert z['event'][0,0,0]==1
 assert z['event'][0,1,0]==-1
 assert z['event'][1,1,1]==1
 assert z['exposure'][0,0,0]==249/250
 assert z['exposure'][0,1,0]==1
 assert z['strict_correct'][0,0] and not z['strict_correct'][0,1]

def test_missing_terminal_exit_stays_censored():
 z=first_passage_risk_sets(np.array([[0,0]],np.int8),
                          np.array([[-1,-1]],np.int32),
                          np.array([[-1,-1]],np.int32),
                          np.array([[-1,-1]],np.int64),
                          np.array([[np.nan,np.nan]]))
 assert z['source_end_censored'].all()
 assert not z['strict_correct'].any()
 assert not z['exposure'].any()

def test_nan_cohort_payoff_must_not_poison_completed_mean():
 z=finite_outcome_group_stats(np.array([0,0,0,1]),np.array([.2,.4,np.nan,-.1]),
                              np.array([1,1,0,-1]),np.array([3,4,-1,5]),min_support=2)
 assert z['completed'][0]==2 and z['censored'][0]==1
 assert np.isclose(z['net_mean'][0],.3)
 assert not z['economic_eligible'][0]

def test_strict_cause_time_contradiction_fails_closed():
 with pytest.raises(ValueError):
  first_passage_risk_sets(np.array([[1,0]],np.int8),np.array([[-1,-1]],np.int32),
                          np.array([[500,500]],np.int32),np.array([[5,5]],np.int64),
                          np.array([[.5,-.5]]))
