"""GRID0254 GRID G0 near-HTF, near-sniper confirmed auction source.
R9 SYNTH sets performance goals; R9 OVERFIT is *retrospective* optimal teacher;
months have distinct conditions. High volume is a progressive objective, never
an excuse to issue unfunded synthetic fills or multiply position size.

ONE invite per 4h structural owner at most. The price has to break a six-
COMPLETED-H4 structural boundary, then retain/extend outside it for a second
consecutive finished M1 close, with >=1 USD/oz last-minute forward movement.
Completed H4 extrema and ATR must be supplied by a lookahead-free upstream
bar builder (six most recent active completed H4 observations). No feed calls,
broker account, lot sizing, overfit scores, or vertical grid access here.
"""
from dataclasses import dataclass
from typing import Optional
H4_MS=14_400_000
M1_MS=60_000

@dataclass(frozen=True)
class H4AsOfBoundary:
    reference_asof_ms:int
    high_raw:int
    low_raw:int
    atr14_raw:int
    recent_tr_to_atr:float

@dataclass(frozen=True)
class H4SecondAcceptance:
    signal_known_at_ms:int
    side:int
    owner:int
    structural_boundary_raw:int
    atr_raw:int
    source:str='GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE'

class H4SecondAcceptanceSource:
    """Strict causal first-acceptance and confirmed-followthrough geometry.

    The first qualifying two-M1 confirmation in an H4 owner *consumes* the
    candidate even if its second impulse < minimum followthrough: no repeated
    intrabar threshold shopping, no future best-candle selection.
    """
    def __init__(self,*,minimum_second_impulse_raw:int=1_000,
                 max_recent_tr_to_atr:float=2.0):
        if minimum_second_impulse_raw<=0 or max_recent_tr_to_atr<=0:
            raise ValueError('strictly positive as-of research requirements')
        self.minimum_second_impulse_raw=minimum_second_impulse_raw
        self.max_recent_tr_to_atr=max_recent_tr_to_atr
        self.last_end_ms:Optional[int]=None
        self.last_owner:Optional[int]=None
        self.last_tested_owner:Optional[int]=None
        self.prior_close:Optional[int]=None
        self.prior_prior_close:Optional[int]=None
        self.n_seen=0;self.n_invites=0
    def on_completed_m1(self,*,end_ms:int,close_raw:int,h4:H4AsOfBoundary)->Optional[H4SecondAcceptance]:
        if self.last_end_ms is not None and end_ms<=self.last_end_ms:
            raise ValueError('completed M1 clock must strictly increase')
        owner=(end_ms-1)//H4_MS
        if h4.reference_asof_ms>owner*H4_MS:
            raise ValueError('reference H4 bar is not yet finished')
        if close_raw<=0:raise ValueError('M1 close must be original positive price')
        continuous=(self.last_end_ms is not None and end_ms-self.last_end_ms==M1_MS)
        same_h4=(self.last_owner is not None and owner==self.last_owner)
        if not (continuous and same_h4):
            # No across-halt or owner-wrap artificial two-minute acceptance.
            self.prior_prior_close=None
        p1=self.prior_close if continuous and same_h4 else None
        p2=self.prior_prior_close if continuous and same_h4 else None
        self.last_end_ms=end_ms;self.last_owner=owner
        if continuous and same_h4:
            self.prior_prior_close=self.prior_close
        else:
            self.prior_prior_close=None
        self.prior_close=close_raw
        self.n_seen+=1
        if p1 is None or p2 is None or self.last_tested_owner==owner:return None
        if (h4.high_raw<=h4.low_raw or h4.low_raw<=0 or h4.atr14_raw<=0
                or not 0<=h4.recent_tr_to_atr<=self.max_recent_tr_to_atr):
            return None
        up=(p2<=h4.high_raw+100 and p1>h4.high_raw+200 and close_raw>p1+250)
        down=(p2>=h4.low_raw-100 and p1<h4.low_raw-200 and close_raw<p1-250)
        if not(up or down):return None
        side=1 if up else -1
        self.last_tested_owner=owner
        if (close_raw-p1)*side<self.minimum_second_impulse_raw:return None
        self.n_invites+=1
        return H4SecondAcceptance(end_ms,side,owner,
                 h4.high_raw if up else h4.low_raw,h4.atr14_raw)
