"""Causal bars, aggregated from an exact 5-second OHLC base to reduce CPU overhead."""
from __future__ import annotations
from dataclasses import dataclass
from .feeds import Quote

TIMEFRAMES = (5, 15, 30, 45, 60, 300, 3600)

@dataclass(frozen=True, slots=True)
class Bar:
    seconds: int
    start_ms: int
    end_ms: int
    bid_open: float
    bid_high: float
    bid_low: float
    bid_close: float
    ask_open: float
    ask_high: float
    ask_low: float
    ask_close: float
    ticks: int

class _Accumulator:
    __slots__ = ('seconds', 'start', 'b0','bh','bl','bc','a0','ah','al','ac','n')
    def __init__(self, seconds:int, quote:Quote|Bar):
        self.seconds=seconds
        t=quote.ms if isinstance(quote,Quote) else quote.start_ms
        self.start=(t//(seconds*1000))*seconds*1000
        if isinstance(quote,Quote):
            self.b0=self.bh=self.bl=self.bc=quote.bid
            self.a0=self.ah=self.al=self.ac=quote.ask
            self.n=1
        else:
            self.b0=quote.bid_open;self.bh=quote.bid_high;self.bl=quote.bid_low;self.bc=quote.bid_close
            self.a0=quote.ask_open;self.ah=quote.ask_high;self.al=quote.ask_low;self.ac=quote.ask_close
            self.n=quote.ticks
    def add_quote(self,q:Quote):
        self.bh=max(self.bh,q.bid);self.bl=min(self.bl,q.bid);self.bc=q.bid
        self.ah=max(self.ah,q.ask);self.al=min(self.al,q.ask);self.ac=q.ask
        self.n+=1
    def add_bar(self,b:Bar):
        self.bh=max(self.bh,b.bid_high);self.bl=min(self.bl,b.bid_low);self.bc=b.bid_close
        self.ah=max(self.ah,b.ask_high);self.al=min(self.al,b.ask_low);self.ac=b.ask_close
        self.n+=b.ticks
    def bar(self)->Bar:
        return Bar(self.seconds,self.start,self.start+self.seconds*1000,
                   self.b0,self.bh,self.bl,self.bc,self.a0,self.ah,self.al,self.ac,self.n)

class CandleStream:
    """Every supported timeframe is a multiple of 5s, preserving OHLC exactly.

    Higher timeframe updates are O(1) per *closed five-second interval*, not per tick.
    Closed candles are exposed only when a later quote establishes their completion.
    """
    def __init__(self,timeframes:tuple[int,...]=TIMEFRAMES):
        if not timeframes or 5 not in timeframes or any(k<5 or k%5 for k in timeframes) or len(set(timeframes))!=len(timeframes):
            raise ValueError('timeframes must be unique multiples of five seconds including S5')
        self.timeframes=timeframes
        self.running: _Accumulator|None=None
        self.higher:dict[int,_Accumulator]={}
        self.last_closed:dict[int,Bar]={}
    def update(self,q:Quote)->list[Bar]:
        slot=(q.ms//5000)*5000
        acc=self.running
        if acc is None:
            self.running=_Accumulator(5,q);return []
        if slot==acc.start:
            acc.add_quote(q);return []
        five=acc.bar()
        self.running=_Accumulator(5,q)
        out=[five];self.last_closed[5]=five
        for seconds in self.timeframes:
            if seconds==5:continue
            parent_start=(five.start_ms//(seconds*1000))*seconds*1000
            a=self.higher.get(seconds)
            if a is None:
                a=_Accumulator(seconds,five)
            elif a.start!=parent_start:
                closed=a.bar();out.append(closed);self.last_closed[seconds]=closed
                a=_Accumulator(seconds,five)
            else:
                a.add_bar(five)
            # The current quote is *past* this bar's end. Only then can it be emitted.
            if (q.ms//(seconds*1000))*seconds*1000!=a.start:
                closed=a.bar();out.append(closed);self.last_closed[seconds]=closed
                self.higher.pop(seconds,None)
            else:self.higher[seconds]=a
        return out
    def flush_end_of_data(self)->list[Bar]:
        """Diagnostics only; must never be delivered as completed strategy information."""
        return ([] if self.running is None else [self.running.bar()])+[a.bar() for a in self.higher.values()]
