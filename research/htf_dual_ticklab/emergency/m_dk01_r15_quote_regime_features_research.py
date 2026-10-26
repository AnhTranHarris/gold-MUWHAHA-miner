"""M-DK-01 research-only, strict-as-of-t0 feature adjunct to existing R12 guard.

NO fitted model, production veto, original tick replay, profitability or market-data claim.
Input quote ordinals MUST be original source ordinals; never infer an index from ms.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from math import log1p, sin, cos, pi, isfinite
from typing import Sequence

@dataclass(frozen=True)
class Quote:
    time_msc: int
    ordinal: int
    bid: float
    ask: float

@dataclass(frozen=True)
class CompletedBar:
    period_sec: int
    published_msc: int
    open: float
    high: float
    low: float
    close: float

@dataclass(frozen=True)
class MaturedEvent:
    label_available_msc: int
    side: int
    label: int  # 0=correct; 1=opposite; 2=neutral/missing

class MissingAsOfQuote(ValueError):
    """Do not veto when original t0 quote ordinal cannot be reconciled."""

def source_native_dk01_features(
    *, broker: str, event_msc: int, original_quote_ordinal: int,
    original_side: int, quotes: Sequence[Quote],
    completed_bars: Sequence[CompletedBar], matured_events: Sequence[MaturedEvent]
) -> dict[str, float]:
    """Deterministic, source-as-of-t0 DK01 hypothesis vector; no label leakage.

    Quote records are expected to be ordered by (time_msc, original native ordinal).
    Same-ms quote ordinals after the selected original event are excluded.
    Exact t0 quote must be present; otherwise fail closed.
    """
    if broker != 'dukascopy':
        raise ValueError('M-DK-01 source specialist is broker-isolated')
    if original_side not in (-1, 1):
        raise ValueError('original BUY/SELL sign must remain unchanged')
    if not quotes:
        raise MissingAsOfQuote('quote history absent')
    if any((q.bid<=0 or q.ask<=0 or q.ask<q.bid or not isfinite(q.ask+q.bid)) for q in quotes):
        raise ValueError('invalid native bid/ask quote: do not impute')
    if any((a.time_msc,a.ordinal)>=(b.time_msc,b.ordinal) for a,b in zip(quotes,quotes[1:])):
        raise ValueError('source quotes not strictly native-ordered')
    anchor = (event_msc,original_quote_ordinal)
    prefix = [q for q in quotes if (q.time_msc,q.ordinal)<=anchor]
    if not prefix or (prefix[-1].time_msc,prefix[-1].ordinal)!=anchor:
        raise MissingAsOfQuote('original source t0/ordinal mismatch')
    now=prefix[-1]
    mid=lambda q:(q.bid+q.ask)/2
    features:dict[str,float]={}
    side=original_side
    features['source_bid_ask_spread']=now.ask-now.bid
    features['original_side']=float(side)
    dt=datetime.fromtimestamp(event_msc/1000,timezone.utc)
    utc_hour=dt.hour + dt.minute/60 + dt.second/3600
    features['utc_hour_sin']=sin(2*pi*utc_hour/24)
    features['utc_hour_cos']=cos(2*pi*utc_hour/24)
    for window_ms in (1000,5000,15000,30000,60000,300000,900000,3600000):
        k=f'w{window_ms}ms'
        prior=[q for q in prefix if q.time_msc >= event_msc-window_ms]
        if not prior:
            prior=[now]
        fst=prior[0]
        db=now.bid-fst.bid; da=now.ask-fst.ask
        signed=side*(db+da)/2
        changes=[(b.bid-a.bid,b.ask-a.ask) for a,b in zip(prior,prior[1:])]
        n=len(changes)
        signed_revisions=sum(side*(x+y)/2 for x,y in changes)
        adverse_revisions=sum(1 for x,y in changes if side*(x+y)<0)
        favorable_revisions=sum(1 for x,y in changes if side*(x+y)>0)
        one_sided=sum(1 for x,y in changes if (x==0)!=(y==0))
        bid_only=sum(1 for x,y in changes if x!=0 and y==0)
        ask_only=sum(1 for x,y in changes if y!=0 and x==0)
        features[f'{k}_side_mid_delta']=signed
        features[f'{k}_side_bid_delta']=side*db
        features[f'{k}_side_ask_delta']=side*da
        features[f'{k}_spread_delta']=(now.ask-now.bid)-(fst.ask-fst.bid)
        features[f'{k}_revisions_per_sec']=n/(window_ms/1000)
        features[f'{k}_side_revision_sum']=signed_revisions
        features[f'{k}_adverse_revision_share']=adverse_revisions/max(1,n)
        features[f'{k}_favorable_revision_share']=favorable_revisions/max(1,n)
        features[f'{k}_bid_only_share']=bid_only/max(1,n)
        features[f'{k}_ask_only_share']=ask_only/max(1,n)
        features[f'{k}_one_sided_share']=one_sided/max(1,n)
        features[f'{k}_efficiency']=abs(signed)/max(1.e-6,sum(abs((x+y)/2) for x,y in changes))
    for period_sec in (60,300,900,3600):
        # Only the last bar *published at or before* event time is eligible.
        bs=[b for b in completed_bars if b.period_sec==period_sec and b.published_msc<=event_msc]
        name=f'completed_{period_sec}s'
        if bs:
            b=max(bs,key=lambda a:a.published_msc)
            if b.high < b.low or b.high < max(b.open,b.close) or b.low>min(b.open,b.close):
                raise ValueError('invalid published HTF bar')
            width=max(1.e-6,b.high-b.low)
            features[name+'_side_body']=side*(b.close-b.open)/width
            features[name+'_side_close_position']=side*(2*(b.close-b.low)/width-1)
            features[name+'_publication_age_s']=(event_msc-b.published_msc)/1000
            features[name+'_available']=1.
        else:
            features[name+'_side_body']=0.
            features[name+'_side_close_position']=0.
            features[name+'_publication_age_s']=-1.
            features[name+'_available']=0.
    for span_ms in (120000,600000,3600000):
        # Event label_available_msc must represent full +30..32s window and +33.001s guard.
        ss=[e for e in matured_events if e.label_available_msc<=event_msc
            and e.label_available_msc>event_msc-span_ms and e.side==side]
        n=len(ss)
        for cls, nm in ((0,'right'),(1,'opposite'),(2,'neutral')):
            features[f'matured_{span_ms}ms_{nm}_smoothed']=(sum(e.label==cls for e in ss)+1)/(n+3)
        features[f'matured_{span_ms}ms_log_count']=log1p(n)
    if not all(isfinite(x) for x in features.values()):
        raise ValueError('invalid causal feature value')
    return features
