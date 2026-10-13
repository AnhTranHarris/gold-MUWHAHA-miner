"""GRID0262 offline-only hardened quote funding adapter.

Repairs two reproducible failure modes in the inherited GRID0259/0261
research sandboxes: a closed-market quote must not count as an executable
settlement, and a stop/close at one timestamp must not be followed by a fresh
entry at that *same timestamp*. The broker permission remains explicitly
supplied and is NEVER derived from UTC hour or from a Dukascopy quote.

This adapter does not replace the frozen GRID0258 signal source, the active
FourSessionV1, or a verified MT5 broker execution simulator. All output is
hypothetical and cannot certify the Coinexx symbol/contract/server-clock.
"""
from __future__ import annotations
from collections import Counter
from typing import Optional
from dataclasses import dataclass
import math

from v1_grid_funded_quote_gate_0259 import (
    RAW,
    ResearchFundingEngine, Quote, BrokerPhysics, ResearchIntent,
    OpenResearchPosition, ResearchSettlement,
)

@dataclass(frozen=True)
class HardenedBrokerPhysics:
    """MT5-shaped, still unverified symbolic contract, not broker proof.

    Allows SYMBOL_TRADE_STOPS_LEVEL=0, which is legal on MT5. Missing
    max_lot/tick-size broker fields remain visibly uncertified instead of
    being silently made up.
    """
    contract_oz_per_lot:float
    leverage:float
    min_lot:float
    lot_step:float
    min_stop_raw:int
    roundtrip_usd_per_lot:float
    specs_broker_verified:bool=False
    source_note:str='ASSUMED_HYPOTHETICAL_RESEARCH_ONLY'
    max_lot:float|None=None
    tick_size_raw:int|None=None

    def __post_init__(self):
        vals=(self.contract_oz_per_lot,self.leverage,self.min_lot,self.lot_step)
        if any(not math.isfinite(v) or v<=0 for v in vals):
            raise ValueError('finite positive contract, margin and lots required')
        if not isinstance(self.min_stop_raw,int) or self.min_stop_raw<0:
            raise ValueError('broker stops level must be a nonnegative integer')
        if not math.isfinite(self.roundtrip_usd_per_lot) or self.roundtrip_usd_per_lot<0:
            raise ValueError('finite round-trip fees required')
        if self.max_lot is not None and (not math.isfinite(self.max_lot) or self.max_lot<self.min_lot):
            raise ValueError('invalid broker maximum lots')
        if self.tick_size_raw is not None and (not isinstance(self.tick_size_raw,int) or self.tick_size_raw<1):
            raise ValueError('invalid broker raw tick size')

class StrictExecutionQuote(Quote):
    """Require explicit `broker_tradable` argument at every observation."""
    def __init__(self, utc_ms:int, bid_raw:int, ask_raw:int, broker_tradable:bool):
        if type(broker_tradable) is not bool:
            raise TypeError('broker permission must be an explicit boolean')
        if not isinstance(utc_ms, int) or not isinstance(bid_raw, int) or not isinstance(ask_raw,int):
            raise TypeError('original quote time and prices must be integer scaled')
        super().__init__(utc_ms, bid_raw, ask_raw, broker_tradable)

class HardenedQuoteFundingEngine(ResearchFundingEngine):
    """Drop-in research funding gate with untradeable exit/entry quarantine."""
    def __init__(self, *, starting_cash_usd:float, physics:BrokerPhysics,
                 max_shared_positions:int=16, maintenance_margin_fraction:float=.5):
        super().__init__(starting_cash_usd=starting_cash_usd, physics=physics,
                         max_shared_positions=max_shared_positions,
                         maintenance_margin_fraction=maintenance_margin_fraction)
        self.blocked_nontradable_settlement_observations=0
        self.blocked_nontradable_entry_observations=0
        self.multi_exit_same_millisecond_count=0
        self._last_settlement_ms:Optional[int]=None
        self._settlement_counts=Counter()

    def offer(self,signal:ResearchIntent):
        if not math.isfinite(signal.research_lot) or signal.research_lot<=0:
            raise ValueError('finite positive lot quantity required')
        max_lot=getattr(self.spec,'max_lot',None)
        if max_lot is not None and signal.research_lot>max_lot+1e-12:
            raise ValueError('broker maximum lots violated')
        return super().offer(signal)

    def _validate_quote(self,q:Quote)->None:
        if type(q.broker_tradable) is not bool:
            raise TypeError('broker permission boolean required')
        if not all(isinstance(x,int) and not isinstance(x,bool) for x in (q.utc_ms,q.bid_raw,q.ask_raw)):
            raise TypeError('scaled integer quote and UTC milliseconds required')
        if q.utc_ms<0 or q.bid_raw<=0 or q.ask_raw<q.bid_raw:
            raise ValueError('invalid observed Bid/Ask quote')
        step=getattr(self.spec,'tick_size_raw',None)
        if step is not None and (q.bid_raw%step or q.ask_raw%step):
            raise ValueError('source price not on verified broker tick-size grid; conversion unspecified')
        if self.last_quote and q.utc_ms<self.last_quote.utc_ms:
            raise ValueError('input original tick order reversed')

    def _close(self,p:OpenResearchPosition,q:Quote,reason:str):
        if not q.broker_tradable:
            raise AssertionError('illegal execution from nontradable quote')
        if self._last_settlement_ms==q.utc_ms:
            self.multi_exit_same_millisecond_count+=1
        self._last_settlement_ms=q.utc_ms
        self._settlement_counts[q.utc_ms]+=1
        # Once an exit executes at this timestamp, entry signals on the same
        # quote must not consume that freed capacity without a later quote.
        self.prev_execution_ms=q.utc_ms
        super()._close(p,q,reason)

    def on_observed_quote(self,q:Quote)->tuple[ResearchSettlement,...]:
        self._validate_quote(q)
        if q.broker_tradable:
            return self._on_tradeable_observed_quote(q)
        self.last_quote=q
        if self.open:
            self.blocked_nontradable_settlement_observations+=1
        if self.waiting:
            self.blocked_nontradable_entry_observations+=1
        # Expire stale invitations, but do not open, liquidate, settle stops,
        # credit targets, or auto-stop-out on a nonexecutable source quote.
        waiting=[]
        for signal in self.waiting:
            if q.utc_ms-signal.known_at_ms>signal.ttl_ms:
                self.rejections['stale']+=1
            else:
                waiting.append(signal)
        self.waiting=waiting
        # Floating equity may still be marked as research-only; no realized
        # PnL can be manufactured from a closed broker market.
        equity=self._mark(q)
        self.peak_marked_equity=max(self.peak_marked_equity,equity)
        self.max_marked_drawdown=max(self.max_marked_drawdown,self.peak_marked_equity-equity)
        return ()

    def _on_tradeable_observed_quote(self,q:Quote)->tuple[ResearchSettlement,...]:
        # A full override is necessary: the inherited engine lets an entry
        # opened at UTC millisecond T exit at another original tick *also at
        # T*, despite its declared conservative order-per-ms gate.
        self.last_quote=q
        before=len(self.settlements)
        alive=[]
        for p in self.open:
            if q.utc_ms<=p.entry_ms:
                alive.append(p)
                continue
            price=q.bid_raw if p.side==1 else q.ask_raw
            stopped=price<=p.stop_raw if p.side==1 else price>=p.stop_raw
            if stopped or q.utc_ms>=p.deadline_ms:
                self._close(p,q,'OBSERVED_GAP_SLIPPED_STOP' if stopped else 'OBSERVED_TIME_EXPIRY')
            else:
                alive.append(p)
        self.open=alive
        equity=self._mark(q)
        if self.open and equity<self._used_margin()*self.maintenance_margin_fraction:
            remaining=[]
            for p in self.open:
                if q.utc_ms<=p.entry_ms:
                    remaining.append(p)
                else:
                    self._close(p,q,'OBSERVED_MARGIN_STOP_OUT')
            self.open=remaining
        waiting=[]
        for signal in self.waiting:
            age=q.utc_ms-signal.known_at_ms
            if age<signal.min_latency_ms:
                waiting.append(signal);continue
            if age>signal.ttl_ms:
                self.rejections['stale']+=1;continue
            # MT5 protective BUY SL is measured against current BID; a
            # protective SELL SL is measured against current ASK. A stop
            # expressed from the entry-side price must clear the SPREAD too.
            current_spread=q.ask_raw-q.bid_raw
            if signal.stop_distance_raw-current_spread<self.spec.min_stop_raw:
                self.rejections['broker_min_stop_after_spread']+=1;continue
            if len(self.open)>=self.cap:
                self.rejections['source_capacity']+=1;continue
            if self.prev_execution_ms==q.utc_ms:
                self.rejections['same_millisecond']+=1;continue
            price=q.ask_raw if signal.side==1 else q.bid_raw
            margin=self._margin(price,signal.research_lot)
            free=self._mark(q)-self._used_margin()
            qty=signal.research_lot*self.spec.contract_oz_per_lot
            immediate_spread=(q.ask_raw-q.bid_raw)/RAW*qty
            fee=self.spec.roundtrip_usd_per_lot*signal.research_lot
            if free<margin+immediate_spread+fee:
                self.rejections['insufficient_free_margin']+=1;continue
            self.open.append(OpenResearchPosition(signal.event_id,signal.source,signal.side,
                   signal.research_lot,qty,q.utc_ms,price,
                   price-signal.side*signal.stop_distance_raw,
                   q.utc_ms+signal.max_hold_ms,margin))
            self.prev_execution_ms=q.utc_ms
            self.high_water_open=max(self.high_water_open,len(self.open))
        self.waiting=waiting
        eq=self._mark(q)
        self.peak_marked_equity=max(self.peak_marked_equity,eq)
        self.max_marked_drawdown=max(self.max_marked_drawdown,self.peak_marked_equity-eq)
        return tuple(self.settlements[before:])

    def summary(self)->dict:
        x=super().summary()
        x.update({'engine':'GRID0262_HARDENED_SHADOW',
            'nontradable_open_position_marks':self.blocked_nontradable_settlement_observations,
            'nontradable_pending_marks':self.blocked_nontradable_entry_observations,
            'same_timestamp_multiple_exits_not_broker_acknowledged':self.multi_exit_same_millisecond_count,
            'mt5_ea_conversion_certified':False,'broker_permission_derivation':'CALLER_EXPLICIT_ONLY',
            'one_shared_research_book':True})
        return x
