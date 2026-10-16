"""Broker-specific readers. Read only user-authorized raw monthly tick exports."""
from __future__ import annotations
from dataclasses import dataclass, field
from .clock import coinexx_export_2026_to_utc
import csv
import gzip
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True, slots=True)
class Quote:
    ms: int
    bid: float
    ask: float
    broker: str
    bid_volume: float | None = None
    ask_volume: float | None = None
    flags: int | None = None
    source_ms: int | None = None  # exact source epoch label before normalization
    clock_offset_minutes: int = 0


@dataclass(slots=True)
class FeedQuality:
    total: int = 0
    duplicates_ms: int = 0
    largest_gap_ms: int = 0
    gaps_over_60s: int = 0
    first_ms: int | None = None
    last_ms: int | None = None
    first_source_ms: int | None = None
    last_source_ms: int | None = None
    clock_profile: str = "raw"
    offset_tick_counts: dict[str, int] = field(default_factory=dict)


def read_ticks(path: str | Path, broker: str, quality: FeedQuality, *, dukas_scale: float = 1000.0, clock_profile: str | None = None) -> Iterator[Quote]:
    """Stream rows in original order. Fail closed on malformed/crossed/out-of-order ticks.

    Input is one monthly .csv.gz; no decompressed file or full-month dataframe is made.
    Repeated timestamps are legal and keep original file order.
    """
    if broker not in {'coinexx', 'dukascopy'}:
        raise ValueError('broker must be coinexx or dukascopy')
    if broker == 'dukascopy' and dukas_scale <= 0:
        raise ValueError('dukas_scale must be positive')
    if clock_profile is None:
        if broker == 'coinexx':
            raise ValueError('Coinexx clock profile must be explicit (raw or coinexx_2026_nyclose)')
        clock_profile = 'raw'
    if clock_profile not in {'raw', 'coinexx_2026_nyclose'}:
        raise ValueError('unsupported clock profile')
    if clock_profile != 'raw' and broker != 'coinexx':
        raise ValueError('Coinexx clock profile cannot be applied to Dukascopy')
    quality.clock_profile = clock_profile
    previous: int | None = None
    cached_minute: int | None = None
    cached_off_min: int = 0
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        expected = ({'time', 'time_msc', 'bid', 'ask', 'flags'} if broker == 'coinexx'
                    else {'timestamp_ms_utc', 'ask_raw', 'bid_raw', 'ask_volume', 'bid_volume'})
        if not reader.fieldnames or not expected.issubset(reader.fieldnames):
            raise ValueError(f'{path}: unexpected {broker} headers {reader.fieldnames!r}')
        for row in reader:
            try:
                if broker == 'coinexx':
                    ms = int(row['time_msc']); bid = float(row['bid']); ask = float(row['ask'])
                    flags = int(row['flags']); bv = av = None
                    if abs(int(row['time']) - ms // 1000) > 1:
                        raise ValueError('time/time_msc mismatch')
                else:
                    ms = int(row['timestamp_ms_utc'])
                    ask = int(row['ask_raw']) / dukas_scale
                    bid = int(row['bid_raw']) / dukas_scale
                    av = float(row['ask_volume']); bv = float(row['bid_volume'])
                    flags = None
                source_ms = ms
                offset_min = 0
                if clock_profile == 'coinexx_2026_nyclose':
                    minute = source_ms // 60_000
                    if minute != cached_minute:
                        ms, cached_off_min = coinexx_export_2026_to_utc(source_ms)
                        cached_minute = minute
                    else:
                        ms = source_ms - cached_off_min * 60_000
                    offset_min = cached_off_min
                if not (0 < bid <= ask < 100000 and 1_500_000_000_000 < ms < 2_500_000_000_000):
                    raise ValueError('invalid quote or timestamp')
                if previous is not None and ms < previous:
                    raise ValueError('timestamp reversal')
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'{path}, data row {reader.line_num}: {exc}') from exc
            if previous is not None:
                gap = ms - previous
                quality.largest_gap_ms = max(quality.largest_gap_ms, gap)
                quality.gaps_over_60s += int(gap > 60_000)
                quality.duplicates_ms += int(ms == previous)
            if quality.first_ms is None: quality.first_ms = ms
            if quality.first_source_ms is None: quality.first_source_ms = source_ms
            quality.last_source_ms = source_ms
            quality.last_ms = ms
            key = str(offset_min)
            quality.offset_tick_counts[key] = quality.offset_tick_counts.get(key, 0) + 1
            quality.total += 1; previous = ms
            yield Quote(ms, bid, ask, broker, bv, av, flags, source_ms, offset_min)
