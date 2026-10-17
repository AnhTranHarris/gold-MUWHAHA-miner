"""Regression tests for online specialist research evidence with no look-ahead."""
import pytest
from htf_ticklab.matured_opportunity import ClosedOutcome, MaturedOpportunityBook

def example(specialist="A",net=1.,maturity=2100,shadow=True):
    return ClosedOutcome("coinexx",specialist,1000,maturity,net,shadow)

def test_future_first_hit_cannot_raise_current_specialist_score():
    book=MaturedOpportunityBook("coinexx")
    for j in range(35):
        book.enqueue(ClosedOutcome("coinexx","A",1000,2100+j,
                                   5. if j%2 else -1.,True))
    assert book.advance(2099)==0
    assert book.score("A",minimum=2) is None
    assert book.advance(2140)==35
    score=book.score("A",minimum=30)
    assert score.observations==35
    assert score.shadow_observations==35
    assert score.conservative_net_usd < score.mean_net_usd

def test_cross_broker_shadow_leak_prohibited():
    book=MaturedOpportunityBook("coinexx")
    with pytest.raises(ValueError,match="cross-broker"):
        book.enqueue(ClosedOutcome("dukascopy","A",1,2,100.,True))

def test_observation_backfill_after_clock_advance_fails_closed():
    book=MaturedOpportunityBook("coinexx")
    book.advance(2000)
    with pytest.raises(ValueError,match="backfill"):
        book.enqueue(example())

def test_equal_maturity_deterministic_and_bounded():
    book=MaturedOpportunityBook("coinexx",observations_per_specialist=3)
    for k in range(6):
        book.enqueue(ClosedOutcome("coinexx","A",1000,2000,float(k),False))
    book.advance(2000)
    value=book.score("A",minimum=2,uncertainty_z=0)
    assert value.observations==3
    assert value.mean_net_usd==pytest.approx(4.)
    assert value.shadow_observations==0

def test_replay_time_cannot_reverse_and_invalid_proposal_rejected():
    book=MaturedOpportunityBook("coinexx")
    book.advance(2000)
    with pytest.raises(ValueError,match="out-of-order"):
        book.advance(1999)
    with pytest.raises(ValueError,match="chronology"):
        ClosedOutcome("coinexx","A",3000,2900,1.)

def test_unobserved_specialist_never_gets_invented_positive_score():
    book=MaturedOpportunityBook("coinexx")
    book.advance(10_000)
    assert book.ranked()==[]
