"""R15 causal, genuinely tick-driven R9-inspired event specialist for XAUUSD.

* R9 original source stays read-only.
* The first quote of each observed UTC minute establishes an in-memory bracket.
* Exactly completed one-second bid quote bars determine the 10s directional
  movement, path efficiency, observed range and turning-point count.
* The current quote triggers a virtual bracket and creates an INTENT ONLY.
  The shared arbiter and Replay decide risk, latency and whether it is filled.
* After a filled position actually disappears, the source arms an OPPOSITE
  direction within that minute, limited by max_rearms.
* No hindsight minute high/low, source mixing, fictional fills or forced volume.

This is a separate strategy hypothesis, NOT a claim the R9 synthetic profit
is executable on the two independent recorded broker quote sources.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import isfinite
from .feeds import Quote
from .bars import Bar
from .signal_bus import AccountView, SignalIntent


@dataclass(frozen=True)
class TickRearmParameters:
    source_id: str = "r15_tick_rearm"
    lots: float = 0.01
    bracket_halfwidth: float = 0.15
    lookback_seconds: int = 10
    min_displacement: float = 0.15
    min_efficiency: float = 0.70
    min_range: float = 0.50
    max_turns: int = 9
    max_rearms: int = 3
    max_spread: float = 0.90
    min_atr: float = 0.0
    stop_distance: float = 1.80
    target_distance: float = 5.0
    priority: int = 18

    def __post_init__(self):
        if (not self.source_id or
            not all(isfinite(v) for v in (
                self.lots,self.bracket_halfwidth,self.min_displacement,
                self.min_efficiency,self.min_range,self.max_spread,
                self.min_atr,self.stop_distance,self.target_distance)) or
            min(self.lots,self.bracket_halfwidth,self.min_displacement,
                self.min_range,self.max_spread,self.stop_distance,
                self.target_distance)<=0 or
            self.min_atr<0 or not 0<self.min_efficiency<=1 or
            self.lookback_seconds<3 or self.max_turns<0 or self.max_rearms<0):
            raise ValueError("invalid research tick-rearm geometry")


class TickRearmSource:
    def __init__(self, params: TickRearmParameters | None = None):
        self.p=params or TickRearmParameters()
        self.broker=None
        self.last_ms=-1
        self.minute=None
        self.minute_mid=0.
        self.mode=2
        self.rearms=0
        self._seen_side=0
        self._current_sec=None
        self._open=self._hi=self._lo=self._close=0.
        self.completed=deque(maxlen=max(32,self.p.lookback_seconds+2))
        self.prev_m5=None
        self.m5_atr=None
        self.counts=dict(armed=0,expired=0,signals=0,
                         opposite_rearms=0,spread_rejections=0,
                         s1_rejections=0,atr_rejections=0,
                         broker_rejections=0)

    def on_bar(self,bar:Bar,q:Quote,account:AccountView):
        if bar.end_ms>q.ms:raise ValueError("future completed bar")
        if self.broker is not None and self.broker!=q.broker:
            raise ValueError("cross-broker bar")
        if bar.seconds==300:
            prev=self.prev_m5
            tr=(bar.bid_high-bar.bid_low if prev is None else
                max(bar.bid_high-bar.bid_low,abs(bar.bid_high-prev),
                    abs(bar.bid_low-prev)))
            self.m5_atr=tr if self.m5_atr is None else (
                (13*self.m5_atr+tr)/14)
            self.prev_m5=bar.bid_close
        return ()

    def _completed_second(self,q:Quote):
        sec=q.ms//1000
        if self._current_sec is None:
            self._current_sec=sec
            self._open=self._hi=self._lo=self._close=q.bid
            return
        if sec!=self._current_sec:
            self.completed.append((self._current_sec,self._open,
                                   self._hi,self._lo,self._close))
            self._current_sec=sec
            self._open=self._hi=self._lo=self._close=q.bid
        else:
            self._hi=max(self._hi,q.bid)
            self._lo=min(self._lo,q.bid)
            self._close=q.bid

    def _quality(self):
        p=self.p
        if len(self.completed)<p.lookback_seconds:return 0
        a=list(self.completed)[-p.lookback_seconds:]
        if any(a[k][0]-a[k-1][0]!=1 for k in range(1,len(a))):
            return 0
        close0=a[0][4];displacement=a[-1][4]-close0
        if abs(displacement)<p.min_displacement:return 0
        path=0.;last_direction=0;turns=0
        for k in range(1,len(a)):
            change=a[k][4]-a[k-1][4]
            path+=abs(change)
            sign=1 if change>0 else (-1 if change<0 else 0)
            if sign:
                if last_direction and sign!=last_direction:turns+=1
                last_direction=sign
        if abs(displacement)/(path+1e-9)<p.min_efficiency or turns>p.max_turns:
            return 0
        if max(b[2] for b in a)-min(b[3] for b in a)<p.min_range:
            return 0
        return 1 if displacement>0 else -1

    def on_tick(self,q:Quote,account:AccountView):
        if self.broker is not None and q.broker!=self.broker:
            raise ValueError("cross-broker tick")
        if not isinstance(q.ms,int) or q.ms<self.last_ms:
            raise ValueError("noncausal tick ordering")
        self.broker=q.broker
        self.last_ms=q.ms
        minute=q.ms//60000
        if minute!=self.minute:
            self.minute=minute
            self.minute_mid=(q.ask+q.bid)*.5
            self.mode=2
            self.rearms=0
            self.counts['armed']+=1
        self._completed_second(q)
        # Distinguish a FILL (nonzero account position observed) from a
        # merely proposed signal; a rejected order must not consume a rearm.
        if account.position_side:
            self._seen_side=account.position_side
            return ()
        if self._seen_side:
            just_closed=self._seen_side
            self._seen_side=0
            self.rearms+=1
            if self.rearms>self.p.max_rearms:
                self.mode=0
                self.counts['expired']+=1
            else:
                self.mode=-just_closed
                self.counts['opposite_rearms']+=1
        if self.mode==0 or account.pending_entry:
            return ()
        if q.ask-q.bid>self.p.max_spread:
            self.counts['spread_rejections']+=1
            return ()
        if self.p.min_atr and (
            self.m5_atr is None or self.m5_atr<self.p.min_atr):
            self.counts['atr_rejections']+=1
            return ()
        side=self._quality()
        if not side:
            self.counts['s1_rejections']+=1
            return ()
        if self.mode!=2 and side!=self.mode:return ()
        if side==1 and q.ask<self.minute_mid+self.p.bracket_halfwidth:return ()
        if side==-1 and q.bid>self.minute_mid-self.p.bracket_halfwidth:return ()
        self.counts['signals']+=1
        return (SignalIntent(
            source_id=self.p.source_id,observed_ms=q.ms,side=side,
            lots=self.p.lots,stop_distance=self.p.stop_distance,
            target_distance=self.p.target_distance,
            priority=self.p.priority,reason="causal_tick_minute_bracket_s1"),)
