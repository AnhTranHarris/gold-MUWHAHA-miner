#!/usr/bin/env python3
"""R34 RESEARCH-ONLY frozen native-quote -> original R24 model shadow adapter.
No MetaTrader5 dependency; does not call OrderSend or modify a position.
The original R17 producer remains external and MUST give verified as-of scores.
Rejects retrospective quote/event/status packets and live accounts.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable,Optional
import json
from f401_r24_broker_cooperative_shadow import FrozenR24TwoBrokerShadow

R17_ARCHIVE_SHA='c993a258987387737b6c909d3f18699633f9159fa077be653c93ad5afa506e8f'
BROKERS={'coinexx','dukascopy'}

class ContractError(ValueError):pass

@dataclass(frozen=True)
class NativeQuote:
    broker:str
    time_msc:int
    ordinal:int
    bid:float
    ask:float
    source_registered:bool

@dataclass(frozen=True)
class PendingIntent:
    intent_id:str
    broker:str
    symbol:str
    account_mode:str
    t0_msc:int
    side:int
    original_signal_was_executed:bool=False
    # This adapter is for newly deferred orders, not original t0-filled R9 entries.

@dataclass(frozen=True)
class OriginalR17Packet:
    broker:str
    intent_id:str
    feature_asof_msc:int
    source_quote_ordinal:int
    source_sha256:str
    source_prefix_verified:bool
    published_htf_bars_verified:bool
    prior_labels_matured_asof_verified:bool
    base_r16:bool
    opposite:float
    neutral:float
    right_guard:float

class DemoShadowBridge:
    def __init__(self,original_r24_folder:str|Path,*,broker:str,emit:Optional[Callable[[dict],None]]=None):
        if broker not in BROKERS:raise ContractError('unknown broker')
        self.broker=broker
        self.original=FrozenR24TwoBrokerShadow(original_r24_folder,broker=broker)
        self.last_order=(-1,-1)
        self.pending={}
        self.first_quote={}
        self.decided=set()
        self.emit=emit

    def add_intent(self,intent:PendingIntent):
        if (intent.broker!=self.broker or intent.symbol!='XAUUSD' or
            intent.account_mode!='DEMO' or intent.side not in (-1,1) or
            not intent.intent_id or intent.t0_msc<0):
            raise ContractError('demo XAUUSD isolated broker/side/event mandatory')
        if intent.intent_id in self.pending or intent.intent_id in self.decided:
            raise ContractError('replayed or duplicated intent')
        self.pending[intent.intent_id]=intent

    def ingest_native_quote(self,quote:NativeQuote):
        if quote.broker!=self.broker or not quote.source_registered:
            raise ContractError('unregistered quote source or broker mismatch')
        if not (quote.bid>0 and quote.ask>=quote.bid and
                quote.ask-quote.bid<100 and quote.ordinal>=0 and quote.time_msc>=0):
            raise ContractError('invalid native bid/ask/time/ordinal')
        key=(quote.time_msc,quote.ordinal)
        if key<=self.last_order:
            raise ContractError('non-monotone same-ms quote source ordinal or replay')
        self.last_order=key
        for id,intent in self.pending.items():
            if id not in self.first_quote and intent.t0_msc+15000<=quote.time_msc<intent.t0_msc+16000:
                self.first_quote[id]=quote

    def evaluate(self,intent_id:str,*,asof_source:OriginalR17Packet,
                 order_currently_filled:bool,order_terminal_status:str='PENDING_UNFILLED'):
        if intent_id not in self.pending or intent_id in self.decided:
            raise ContractError('unknown or already decided intent')
        intent=self.pending[intent_id]
        if intent.original_signal_was_executed or order_currently_filled or order_terminal_status!='PENDING_UNFILLED':
            self.decided.add(intent_id)
            return self._receipt(intent,'ORIGINAL_FILLED_OR_NOT_PENDING_IMMUTABLE',None)
        quote=self.first_quote.get(intent_id)
        if quote is None:
            return self._receipt(intent,'NO_T15_GENUINE_QUOTE__NO_FILTER_ACTION',None)
        if (asof_source.broker!=intent.broker or asof_source.intent_id!=intent_id or
            asof_source.feature_asof_msc!=quote.time_msc or
            asof_source.source_quote_ordinal!=quote.ordinal or
            asof_source.source_sha256!=R17_ARCHIVE_SHA or
            not asof_source.source_prefix_verified or
            not asof_source.published_htf_bars_verified or
            not asof_source.prior_labels_matured_asof_verified):
            return self._receipt(intent,'UPSTREAM_R17_ASOF_SOURCE_UNVERIFIED__NO_FILTER_ACTION',quote)
        outcome=self.original.shadow_decision(
            broker=intent.broker,t0=intent.t0_msc,decision_msc=quote.time_msc,
            source_quote_msc=quote.time_msc,original_side=intent.side,
            original_quote_ordinal=quote.ordinal,source_quote_ordinal_reconciled=True,
            first_genuine_native_quote_verified=True,base_r16=asof_source.base_r16,
            opposite=asof_source.opposite,neutral=asof_source.neutral,
            right_guard=asof_source.right_guard,already_filled=False,
            valid_native_quote=True)
        self.decided.add(intent_id)
        predicted=outcome.get('action')
        action=('SHADOW_WOULD_VETO' if predicted=='VETO_NEW_UNFILLED_ORDER'
                else 'SHADOW_WOULD_RELEASE' if predicted=='RELEASE_TO_SEPARATE_EXECUTION_CHECK'
                else 'NO_FILTER_ACTION')
        return self._receipt(intent,action,quote,{'original_r24_output':outcome})

    def _receipt(self,intent:PendingIntent,action:str,q:NativeQuote|None,extra:dict|None=None):
        result={'research_only':True,'has_order_send':False,'broker':self.broker,
                'symbol':intent.symbol,'account_mode':intent.account_mode,
                'intent_id':intent.intent_id,'t0_msc':intent.t0_msc,
                'quote_msc':q.time_msc if q else None,
                'quote_ordinal':q.ordinal if q else None,'action':action,
                'veto_is_effective_on_broker':False}
        if extra:result.update(extra)
        if self.emit:self.emit(result)
        return result
