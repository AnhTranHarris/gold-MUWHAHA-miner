"""Strict streaming input adapter for Jan–Jul ORIGINAL Dukascopy XAUUSD ticks.

No time-bucket aggregation, future leakage, month identity inputs or broker
session inference. Every row is yielded in its original CSV order. Repeated
millisecond timestamps are supported in file order. August sealed externally.
"""
from __future__ import annotations
import csv, gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Callable
from v1_grid_funded_quote_gate_0262_hardened import StrictExecutionQuote

COLUMNS=('timestamp_ms_utc','ask_raw','bid_raw','ask_volume','bid_volume')

@dataclass(frozen=True)
class DukascopyObservation:
    ordinal:int
    quote:StrictExecutionQuote
    ask_volume:float
    bid_volume:float


def stream_original_ticks(path:str|Path, *, permission:Callable[[int,int,int],bool],
                          maximum:int|None=None)->Iterator[DukascopyObservation]:
    """Caller MUST provide explicit broker research permission.

    `permission` is deliberately required, never inferred from Dukascopy UTC
    clock or prices. It may be constantly False for non-executable audits;
    artificially True permissions make shadow-only mechanics tests, not
    Coinexx execution claims. Does not treat Dukascopy quote depth as trades.
    """
    if not callable(permission):
        raise TypeError('explicit permission callback required; None means unknown')
    path=Path(path)
    if '2026_08_' in path.name or '2026_09_' in path.name:
        raise PermissionError('August sealed; later months outside authorized Jan-Jul test range')
    if maximum is not None and maximum<1:
        raise ValueError('positive bounded rows required')
    opener=gzip.open if path.name.endswith('.gz') else open
    prev=None
    with opener(path,'rt',newline='') as handle:
        reader=csv.DictReader(handle)
        if tuple(reader.fieldnames or ())!=COLUMNS:
            raise ValueError(f'noncanonical original tick columns {reader.fieldnames}')
        for ordinal,row in enumerate(reader):
            if maximum is not None and ordinal>=maximum:break
            ms=int(row['timestamp_ms_utc']);a=int(row['ask_raw']);b=int(row['bid_raw'])
            if prev is not None and ms<prev:
                raise ValueError(f'out-of-order original ticks at row {ordinal+2}')
            prev=ms
            av=float(row['ask_volume']);bv=float(row['bid_volume'])
            if av<0 or bv<0:
                raise ValueError('negative advertised quote depth')
            explicit=permission(ms,b,a)
            quote=StrictExecutionQuote(ms,b,a,explicit)
            yield DukascopyObservation(ordinal,quote,av,bv)
