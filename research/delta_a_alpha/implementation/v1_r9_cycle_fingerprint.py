"""GRID0250: as-of R9 SYNTH / OVERFIT cycle research state, GRID G0 only.

R9 SYNTH is performance target. R9 OVERFIT is OFFLINE best-trades teacher.
Never load OVERFIT scores or forward markouts. Only observed Bid/Ask quotes
and past tick sequence are inputs. Does NOT direct, size or approve orders.
SYNTH/REAL analysis showed identical M1 envelopes but radically different
intraminute churn and post-entry survival. Feed contract prices are raw /1000.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from typing import Optional

@dataclass(frozen=True)
class GridCycleFingerprint:
    available_ms:int
    spread_raw:int
    nominal_r9_stop_raw:int
    spread_over_nominal_stop:bool
    observed_quote_count_5s:int
    preentry_efficiency_5s:Optional[float]
    preentry_range_raw_15s:Optional[int]
    preentry_path_raw_5s:Optional[int]
    preentry_directional_turns_5s:Optional[int]
    # This is a causal description, NOT probability, signal side or oracle.

class R9CycleFingerprintResearch:
    def __init__(self,*,nominal_stop_raw:int=300,history_ms:int=30000,
                 hiatus_ms:int=60000):
        if min(nominal_stop_raw,history_ms,hiatus_ms)<=0:raise ValueError('positive parameters')
        self.nominal_stop_raw=nominal_stop_raw
        self.history_ms=history_ms
        self.hiatus_ms=hiatus_ms
        self.history=deque()
        self.last_time=None
        self.snapshots=0
        self.current_spread_raw=None
    def push_quote(self,*,time_ms:int,bid_raw:int,ask_raw:int)->None:
        if time_ms<0 or bid_raw<=0 or ask_raw<bid_raw:raise ValueError('bad quote')
        if self.last_time is not None:
            if time_ms<self.last_time:raise ValueError('unordered ticks')
            if time_ms-self.last_time>self.hiatus_ms:self.history.clear()
        self.last_time=time_ms
        self.current_spread_raw=ask_raw-bid_raw
        mid=(bid_raw+ask_raw)//2
        self.history.append((time_ms,mid))
        while self.history and self.history[0][0]<time_ms-self.history_ms:
            self.history.popleft()
    def snapshot(self)->GridCycleFingerprint:
        if self.last_time is None:raise ValueError("no observed quote")
        time_ms=self.last_time
        spread_raw=self.current_spread_raw
        q5=[(ms,p) for ms,p in self.history if ms>=time_ms-5000]
        q15=[(ms,p) for ms,p in self.history if ms>=time_ms-15000]
        # Require actual past coverage rather than fake completed 5s/15s after hiatus.
        covered5=bool(q5) and q5[0][0]<=time_ms-3500 and len(q5)>=3
        covered15=bool(q15) and q15[0][0]<=time_ms-12500 and len(q15)>=3
        eff=None;path=None;turns=None
        if covered5:
            seq=[x[1] for x in q5]
            diffs=[v-u for u,v in zip(seq[:-1],seq[1:])]
            path=sum(abs(x) for x in diffs)
            eff=abs(seq[-1]-seq[0])/path if path>0 else 0.
            signs=[1 if x>0 else -1 for x in diffs if x!=0]
            turns=sum(a!=b for a,b in zip(signs[:-1],signs[1:]))
        rr=(max(x[1] for x in q15)-min(x[1] for x in q15)) if covered15 else None
        self.snapshots+=1
        return GridCycleFingerprint(time_ms,spread_raw,self.nominal_stop_raw,
            spread_raw>self.nominal_stop_raw,len(q5),eff,rr,path,turns)
    def observe(self,*,time_ms:int,bid_raw:int,ask_raw:int)->GridCycleFingerprint:
        self.push_quote(time_ms=time_ms,bid_raw=bid_raw,ask_raw=ask_raw)
        return self.snapshot()
