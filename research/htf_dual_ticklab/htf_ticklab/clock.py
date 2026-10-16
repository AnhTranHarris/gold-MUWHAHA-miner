"""Empirically validated Coinexx 2026 timestamp normalization.

Authorized 2026 Coinexx export fields are server-wall epoch labels, *not*
correct UTC instants. Jan/Feb -> 120 minutes ahead; Mar 9-Jul -> 180 ahead.
Validated against Dukascopy UTC independently (one-minute return correlation).
Never rewrite raw source timestamps. This profile covers Jan-Sep 2026 only;
future files must be separately certified. US DST applied as NY-close proxy,
not a claim about broker implementation or future timezone policy.
"""
from __future__ import annotations
from datetime import datetime, timezone
import calendar

_HOUR_MS = 3_600_000
_MINUTE_MS = 60_000


def _nth_sunday(year: int, month: int, nth: int) -> int:
    first_weekday = calendar.weekday(year, month, 1)  # Mon=0 ... Sun=6
    first_sunday = 1 + ((6 - first_weekday) % 7)
    return first_sunday + 7 * (nth - 1)


def _is_new_york_dst(utc_ms: int) -> bool:
    utc = datetime.fromtimestamp(utc_ms / 1000, tz=timezone.utc)
    year = utc.year
    start_day = _nth_sunday(year, 3, 2)
    end_day = _nth_sunday(year, 11, 1)
    start = int(datetime(year, 3, start_day, 7, tzinfo=timezone.utc).timestamp() * 1000)
    end = int(datetime(year, 11, end_day, 6, tzinfo=timezone.utc).timestamp() * 1000)
    return start <= utc_ms < end


def coinexx_export_2026_to_utc(raw_ms: int) -> tuple[int, int]:
    """Return (canonical UTC millisecond, raw-clock offset in minutes).

    The approved Coinexx 2026 files have Jan-Sep labels observed +2 hours
    in NY standard time, +3 hours in NY DST. Both candidate real times are
    evaluated; reject any ambiguous/invalid transition interval rather than
    silently fabricate ordering. November fall transition not validated.
    """
    wall = datetime.fromtimestamp(raw_ms / 1000, tz=timezone.utc)
    if wall.year != 2026 or not 1 <= wall.month <= 9:
        raise ValueError('Coinexx clock profile only verified Jan-Sep 2026')
    options = []
    for off_min in (120, 180):
        true_ms = raw_ms - off_min * _MINUTE_MS
        if _is_new_york_dst(true_ms) == (off_min == 180):
            options.append((true_ms, off_min))
    if len(options) != 1:
        raise ValueError('ambiguous Coinexx 2026 clock near DST transition')
    return options[0]
