"""GRID0259 complete-source-to-quote *hypothetical* funded physics sandbox.

Never opens an actual order or treats an R9 OVERFIT oracle as an entry. Separate
from the original FourSessionV1 and G0 source router; single shared account,
no loss-based size increase, no artificial intragap fills, original Bid/Ask.

Only an actual verified Coinexx contract specification can certify broker
compatibility; all demonstration profiles are explicitly ASSUMED. Simulation
requires caller-provided observed future ticks, never predicts next tick.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from collections import Counter

RAW=1000
@dataclass(frozen=True)
class BrokerPhysics:
    contract_oz_per_lot:float
    leverage:float
    min_lot:float
    lot_step:float
    min_stop_raw:int
    roundtrip_usd_per_lot:float
    specs_broker_verified:bool=False
    source_note:str='ASSUMED_HYPOTHETICAL_RESEARCH_ONLY'
    def __post_init__(self):
        if min(self.contract_oz_per_lot,self.leverage,self.min_lot,self.lot_step)<=0:
            raise ValueError('invalid broker contract or leverage')
        if self.min_stop_raw<=0 or self.roundtrip_usd_per_lot<0:
            raise ValueError('broker stops and fee must be bounded')

@dataclass(frozen=True)
class Quote:
    utc_ms:int
    bid_raw:int
    ask_raw:int
    broker_tradable:bool=True

@dataclass(frozen=True)
class ResearchIntent:
    event_id:str
    source:str
    known_at_ms:int
    side:int
    stop_distance_raw:int
    max_hold_ms:int
    research_lot:float=0.01
    min_latency_ms:int=250
    ttl_ms:int=2000

@dataclass
class OpenResearchPosition:
    event_id:str
    source:str
    side:int
    lot:float
    qty_oz:float
    entry_ms:int
    entry_raw:int
    stop_raw:int
    deadline_ms:int
    margin_usd:float

@dataclass(frozen=True)
class ResearchSettlement:
    event_id:str
    source:str
    side:int
    entry_ms:int
    exit_ms:int
    entry_raw:int
    observed_exit_raw:int
    net_usd:float
    fee_usd:float
    reason:str
    hypothetical:bool=True

class ResearchFundingEngine:
    def __init__(self,*,starting_cash_usd:float,physics:BrokerPhysics,
                 max_shared_positions:int=16,maintenance_margin_fraction:float=0.5):
        if starting_cash_usd<=0 or max_shared_positions<=0:
            raise ValueError('initial margin cash and slots required')
        if not 0<maintenance_margin_fraction<=1:raise ValueError('maintenance fraction')
        self.initial_cash=float(starting_cash_usd)
        self.cash=self.initial_cash
        self.spec=physics
        self.cap=max_shared_positions
        self.maintenance_margin_fraction=maintenance_margin_fraction
        self.open:list[OpenResearchPosition]=[]
        self.waiting:list[ResearchIntent]=[]
        self.settlements:list[ResearchSettlement]=[]
        self.seen_ids:set[str]=set()
        self.last_quote:Optional[Quote]=None
        self.prev_execution_ms:Optional[int]=None
        self.peak_marked_equity=self.initial_cash
        self.max_marked_drawdown=0.
        self.rejections=Counter()
        self.high_water_open=0
    def offer(self,signal:ResearchIntent):
        if signal.event_id in self.seen_ids:raise ValueError('duplicate event ID')
        if (signal.side not in (-1,1) or signal.stop_distance_raw<=0
                or signal.max_hold_ms<=0 or signal.known_at_ms<0 or
                signal.min_latency_ms<0 or signal.ttl_ms<signal.min_latency_ms):
            raise ValueError('invalid bounded source lifecycle')
        if self.last_quote and signal.known_at_ms<self.last_quote.utc_ms:
            raise ValueError('cannot backdate pending source after observation')
        ratio=signal.research_lot/self.spec.lot_step
        if (signal.research_lot+1e-12<self.spec.min_lot
                or abs(ratio-round(ratio))>1e-7):
            raise ValueError('contract lot minimum/step violated')
        self.seen_ids.add(signal.event_id)
        self.waiting.append(signal)
    def _margin(self,price_raw:int,lot:float)->float:
        return price_raw/RAW*self.spec.contract_oz_per_lot*lot/self.spec.leverage
    def _mark(self,q:Quote)->float:
        floating=sum((q.bid_raw-p.entry_raw if p.side==1 else
                      p.entry_raw-q.ask_raw)/RAW*p.qty_oz for p in self.open)
        return self.cash+floating
    def _used_margin(self)->float:return sum(p.margin_usd for p in self.open)
    def _close(self,p:OpenResearchPosition,q:Quote,reason:str):
        price=q.bid_raw if p.side==1 else q.ask_raw
        fee=self.spec.roundtrip_usd_per_lot*p.lot
        net=(price-p.entry_raw)/RAW*p.qty_oz*p.side-fee
        self.cash+=net
        self.settlements.append(ResearchSettlement(p.event_id,p.source,p.side,
             p.entry_ms,q.utc_ms,p.entry_raw,price,net,fee,reason))
    def on_observed_quote(self,q:Quote)->tuple[ResearchSettlement,...]:
        if q.utc_ms<0 or q.bid_raw<=0 or q.ask_raw<q.bid_raw:
            raise ValueError('invalid quoted market price')
        if self.last_quote and q.utc_ms<self.last_quote.utc_ms:
            raise ValueError('reversed actual tick stream')
        self.last_quote=q
        before=len(self.settlements)
        active=[]
        for p in self.open:
            mark=q.bid_raw if p.side==1 else q.ask_raw
            hit=mark<=p.stop_raw if p.side==1 else mark>=p.stop_raw
            if hit or q.utc_ms>=p.deadline_ms:
                self._close(p,q,'OBSERVED_GAP_SLIPPED_STOP' if hit else 'OBSERVED_TIME_EXPIRY')
            else:active.append(p)
        self.open=active
        equity=self._mark(q)
        if self.open and equity<self._used_margin()*self.maintenance_margin_fraction:
            for p in self.open:self._close(p,q,'OBSERVED_MARGIN_STOP_OUT')
            self.open.clear()
            equity=self.cash
        eligible=[]
        for signal in self.waiting:
            age=q.utc_ms-signal.known_at_ms
            if age<signal.min_latency_ms:
                eligible.append(signal);continue
            if age>signal.ttl_ms:
                self.rejections['stale']+=1;continue
            if not q.broker_tradable:
                eligible.append(signal);continue
            if signal.stop_distance_raw<self.spec.min_stop_raw:
                self.rejections['broker_min_stop']+=1;continue
            if len(self.open)>=self.cap:
                self.rejections['source_capacity']+=1;continue
            if self.prev_execution_ms==q.utc_ms:
                self.rejections['same_millisecond']+=1;continue
            price=q.ask_raw if signal.side==1 else q.bid_raw
            margin=self._margin(price,signal.research_lot)
            free=self._mark(q)-self._used_margin()
            # Reject if the account cannot fund margin plus entrance spread/fees.
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
        self.waiting=eligible
        eq=self._mark(q)
        self.peak_marked_equity=max(self.peak_marked_equity,eq)
        self.max_marked_drawdown=max(self.max_marked_drawdown,self.peak_marked_equity-eq)
        return tuple(self.settlements[before:])
    def summary(self)->dict:
        net=sum(x.net_usd for x in self.settlements)
        return {'research_only':True,'broker_contract_verified':self.spec.specs_broker_verified,
          'contract_source':self.spec.source_note,'funded_broker_orders_placed':0,
          'initial_usd':self.initial_cash,'realized_usd':self.cash,
          'closed_count':len(self.settlements),'open_count':len(self.open),
          'net_research_usd':net,'gross_profit_usd':sum(max(0,x.net_usd) for x in self.settlements),
          'gross_loss_usd':sum(min(0,x.net_usd) for x in self.settlements),
          'max_marked_dd_usd':self.max_marked_drawdown,'peak_slots':self.high_water_open,
          'last_used_margin_usd':self._used_margin(),
          'denials':dict(self.rejections),'live_trading_enabled':False}
