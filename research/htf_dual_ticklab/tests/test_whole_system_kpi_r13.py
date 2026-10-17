"""R13 system-level investor-period gating, never isolated indicator accuracy."""
from datetime import datetime,timezone
import pytest
from htf_ticklab.whole_system_kpi_r13 import (
    AccountKey,FilledTrade,period_ledger,system_grade,r9_nominal_date_gap)

def ms(y,m,d,h=0):
    return int(datetime(y,m,d,h,tzinfo=timezone.utc).timestamp()*1000)

def test_utc_four_time_horizons_and_finished_trades_only():
    items=[FilledTrade(ms(2026,3,3,9),ms(2026,3,3,9)+3000,1.2),
           FilledTrade(ms(2026,3,3,10),ms(2026,3,3,10)+1000,-.4)]
    x=period_ledger(items)
    assert len(x['month'])==len(x['iso_week'])==len(x['day'])==1
    assert len(x['hour'])==2
    assert x['day'][0]['trades']==2
    assert x['day'][0]['net_usd']==pytest.approx(.8)

def test_full_twelve_scenarios_no_independent_capital_sum():
    src='a'*64
    pairs=[(AccountKey(b,c,l,src),{'net_usd':10.,'trades':50,
                                   'stopouts':0,'margin_calls':0,'bankruptcies':0})
           for b in ('coinexx','dukascopy') for c in (100,200)
           for l in (0,250,1000)]
    a=system_grade(pairs)
    assert a['complete_12slot'] and a['candidate_investor_pass']
    assert a['other_gates_pending']
    assert not system_grade(pairs[:-1])['complete_12slot']
    pairs[2][1]['bankruptcies']=1
    assert not system_grade(pairs)['candidate_investor_pass']
    with pytest.raises(ValueError,match='duplicate'):
        system_grade(pairs+[pairs[0]])

def test_no_overlapping_funded_trades():
    with pytest.raises(ValueError,match='overlapping'):
        period_ledger([FilledTrade(100,400,1),FilledTrade(300,450,-1)])

def test_r9_server_hours_cannot_be_laundered_into_utc():
    x=r9_nominal_date_gap(100,1000)
    assert x['nominal_calendar_only']
    assert x['r9_server_utc_clock_not_verified']
    assert x['relative_trade_density']==pytest.approx(.10)
