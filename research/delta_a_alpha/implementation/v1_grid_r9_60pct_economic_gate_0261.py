"""GRID0261: financial/scientific 60% R9 SYNTH target acceptance, OFFLINE.

R9 SYNTH sets performance goals; R9 OVERFIT is a retrospective teacher.
Dukascopy ticks are causal testing feed, NOT same as broker-account results.
NEVER certify a hindsight oracle, nonfunded events, source-quote USD/oz, or
unmapped UTC date as broker daily net/completed trade objectives.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil
from typing import Mapping,Optional

R9_MONTHLY_CASH=(41520.82,66213.65,75698.63,38353.96,29545.35,35348.30,22442.14)
R9_MONTHLY_TRADE=(27980,33523,40985,31758,28913,31801,24382)
R9_TOTAL_BROKER_NET_USD=309122.85
R9_TOTAL_COMPLETED=219342
CONSERVATIVE_FRACTION=.60

@dataclass(frozen=True)
class MonthlyGoal:
    month:str
    required_mt5_cash_usd:float
    required_completed_deals:int
    r9_original_net_usd:float
    r9_original_deals:int

def goals()->tuple[MonthlyGoal,...]:
    result=tuple(MonthlyGoal(f'2026-{i:02d}',round(v*CONSERVATIVE_FRACTION,2),
                  ceil(n*CONSERVATIVE_FRACTION),v,n)
                 for i,(v,n) in enumerate(zip(R9_MONTHLY_CASH,R9_MONTHLY_TRADE),1))
    assert sum(R9_MONTHLY_TRADE)==R9_TOTAL_COMPLETED
    assert abs(sum(R9_MONTHLY_CASH)-R9_TOTAL_BROKER_NET_USD)<.005
    return result

@dataclass(frozen=True)
class BrokerPeriod:
    month:str
    net_usd:float
    completed_deals:int
    all_corresponding_iso_weeks_positive:bool
    source:str='VERIFIED_MT5_REAL_TICK_ACCOUNT_CASH'

def assess_60pct_monthly(progress:Mapping[str,BrokerPeriod],*,
                         verified_mt5_to_utc_calendar:bool=False,
                         verified_broker_contract_fees_margin:bool=False,
                         hindsight_labels_present:bool=False)->dict:
    allowed=verified_mt5_to_utc_calendar and verified_broker_contract_fees_margin and not hindsight_labels_present
    missing=[];failed=[];matched=[]
    for target in goals():
        x=progress.get(target.month)
        if x is None:missing.append(target.month);continue
        if (x.source!='VERIFIED_MT5_REAL_TICK_ACCOUNT_CASH' or x.completed_deals<0
                or x.net_usd!=x.net_usd):
            failed.append(target.month);continue
        matched.append(x)
        if not (x.net_usd>0 and x.net_usd+1e-9>=target.required_mt5_cash_usd
                and x.completed_deals>=target.required_completed_deals
                and x.all_corresponding_iso_weeks_positive):
            failed.append(target.month)
    # No partial 7-month promotion, even if a single candidate month looks good.
    passed=allowed and not missing and not failed and len(matched)==7
    return {'r9_synth_target_fraction':CONSERVATIVE_FRACTION,
            'r9_synth_60pct_cash_goal_usd':round(R9_TOTAL_BROKER_NET_USD*.60,2),
            'r9_synth_60pct_complete_deal_goal':ceil(R9_TOTAL_COMPLETED*.60),
            'science_promotion_accepted':bool(passed),'clock_contract_and_replay_verified':bool(allowed),
            'missing_months':missing,'unqualified_months':failed,
            'original_r9_synth_cleared_by_causal_BIDASK_broker_cash':bool(passed)}

def oracle_density_is_evidence_only(monthly_oracle_counts:Mapping[str,int],*,slots:int,
                                    completion_and_broker_cash_verified:bool=False)->dict:
    if slots<=0:raise ValueError('finite slot cap required')
    m=goals();missing=[g.month for g in m if g.month not in monthly_oracle_counts]
    enough=not missing and all(monthly_oracle_counts[g.month]>=g.required_completed_deals for g in m)
    return {'slots':slots,'retrospective_eligibility_can_supply_count_in_each_month':enough,
            'causally_executable_deal_count_certified':False,
            'cash_target_certified':False,
            'source':'FUTURE_BEST_EXIT_AND_DIRECTION_USED_AS_ORACLE_OFFLINE_ONLY',
            'cannot_be_promoted':True}
