"""Safety/cost/priority tests for probabilistic price-path opportunity auction."""
from dataclasses import replace
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.engine import BrokerConfig
from htf_ticklab.path_auction import PathProposal,select_path

Q=Quote(1767312001000,100.,100.2,"coinexx")
C=BrokerConfig(name="coinexx",initial_balance=100.,commission_per_lot_side=3.5,
               adverse_slippage_price=.1,max_spread_price=1.)

def proposal(name="fast",prob=.8,samples=200):
    return PathProposal(name,Q.ms,"coinexx",1,.01,samples,prob,2.,.4,1.,2.5)

def test_profitable_path_beats_weaker_specialist_after_both_sided_costs():
    x=select_path(Q,[proposal("fast"),proposal("slow",.25)],C)
    assert x.selected.specialist=="fast"
    assert x.expected_net_usd>0
    assert "slow:negative_expected_net" in x.rejected

def test_uncalibrated_is_rejected_without_guessing_model_quality():
    x=select_path(Q,[proposal(samples=2)],C)
    assert x.selected is None
    assert "fast:uncalibrated" in x.rejected

def test_cross_broker_and_future_observations_not_usable():
    x=select_path(Q,[replace(proposal(),broker="dukascopy"),
                     replace(proposal("future"),observed_ms=Q.ms+5)],C)
    assert x.selected is None
    assert "fast:cross_broker" in x.rejected
    assert "future:stale_or_future" in x.rejected

def test_unaffordable_minimum_and_no_market_order_promise():
    tight=replace(C,initial_balance=.1)
    x=select_path(Q,[proposal()],tight)
    assert x.selected is None
    assert "fast:minimum_margin" in x.rejected
    assert x.expected_net_usd==0

def test_strict_quotes_and_predeclared_parameters():
    with pytest.raises(ValueError,match="broker account"):
        select_path(Q,[proposal()],replace(C,name="dukascopy"))
    with pytest.raises(ValueError,match="calibration"):
        select_path(Q,[proposal()],C,minimum_samples=0)
