"""Investor gate must fail closed for 12-case, whole-system promotion."""
from dataclasses import replace
from htf_ticklab.investor_gate_r16 import FullAccountScore,investor_gate
def cases():
    return [FullAccountScore(
        broker=b,capital=c,latency_ms=l,net=100.,gross_loss=50.,
        marked_max_drawdown=10.,min_equity=80.,stopouts=0,
        completed_trades=1000,active_days=1,
        positive_eligible_hours=7,eligible_hours=10,
        nonpositive_days=0,nonpositive_weeks=0,nonpositive_months=0,
        profit_factor=3.,complete_months=1)
        for b in ('coinexx','dukascopy') for c in (100.,200.)
        for l in (0,250,1000)]
def test_accepts_only_complete_twelve_slot_profitable_and_active_system():
    assert investor_gate(cases())['qualified']
def test_rejects_one_nonprofitable_broker_case():
    rows=cases();rows[3]=replace(rows[3],net=-1.,profit_factor=.8)
    got=investor_gate(rows)
    assert not got['qualified']
    assert any('no_positive_aftercost_net' in x for x in got['reasons'])
def test_rejects_no_trade_incomplete_month_and_phantom_hourly_success():
    rows=cases()
    rows[0]=replace(rows[0],completed_trades=0,
                    eligible_hours=0,positive_eligible_hours=0,
                    complete_months=0)
    got=investor_gate(rows)
    assert not got['qualified']
    assert any('frequency_below_aspiration' in x for x in got['reasons'])
    assert any('no_complete_month' in x for x in got['reasons'])
def test_rejects_missing_scenario_and_hidden_stopout():
    got=investor_gate(cases()[:-1])
    assert not got['qualified']
    assert got['reasons'][0]=='missing_or_duplicate_twelve_scenario_slices'
    rows=cases();rows[0]=replace(rows[0],stopouts=1)
    assert not investor_gate(rows)['qualified']
