"""Broker-acknowledged, genuinely paid-close Watchdog ownership contract.

No simulator P&L or planned TP/SL can mint renewal permission. Only:
(1) registered parent intent, (2) actual unique IN and OUT DEAL_ADD events,
(3) fully observed original .01 volume, (4) explicit verified broker-history
settlement matching all fees, (5) a LATER observed quote, and (6) one-time
consumption may release a child *proposal*. L2-L7 still owns any real order.
MT5 integration must pass transaction ARRIVAL time, not backdated deal time.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

VOLUME_EPS=Decimal('0.00000001')

def vol(x):
    d=Decimal(str(x))
    if not d.is_finite() or d<=0:raise ValueError('nonpositive/invalid volume')
    return d

@dataclass(frozen=True)
class DealAck:
    deal_id:int
    position_id:int
    entry_kind:str
    volume:Decimal
    net_cash:Decimal
    observed_ms:int

@dataclass
class Parent:
    position_id:int
    desk:str
    expected:Decimal
    intent_ms:int
    opened:Decimal=Decimal(0)
    closed:Decimal=Decimal(0)
    net_cash:Decimal=Decimal(0)
    last_observed_ms:int=0
    settlement_verified:bool=False
    canceled:bool=False

@dataclass
class RenewalPermit:
    position_id:int
    desk:str
    granted_ms:int
    expires_ms:int
    net_cash:Decimal
    consumed:bool=False

class PaidCloseWatchdog:
    def __init__(self,*,permit_ttl_ms:int=30_000,expected_lot:float=.01):
        if permit_ttl_ms<=0:raise ValueError('permit TTL must be positive')
        self.permit_ttl_ms=permit_ttl_ms
        self.expected_lot=vol(expected_lot)
        self.parents:dict[int,Parent]={}
        self.orphans:dict[int,list[DealAck]]={}
        self.permits:dict[int,RenewalPermit]={}
        self.seen_deals:set[int]=set()
        self.last_observed_ms:Optional[int]=None
        self.duplicates=0
        self.orphan_deals=0
        self.settlements=0
        self.denied_nonprofit=0

    def _clock(self,observed_ms:int):
        if not isinstance(observed_ms,int) or observed_ms<0:
            raise ValueError('invalid transaction observation timestamp')
        if self.last_observed_ms is not None and observed_ms<self.last_observed_ms:
            raise ValueError('out-of-order OBSERVATION (broker deal time may differ)')
        self.last_observed_ms=observed_ms

    def register_parent(self,position_id:int,desk:str,expected_volume:float,observed_ms:int):
        self._clock(observed_ms)
        if not isinstance(position_id,int) or position_id<=0 or not desk:
            raise ValueError('invalid broker position/desk')
        if position_id in self.parents:raise ValueError('duplicate parent intent')
        amount=vol(expected_volume)
        if amount!=self.expected_lot:raise ValueError('fixed-lot policy violated')
        p=Parent(position_id,desk,amount,observed_ms,last_observed_ms=observed_ms)
        self.parents[position_id]=p
        # OUT can be delivered before IN, but only observed settlement may grant.
        for d in self.orphans.pop(position_id,[]):self._apply(p,d)
        return p

    def _apply(self,p:Parent,d:DealAck):
        if p.canceled:raise ValueError('deal on canceled parent')
        new_open=p.opened+(d.volume if d.entry_kind=='IN' else Decimal(0))
        new_close=p.closed+(d.volume if d.entry_kind=='OUT' else Decimal(0))
        if d.entry_kind not in ('IN','OUT'):
            raise ValueError('unsupported deal entry type')
        if new_open>p.expected+VOLUME_EPS or new_close>p.expected+VOLUME_EPS:
            raise ValueError('broker deal volume exceeds parent .01 lot')
        p.opened=new_open;p.closed=new_close
        p.net_cash+=d.net_cash
        p.last_observed_ms=max(p.last_observed_ms,d.observed_ms)

    def on_deal_add(self,*,deal_id:int,position_id:int,entry_kind:str,volume:float,
                    profit:float=0.,commission:float=0.,swap:float=0.,fee:float=0.,
                    observed_ms:int):
        self._clock(observed_ms)
        if not isinstance(deal_id,int) or deal_id<=0 or not isinstance(position_id,int) or position_id<=0:
            raise ValueError('invalid broker deal identity')
        if entry_kind not in ('IN','OUT'):raise ValueError('unsupported broker deal entry')
        if deal_id in self.seen_deals:
            self.duplicates+=1
            return False
        amount=vol(volume)
        cash=sum((Decimal(str(x)) for x in (profit,commission,swap,fee)),Decimal(0))
        if not cash.is_finite():raise ValueError('invalid cash settlement')
        d=DealAck(deal_id,position_id,entry_kind,amount,cash,observed_ms)
        p=self.parents.get(position_id)
        if p is None:
            self.orphans.setdefault(position_id,[]).append(d)
            self.orphan_deals+=1
        else:self._apply(p,d)
        self.seen_deals.add(deal_id)
        return True

    def confirm_settlement(self,position_id:int,*,observed_ms:int,
                           verified_broker_history:bool,confirmed_net_cash:float):
        self._clock(observed_ms)
        p=self.parents.get(position_id)
        if p is None or p.canceled or p.settlement_verified:return None
        if not verified_broker_history:return None
        if abs(p.opened-p.expected)>VOLUME_EPS or abs(p.closed-p.expected)>VOLUME_EPS:
            return None
        confirmed=Decimal(str(confirmed_net_cash))
        if not confirmed.is_finite() or abs(confirmed-p.net_cash)>Decimal('.01'):
            return None
        p.settlement_verified=True
        self.settlements+=1
        if confirmed<=0:
            self.denied_nonprofit+=1
            return None
        permit=RenewalPermit(position_id,p.desk,observed_ms,
                             observed_ms+self.permit_ttl_ms,confirmed)
        self.permits[position_id]=permit
        return permit

    def permit_ready(self,desk:str,quote_ms:int,*,broker_tradable:bool=True)->bool:
        if not broker_tradable:return False
        return any(x.desk==desk and not x.consumed and
                   x.granted_ms<quote_ms<=x.expires_ms for x in self.permits.values())

    def consume(self,desk:str,quote_ms:int,*,broker_tradable:bool=True):
        if not broker_tradable:return None
        for x in self.permits.values():
            if x.desk==desk and not x.consumed and x.granted_ms<quote_ms<=x.expires_ms:
                x.consumed=True
                return x
        return None

    def cancel_parent(self,position_id:int):
        p=self.parents.get(position_id)
        if p:p.canceled=True
        self.permits.pop(position_id,None)

    def stats(self):
        return dict(parent_intents=len(self.parents),unique_deals=len(self.seen_deals),
            orphan_deals=self.orphan_deals,duplicate_deals=self.duplicates,
            verified_settlements=self.settlements,positive_permits=len(self.permits),
            consumed_permits=sum(p.consumed for p in self.permits.values()),
            denied_nonprofit=self.denied_nonprofit)
