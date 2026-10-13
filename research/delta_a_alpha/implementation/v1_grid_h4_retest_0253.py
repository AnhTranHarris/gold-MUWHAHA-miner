"""GRID0253 causal completed-H4 BREAK -> PULLBACK -> RE-CROSS source.

Research-only: R9 SYNTH is goal; R9 OVERFIT provides retrospective optimal
trades but cannot feed runtime decisions. Unique monthly market conditions
are handled by completed HTF state; there is NO calendar-month selector.
Source emits no orders, cash accounting or broker fills. Signal is known only
AFTER an M1 completes; any order needs a later original observed quote.
"""
from dataclasses import dataclass
from typing import Optional

H4_MS=4*60*60*1000
M1_MS=60*1000

@dataclass(frozen=True)
class FinishedH4Rung:
    reference_asof_ms:int
    high_raw:int
    low_raw:int
    atr14_raw:int
    tr_over_atr:float

@dataclass(frozen=True)
class H4RetestInvitation:
    signal_known_at_ms:int
    side:int
    owner:int
    prior_breakout_level_raw:int
    atr14_raw:int
    source:str='GRID0253_COMPLETED_H4_BREAK_PULLBACK_RECROSS'

class CompletedH4RetestGrid:
    """IDLE->BROKEN->PULLED_BACK->re-cross. One signal per H4 owner.

    Source prices are integer 1/1000 USD/oz. Reference H4 window must be
    completed before current M1, not relabeled from the still-forming bar.
    A price-observation hiatus kills pending confirmations.
    """
    def __init__(self,*,max_age_minutes=120,max_tr_over_atr=2.0):
        if max_age_minutes<=0 or max_tr_over_atr<=0:raise ValueError('positive limits')
        self.max_age_minutes=max_age_minutes
        self.max_tr_over_atr=max_tr_over_atr
        self.last_end_ms:Optional[int]=None
        self.last_invited_owner:Optional[int]=None
        self.state='IDLE'
        self.owner=None
        self.side=0
        self.level=0
        self.broke_at_ms=None
        self.atr=0
    def on_completed_m1(self,*,end_ms:int,prev_close_raw:int,close_raw:int,h4:FinishedH4Rung):
        if self.last_end_ms is not None and end_ms<=self.last_end_ms:
            raise ValueError('completed minutes must advance monotonically')
        continuous=self.last_end_ms is None or end_ms-self.last_end_ms==M1_MS
        self.last_end_ms=end_ms
        owner=(end_ms-1)//H4_MS
        if h4.reference_asof_ms>owner*H4_MS:
            raise ValueError('unfinished H4 bar was supplied as source')
        if not continuous:self.state='IDLE'
        if self.state!='IDLE' and (owner!=self.owner or end_ms-self.broke_at_ms>self.max_age_minutes*M1_MS):
            self.state='IDLE'
        if min(h4.high_raw,h4.low_raw,h4.atr14_raw,prev_close_raw,close_raw)<=0 or h4.high_raw<=h4.low_raw:
            return None
        if not (0<=h4.tr_over_atr<=self.max_tr_over_atr):return None
        if self.state=='IDLE':
            if owner==self.last_invited_owner or not continuous:return None
            up=prev_close_raw<=h4.high_raw and close_raw>h4.high_raw
            down=prev_close_raw>=h4.low_raw and close_raw<h4.low_raw
            if not up and not down:return None
            self.side=1 if up else -1
            self.level=h4.high_raw if up else h4.low_raw
            self.owner=owner
            self.broke_at_ms=end_ms
            self.atr=h4.atr14_raw
            self.state='BROKEN'
            return None
        if self.state=='BROKEN':
            if self.side*(close_raw-self.level)<-max(150,self.atr//8):
                self.state='PULLED_BACK'
        elif self.state=='PULLED_BACK':
            if self.side*(close_raw-self.level)>max(150,self.atr//12):
                self.last_invited_owner=owner
                self.state='IDLE'
                return H4RetestInvitation(end_ms,self.side,owner,self.level,self.atr)
        return None
