"""GRID0256: source-faithful *permission* for archived GRID0185 causal J179F T1/T2.

R9 SYNTH is performance target; R9 OVERFIT's optimal trades are retrospective,
NEVER a feature. Each month differs, so calendar month is not used to choose
trades. Grid source is multi-HTF, multi-scalp, near-sniper, high-volume target.

This is an *optional source permission* awaiting the original J179F T1 event
stream; not a generator of fictional invitation timestamps, not a backtest
surrogate, and not an MT5 order sender. The original 12-slot source plus
separate other grid families was economically replayed in GRID0256.

Source role rule faithfully reproduced from the original GRID0185 historical
strict T2 script in GRID0185 archive. Current observable Bid/Ask only.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Mapping

TOTAL_PORTFOLIO_MAX=16
GRID0185_SOURCE_MAX=12
MAX_SPREAD_RAW=1000
FEE_RAW=520

@dataclass(frozen=True)
class StrictJ179FObservedT2:
    t1_ms:int
    source_t1_verified:bool
    observed_t2_ms:int
    kind:int
    h4:int
    h1:int
    m15:int
    m5:int
    h1_structural_location:float
    bid_raw:int
    ask_raw:int
    completed_m5_tr_raw:int
    finished_day_loss_raw:int=0
    friday_last_hour_denied:bool=False

@dataclass(frozen=True)
class StrictJ179FPermission:
    known_at_ms:int
    direction:int
    role:str
    original_auction_side:int
    source:str='GRID0185_CAUSAL_PRESERVED_T2'
    research_horizon_ms:int=90*60*1000

class OriginalJ179FStrictPermission0256:
    """12 independent source slots, one global 16-position research cap.

    No future T2 bar, historical winner, inferred fill, lot escalation or
    fabricated paid prior. The caller must validate real source T1 ownership.
    A non-BASE transition *only* uses truly settled prior 4 hourly buckets.
    """
    def __init__(self):
        self.last_permission_ms:Optional[int]=None
        self.last_risk_pilot_ms:Optional[int]=None
        self.accepted=0
        self.denied=0
    def evaluate(self,q:StrictJ179FObservedT2,*,current_j179f_reserved:int,
                 current_global_reserved:int,prior_completed_hourly_pnl_raw:Mapping[int,int],
                 prior_completed_hourly_close_count:Mapping[int,int]):
        if not q.source_t1_verified:return self._no()
        if (q.t1_ms<0 or q.observed_t2_ms<q.t1_ms or
            q.ask_raw<q.bid_raw or q.bid_raw<=0 or q.kind not in (0,1) or
            q.completed_m5_tr_raw<0 or
            current_j179f_reserved<0 or current_global_reserved<0):
            raise ValueError('invalid original observed J179F T1/T2 input')
        if current_j179f_reserved>current_global_reserved:
            raise ValueError('global occupancy must include J179F')
        # The original T2 must be 2-10s after T1, no interpolated time.
        delay=q.observed_t2_ms-q.t1_ms
        if not(2000<=delay<=10000):return self._no()
        if current_j179f_reserved>=GRID0185_SOURCE_MAX or current_global_reserved>=TOTAL_PORTFOLIO_MAX:
            return self._no()
        if q.friday_last_hour_denied or q.observed_t2_ms==self.last_permission_ms:
            return self._no()
        spread=q.ask_raw-q.bid_raw
        if spread>MAX_SPREAD_RAW or q.completed_m5_tr_raw*1000>6*(spread+FEE_RAW)*1000:
            return self._no()
        # Primary role: completed H4/M15 alignment; no current unfinished bar.
        d=q.h4
        if d not in (-1,1) or q.m15!=d:return self._no()
        strict=q.h1==d and q.m5==-d
        ignition=q.h1==d and q.m5==d
        transfer=q.h1==-d and q.m5==-d
        loc=q.h1_structural_location
        if not (0<=loc<=1):return self._no()
        direction=0;role=''
        if q.kind==1 and strict:
            direction=d;role='STRICT_H4'
        elif q.kind==0 and strict and loc<=.15:
            direction=d;role='BASE'
        elif q.kind==0 and ignition and loc<=.15:
            direction=d;role='IGNITION'
        elif q.kind==0 and transfer and .3<=loc<=.7:
            nowhour=q.observed_t2_ms//3600000
            prev=range(nowhour-4,nowhour)
            had_close=any(prior_completed_hourly_close_count.get(h,0)>0 for h in prev)
            loss_sum=sum(prior_completed_hourly_pnl_raw.get(h,0) for h in prev)
            if not had_close or loss_sum>=-10000:return self._no()
            direction=-d;role='PAID_PRIOR_4H_TRANSITION'
        else:return self._no()
        if q.finished_day_loss_raw>=40000:
            if (self.last_risk_pilot_ms is not None and
                q.observed_t2_ms-self.last_risk_pilot_ms<3600000):
                return self._no()
            self.last_risk_pilot_ms=q.observed_t2_ms
        self.last_permission_ms=q.observed_t2_ms
        self.accepted+=1
        return StrictJ179FPermission(q.observed_t2_ms,direction,role,d)
    def _no(self):
        self.denied+=1
        return None

