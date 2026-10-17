"""R13 whole-EA performance grading. All source timestamps here are UTC.

R9 historical SYNTH remains server-local until independently verified.
Research reporting ONLY; no brokerage fills or investor certification.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone
from collections import defaultdict
from math import isfinite

@dataclass(frozen=True)
class AccountKey:
    broker: str
    starting_usd: int
    latency_ms: int
    source_sha256: str
    def __post_init__(self):
        if (self.broker not in ('coinexx','dukascopy') or
            self.starting_usd not in (100,200) or
            self.latency_ms not in (0,250,1000) or
            len(self.source_sha256)!=64):
            raise ValueError('invalid funded account or source SHA')

@dataclass(frozen=True)
class FilledTrade:
    entry_ms: int
    exit_ms: int
    net_usd: float
    def __post_init__(self):
        if self.entry_ms<0 or self.exit_ms<self.entry_ms or not isfinite(self.net_usd):
            raise ValueError('invalid deal chronology/P&L')

def period_ledger(trades):
    """Only realized, completed trades; never unfilled intent or future markout."""
    trades=sorted(trades,key=lambda x:(x.entry_ms,x.exit_ms))
    for i in range(1,len(trades)):
        if trades[i].entry_ms<trades[i-1].exit_ms:
            raise ValueError('single funded account cannot have overlapping positions')
    rows={p:defaultdict(list) for p in ('month','iso_week','day','hour')}
    for t in trades:
        d=datetime.fromtimestamp(t.entry_ms/1000,timezone.utc)
        iso=d.isocalendar()
        keys=(d.strftime('%Y-%m'),f'{iso.year}-W{iso.week:02}',
              d.strftime('%Y-%m-%d'),d.strftime('%Y-%m-%d %H:00'))
        for p,k in zip(rows,keys):rows[p][k].append(t.net_usd)
    result={}
    for p,buckets in rows.items():
        result[p]=[]
        for time,vals in sorted(buckets.items()):
            gain=sum(v for v in vals if v>0)
            loss=-sum(v for v in vals if v<0)
            result[p].append(dict(period_utc=time,trades=len(vals),
                net_usd=round(sum(vals),6),gross_profit=round(gain,6),
                gross_loss=round(loss,6),win_rate=sum(v>0 for v in vals)/len(vals),
                profit_factor=gain/loss if loss else (float('inf') if gain else 0)))
    return result

def system_grade(cases):
    """Grade all 12 distinct broker/capital/latency states; no capital summation."""
    cases=list(cases)
    target={(b,e,l) for b in ('coinexx','dukascopy') for e in (100,200)
           for l in (0,250,1000)}
    slots={}
    for key,metrics in cases:
        ident=(key.broker,key.starting_usd,key.latency_ms)
        if ident in slots:raise ValueError('duplicate funded account')
        slots[ident]=metrics
    complete=set(slots)==target
    zero_ruin=all(
        all(m.get(k,0)==0 for k in ('bankruptcies','stopouts','margin_calls'))
        for m in slots.values())
    active_profit=all(m.get('net_usd',0)>0 and m.get('trades',0)>0
                      for m in slots.values()) if complete else False
    return dict(populated=len(slots),complete_12slot=complete,
        zero_modeled_ruin=zero_ruin,positive_net_all=active_profit,
        candidate_investor_pass=complete and zero_ruin and active_profit,
        other_gates_pending=True,  # no win/volume/DD/positive-hours inference
        r9_synthetic_not_real_broker_profit=True)

def r9_nominal_date_gap(new_trades:int,reference_trades:int):
    if new_trades<0 or reference_trades<=0:raise ValueError('invalid count')
    return dict(nominal_calendar_only=True,
                r9_server_utc_clock_not_verified=True,
                relative_trade_density=new_trades/reference_trades)
