"""Bounded 250ms source-ordinal quote path for existing rolling Micro180.

Input quote order is never sorted by milliseconds; equal timestamps retain
source sequence. Quote updates are *not* traded volume or order-flow imbalance.
Only observed events create bins: no missing-quarter-second OHLC imputation.
"""
from collections import deque
from dataclasses import dataclass
from typing import Optional
from coinexx_r9.models import Tick

@dataclass
class QuarterBin:
    start_ms:int
    first_ms:int
    last_ms:int
    first_bid:int
    first_ask:int
    last_bid:int
    last_ask:int
    n:int=1
    path_bid:int=0
    path_ask:int=0
    coherent_up:int=0
    coherent_down:int=0
    observed_deltas:int=0

    def feed(self,t:Tick,db:int,da:int,count_motion:bool):
        self.last_ms=t.time_msc
        self.last_bid=t.bid_u
        self.last_ask=t.ask_u
        self.n+=1
        if count_motion:
            self.path_bid+=abs(db)
            self.path_ask+=abs(da)
            self.observed_deltas+=1
            if db>0 and da>0:self.coherent_up+=1
            if db<0 and da<0:self.coherent_down+=1

@dataclass(frozen=True)
class MicroEvidence:
    side:int
    efficiency:float
    coherence:float
    updates:int
    last_ms:int

class MsQuarterPath:
    """3m rolling 250ms observation bins, max 720 completed + active; O(1)/tick."""
    __slots__=('finished','current','previous_ms','last_bid','last_ask','rows','out_of_order')
    def __init__(self):
        self.finished=deque(maxlen=720)
        self.current:Optional[QuarterBin]=None
        self.previous_ms:Optional[int]=None
        self.last_bid=0
        self.last_ask=0
        self.rows=0
        self.out_of_order=False

    def update(self,t:Tick):
        if self.previous_ms is not None and t.time_msc<self.previous_ms:
            self.out_of_order=True
            raise ValueError('Out of order source quote, including same-ms row sequencing')
        start=t.time_msc//250*250
        db=t.bid_u-self.last_bid if self.previous_ms is not None else 0
        da=t.ask_u-self.last_ask if self.previous_ms is not None else 0
        valid=(self.previous_ms is not None and t.time_msc-self.previous_ms<=2500)
        if self.current is None or start!=self.current.start_ms:
            if self.current is not None:
                self.finished.append(self.current)
            self.current=QuarterBin(start,t.time_msc,t.time_msc,
                 t.bid_u,t.ask_u,t.bid_u,t.ask_u)
            # A change from the previous tick belongs to the new time bin.
            if valid:
                self.current.path_bid+=abs(db)
                self.current.path_ask+=abs(da)
                self.current.observed_deltas+=1
                if db>0 and da>0:self.current.coherent_up+=1
                if db<0 and da<0:self.current.coherent_down+=1
        else:
            self.current.feed(t,db,da,valid)
        self.last_bid=t.bid_u;self.last_ask=t.ask_u
        self.previous_ms=t.time_msc;self.rows+=1

    def signature(self,now_ms:int,side:int,window_ms:int=5000)->Optional[MicroEvidence]:
        if side not in (-1,1):raise ValueError('side')
        if not 250<=window_ms<=180_000:raise ValueError('window')
        if self.current is None or now_ms-self.current.last_ms>2500:
            return None
        min_start=(now_ms//250*250)-window_ms
        recent=[b for b in self.finished if b.start_ms>=min_start]
        if self.current.start_ms>=min_start:recent.append(self.current)
        if len(recent)<2:return None
        if any(b.start_ms-a.start_ms>2500 for a,b in zip(recent,recent[1:])):
            return None
        oldest=recent[0];newest=recent[-1]
        first=oldest.first_bid if side>0 else oldest.first_ask
        last=newest.last_bid if side>0 else newest.last_ask
        travel=sum(b.path_bid if side>0 else b.path_ask for b in recent)
        coherent=sum(b.coherent_up if side>0 else b.coherent_down for b in recent)
        observed=sum(b.observed_deltas for b in recent)
        if observed==0:return None
        return MicroEvidence(side,max(-1.,min(1.,side*(last-first)/max(1,travel))),
                             coherent/max(1,observed),observed,newest.last_ms)
