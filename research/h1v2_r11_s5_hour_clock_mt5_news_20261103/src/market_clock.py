"""R11S5: research time-of-day/session geometry. No trade authorization.

Market convention windows are nominal research sessions, not broker trading hours.
UTC conversions use IANA timezone history at every timestamp; never a fixed DST shift.
Historical broker session/prop firm permissions are UNKNOWN unless user-supplied.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
from typing import Optional

UTC = timezone.utc

@dataclass(frozen=True)
class NominalSession:
    name: str
    zone: str
    local_open: int
    local_close: int
    weekdays: tuple[int, ...] = (0, 1, 2, 3, 4)

SESSIONS = (
    NominalSession('SYDNEY', 'Australia/Sydney', 8, 17),
    NominalSession('TOKYO', 'Asia/Tokyo', 9, 18),
    NominalSession('LONDON', 'Europe/London', 8, 17),
    NominalSession('NEW_YORK', 'America/New_York', 8, 17),
)

def utc_hour(iso: str) -> datetime:
    d = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    if d.tzinfo is None or d.utcoffset() != timedelta(0):
        raise ValueError('source clock must be explicit UTC')
    if d.minute or d.second or d.microsecond:
        raise ValueError('source timestamp must begin at an exact UTC hour')
    return d

def is_session_open(instant: datetime, session: NominalSession) -> bool:
    if instant.tzinfo is None:
        raise ValueError('naive wall clock prohibited')
    local = instant.astimezone(ZoneInfo(session.zone))
    return local.weekday() in session.weekdays and session.local_open <= local.hour < session.local_close

def next_session_open(start: datetime, session: NominalSession, max_days: int = 8) -> int:
    """Minutes to next nominal local open; zero if at the open (never means broker permission)."""
    if start.tzinfo is None:
        raise ValueError('UTC-aware clock required')
    z = ZoneInfo(session.zone)
    local = start.astimezone(z)
    for dd in range(max_days + 1):
        day = local.date() + timedelta(days=dd)
        if day.weekday() not in session.weekdays:
            continue
        candidate = datetime.combine(day, time(session.local_open), tzinfo=z).astimezone(UTC)
        if candidate >= start:
            return int((candidate - start).total_seconds() // 60)
    raise AssertionError('no open within search horizon')

def next_session_close(start: datetime, session: NominalSession, max_days: int = 8) -> int:
    if start.tzinfo is None:
        raise ValueError('UTC-aware clock required')
    z = ZoneInfo(session.zone)
    local = start.astimezone(z)
    for dd in range(max_days + 1):
        day = local.date() + timedelta(days=dd)
        if day.weekday() not in session.weekdays:
            continue
        candidate = datetime.combine(day, time(session.local_close), tzinfo=z).astimezone(UTC)
        if candidate >= start:
            return int((candidate - start).total_seconds() // 60)
    raise AssertionError('no close within search horizon')

def clock_hour(iso: str) -> dict:
    """Complete 60-min UTC scan. Handles US/EU/AU DST transitions and weekend shifts."""
    start = utc_hour(iso)
    minutes = [start + timedelta(minutes=m) for m in range(60)]
    masks = {s.name: tuple(is_session_open(x, s) for x in minutes) for s in SESSIONS}
    sums = {name: sum(mask) for name, mask in masks.items()}
    counts = [sum(masks[name][m] for name in masks) for m in range(60)]
    active = tuple(name for name, amt in sums.items() if amt)
    local = start.astimezone(ZoneInfo('America/Chicago'))
    out = {
        'hour_utc_verified': start.isoformat().replace('+00:00', 'Z'),
        'chicago_wall_hour': local.isoformat(),
        'chicago_fold': local.fold,
        'nominal_session_names': '+'.join(active) if active else 'NONE',
        'nominal_max_simultaneous_sessions': max(counts),
        'nominal_minutes_ge2_sessions': sum(x >= 2 for x in counts),
        'nominal_minutes_ge3_sessions': sum(x >= 3 for x in counts),
        'market_actual_broker_permission': 'UNKNOWN_NEEDS_HISTORICAL_MT5_SESSION_SOURCE',
        'prop_firm_operating_permission': 'UNCONFIGURED_NEEDS_OWNER_RULES',
        'source_clock_contract': 'IANA_DST_NOMINAL_ONLY_NOT_BROKER_EXECUTION',
    }
    for s in SESSIONS:
        out['nominal_'+s.name+'_minutes'] = sums[s.name]
        out['nominal_'+s.name+'_next_open_min'] = next_session_open(start,s)
        out['nominal_'+s.name+'_next_close_min'] = next_session_close(start,s)
    assert all(0 <= x <= 60 for x in sums.values())
    return out

if __name__ == '__main__':
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--utc-hour',required=True)
    print(json.dumps(clock_hour(p.parse_args().utc_hour),indent=2))
