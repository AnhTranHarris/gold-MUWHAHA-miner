"""Experimental causal 180s BUY/SELL quote signatures, independent of old AUC.

Works only with the existing Micro180 quote ring; no volume, DOM, model
probability, raw-data writer, or new tick engine. NOT trained or OOS certified.
"""
from __future__ import annotations
from dataclasses import dataclass
from statistics import median
from typing import Optional
from coinexx_r9.models import Tick
from micro180 import Micro180R9, RollingThreeMinute


@dataclass(frozen=True)
class AsymSpec:
    # Predeclared RESEARCH thresholds; not fitted win probabilities.
    min_buy_score: float = 0.15
    min_sell_score: float = 0.15
    min_coincident_quote_fraction: float = 0.30
    minimum_history_seconds: int = 45
    active: bool = True

    def __post_init__(self):
        if (not -2.0 <= self.min_buy_score <= 2.0 or
            not -2.0 <= self.min_sell_score <= 2.0 or
            not 0.0 <= self.min_coincident_quote_fraction <= 1.0 or
            not 30 <= self.minimum_history_seconds <= 175):
            raise ValueError("Invalid research-only asymmetric score contract")


@dataclass(frozen=True)
class SideSignature:
    side: int
    score: float
    eff5: float
    eff15: float
    eff30: float
    eff180: float
    quote_intensity_ratio: float
    spread_shock: float
    joint_quote_fraction: float
    extreme_extension: float
    indicator_bias: float


def _eff(vals: list[int], live: int, side: int) -> float:
    # Signed direction must be computed from the LIQUIDATION side.
    if len(vals) < 2:
        return 0.0
    travel = sum(abs(b-a) for a,b in zip(vals,vals[1:])) + abs(live-vals[-1])
    return max(-1.0,min(1.0,side*(live-vals[0])/max(1,travel)))


def signature(ring: RollingThreeMinute, tick: Tick, side: int,
              history_seconds: int = 45) -> Optional[SideSignature]:
    """Only previous fully completed observed-second Bid/Ask closes; live quote
    used strictly as today's *candidate* liquidation price, not future OHLC.
    Both legs must be continuous enough; no synthetic missing-second values.
    """
    if side not in (-1,1):
        raise ValueError("side must be BUY=+1 or SELL=-1")
    if history_seconds < 30 or history_seconds > 175:
        raise ValueError("history_seconds out of range")
    now = tick.time_msc
    groups = [ring.closes(now,ms) for ms in (5000,15000,30000,180000)]
    q5,q15,q30,q180=groups
    if (len(q5)<3 or len(q15)<8 or len(q30)<15 or
        len(q180)<history_seconds or now-q5[-1].last_ms>2500):
        return None
    if any(b.start_ms-a.start_ms>3000 for q in groups[:3]
           for a,b in zip(q,q[1:])):
        return None
    liquidate = tick.bid_u if side>0 else tick.ask_u
    def closes(q):
        return [x.bid_close if side>0 else x.ask_close for x in q]
    e5,e15,e30,e180=(_eff(closes(q),liquidate,side) for q in groups)
    joined = sum(1 for a,b in zip(q15,q15[1:])
                 if side*(b.bid_close-a.bid_close)>0 and
                    side*(b.ask_close-a.ask_close)>0)
    coincidence=joined/max(1,len(q15)-1)

    # Count is a QUOTE UPDATE proxy and is NOT executed trade volume.
    rate5=sum(x.n for x in q5)/5.0
    rate180=sum(x.n for x in q180)/180.0
    intensity=min(3.0,rate5/max(0.1,rate180))
    spreads=sorted(x.spread_close for x in q15)
    historical_spread=spreads[len(spreads)//2]
    spread_shock=max(0.0,tick.spread_points/max(1,historical_spread)-1.0)

    # Detect overextension beyond the *previously completed* 180s range.
    vals=closes(q180)
    increments=[abs(b-a) for a,b in zip(vals,vals[1:])]
    robust_move=max(1.0,float(median(increments)) if increments else 1.0)
    beyond=(liquidate-max(vals)) if side>0 else (min(vals)-liquidate)
    extension=min(3.0,max(0.0,beyond/robust_move))
    bias=ring.m1.bias(side)
    if bias is None:
        bias=0.0 # documented completed-bar indicator proxy fallback
    # Buy/Sell coefficients are asymmetric hypotheses, NOT estimates of alpha.
    if side>0:
        score=(.28*e5+.27*e15+.15*e30+.06*e180
               +.16*coincidence+.08*(intensity-1)+.10*bias
               -.25*spread_shock-.12*extension)
    else:
        score=(.25*e5+.28*e15+.17*e30+.07*e180
               +.16*coincidence+.08*(intensity-1)+.09*bias
               -.29*spread_shock-.12*extension)
    return SideSignature(side,score,e5,e15,e30,e180,intensity,
                         spread_shock,coincidence,extension,bias)


class AsymmetricMicroR9(Micro180R9):
    """Opt-in entry permission and runner context layered on original fork.
    Base stop/30s hold, cash harvest, slippage modeling and governors unchanged.
    """
    def __init__(self, cfg, cash, spec, quant: AsymSpec = AsymSpec()):
        super().__init__(cfg,cash,spec)
        self.quant=quant

    def _open_trade(self,t:Tick,side:int):
        if not self.quant.active:
            return super()._open_trade(t,side)
        e=signature(self.rolling,t,side,self.quant.minimum_history_seconds)
        if e is None:
            self.stats["asym_missing_completed_history"]+=1
            return
        required=self.quant.min_buy_score if side>0 else self.quant.min_sell_score
        if e.score<required or e.joint_quote_fraction<self.quant.min_coincident_quote_fraction:
            self.stats["asym_quant_veto"]+=1
            return
        self._signal_meta.update({
            "asym_score":round(e.score,6),
            "asym_eff_5":round(e.eff5,4),
            "asym_eff_15":round(e.eff15,4),
            "asym_eff_30":round(e.eff30,4),
            "asym_eff_180":round(e.eff180,4),
            "asym_joint_quote_fraction":round(e.joint_quote_fraction,4),
            "asym_quote_intensity_proxy":round(e.quote_intensity_ratio,4),
            "asym_spread_shock":round(e.spread_shock,4),
            "asym_180s_extension":round(e.extreme_extension,4)
        })
        return super()._open_trade(t,side)

    def _signed_trend_score(self,side:int,t:Tick)->float:
        if not self.quant.active:
            return super()._signed_trend_score(side,t)
        e=signature(self.rolling,t,side,self.quant.minimum_history_seconds)
        if e is None:
            return -1.0
        # A continuation SCORE is not a fitted hold-vs-harvest expectation.
        # The parent still requires broker-feasible profitable stop protection.
        return max(-1.0,min(1.0,e.score))

    def report(self):
        out=super().report()
        out["asymmetric_v3"]={
            "mode":"research_only_untrained",
            "buy_score_floor":self.quant.min_buy_score,
            "sell_score_floor":self.quant.min_sell_score,
            "quote_coincidence_floor":self.quant.min_coincident_quote_fraction,
            "accepted_signals":int(self.stats["micro_positions"]),
            "vetoes":int(self.stats["asym_quant_veto"]),
            "unavailable_history":int(self.stats["asym_missing_completed_history"]),
            "uses_real_traded_volume":False,
            "native_mt5_parity_verified":False,
            "hold_rule":"runner disabled unless separately enabled and protected"
        }
        return out
