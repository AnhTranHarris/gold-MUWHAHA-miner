"""Causal micro-campaign state and broker isolation tests."""
import pytest
from htf_ticklab.feeds import Quote
from htf_ticklab.bars import Bar
from htf_ticklab.signal_bus import AccountView
from htf_ticklab.event_campaign_r09 import EventCampaignSource,CampaignParameters

def q(ms,px,broker="coinexx"):
    return Quote(ms,px,px+.2,broker)

def view(ms,broker="coinexx",side=0,pending=False):
    return AccountView(broker,ms,100.,100.,side,pending,0.)

def bar(ms,impulse=.5):
    return Bar(5,ms-5000,ms,
               100.,100.6,99.9,100.+impulse,
               100.2,100.8,100.1,100.2+impulse,20)

def test_arm_retrace_reaccelerate_only_later_tick():
    s=EventCampaignSource()
    start=100000
    s.on_bar(bar(start),q(start,100.5),view(start))
    assert s.events["armed"]==1
    assert s.on_tick(q(start,100.5),view(start))==()
    assert s.on_tick(q(start+100,100.25),view(start+100))==()
    assert s.events["pullbacks"]==1
    intents=s.on_tick(q(start+200,100.38),view(start+200))
    assert len(intents)==1 and intents[0].side==1
    assert intents[0].observed_ms==start+200
    assert s.on_tick(q(start+201,100.40),view(start+201))==()

def test_expiration_does_not_count_a_trade():
    s=EventCampaignSource(CampaignParameters(max_arm_ms=1000))
    start=100000
    s.on_bar(bar(start),q(start,100.5),view(start))
    assert s.on_tick(q(start+1001,100.3),view(start+1001))==()
    assert s.events["expired"]==1
    assert s.events["reaccelerations"]==0

def test_bar_from_future_fails():
    s=EventCampaignSource()
    with pytest.raises(ValueError,match="future"):
        s.on_bar(bar(100000),q(99999,100.5),view(99999))

def test_cross_broker_contamination_cannot_occur():
    s=EventCampaignSource()
    s.on_bar(bar(100000),q(100000,100.5),view(100000))
    with pytest.raises(ValueError,match="cross-broker"):
        s.on_tick(q(100100,100.3,"dukascopy"),view(100100,"dukascopy"))

def test_capital_occupancy_preempts_campaign():
    s=EventCampaignSource()
    s.on_bar(bar(100000),q(100000,100.5),view(100000))
    assert s.on_tick(q(100100,100.25),view(100100,pending=True))==()
    assert s.phase=="IDLE"

def test_invalid_parameter_geometries_rejected():
    with pytest.raises(ValueError,match="invalid"):
        CampaignParameters(fib_retracement=1.5)
    with pytest.raises(ValueError,match="invalid"):
        CampaignParameters(lots=0.)
