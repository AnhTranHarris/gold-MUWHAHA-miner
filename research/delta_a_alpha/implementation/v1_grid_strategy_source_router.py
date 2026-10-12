"""GRID0246: coherent creator+S1/M1/M5+funded-anchor grid SOURCE.

Grid strategy discovery *before* any Vertical L1-L7 action. The existing
multiscale G0 keeps priority: it is never replaced by an unverified
fill-anchored proposal. No trade, no cash, no sizing, no predictive edge.
True fills can be acknowledged only through FundedGridCampaign by an external
broker-calibrated executor (not present in this research module).
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import Optional
from v1_grid_multiscale_stack import MultiSpeedGridGenesis
from v1_grid_funded_campaign import FundedGridCampaign

SCALE=1000

@dataclass(frozen=True)
class SourceCandidate:
    time_ms:int
    side:int
    source:str
    rung:int
    level_raw:int
    bid_raw:int
    ask_raw:int
    paid_proposal_id:Optional[int]=None
    paid_prior_close_id:Optional[int]=None
    # Both future signs remain research hypotheses, not asserted profitable.

class GridStrategySourceRouter:
    """One G0 candidate per distinct UTC millisecond; no vertical quality gate.

    Last-48 ACTIVE completed H1 extrema belong to canonical creator engine.
    The funded-anchor gap is chosen ONCE per changed completed H1 window,
    from the completed creator gap if present or a fixed research floor.
    It never follows current-tick spread within the same auction window.
    """
    def __init__(self,*,multiscale=None,funded=None,paid_gap_floor_raw=1200):
        if paid_gap_floor_raw<=0:raise ValueError('positive grid gap floor')
        self.multiscale=multiscale if multiscale is not None else MultiSpeedGridGenesis()
        self.funded=funded if funded is not None else FundedGridCampaign()
        self.paid_gap_floor_raw=paid_gap_floor_raw
        self.h1_owner=None
        self.frozen_gap_raw=None
        self.last_ms=None
        self.last_emitted_ms=None
        self.counts=Counter()
    def on_tick(self,q,h1,geometry,*,m5=None,broker_tradable=True):
        ms=q.time_ms_utc
        if self.last_ms is not None and ms<self.last_ms:
            raise ValueError('nonmonotonic original source')
        if q.bid_raw<=0 or q.ask_raw<q.bid_raw:
            raise ValueError('bad executable quote')
        self.last_ms=ms
        self.counts['ticks']+=1
        base=self.multiscale.on_tick(q,h1,geometry,last_completed_m5=m5,
                                     broker_tradable=broker_tradable)
        self.counts['old_multiscale_generated']+=len(base)
        if not self.multiscale.ready or h1 is None:
            self.counts['before_creator_warmup']+=1
            return ()
        if h1.end_ms>ms:raise ValueError('future/unfinished completed H1')
        if h1.start_ms!=self.h1_owner:
            self.h1_owner=h1.start_ms
            # Creator parent_gap_usd is itself frozen at completed H1.
            # It may be None on a first quote; use prior disclosed floor then.
            original=self.multiscale.parent.parent
            gap=getattr(original,'parent_gap_usd',None)
            self.frozen_gap_raw=max(self.paid_gap_floor_raw,
                  int(round(gap*SCALE)) if gap is not None else self.paid_gap_floor_raw)
        creator=self.multiscale.parent.parent
        hi=getattr(creator,'cached_high',None)
        lo=getattr(creator,'cached_low',None)
        if hi is None or lo is None:return tuple(self._base_candidate(q,base))
        paid=self.funded.observe(time_ms=ms,bid_raw=q.bid_raw,ask_raw=q.ask_raw,
                 completed_h1_window_id=self.h1_owner,
                 completed_h1_high_raw=int(round(hi*SCALE)),
                 completed_h1_low_raw=int(round(lo*SCALE)),
                 gap_raw=self.frozen_gap_raw,broker_tradable=broker_tradable)
        self.counts['creator_paid_anchor_generated']+=len(paid)
        if paid and (base or ms==self.last_emitted_ms):
            # Unadmitted shadow G0 cannot later acknowledge a paid fill.
            for p in paid:self.funded.proposals.pop(p.id,None)
            self.counts['paid_collisions_rejected']+=len(paid)
        if ms==self.last_emitted_ms:
            self.counts['duplicate_millisecond_rejected']+=len(base)
            return ()
        if base:
            event=base[0]
            self.last_emitted_ms=ms
            self.counts['preserved_multiscale_selected']+=1
            return (SourceCandidate(ms,event.side,event.source,event.rung,
                   int(round(event.crossing_level_usd*SCALE)),q.bid_raw,q.ask_raw),)
        if paid:
            p=paid[0]
            if p.id not in self.funded.proposals:return ()
            self.last_emitted_ms=ms
            self.counts['funded_anchor_selected']+=1
            return (SourceCandidate(ms,p.side,'OMEGAFX_ACKNOWLEDGED_FILL_ANCHOR',p.rung,
                  p.threshold_raw,q.bid_raw,q.ask_raw,p.id,p.prior_paid_close_id),)
        return ()
    @staticmethod
    def _base_candidate(q,base):
        for e in base[:1]:
            yield SourceCandidate(q.time_ms_utc,e.side,e.source,e.rung,
                   int(round(e.crossing_level_usd*SCALE)),q.bid_raw,q.ask_raw)
    def stats(self):
        return {'stage':'G0_UNFUNDED_SOURCE_ONLY',
                'counts':dict(self.counts),
                'base':self.multiscale.stats(),
                'paid':dict(self.funded.counts)}
