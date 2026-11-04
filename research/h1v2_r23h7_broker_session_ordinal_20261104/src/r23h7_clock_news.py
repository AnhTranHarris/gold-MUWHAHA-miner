"""R23H-0007 point-in-time calendar and UTC regional-session research adapter.

Regional clocks are *proxies*, NOT actual Coinexx symbol tradability or prop-firm authorization.
Historical MT5/ForexFactory data must carry a verifiable as-of snapshot before use.
No economic event values or fabricated trading permission are created here.
"""
from __future__ import annotations
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np

ZONES = ('Australia/Sydney', 'Asia/Tokyo', 'Europe/London', 'America/New_York')
# Research-only region-local daytime windows. NOT verified venue or broker sessions.
PROXY_HOURS = ((8,17),(9,18),(8,17),(8,17))
CLOCK_NAMES = (
    'utc_hour_sin','utc_hour_cos','utc_weekday','utc_minute_of_quarter_sin',
    'sydney_proxy','tokyo_proxy','london_proxy','newyork_proxy',
    'sydney_dst','london_dst','newyork_dst','london_newyork_proxy_overlap',
    'sydney_minutes_to_proxy_close','tokyo_minutes_to_proxy_close',
    'london_minutes_to_proxy_close','newyork_minutes_to_proxy_close',
)

def hour_clock(utc_hour_epoch: int) -> np.ndarray:
    d=datetime.fromtimestamp(utc_hour_epoch*3600, timezone.utc)
    out=np.zeros(len(CLOCK_NAMES), dtype=np.float32)
    out[0]=np.sin(2*np.pi*d.hour/24);out[1]=np.cos(2*np.pi*d.hour/24)
    out[2]=d.weekday()
    isopen=[]
    for j,(zone,(begin,end)) in enumerate(zip(ZONES,PROXY_HOURS)):
        loc=d.astimezone(ZoneInfo(zone))
        active=int(loc.weekday()<5 and begin<=loc.hour<end)
        isopen.append(active);out[4+j]=active
        if j!=1:out[8+(0 if j==0 else j-1)]=int(bool(loc.dst()))
        out[12+j]=(end-loc.hour)*60 if active else -1
    out[11]=isopen[2]*isopen[3]
    return out

def clock_features(utc_ms: np.ndarray) -> np.ndarray:
    t=np.asarray(utc_ms,dtype=np.int64)
    if not len(t):return np.empty((0,len(CLOCK_NAMES)),np.float32)
    hours,idx=np.unique(t//3600000,return_inverse=True)
    base=np.vstack([hour_clock(int(h)) for h in hours]).astype(np.float32)
    base=base[idx].copy()
    quarter=(t//60000)%15
    base[:,3]=np.sin(2*np.pi*quarter/15).astype(np.float32)
    return base

def asof_news_state(decision_utc_ms: int, snapshots: list[dict] | None) -> dict:
    """Fail-closed. Retrospectively scraped events do NOT establish historic schedule vintage.

    A signed/verified *complete* event inventory, its snapshot capture time and
    source timezone normalization are required, even when there are no events.
    Event rows must include known_at_utc_ms; otherwise the entire state is UNKNOWN.
    Actual/forecast/revision values are never exposed as pre-release features.
    """
    if snapshots is None:
        return {'status':'UNKNOWN_NO_VERIFIED_SNAPSHOT','next60m_medium_high':None,
                'prev30m_medium_high':None,'prop_authorized':None,'broker_tradable':None}
    valid=[s for s in snapshots if s.get('coverage_complete') is True and
           s.get('utc_offsets_verified') is True and
           type(s.get('captured_utc_ms')) is int and s['captured_utc_ms']<=decision_utc_ms and
           s.get('provider') in ('MT5','FOREX_FACTORY')]
    if not valid:return {'status':'UNKNOWN_NO_ASOF_COVERAGE','next60m_medium_high':None,
                         'prev30m_medium_high':None,'prop_authorized':None,'broker_tradable':None}
    latest=max(valid,key=lambda s:s['captured_utc_ms'])
    event_rows=latest.get('events')
    if not isinstance(event_rows,list) or any(not isinstance(e,dict) or
            type(e.get('known_at_utc_ms')) is not int or e.get('known_at_utc_ms')>latest['captured_utc_ms'] or
            type(e.get('event_utc_ms')) is not int or e.get('impact') not in ('HIGH','MODERATE','LOW','NONE')
            for e in event_rows):
        return {'status':'UNKNOWN_MALFORMED_EVENT_VINTAGE','next60m_medium_high':None,
                'prev30m_medium_high':None,'prop_authorized':None,'broker_tradable':None}
    # Inventory coverage must explicitly span the query horizon, not just have a timestamp.
    if latest.get('coverage_from_utc_ms',2**63-1)>decision_utc_ms-1800000 or latest.get('coverage_to_utc_ms',-1)<decision_utc_ms+3600000:
        return {'status':'UNKNOWN_INCOMPLETE_WINDOW','next60m_medium_high':None,
                'prev30m_medium_high':None,'prop_authorized':None,'broker_tradable':None}
    filtered=[e for e in event_rows if e['known_at_utc_ms']<=decision_utc_ms and
              e['impact'] in ('HIGH','MODERATE') and e.get('currency')=='USD']
    return {'status':'VERIFIED_ASOF_SCHEDULE',
            'next60m_medium_high':sum(decision_utc_ms<=e['event_utc_ms']<=decision_utc_ms+3600000 for e in filtered),
            'prev30m_medium_high':sum(decision_utc_ms-1800000<=e['event_utc_ms']<decision_utc_ms for e in filtered),
            'prop_authorized':None,'broker_tradable':None,
            'calendar_provider':latest['provider'],'snapshot_utc_ms':latest['captured_utc_ms']}
