"""R11S5 MT5 historical-calendar join. Scientific data and timezone contract.

MQL5 calendar dates are in *trade server* time, NOT UTC. Full history is a
retrospective archive, not proof that event schedules or actual/forecast were
known at the entry timestamp. Without a verified historical server offset
schedule: refuse any event/hit classification (UNKNOWN, never zero).

Do not use post-event actual values, surprise or revised forecasts as as-of
pre-news features. No trading permission is inferred from calendar state.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC=timezone.utc
IMPORTANCE={'CALENDAR_IMPORTANCE_MODERATE','CALENDAR_IMPORTANCE_HIGH','MODERATE','HIGH','2','3'}
DATETIME_MODES={'CALENDAR_TIMEMODE_DATETIME','DATETIME','0'}

@dataclass(frozen=True)
class ServerInterval:
    from_utc: datetime
    to_utc: datetime
    offset_min: int
    broker: str
    evidence: str

@dataclass(frozen=True)
class Event:
    id: str
    event_id: str
    time_utc: datetime
    currency: str
    importance: str
    event_name: str
    provenance: str


def _aware_utc(s: str) -> datetime:
    x=datetime.fromisoformat(s.strip().replace('Z','+00:00'))
    if x.tzinfo is None or x.utcoffset()!=timedelta(0):
        raise ValueError(f'expected timezone-aware UTC: {s}')
    return x

def _server(s: str) -> datetime:
    s=s.strip().replace('.','-',2)
    return datetime.strptime(s,'%Y-%m-%d %H:%M:%S')

def load_server_intervals(path: str|Path)->list[ServerInterval]:
    """Input offset file must have independent documented historical evidence."""
    z=[]
    with open(path,newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            a=_aware_utc(r['from_utc']);b=_aware_utc(r['to_utc'])
            off=int(r['server_utc_offset_min'])
            if a>=b or not -840<=off<=840:
                raise ValueError('invalid historical server-time offset interval')
            if not r['broker'] or not r['verified_evidence']:
                raise ValueError('historical mapping requires identified broker + verification provenance')
            z.append(ServerInterval(a,b,off,r['broker'],r['verified_evidence']))
    if not z:raise ValueError('empty offset provenance')
    z.sort(key=lambda v:v.from_utc)
    for x,y in zip(z,z[1:]):
        if x.to_utc>y.from_utc:
            raise ValueError('ambiguous overlapping historical offsets')
    return z

def server_to_utc(s: str, intervals: list[ServerInterval]) -> datetime:
    w=_server(s)
    valid=[]
    for p in intervals:
        d=(w-timedelta(minutes=p.offset_min)).replace(tzinfo=UTC)
        if p.from_utc<=d<p.to_utc:
            valid.append(d)
    if len(valid)!=1:
        raise ValueError(f'historical server time cannot be uniquely mapped (matches={len(valid)}): {s}')
    return valid[0]

def load_events(path: str|Path, offsets: list[ServerInterval], *, require_complete: bool=True)->list[Event]:
    if not offsets:
        raise ValueError('MT5 historical UTC offsets required')
    out=[];ids=set();invalid=[]
    with open(path,newline='',encoding='utf-8-sig') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            ident=row['value_id'].strip();imp=row['importance'].strip().upper();currency=row['currency'].strip().upper()
            if not ident:raise ValueError('calendar event with no unique value ID')
            if ident in ids:raise ValueError(f'duplicate calendar value ID {ident}')
            ids.add(ident)
            if imp not in IMPORTANCE:continue
            tm=row['time_mode'].strip().upper()
            if tm not in DATETIME_MODES:
                invalid.append((ident,tm));continue
            d=server_to_utc(row['event_time_server'],offsets)
            out.append(Event(ident,row['event_id'],d,currency,imp,row['event_name'],
                             'HISTORICAL_RETROSPECTIVE_NOT_PROVEN_ASOF'))
    if invalid and require_complete:
        raise ValueError(f'{len(invalid)} relevant calendar events lack exact announced event time')
    return sorted(out,key=lambda x:x.time_utc)

def hourly_event_features(hour_utc:datetime, events: list[Event]|None, *, complete:bool=False)->dict:
    if hour_utc.tzinfo is None or hour_utc.utcoffset()!=timedelta(0):
        raise ValueError('UTC hour required')
    if not complete or events is None:
        return {'mt5_news_state':'UNKNOWN_NO_VERIFIED_COMPLETE_HISTORICAL_EXPORT',
                'mt5_medium_high_events_in_hour':'UNKNOWN',
                'mt5_high_events_in_hour':'UNKNOWN',
                'mt5_high_events_pre60':'UNKNOWN',
                'mt5_high_events_post60':'UNKNOWN',
                'mt5_nearest_news_minutes':'UNKNOWN',
                'mt5_pre_release_asof_actual_allowed':0}
    a=hour_utc;b=a+timedelta(hours=1)
    in_hour=[e for e in events if a<=e.time_utc<b]
    high=lambda e:e.importance.endswith('HIGH') or e.importance in {'3'}
    pre=[e for e in events if a-timedelta(minutes=60)<=e.time_utc<a and high(e)]
    post=[e for e in events if b<=e.time_utc<b+timedelta(minutes=60) and high(e)]
    nearest=min((abs(int((e.time_utc-a).total_seconds()/60)) for e in events),default=None)
    return {'mt5_news_state':'RETROSPECTIVE_VERIFIED_OFFSET_NOT_POINT_IN_TIME',
            'mt5_medium_high_events_in_hour':len(in_hour),
            'mt5_high_events_in_hour':sum(high(e) for e in in_hour),
            'mt5_high_events_pre60':len(pre),
            'mt5_high_events_post60':len(post),
            'mt5_nearest_news_minutes':nearest if nearest is not None else 'NO_SCHEDULED_EVENTS_IN_COMPLETE_EXPORT',
            'mt5_pre_release_asof_actual_allowed':0}
