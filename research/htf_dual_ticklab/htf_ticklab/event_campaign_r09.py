"""R09 event-campaign source: macro context -> meta hypothesis -> micro execution.

Independent source compatible with SharedSignalArbiter. Produces *order intents*,
not fills. Its price-improvement/reacceleration decisions use only observed
quotes and completed S5/M5 bars; all orders remain centralized in Replay.
Fibonacci is a price-location state, ATR an exit/stop geometry, RSI a contextual
priority modifier and quote-anchored mean a contextual displacement feature.
This is a new research hypothesis, not a tested profitable configuration.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from .bars import Bar
from .feeds import Quote
from .signal_bus import AccountView, SignalIntent


@dataclass(frozen=True)
class CampaignParameters:
    source_id: str = "campaign_r09"
    lots: float = 0.01
    min_impulse_price: float = 0.25
    fib_retracement: float = 0.382
    rebound_price: float = 0.10
    max_arm_ms: int = 6000
    maximum_spread_price: float = 1.0
    stop_distance_price: float = 1.5
    target_distance_price: float = 3.0
    priority: int = 1

    def __post_init__(self):
        if (not self.source_id or
            not all(isfinite(x) for x in (
                self.lots, self.min_impulse_price, self.fib_retracement,
                self.rebound_price, self.maximum_spread_price,
                self.stop_distance_price, self.target_distance_price)) or
            self.lots<=0 or self.min_impulse_price<=0 or
            not 0<self.fib_retracement<1 or self.rebound_price<=0 or
            self.maximum_spread_price<=0 or
            self.stop_distance_price<=0 or self.target_distance_price<=0 or
            self.max_arm_ms<=0):
            raise ValueError("invalid event-campaign parameter set")


class EventCampaignSource:
    """Use a completed S5 impulse to ARM, then require pullback and rebound.

    A new S5 event is not counted as a trade. An intent appears only on the
    first eligible later tick; the central arbiter may still refuse it for
    risk, margin, shared occupancy or broker execution constraints.
    """

    def __init__(self, parameters: CampaignParameters | None = None):
        self.p=parameters or CampaignParameters()
        self.broker: str | None=None
        self.armed_side=0
        self.armed_ms=0
        self.extreme_mid=0.
        self.pullback_mid=0.
        self.phase="IDLE"
        self.atr5: float | None=None
        self.last_m5_close: float | None=None
        self.m5_bars=0
        self.rsi_g=None
        self.rsi_l=None
        self.rsi=50.
        self.events={"armed":0,"pullbacks":0,"reaccelerations":0,
                     "expired":0,"spread_cancelled":0}

    def on_bar(self,bar:Bar,q:Quote,account:AccountView):
        if bar.end_ms>q.ms:
            raise ValueError("future/incomplete candle")
        if self.broker is not None and self.broker!=q.broker:
            raise ValueError("cross-broker state is forbidden")
        self.broker=q.broker
        if bar.seconds==300:
            prev=self.last_m5_close
            tr=(bar.bid_high-bar.bid_low if prev is None
                else max(bar.bid_high-bar.bid_low,
                         abs(bar.bid_high-prev),abs(bar.bid_low-prev)))
            self.atr5=tr if self.atr5 is None else (13*self.atr5+tr)/14
            if prev is not None:
                delta=bar.bid_close-prev
                g=max(delta,0.);l=max(-delta,0.)
                self.rsi_g=g if self.rsi_g is None else (13*self.rsi_g+g)/14
                self.rsi_l=l if self.rsi_l is None else (13*self.rsi_l+l)/14
                self.rsi=100*self.rsi_g/max(self.rsi_g+self.rsi_l,1e-9)
            self.last_m5_close=bar.bid_close
            self.m5_bars+=1
        if bar.seconds!=5 or account.position_side!=0 or account.pending_entry:
            return ()
        impulse=bar.bid_close-bar.bid_open
        atr_ref=(self.atr5/20 if self.m5_bars>=14 else 0.)
        floor=max(self.p.min_impulse_price,atr_ref)
        if abs(impulse)<floor or q.ask-q.bid>self.p.maximum_spread_price:
            return ()
        self.armed_side=1 if impulse>0 else -1
        self.armed_ms=q.ms
        self.extreme_mid=(q.bid+q.ask)/2
        self.pullback_mid=self.extreme_mid
        self.phase="ARMED"
        self.events["armed"]+=1
        return ()

    def on_tick(self,q:Quote,account:AccountView):
        if self.broker is not None and self.broker!=q.broker:
            raise ValueError("cross-broker state is forbidden")
        self.broker=q.broker
        if self.phase=="IDLE":return ()
        if q.ms<self.armed_ms:
            raise ValueError("reordered campaign chronology")
        if q.ms-self.armed_ms>self.p.max_arm_ms:
            self.phase="IDLE"
            self.events["expired"]+=1
            return ()
        if account.position_side!=0 or account.pending_entry:
            self.phase="IDLE"
            return ()
        if q.ask-q.bid>self.p.maximum_spread_price:
            self.phase="IDLE"
            self.events["spread_cancelled"]+=1
            return ()
        px=(q.ask+q.bid)/2
        side=self.armed_side
        if self.phase=="ARMED":
            # A genuinely observed price improvement after the impulse.
            improvement=side*(self.extreme_mid-px)
            if improvement>=self.p.min_impulse_price*self.p.fib_retracement:
                self.phase="PULLBACK"
                self.pullback_mid=px
                self.events["pullbacks"]+=1
            return ()
        if side*(self.pullback_mid-px)>0:
            self.pullback_mid=px
            return ()
        if side*(px-self.pullback_mid)<self.p.rebound_price:
            return ()
        if q.ms==self.armed_ms:
            return ()
        self.phase="IDLE"
        self.events["reaccelerations"]+=1
        # Macro context changes *priority*, not global permission. A rich
        # scientific model may later rank this campaign against specialists.
        context=1 if (side==1 and self.rsi>=50 or
                      side==-1 and self.rsi<50) else 0
        return (SignalIntent(
            source_id=self.p.source_id,observed_ms=q.ms,side=side,
            lots=self.p.lots,stop_distance=self.p.stop_distance_price,
            target_distance=self.p.target_distance_price,
            priority=self.p.priority+context,
            reason="fib_impulse_pullback_reacceleration"),)
