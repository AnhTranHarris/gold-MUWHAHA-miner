"""R14 research-only price acquisition: causal opportunity -> executable quote.

Wrap any SignalSource. Buy decisions wait for an observed improvement to ASK,
sell decisions wait for an improvement to BID; the order intent is submitted on
a strictly later quote. No guaranteed resting-limit fills or fictional maker
rebates. The shared arbiter still controls capital, queueing and actual fills.
This ports a mechanism hypothesis from the R14 standalone native-tick replay;
quantitative parity to that experimental simulator is NOT certified.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from .signal_bus import SignalIntent


@dataclass(frozen=True)
class PriceAcquisitionConfig:
    improvement_price: float = 0.30
    expiry_ms: int = 3000
    max_spread: float = 2.0

    def __post_init__(self):
        if (not all(isfinite(v) for v in (self.improvement_price,self.max_spread))
            or self.improvement_price<=0 or self.max_spread<=0
            or self.expiry_ms<=0):
            raise ValueError("invalid observation-based acquisition contract")


class CausalPriceAcquisition:
    def __init__(self, source, cfg: PriceAcquisitionConfig | None=None):
        self.source=source
        self.cfg=cfg or PriceAcquisitionConfig()
        self.broker=None
        self.armed=None
        self.reference=0.
        self.start_ms=0
        self.last_ms=-1
        self.cross_ms=None
        self.counters=dict(armed=0,improved=0,emitted=0,expired=0,
                           busy=0,spread_rejected=0)

    def _clock(self, quote):
        if not quote.broker or not isinstance(quote.ms,int):
            raise ValueError("invalid quote")
        if self.broker is not None and quote.broker!=self.broker:
            raise ValueError("cross-broker quote")
        if quote.ms<self.last_ms:
            raise ValueError("out-of-order observation")
        self.broker=quote.broker
        self.last_ms=quote.ms

    def _absorb(self, proposals,quote,account):
        for p in proposals or ():
            if not isinstance(p,SignalIntent):
                raise TypeError("unexpected source intent")
            if p.kind!="entry":
                # Important: protective EXIT intents cannot be postponed.
                return (p,)
            if self.armed is not None or account.position_side!=0 or account.pending_entry:
                self.counters['busy']+=1
                continue
            if p.observed_ms>quote.ms:
                raise ValueError("future source signal")
            if quote.ask-quote.bid>self.cfg.max_spread:
                self.counters['spread_rejected']+=1
                continue
            self.armed=p
            self.reference=quote.ask if p.side==1 else quote.bid
            self.start_ms=quote.ms
            self.cross_ms=None
            self.counters['armed']+=1
        return ()

    def on_bar(self,bar,quote,account):
        self._clock(quote)
        if bar.end_ms>quote.ms:
            raise ValueError("future completed bar")
        return self._absorb(self.source.on_bar(bar,quote,account),quote,account)

    def on_tick(self,quote,account):
        self._clock(quote)
        proposal=self._absorb(self.source.on_tick(quote,account),quote,account)
        if proposal:
            return proposal
        p=self.armed
        if p is None:
            return ()
        if account.position_side!=0 or account.pending_entry:
            self.armed=None
            self.counters['busy']+=1
            return ()
        if quote.ms-self.start_ms>self.cfg.expiry_ms:
            self.armed=None
            self.counters['expired']+=1
            return ()
        if quote.ask-quote.bid>self.cfg.max_spread:
            self.armed=None
            self.counters['spread_rejected']+=1
            return ()
        if self.cross_ms is None:
            at=quote.ask if p.side==1 else quote.bid
            if (p.side==1 and at<=self.reference-self.cfg.improvement_price or
                p.side==-1 and at>=self.reference+self.cfg.improvement_price):
                self.cross_ms=quote.ms
                self.counters['improved']+=1
            return ()
        # Must be a later observed tick, *including when time_msc is equal*.
        # When the broker reports equal milliseconds, conservatively wait.
        if quote.ms<=self.cross_ms:
            return ()
        self.armed=None
        self.counters['emitted']+=1
        from dataclasses import replace
        return (replace(p,observed_ms=quote.ms),)
