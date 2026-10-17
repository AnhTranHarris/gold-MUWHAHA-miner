"""R16 admission gate for WHOLE-EA, complete-month investor scorecard.

Refuses candidate promotion when any broker/account/latency scenario fails.
Never calls a lowest-loss or inactive system 'best'. Dollar-risk caps remain
TBD unless investor explicitly approves; only mandated feasibility is checked.
"""
from dataclasses import dataclass
from math import isfinite
@dataclass(frozen=True)
class FullAccountScore:
    broker:str
    capital:float
    latency_ms:int
    net:float
    gross_loss:float
    marked_max_drawdown:float
    min_equity:float
    stopouts:int
    completed_trades:int
    active_days:int
    positive_eligible_hours:int
    eligible_hours:int
    nonpositive_days:int
    nonpositive_weeks:int
    nonpositive_months:int
    profit_factor:float
    complete_months:int

def investor_gate(rows, min_trades_per_active_day=710):
    """Return explicit failures. Empty periods, missing broker/capital/latency
    or incomplete months cannot be silently called a success."""
    required={(b,c,l) for b in ('coinexx','dukascopy')
        for c in (100.,200.) for l in (0,250,1000)}
    rows=list(rows)
    actual={(r.broker,r.capital,r.latency_ms) for r in rows}
    reasons=[]
    if actual!=required or len(rows)!=12:
        reasons.append('missing_or_duplicate_twelve_scenario_slices')
    for r in rows:
        key=f'{r.broker}:{r.capital}:{r.latency_ms}'
        if r.complete_months<1:reasons.append(key+':no_complete_month')
        if r.min_equity<=0 or r.stopouts>0:
            reasons.append(key+':survival_breach')
        if not isfinite(r.net) or r.net<=0:
            reasons.append(key+':no_positive_aftercost_net')
        if not isfinite(r.profit_factor) or r.profit_factor<=1:
            reasons.append(key+':no_positive_profit_factor')
        if r.completed_trades<min_trades_per_active_day*r.active_days or r.active_days<1:
            reasons.append(key+':frequency_below_aspiration')
        if r.eligible_hours<1 or r.positive_eligible_hours/r.eligible_hours<.60:
            reasons.append(key+':positive_hour_below_mandate')
        if (r.nonpositive_days>0 or r.nonpositive_weeks>0 or
                r.nonpositive_months>0):
            reasons.append(key+':nonpositive_reporting_period')
    return {'qualified':not reasons,
            'reasons':tuple(reasons),
            'eligible_to_call_best':not reasons}
