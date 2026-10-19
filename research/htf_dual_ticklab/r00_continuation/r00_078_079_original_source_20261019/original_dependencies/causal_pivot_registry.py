"""DESIGN-ONLY fully-confirmed HTF pivots; uses externally built ORIGINAL completed bars.
Does not fetch data, change broker UTC, fill trades or claim realized accuracy.
"""
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class CompleteBar:
    start_utc_ms: int
    end_utc_ms: int
    high: float
    low: float
    close: float

@dataclass(frozen=True)
class ConfirmedPivot:
    kind: str
    pivot_bar_start_utc_ms: int
    level: float
    publicly_known_utc_ms: int


def confirm_pivots(completed_bars: Sequence[CompleteBar], left: int = 2, right: int = 2):
    """As-of confirmation uses right-side CLOSED bars only, publication on right close.

    Time gaps are never fabricated: caller must provide actual completed bar timeline.
    Consecutive bars required within each pivot window to avoid false pivots on gaps.
    """
    if left < 1 or right < 1:
        raise ValueError('swing left/right must be >=1')
    bars=list(completed_bars)
    for i,b in enumerate(bars):
        if not (b.start_utc_ms<b.end_utc_ms and b.low<=b.close<=b.high):
            raise ValueError('invalid actual completed bar')
        if i and bars[i-1].end_utc_ms>b.start_utc_ms:
            raise ValueError('overlapping/unsorted completed bars')
    pivots=[]
    for i in range(left,len(bars)-right):
        window=bars[i-left:i+right+1]
        if any(x.end_utc_ms!=y.start_utc_ms for x,y in zip(window,window[1:])):
            continue  # no interpolation across missing bars or closed-market gaps
        mid=bars[i]; other=window[:left]+window[left+1:]
        publish=bars[i+right].end_utc_ms
        if all(mid.high>z.high for z in other):
            pivots.append(ConfirmedPivot('HIGH',mid.start_utc_ms,mid.high,publish))
        if all(mid.low<z.low for z in other):
            pivots.append(ConfirmedPivot('LOW',mid.start_utc_ms,mid.low,publish))
    pivots.sort(key=lambda x:(x.publicly_known_utc_ms,x.pivot_bar_start_utc_ms,x.kind))
    return pivots


def available_pivots(pivots,decision_utc_ms:int):
    return [p for p in pivots if p.publicly_known_utc_ms<=decision_utc_ms]
