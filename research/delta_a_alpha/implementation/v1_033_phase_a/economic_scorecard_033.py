"""Evaluation-only UTC scorecards for endogenous funded closes.

Calendar partitions are deliberately forbidden as live V1 execution signals;
this module is invoked AFTER replay to audit performance by hour/day/week/month/year.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean
from v1_funded_core_033 import Close


def _keys(c: Close) -> dict[str,str]:
    z = datetime.fromtimestamp(c.time_ms/1000,timezone.utc)
    iy,iw,_ = z.isocalendar()
    return dict(hour=z.strftime('%Y-%m-%dT%H:00Z'), day=z.strftime('%Y-%m-%d'),
                week=f'{iy}-W{iw:02d}', month=z.strftime('%Y-%m'), year=z.strftime('%Y'))


def _metrics(rows: list[Close]) -> dict:
    gp=sum(max(x.net_usd,0) for x in rows)
    gl=sum(min(x.net_usd,0) for x in rows)
    count=len(rows)
    return dict(trades=count, wins=sum(x.net_usd>0 for x in rows),
                net=round(gp+gl,6), gross_profit=round(gp,6),
                gross_loss=round(gl,6),profit_factor=round(gp/-gl,6) if gl<0 else None,
                expectancy=round((gp+gl)/count,6) if count else None,
                average_hold_seconds=round(mean(x.held_ms for x in rows)/1000,3) if rows else None)


def reporting_only_scorecards(rows: list[Close]) -> dict:
    out={'trade':_metrics(rows)}
    for period in ('hour','day','week','month','year'):
        groups=defaultdict(list)
        for c in rows:
            groups[_keys(c)[period]].append(c)
        out[period]={k:_metrics(v) for k,v in sorted(groups.items())}
    return out