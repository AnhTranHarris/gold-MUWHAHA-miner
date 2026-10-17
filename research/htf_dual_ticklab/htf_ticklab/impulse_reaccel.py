"""R05 fast impulse -> Fibonacci retracement -> tick reacceleration expert.

Event states are causal and the only emitted action is a SignalIntent.
Use with SharedSignalArbiter and CostAwareLifecycle, NEVER bypass them.
No claim of statistical profitability or native-research implementation parity.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import isfinite
from statistics import median
from .bars import Bar
from .feeds import Quote
from .signal_bus import AccountView, SignalIntent

@dataclass(frozen=True)
class ReaccelConfig:
    source_id: str = "r05_reaccel"
    lots: float = 0.01
    impulse_min: float = 0.30
    efficiency_min: float = 0.55
    atr_min: float = 1.5
    atr_impulse_ratio: float = 0.03
    fib_pullback: float = 0.382
    rebound: float = 0.08
    expiration_ms: int = 8000
    spread_max: float = 0.55
    relative_spread_max: float = 1.5
    relative_quote_activity_min: float = 0.5
    atr_stop_fraction: float = 0.1
    stop_min: float = 0.7
    stop_max: float = 1.6
    reward_multiple: float = 1.6

    def __post_init__(self):
        nums=(self.lots,self.impulse_min,self.efficiency_min,self.atr_min,
              self.atr_impulse_ratio,self.fib_pullback,self.rebound,
              self.spread_max,self.relative_spread_max,
              self.relative_quote_activity_min,self.atr_stop_fraction,
              self.stop_min,self.stop_max,self.reward_multiple)
        if (not self.source_id or any(not isfinite(x) for x in nums) or
            self.lots<=0 or self.impulse_min<=0 or
            not 0<self.efficiency_min<=1 or self.atr_min<0 or
            self.atr_impulse_ratio<0 or not 0<self.fib_pullback<1 or
            self.rebound<=0 or self.expiration_ms<=0 or
            self.spread_max<=0 or self.relative_spread_max<1 or
            self.relative_quote_activity_min<0 or self.atr_stop_fraction<=0 or
            not 0<self.stop_min<=self.stop_max or self.reward_multiple<=0):
            raise ValueError("invalid R05 parameters")

class ImpulseRetracementExpert:
    """Closed S5 arms, observed ticks confirm, account arbiter executes."""
    def __init__(self, config:ReaccelConfig|None=None):
        self.p=config or ReaccelConfig()
        self.closed=deque(maxlen=32)
        self.activity=deque(maxlen=48)
        self.spreads=deque(maxlen=256)
        self.atr=None
        self.atr_bars=0
        self.previous_m5_close=None
        self.h1_close=None
        self.h1_vote=0
        self.arm=None
        self.previous_tick_mid=None
        self.previous_tick_ms=None
        self.counters=dict(arms=0,pullbacks=0,signals=0,expired=0,spread_block=0)

    def on_bar(self,bar:Bar,q:Quote,account:AccountView):
        if bar.end_ms>q.ms:
            raise ValueError("incomplete bar entered signal engine")
        if bar.seconds==300:
            old=self.previous_m5_close
            tr=(max(bar.bid_high-bar.bid_low,abs(bar.bid_high-old),
                    abs(bar.bid_low-old)) if old is not None
                else bar.bid_high-bar.bid_low)
            self.atr=tr if self.atr is None else (13*self.atr+tr)/14
            self.previous_m5_close=bar.bid_close
            self.atr_bars+=1
            return ()
        if bar.seconds==3600:
            mid=(bar.bid_close+bar.ask_close)*0.5
            if self.h1_close is not None:
                self.h1_vote=(1 if mid>self.h1_close
                              else (-1 if mid<self.h1_close else 0))
            self.h1_close=mid
            return ()
        if bar.seconds!=5:
            return ()
        mid=(bar.bid_close+bar.ask_close)*0.5
        old=list(self.closed)
        self.closed.append((bar.start_ms,mid))
        self.activity.append(bar.ticks)
        if (len(old)<3 or account.position_side or account.pending_entry or
            self.atr is None or self.atr_bars<14 or
            q.ms-bar.end_ms>2500):
            return ()
        if bar.start_ms-old[-3][0]>16000:
            self.closed.clear()
            self.arm=None
            return ()
        if self.atr<self.p.atr_min or bar.ticks<(
                sum(self.activity)/len(self.activity)
                *self.p.relative_quote_activity_min):
            return ()
        movement=mid-old[-3][1]
        path=sum(abs(self.closed[i][1]-self.closed[i-1][1])
                 for i in (-3,-2,-1))
        quality=abs(movement)/(path+1e-12)
        if (abs(movement)<max(self.p.impulse_min,
                             self.atr*self.p.atr_impulse_ratio) or
            quality<self.p.efficiency_min):
            return ()
        if self.arm is not None and q.ms<=self.arm["expiry"]:
            return ()
        side=1 if movement>0 else -1
        self.arm={"side":side,"pullback":mid-side*abs(movement)
                  *self.p.fib_pullback,"expiry":q.ms+self.p.expiration_ms,
                  "armed_at":q.ms,"extreme":None,"pullback_hit":False,
                  "atr":self.atr,"quality":quality}
        self.counters["arms"]+=1
        return ()

    def on_tick(self,q:Quote,account:AccountView):
        if self.previous_tick_ms is not None and q.ms<self.previous_tick_ms:
            raise ValueError("tick-order reversal")
        mid=(q.bid+q.ask)*0.5
        spread=q.ask-q.bid
        pre_tick_median=median(self.spreads) if len(self.spreads)>=16 else spread
        previous_mid=self.previous_tick_mid
        self.spreads.append(spread)
        self.previous_tick_mid=mid
        self.previous_tick_ms=q.ms
        if account.position_side or account.pending_entry:
            self.arm=None
            return ()
        arm=self.arm
        if arm is None:
            return ()
        if q.ms>arm["expiry"]:
            self.counters["expired"]+=1
            self.arm=None
            return ()
        if q.ms<=arm["armed_at"] or previous_mid is None:
            return ()
        if (spread>self.p.spread_max or
            spread>max(.02,pre_tick_median*self.p.relative_spread_max)):
            self.counters["spread_block"]+=1
            return ()
        side=arm["side"]
        if not arm["pullback_hit"]:
            if ((side==1 and mid<=arm["pullback"]) or
                (side==-1 and mid>=arm["pullback"])):
                arm["pullback_hit"]=True
                arm["extreme"]=mid
                self.counters["pullbacks"]+=1
            return ()
        if side==1:arm["extreme"]=min(arm["extreme"],mid)
        else:arm["extreme"]=max(arm["extreme"],mid)
        if (side*(mid-arm["extreme"])<self.p.rebound or
            side*(mid-previous_mid)<=0):
            return ()
        stop=max(self.p.stop_min,min(self.p.stop_max,
                                    arm["atr"]*self.p.atr_stop_fraction))
        priority=20+int(arm["quality"]*10)+(2 if side==self.h1_vote else 0)
        self.arm=None
        self.counters["signals"]+=1
        return (SignalIntent(source_id=self.p.source_id,
            observed_ms=q.ms,side=side,lots=self.p.lots,
            stop_distance=stop,target_distance=stop*self.p.reward_multiple,
            priority=priority,reason="impulse_fib_pullback_reaccel"),)
