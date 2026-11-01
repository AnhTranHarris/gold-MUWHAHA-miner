#!/usr/bin/env python3
"""Causal future-path labeler for R9 Probabilistic Entry Router v2.

Future ticks are used ONLY offline to label a decision that was already made from
causal features. Labels describe competing executable first-passage events under
R9-style initial stop, trailing activation and 30 second timeout.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from router_v2_features import Quote

ENTRY_FEE = 0.02
HOLD_MS = 30_000
TARGETS = (0.10, 0.30, 0.50)


def round_tick(x:float,tick:float=.01)->float:
    return round(math.floor(x/tick + .5)*tick, 2)

@dataclass
class FirstPassageOutcome:
    side:int
    entry_ms:int
    entry_price:float
    spread:float
    initial_stop:float
    first_target_ms:Dict[str,Optional[int]]
    adverse_stop_ms:Optional[int]
    exit_ms:int
    exit_type:str
    exit_price:float
    net:float
    mfe:float
    mae:float
    cvar_proxy:float
    teacher:int=0

    def to_dict(self):
        return asdict(self)


class ActivePath:
    def __init__(self,q:Quote,side:int,teacher:int=0,fee:float=ENTRY_FEE):
        if side not in (-1,1):raise ValueError('side')
        self.side=side;self.entry_ms=q.utc_ms;self.spread=q.spread;self.fee=fee;self.teacher=teacher
        self.entry_price=q.ask if side>0 else q.bid
        self.stop=round_tick(q.bid-.30 if side>0 else q.ask+.30)
        self.initial_stop=self.stop
        self.targets={f'{x:.2f}':None for x in TARGETS}
        self.stop_ms=None
        self.mfe=0.;self.mae=0.;self.loss_tail=[]
        self.done=False

    def update(self,q:Quote)->Optional[FirstPassageOutcome]:
        if self.done:return None
        if q.utc_ms < self.entry_ms:raise ValueError('future path out of order')
        if q.utc_ms == self.entry_ms:return None
        px=q.bid if self.side>0 else q.ask
        excursion=(px-self.entry_price)*self.side
        self.mfe=max(self.mfe,excursion);self.mae=min(self.mae,excursion)
        self.loss_tail.append(excursion-self.fee)
        if len(self.loss_tail)>256:self.loss_tail.pop(0)
        net_exc=excursion-self.fee
        for t in TARGETS:
            k=f'{t:.2f}'
            if self.targets[k] is None and net_exc>=t-1e-12:self.targets[k]=q.utc_ms
        # stop check before trail update: executable barrier ordering on this quote
        if (self.side>0 and q.bid<=self.stop) or (self.side<0 and q.ask>=self.stop):
            self.stop_ms=q.utc_ms
            return self.finish(q,'SL',px)
        # R9 trailing rule: activation on executable quote, monotonic stop
        if excursion>=0.10-1e-12:
            newstop=round_tick(px-self.side*.03)
            self.stop=max(self.stop,newstop) if self.side>0 else min(self.stop,newstop)
        if q.utc_ms-self.entry_ms>=HOLD_MS:
            return self.finish(q,'TIMEOUT',px)
        return None

    def finish(self,q:Quote,reason:str,px:float)->FirstPassageOutcome:
        self.done=True
        net=(px-self.entry_price)*self.side-self.fee
        tail=sorted(self.loss_tail)
        n=max(1,int(math.ceil(.10*len(tail)))) if tail else 1
        cvar=sum(tail[:n])/n if tail else net
        return FirstPassageOutcome(
            side=self.side,entry_ms=self.entry_ms,entry_price=round(self.entry_price,5),spread=round(self.spread,5),
            initial_stop=self.initial_stop,first_target_ms=self.targets.copy(),adverse_stop_ms=self.stop_ms,
            exit_ms=q.utc_ms,exit_type=reason,exit_price=round(px,5),net=round(net,5),mfe=round(self.mfe,5),
            mae=round(self.mae,5),cvar_proxy=round(cvar,5),teacher=self.teacher)


def outcome_class(o:FirstPassageOutcome)->str:
    t=o.first_target_ms.get('0.10')
    if t is not None and (o.adverse_stop_ms is None or t<o.adverse_stop_ms):return 'FAVORABLE'
    if o.exit_type=='SL' and o.net<0:return 'ADVERSE'
    return 'TIMEOUT'


__all__=['ActivePath','FirstPassageOutcome','outcome_class','ENTRY_FEE','HOLD_MS','TARGETS']
