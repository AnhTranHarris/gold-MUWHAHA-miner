"""GRID0263 — offline MT5-event-contract state machine, NOT an MT5 implementation.

An OrderCheck approval, OrderSend acceptance, actual DEAL_ADD fill, and
SLTP modification acknowledgement are distinct. No quote-based or fictional
fills, no implicit Coinexx contract verification, no actual MT5 API access.
All broker money values come from externally supplied event evidence. This
portable contract only models HEDGING, not NETTING, pending symbol verification.
"""
from __future__ import annotations
from dataclasses import dataclass,field
from decimal import Decimal, InvalidOperation
from typing import Optional


def money(x)->Decimal:
    d=Decimal(str(x))
    if not d.is_finite():raise ValueError('finite amount required')
    return d

@dataclass(frozen=True)
class BrokerOrder:
    source_id:str
    order_id:str
    available_ms:int
    request_ms:int
    side:int
    lots:Decimal
    requested_stop_raw:int
    intended_expiry_ms:int
    def __post_init__(self):
        if not self.source_id or not self.order_id or not isinstance(self.available_ms,int) or not isinstance(self.request_ms,int) or self.request_ms<self.available_ms:
            raise ValueError('source must be available before request')
        if self.side not in (-1,1) or money(self.lots)<=0 or self.requested_stop_raw<=0 or self.intended_expiry_ms<=self.request_ms:
            raise ValueError('invalid order facts')

@dataclass(frozen=True)
class BrokerDeal:
    order_id:str
    deal_id:str
    time_ms:int
    lots:Decimal
    executed_price_raw:int
    realized_cash:Decimal=Decimal('0')
    fee_cash:Decimal=Decimal('0')
    def __post_init__(self):
        if not self.order_id or not self.deal_id or not isinstance(self.time_ms,int) or self.time_ms<0 or money(self.lots)<=0 or self.executed_price_raw<=0:
            raise ValueError('invalid broker deal evidence')
        money(self.realized_cash);money(self.fee_cash)

@dataclass
class OrderRecord:
    proposed:BrokerOrder
    check_approved:Optional[bool]=None
    send_accepted:Optional[bool]=None
    entry_lots:Decimal=Decimal('0')
    close_lots:Decimal=Decimal('0')
    stopped_raw:Optional[int]=None
    broker_fees:Decimal=Decimal('0')
    realized_cash:Decimal=Decimal('0')
    last_deal_ms:Optional[int]=None
    deal_ids:set[str]=field(default_factory=set)
    stopped_change_id:set[str]=field(default_factory=set)
    rejection:str=''

class MT5EventContractResearchOnly:
    def __init__(self, *, account_mode:str='UNKNOWN', verified_symbol:bool=False):
        if account_mode not in ('UNKNOWN','HEDGING','NETTING'):raise ValueError('invalid account mode')
        self.account_mode=account_mode
        self.verified_symbol=verified_symbol
        self.orders:dict[str,OrderRecord]={}
        self.deal_owner:dict[str,str]={}
        self.confirmed_net_cash=Decimal('0')
        self.confirmed_fee_cash=Decimal('0')
    def submit(self,q:BrokerOrder):
        if q.order_id in self.orders:raise ValueError('duplicate order id')
        self.orders[q.order_id]=OrderRecord(q)
    def check(self,order_id:str,*,approved:bool,reason:str=''):
        p=self.orders[order_id]
        if type(approved) is not bool or p.check_approved is not None:raise ValueError('duplicate/unverified OrderCheck')
        p.check_approved=approved
        if not approved:p.rejection=reason or 'OrderCheck refused'
    def send(self,order_id:str,*,accepted:bool,reason:str=''):
        p=self.orders[order_id]
        if type(accepted) is not bool or p.check_approved is not True or p.send_accepted is not None:
            raise ValueError('OrderSend requires positive unique check')
        p.send_accepted=accepted
        if not accepted:p.rejection=reason or 'OrderSend refused'
    def fill(self,d:BrokerDeal):
        p=self.orders[d.order_id]
        if self.account_mode!='HEDGING' or not self.verified_symbol:
            raise ValueError('cannot claim broker fills without verified HEDGING symbol contract')
        if p.check_approved is not True or p.send_accepted is not True:
            raise ValueError('OrderSend acceptance alone is not a fill')
        if d.deal_id in self.deal_owner:raise ValueError('duplicate DEAL_ADD')
        if d.time_ms<p.proposed.request_ms or (p.last_deal_ms is not None and d.time_ms<p.last_deal_ms):
            raise ValueError('transaction time cannot precede request/prior deal')
        if p.entry_lots+money(d.lots)>money(p.proposed.lots):raise ValueError('broker filled more lots than requested')
        p.entry_lots+=money(d.lots)
        p.broker_fees+=money(d.fee_cash)
        self.confirmed_fee_cash+=money(d.fee_cash)
        self.confirmed_net_cash+=money(d.fee_cash)
        p.last_deal_ms=d.time_ms
        p.deal_ids.add(d.deal_id)
        self.deal_owner[d.deal_id]=d.order_id
    def modify_stop(self,order_id:str,*,modify_id:str,at_ms:int,proposed_stop_raw:int,
                    broker_accepted:bool,freeze_clear:bool):
        p=self.orders[order_id]
        if not modify_id or modify_id in p.stopped_change_id:raise ValueError('duplicate stop request')
        if type(broker_accepted) is not bool or type(freeze_clear) is not bool or proposed_stop_raw<=0:
            raise ValueError('explicit stop ACK and freeze conditions required')
        if p.entry_lots<=p.close_lots or p.entry_lots==0:raise ValueError('no open fill for stop')
        if p.last_deal_ms is not None and at_ms<p.last_deal_ms:raise ValueError('out-of-order stop change')
        p.stopped_change_id.add(modify_id)
        if broker_accepted and freeze_clear:p.stopped_raw=proposed_stop_raw
        return p.stopped_raw
    def close(self,d:BrokerDeal):
        p=self.orders[d.order_id]
        if self.account_mode!='HEDGING' or not self.verified_symbol:
            raise ValueError('unknown broker-mode semantics')
        if d.deal_id in self.deal_owner:raise ValueError('duplicate close DEAL_ADD')
        if p.last_deal_ms is None or d.time_ms<p.last_deal_ms or p.close_lots+money(d.lots)>p.entry_lots:
            raise ValueError('invalid settlement chronology or overclose')
        p.close_lots+=money(d.lots)
        p.realized_cash+=money(d.realized_cash)
        p.broker_fees+=money(d.fee_cash)
        p.deal_ids.add(d.deal_id)
        p.last_deal_ms=d.time_ms
        self.confirmed_fee_cash+=money(d.fee_cash)
        self.confirmed_net_cash+=money(d.realized_cash)+money(d.fee_cash)
        self.deal_owner[d.deal_id]=d.order_id
    def summary(self):
        open_lots=sum((p.entry_lots-p.close_lots for p in self.orders.values()),Decimal(0))
        return dict(research_event_contract_only=True,real_mt5_connected=False,
             symbol_verified=self.verified_symbol,account_mode=self.account_mode,
             orders=len(self.orders),broker_filled_entries=sum(x.entry_lots>0 for x in self.orders.values()),
             confirmed_deals=len(self.deal_owner),open_lots=str(open_lots),
             confirmed_reported_deal_cash_including_observed_fees=str(self.confirmed_net_cash),
             all_observed_fees=str(self.confirmed_fee_cash),
             cannot_certify_from_original_Dukascopy_ticks=True)
