"""R10 multi-specialist causal quote-flow prioritization and funded equity circuit.

Research-only. Arbitrates R09 event campaigns and R03 specialists by changing
their priorities, never their observed prices or fill timing. The existing
SharedSignalArbiter owns all final order requests, occupancy and margin.
Source signals are unchanged if the quote-flow prior is uncalibrated.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
from math import isfinite
from .quote_flow import ClosedQuoteFlow
from .signal_bus import SignalIntent


class FlowPrioritySource:
    """Decorate one broker/source with the last *completed* quote-flow second."""
    def __init__(self, source: object, history: int = 300):
        self.source=source
        self.flow=ClosedQuoteFlow(history=history)
        self.flow_bonus_events=0

    def _score(self, proposals):
        state=self.flow.snapshot()
        if state is None or state.total_updates < 2:
            return tuple(proposals or ())
        out=[]
        for x in proposals or ():
            if not isinstance(x,SignalIntent):
                raise TypeError("only SignalIntent may be prioritized")
            directional=state.normalized_flow*x.side
            # Soft prioritization, not a universal indicator AND-gate.
            bonus=(3 if directional>.4 else 1 if directional>.1 else
                   -1 if directional<-.3 else 0)
            if directional>.1 and state.spread_compression>0:
                bonus+=1
            if bonus:self.flow_bonus_events+=1
            out.append(replace(x,priority=x.priority+bonus))
        return tuple(out)

    def on_bar(self,bar,quote,account):
        # No new quote is incorporated until on_tick; as-of previous
        # completed observed second cannot contain the current incomplete bar.
        return self._score(self.source.on_bar(bar,quote,account))

    def on_tick(self,quote,account):
        # Publish only a fully completed second on its first *later* quote.
        self.flow.update(quote)
        return self._score(self.source.on_tick(quote,account))


@dataclass(frozen=True,slots=True)
class CircuitCaps:
    max_daily_loss_fraction:float
    max_peak_drawdown_fraction:float

    def __post_init__(self):
        if not all(isfinite(v) and 0<v<=1 for v in
                   (self.max_daily_loss_fraction,self.max_peak_drawdown_fraction)):
            raise ValueError("research-only loss caps must be in (0,1]")


class FundedCircuit:
    """One per independently funded account; does not block protective EXIT."""
    def __init__(self,caps:CircuitCaps):
        self.caps=caps
        self.clock=None
        self.day=None
        self.day_open=None
        self.peak=0.
        self.daily_latched=False
        self.peak_latched=False
        self.rejections={}

    def observe(self,ms:int,equity:float):
        if not isinstance(ms,int) or ms<0 or (
                self.clock is not None and ms<self.clock):
            raise ValueError("noncausal equity timestamp")
        if not isfinite(equity):
            raise ValueError("nonfinite account equity")
        self.clock=ms
        new_day=ms//86400000
        if new_day!=self.day:
            self.day=new_day
            self.day_open=equity
            self.daily_latched=False
        self.peak=max(self.peak,equity)
        if equity<=self.day_open*(1-self.caps.max_daily_loss_fraction):
            self.daily_latched=True
        if equity<=self.peak*(1-self.caps.max_peak_drawdown_fraction):
            self.peak_latched=True

    def approve(self,ms:int,equity:float,estimated_loss:float,estimated_margin:float):
        if self.clock is None or self.clock!=ms:
            raise ValueError("must observe account at this quote before approval")
        if not all(isfinite(v) and v>=0 for v in (
                estimated_loss,estimated_margin)):
            raise ValueError("invalid monetary exposure")
        if equity<=0:
            reason="equity_nonpositive"
        elif self.peak_latched:
            reason="peak_equity_circuit"
        elif self.daily_latched:
            reason="daily_equity_circuit"
        else:
            return True,"funded_circuit_accept"
        self.rejections[reason]=self.rejections.get(reason,0)+1
        return False,reason
