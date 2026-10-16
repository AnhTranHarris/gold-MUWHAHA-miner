"""Broker-specific readers. Read only user-authorized raw monthly tick exports."""
from __future__ import annotations
from dataclasses import dataclass
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


@dataclass(slots=True)
class FeedQuality:
    total: int = 0
    duplicates_ms: int = 0
    largest_gap_ms: int = 0
    gaps_over_60s: int = 0
    first_ms: int | None = None
    last_ms: int | None = None


def read_ticks(path: str | Path, broker: str, quality: FeedQuality, *, dukas_scale: float = 1000.0) -> Iterator[Quote]:
    """Stream rows in original order. Fail closed on malformed/crossed/out-of-order ticks.

    Input is one monthly .csv.gz; no decompressed file or full-month dataframe is made.
    Repeated timestamps are legal and keep original file order.
    """
    if broker not in {'coinexx', 'dukascopy'}:
        raise ValueError('broker must be coinexx or dukascopy')
    if broker == 'dukascopy' and dukas_scale <= 0:
        raise ValueError('dukas_scale must be positive')
    previous: int | None = None
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
            quality.last_ms = ms
            quality.total += 1; previous = ms
            yield Quote(ms, bid, ask, broker, bv, av, flags)
