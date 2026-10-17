"""Research budget correctness, not a profitability claim."""
import pytest
from htf_ticklab.entry_survival_budget import ResearchBudget, SurvivalBudget

def maker():
    return SurvivalBudget(ResearchBudget(.025,.35,.10,.30))

def test_minimum_lot_risk_can_be_infeasible_on_100_and_feasible_on_200():
    a=maker()
    assert not a.review_entry(1_700_000_000_000,100.,3.,12.).allowed
    b=maker()
    assert b.review_entry(1_700_000_000_000,200.,3.,12.).allowed

def test_margin_is_separate_from_stop_risk():
    a=maker()
    d=a.review_entry(1_700_000_000_000,100.,1.,40.)
    assert not d.allowed and d.reason=="margin_budget"

def test_daily_latch_and_next_day_reset():
    a=maker();t=1_700_000_000_000
    assert a.review_entry(t,100.,1.,5.).allowed
    assert a.review_entry(t+1_000,89.,1.,5.).reason=="daily_loss_pause"
    assert a.review_entry(t+2_000,105.,1.,5.).reason=="daily_loss_pause"
    assert a.review_entry((t//86_400_000+1)*86_400_000+1,105.,1.,5.).allowed

def test_peak_drawdown_is_sticky_across_day():
    a=maker();t=1_700_000_000_000
    assert a.review_entry(t,100.,1.,5.).allowed
    assert a.review_entry(t+1_000,69.,1.,5.).reason=="peak_drawdown_latch"
    assert a.review_entry((t//86_400_000+2)*86_400_000,100.,1.,5.).reason=="peak_drawdown_latch"

def test_out_of_order_rejected():
    a=maker();t=1_700_000_000_000
    a.review_entry(t,100.,1.,5.)
    with pytest.raises(ValueError,match="noncausal"):
        a.review_entry(t-1,100.,1.,5.)

def test_invalid_research_cap_not_silently_approved():
    with pytest.raises(ValueError):
        ResearchBudget(0,.35,.1,.3)
