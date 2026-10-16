"""Demonstration-only strategy: *not* an R9 clone or investor-approved strategy."""
from __future__ import annotations
from datetime import datetime, timezone
from .bars import Bar
from .feeds import Quote

class NoTrades:
    def on_bar(self, bar: Bar, q: Quote, engine): pass
    def on_tick(self, q: Quote, engine): pass

class ClosedBarImpulseDemo:
    """Optional smoke-test: a completed S15 candle triggers a next-tick request.

    This is a diagnostic harness to exercise accounting and fills, not an alpha claim.
    """
    def __init__(self,*,lots:float=0.01,impulse_price:float=0.5,
                 stop_price:float=1.0,target_price:float=1.5,
                 cooldown_ms:int=120_000,max_entries_per_day:int=40):
        self.lots=lots;self.impulse_price=impulse_price
        self.stop_price=stop_price;self.target_price=target_price
        self.cooldown_ms=cooldown_ms;self.max_entries_per_day=max_entries_per_day
        self.last_sent_ms=-10**30;self.day=None;self.daily_sent=0
    def on_bar(self,bar:Bar,q:Quote,engine):
        if bar.seconds!=15: return
        day=datetime.fromtimestamp(q.ms/1000,timezone.utc).date()
        if day!=self.day: self.day=day;self.daily_sent=0
        if (engine.position or engine.pending or q.ms-self.last_sent_ms<self.cooldown_ms or
            self.daily_sent>=self.max_entries_per_day): return
        if q.ask-q.bid>engine.cfg.max_spread_price:return
        impulse=bar.bid_close-bar.bid_open
        if abs(impulse)<self.impulse_price: return
        side=1 if impulse>0 else -1
        engine.request_entry(side,self.lots,stop_distance=self.stop_price,
                             target_distance=self.target_price,reason='closed_s15_demo')
        self.last_sent_ms=q.ms;self.daily_sent+=1
    def on_tick(self,q:Quote,engine): pass
