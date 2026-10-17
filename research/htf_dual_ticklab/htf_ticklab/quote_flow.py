"""Causal retail bid/ask quote-update microstructure.

Quotes are not exchange order flow. Features become available only at the
first subsequent quote following the completed observed second.
"""
from dataclasses import dataclass
from math import isfinite
from collections import deque

@dataclass(frozen=True, slots=True)
class QuoteFlowState:
    broker: str
    second: int
    total_updates: int
    aligned_updates: int
    bid_only_net: int
    ask_only_net: int
    signed_flow: int
    spread_compression: float
    mid_range: float

    @property
    def quote_pressure(self):
        return (self.bid_only_net-self.ask_only_net)/max(1,self.total_updates)

    @property
    def normalized_flow(self):
        return self.signed_flow/max(1,self.total_updates)

class ClosedQuoteFlow:
    def __init__(self, history=300):
        if history < 2:
            raise ValueError("history must be >= 2")
        self.history=deque(maxlen=history)
        self.prev=None
        self.cur=None
        self.cur_start_spread=0.
        self.cur_last_spread=0.
        self.bid_only=0
        self.ask_only=0
        self.signed=0
        self.both=0
        self.n=0
        self.max_mid=-float("inf")
        self.min_mid=float("inf")

    def update(self, quote):
        if (not quote.broker or not isinstance(quote.ms,int) or quote.ms<0 or
            not all(isfinite(x) for x in (quote.bid,quote.ask)) or
            quote.bid<=0 or quote.bid>quote.ask):
            raise ValueError("invalid broker quote")
        if self.prev is not None:
            if quote.broker!=self.prev.broker:
                raise ValueError("cross-broker tape prohibited")
            if quote.ms<self.prev.ms:
                raise ValueError("out-of-order tick")
        second=quote.ms//1000
        result=None
        if self.cur is None:
            self.cur=second
            self.cur_start_spread=quote.ask-quote.bid
        elif second!=self.cur:
            result=QuoteFlowState(
                self.prev.broker,self.cur,self.n,self.both,self.bid_only,
                self.ask_only,self.signed,
                self.cur_start_spread-self.cur_last_spread,
                max(0.,self.max_mid-self.min_mid))
            self.history.append(result)
            self.cur=second
            self.cur_start_spread=quote.ask-quote.bid
            self.bid_only=self.ask_only=self.signed=self.both=self.n=0
            self.max_mid=-float("inf")
            self.min_mid=float("inf")
        if self.prev is not None:
            db=quote.bid-self.prev.bid
            da=quote.ask-self.prev.ask
            if db>0 and da==0:self.bid_only+=1
            elif db<0 and da==0:self.bid_only-=1
            if da>0 and db==0:self.ask_only+=1
            elif da<0 and db==0:self.ask_only-=1
            if db*da>0:self.both+=1
            self.signed+=int(db+da>0)-int(db+da<0)
        mid=(quote.bid+quote.ask)/2
        self.max_mid=max(self.max_mid,mid)
        self.min_mid=min(self.min_mid,mid)
        self.n+=1
        self.cur_last_spread=quote.ask-quote.bid
        self.prev=quote
        return result

    def snapshot(self):
        return self.history[-1] if self.history else None
