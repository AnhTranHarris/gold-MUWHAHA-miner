"""GRID0266: original Bid/Ask source-locked replay for the CURRENT Python V1.

Dukascopy is independent research quotes; Coinexx REAL is historical MT5 tester
quotes and logger events; SYNTH is teacher only. No feed mints actual MT5 deals.
"""
from __future__ import annotations
import csv, gzip
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Callable, Iterator
from v1_grid_r9_benchmark_utc_0268 import verify_coinexx_utc_text

PRICE_SCALE=1000
START_MS=1767225600000  # Jan 1, 2026 UTC
STOP_MS=1785542400000   # Aug 1, 2026 UTC: excluded
R9_HEADER=('run_label','time_msc','time','bid','ask','last','tick_volume',
'volume_real','flags','spread','minute_start','minute_second','cycle_buy',
'cycle_sell','pending_mode','rearm_number','s1_disp','s1_eff','s1_range',
's1_turns','atr','session','gate_open','position_open','position_side',
'entry_price','mfe','mae','current_sl','trail_armed','event')
DUKAS_HEADER=('timestamp_ms_utc','ask_raw','bid_raw','ask_volume','bid_volume')

class FeedKind(str,Enum):
    DUKAS='DUKASCOPY_ORIGINAL'
    COINEXX_REAL='COINEXX_R9_REAL_TESTER'
    COINEXX_SYNTH='COINEXX_R9_SYNTH_TESTER'

@dataclass(frozen=True)
class StampedMarketTick:
    feed:FeedKind
    ordinal:int
    utc_ms:int
    bid_raw:int
    ask_raw:int
    logger_event:str|None=None
    logger_gate_open:bool|None=None
    source_filename:str|None=None
    def __post_init__(self):
        if type(self.utc_ms)!=int or self.utc_ms<0 or type(self.ordinal)!=int or self.ordinal<0:
            raise ValueError('positive UTC ms and original row identity required')
        if type(self.bid_raw)!=int or type(self.ask_raw)!=int or self.bid_raw<=0 or self.ask_raw<self.bid_raw:
            raise ValueError('original positive noncrossed bid/ask required')
    def as_quote(self):
        from v1_vertical_grid import Quote
        return Quote(self.utc_ms,self.bid_raw,self.ask_raw)

def _exact_scaled_price(s:str,name:str)->int:
    try:p=Decimal(s)
    except (InvalidOperation,TypeError) as exc:raise ValueError(f'invalid {name}') from exc
    if not p.is_finite() or p<=0 or p*PRICE_SCALE!=(p*PRICE_SCALE).to_integral_value():
        raise ValueError(f'{name} cannot be represented exactly at 0.001 USD')
    return int(p*PRICE_SCALE)

def _allowed_source_time(tm:int):
    if not START_MS<=tm<STOP_MS:
        raise PermissionError('only Jan-Jul 2026; August sealed')

def _allowed_original_path(path:Path):
    n=path.name.lower()
    if any(x in n for x in ('2026_08','2026-08','2026_09','2026-09')):
        raise PermissionError('August 2026 sealed')

def _open(path):
    return gzip.open(path,'rt',newline='') if str(path).endswith('.gz') else open(path,'rt',newline='')

def stream_dukas_original(path:str|Path,*,maximum:int|None=None)->Iterator[StampedMarketTick]:
    path=Path(path);_allowed_original_path(path)
    prev=-1
    with _open(path) as f:
        r=csv.DictReader(f)
        if tuple(r.fieldnames or ())!=DUKAS_HEADER:raise ValueError('noncanonical Dukascopy header')
        for n,row in enumerate(r):
            if maximum is not None and n>=maximum:break
            tm=int(row['timestamp_ms_utc']);b=int(row['bid_raw']);a=int(row['ask_raw'])
            _allowed_source_time(tm)
            if tm<prev:raise ValueError(f'Dukascopy time reversed at row {n+2}')
            if any(not Decimal(row[k]).is_finite() or Decimal(row[k])<0
                   for k in ('ask_volume','bid_volume')):
                raise ValueError('negative or invalid quoted depth')
            yield StampedMarketTick(FeedKind.DUKAS,n,tm,b,a,source_filename=path.name)
            prev=tm

def stream_coinexx_r9_original(path:str|Path,*,kind:FeedKind,maximum:int|None=None,
                              historical_point_usd:Decimal|str='0.01')->Iterator[StampedMarketTick]:
    path=Path(path);_allowed_original_path(path)
    if kind not in (FeedKind.COINEXX_REAL,FeedKind.COINEXX_SYNTH):
        raise ValueError('explicit Coinexx R9 REAL or SYNTH identity required')
    point=Decimal(str(historical_point_usd))
    if not point.is_finite() or point<=0:raise ValueError('invalid R9 historical point')
    label='REAL' if kind==FeedKind.COINEXX_REAL else 'SYNTH'
    prev=-1
    with _open(path) as f:
        r=csv.DictReader(f)
        if tuple(r.fieldnames or ())!=R9_HEADER:raise ValueError('not full 31-column R9 logger')
        for n,row in enumerate(r):
            if maximum is not None and n>=maximum:break
            if row['run_label']!=label:raise ValueError('REAL/SYNTH label mismatch')
            tm=int(row['time_msc'])
            b=_exact_scaled_price(row['bid'],'Coinexx bid')
            a=_exact_scaled_price(row['ask'],'Coinexx ask')
            _allowed_source_time(tm)
            if tm<prev:raise ValueError(f'Coinexx time reversed at row {n+2}')
            spread=Decimal(row['spread'])
            if not spread.is_finite() or spread<0 or spread*point!=Decimal(a-b)/PRICE_SCALE:
                raise ValueError(f'R9 logged spread inconsistent with actual quote at row {n+2}')
            # Independently verify MT5 integer UTC epoch, minute, second and
            # elapsed minute-second; never guess a Coinexx offset.
            verify_coinexx_utc_text(tm,row['time'],row['minute_start'],row['minute_second'])
            if row['gate_open'] not in ('0','1'):raise ValueError('historical gate flag unknown')
            yield StampedMarketTick(kind,n,tm,b,a,row['event'],row['gate_open']=='1',path.name)
            prev=tm

class SourceLockedV1ResearchReplay:
    """One source, one chronology. Permission is an explicit HYPOTHETICAL
    research availability callback; not actual DEAL_ADD confirmation."""
    def __init__(self,engine,*,kind:FeedKind,permission:Callable[[StampedMarketTick],bool],
                 simulate_shadow:bool=False):
        if not isinstance(kind,FeedKind) or not callable(permission):
            raise TypeError('explicit source and hypothetical session availability required')
        if type(simulate_shadow) is not bool:raise TypeError('explicit shadow toggle required')
        self.engine=engine;self.kind=kind;self.permission=permission
        self.simulate_shadow=simulate_shadow
        self.last_ms=None;self.last_ordinal=None;self.quotes=0
    def on_observation(self,o:StampedMarketTick):
        if not isinstance(o,StampedMarketTick) or o.feed!=self.kind:
            raise ValueError('cross-feed quote substitution is forbidden')
        if self.last_ms is not None and (o.utc_ms<self.last_ms or o.ordinal<=self.last_ordinal):
            raise ValueError('source quote order/identity reversed')
        allow=self.permission(o)
        if type(allow) is not bool:raise TypeError('never infer broker tradability')
        if hasattr(self.engine,'_feed_replay_authorized'):
            self.engine._feed_replay_authorized=True
        try:
            result=self.engine.on_tick(o.as_quote(),broker_tradable=allow,
                         simulate_broker=self.simulate_shadow)
        finally:
            if hasattr(self.engine,'_feed_replay_authorized'):
                self.engine._feed_replay_authorized=False
        self.last_ms=o.utc_ms;self.last_ordinal=o.ordinal;self.quotes+=1
        return result
    def provenance(self):
        return dict(feed=self.kind.value,quotes=self.quotes,
                    shadow_mode=self.simulate_shadow,
                    live_mt5_deals_confirmed_by_feed=0,
                    external_broker_contract_verified_by_feed=False,
                    raw_timestamp_authority='UTC_EPOCH_MS_UNSHIFTED',
                    coinexx_chart_candle_phase_inferred=False)
