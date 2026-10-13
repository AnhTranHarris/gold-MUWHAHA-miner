"""GRID0260: PRE-EXPENSIVE-BACKTEST gate for primary R9-like grid velocity.
The user prioritizes >=10% of R9 SYNTH DAILY trade volume as material step;
R9 OVERFIT is offline oracle, never runtime input. No broker fills or money
claims. Source events are UPPER BOUNDS, not completed positions.
Never compare daily source UTC and MT5 server day until clock mapping verified.
"""
from dataclasses import dataclass
from math import ceil

R9_SYNTH_COMPLETED_JAN_JUL=219_342
R9_SYNTH_BROKER_NET_USD_JAN_JUL=309_122.85
R9_SYNTH_MT5_TRADING_DAYS=149

@dataclass(frozen=True)
class SourceVelocityReport:
    source:str
    original_source_events:int
    inherited_completed_quote_research_tickets:int
    max_distinct_children_per_source_event:int
    max_possible_total_research_tickets:int
    min_paid_cycles_per_source_for_10pct:int
    min_paid_cycles_per_source_for_full_r9:int
    target_ten_pct_completed:int
    target_full_completed:int
    source_can_supply_ten_pct_upper_bound:bool
    daily_cash_comparison_authorized:bool=False
    broker_cash_achieved:bool=False


def ceiling_for_source(source:str,original_source_events:int,
                       *,inherited_completed_quote_research_tickets:int=0,
                       max_distinct_children_per_source_event:int=1,
                       verified_mt5_server_utc_clock:bool=False,
                       verified_broker_cash:bool=False)->SourceVelocityReport:
    if not source or original_source_events<0 or inherited_completed_quote_research_tickets<0:
        raise ValueError('source and nonnegative observed counts required')
    if max_distinct_children_per_source_event<0:
        raise ValueError('finite explicitly verified paid children bound required')
    target10=ceil(.10*R9_SYNTH_COMPLETED_JAN_JUL)
    event=original_source_events;inherited=inherited_completed_quote_research_tickets
    supply=inherited+event*max_distinct_children_per_source_event
    missing10=max(0,target10-inherited)
    missing100=max(0,R9_SYNTH_COMPLETED_JAN_JUL-inherited)
    req10=ceil(missing10/event) if event else (0 if missing10==0 else -1)
    req100=ceil(missing100/event) if event else (0 if missing100==0 else -1)
    # Daily R9 parity also requires an approved MT5-server timezone map and
    # broker-cash source; a statistical total count alone cannot authorize it.
    return SourceVelocityReport(source,event,inherited,max_distinct_children_per_source_event,
        supply,req10,req100,target10,R9_SYNTH_COMPLETED_JAN_JUL,
        supply>=target10,verified_mt5_server_utc_clock and verified_broker_cash,
        False)
