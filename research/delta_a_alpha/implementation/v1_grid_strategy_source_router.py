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
from v1_grid_renewal_signature import broker_cash_context
from v1_grid_auction_genesis_136b import NativeAuctionGrid136B
from v1_grid_native_136a import NativeMinuteRungs136A
from v1_grid_earned_harvest_runner import AsOfM5EnergyHarvestRunner
from v1_r9_cycle_fingerprint import R9CycleFingerprintResearch,GridCycleFingerprint
from dataclasses import replace

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
    paid_prior_hold_bucket:Optional[int]=None
    paid_prior_broker_cash_usd:Optional[float]=None
    raw_cross_sign:Optional[int]=None
    research_horizon_ms:Optional[int]=None
    available_ms:Optional[int]=None  # emitted on observed quote, never retroactively fill
    cycle_fingerprint:Optional[GridCycleFingerprint]=None  # strictly available-quote as-of
    # Both future signs remain research hypotheses, not asserted profitable.

class GridStrategySourceRouter:
    """One G0 candidate per distinct UTC millisecond; no vertical quality gate.

    Last-48 ACTIVE completed H1 extrema belong to canonical creator engine.
    The funded-anchor gap is chosen ONCE per changed completed H1 window,
    from the completed creator gap if present or a fixed research floor.
    It never follows current-tick spread within the same auction window.
    """
    def __init__(self,*,multiscale=None,funded=None,auction=None,native=None,
                 harvest_runner=None,cycle_research=None,paid_gap_floor_raw=1200):
        if paid_gap_floor_raw<=0:raise ValueError('positive grid gap floor')
        self.multiscale=multiscale if multiscale is not None else MultiSpeedGridGenesis()
        self.funded=funded if funded is not None else FundedGridCampaign()
        self.paid_gap_floor_raw=paid_gap_floor_raw
        self.auction=auction if auction is not None else NativeAuctionGrid136B()
        self.native=native if native is not None else NativeMinuteRungs136A()
        self.harvest_runner=harvest_runner if harvest_runner is not None else AsOfM5EnergyHarvestRunner()
        self.cycle_research=cycle_research if cycle_research is not None else R9CycleFingerprintResearch()
        self._exit_hint=None
        self.h1_owner=None
        self.frozen_gap_raw=None
        self.last_ms=None
        self.last_emitted_ms=None
        self._low_priority_pending=None
        self._ready_release=()
        self.counts=Counter()
    def on_tick(self,q,h1,geometry,*,m5=None,broker_tradable=True,
                completed_grid_signs=None,completed_m5_tr_raw=None,m5_tr_asof_ms=None):
        ms=q.time_ms_utc
        if self.last_ms is not None and ms<self.last_ms:
            raise ValueError('nonmonotonic original source')
        self._ready_release=()
        if self._low_priority_pending and ms>self._low_priority_pending.time_ms:
            self._ready_release=(self._low_priority_pending,)
            self._low_priority_pending=None
            self.counts['supplemental_timestamp_finalized']+=1
        if q.bid_raw<=0 or q.ask_raw<q.bid_raw:
            raise ValueError('bad executable quote')
        self.last_ms=ms
        self.cycle_research.push_quote(time_ms=ms,bid_raw=q.bid_raw,ask_raw=q.ask_raw)
        self._exit_hint=self.harvest_runner.select(quote_ms=ms,bid_raw=q.bid_raw,
                  ask_raw=q.ask_raw,completed_m5_tr_raw=completed_m5_tr_raw,
                  asof_ms=m5_tr_asof_ms)
        self.counts['ticks']+=1
        base=self.multiscale.on_tick(q,h1,geometry,last_completed_m5=m5,
                                     broker_tradable=broker_tradable)
        self.counts['old_multiscale_generated']+=len(base)
        new_auction=self.auction.on_quote(time_ms=ms,bid_raw=q.bid_raw,
                       ask_raw=q.ask_raw,tradable=broker_tradable)
        self.counts['original_136b_generated']+=len(new_auction)
        completed=completed_grid_signs or (None,None,None,None)
        if len(completed)!=4:raise ValueError('completed grid signs must be four role states')
        new_native=self.native.on_quote(time_ms=ms,bid_raw=q.bid_raw,
                       ask_raw=q.ask_raw,completed_h4_sign=completed[0],
                       completed_h1_sign=completed[1],completed_m15_sign=completed[2],
                       completed_m5_sign=completed[3],broker_tradable=broker_tradable)
        self.counts['original_136a_generated']+=len(new_native)
        if not self.multiscale.ready or h1 is None:
            # Native sources may observe all real quotes before 48 active H1;
            # old generator's original warmup state is never fabricated.
            self.counts['before_creator_warmup']+=1
            return self._supplemental(q,(),new_native,new_auction)
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
        if hi is None or lo is None:
            if base:
                self._cancel_same_ms_lower(ms)
                self.last_emitted_ms=ms
                self.counts['preserved_multiscale_selected']+=1
                return self._deliver(tuple(self._base_candidate(q,base)))
            return self._supplemental(q,(),new_native,new_auction)
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
            return self._deliver(())
        if base:
            event=base[0]
            self._cancel_same_ms_lower(ms)
            self.last_emitted_ms=ms
            self.counts['preserved_multiscale_selected']+=1
            return self._deliver((SourceCandidate(ms,event.side,event.source,event.rung,
                   int(round(event.crossing_level_usd*SCALE)),q.bid_raw,q.ask_raw),))
        if paid:
            p=paid[0]
            if p.id not in self.funded.proposals:return self._deliver(())
            context=broker_cash_context(p,self.funded)
            self._cancel_same_ms_lower(ms)
            self.last_emitted_ms=ms
            self.counts['funded_anchor_selected']+=1
            return self._deliver((SourceCandidate(ms,p.side,'OMEGAFX_ACKNOWLEDGED_FILL_ANCHOR',p.rung,
                  p.threshold_raw,q.bid_raw,q.ask_raw,p.id,p.prior_paid_close_id,
                  context['prior_hold_bucket'] if context['verified_parent_available'] else None,
                  context.get('broker_cash_recorded_usd')),))
        return self._supplemental(q,(),new_native,new_auction)
    def _deliver(self,current):
        # This is metadata from known completed M5 and current Bid/Ask only.
        # A delayed earlier-timestamp event must not borrow today's next-tick
        # horizon hint: retain no hint unless source time == current timestamp.
        current=tuple(replace(x,research_horizon_ms=self._exit_hint.horizon_ms)
                      if self._exit_hint is not None and x.time_ms==self.last_ms
                      else x for x in current)
        # Provisional prior-ms source is released ONLY on this observed quote.
        # Do not backdate order availability to its original trigger quote.
        past=tuple(replace(x,available_ms=self.last_ms) for x in self._ready_release)
        current=tuple(replace(x,available_ms=self.last_ms) for x in current)
        out=past+current
        if out:
            # No teacher score and no lookahead; delayed G0 stamped at now.
            causal=self.cycle_research.snapshot()
            out=tuple(replace(x,cycle_fingerprint=causal) for x in out)
        self._ready_release=()
        return out
    def _supplemental(self,q,base,native,auction):
        ms=q.time_ms_utc
        if ms==self.last_emitted_ms:
            self.counts['supplemental_timestamp_rejected']+=len(native)+len(auction)
            return self._deliver(())
        if base:raise ValueError('base must be handled before supplemental')
        if native:
            x=native[0]
            candidate=SourceCandidate(ms,x.side,x.source,
                max(1,x.rung_raw//x.grid_step_raw),
                (q.bid_raw+q.ask_raw)//2,q.bid_raw,q.ask_raw)
            rank=2
        elif auction:
            x=auction[0]
            candidate=SourceCandidate(ms,0,x.source+':'+x.family,abs(x.boundary_cell),
                   x.anchor_raw+x.boundary_cell*x.gap_raw,q.bid_raw,q.ask_raw,
                   raw_cross_sign=x.cross_sign)
            rank=1
        else:
            return self._deliver(())
        # Supplemental sources remain provisional throughout source timestamp.
        # An S1/M1/M5 or actually acknowledged creator source on any later
        # tick of SAME millisecond must win without an invented extra ticket.
        p=self._low_priority_pending
        if p is None or self._candidate_rank(p)<rank:
            self._low_priority_pending=candidate
            self.counts['provisional_'+('native_136a' if native else 'auction_136b')]+=1
        return self._deliver(())
    @staticmethod
    def _candidate_rank(p):
        return 2 if p.source=='APRIL136A_CAUSAL_NATIVE_MINUTE_RUNG' else 1
    def _cancel_same_ms_lower(self,ms):
        if self._low_priority_pending and self._low_priority_pending.time_ms==ms:
            self._low_priority_pending=None
            self.counts['provisional_suppressed_by_original_grid']+=1
    @staticmethod
    def _base_candidate(q,base):
        for e in base[:1]:
            yield SourceCandidate(q.time_ms_utc,e.side,e.source,e.rung,
                   int(round(e.crossing_level_usd*SCALE)),q.bid_raw,q.ask_raw)
    def stats(self):
        return {'stage':'G0_UNFUNDED_SOURCE_ONLY',
                'counts':dict(self.counts),
                'base':self.multiscale.stats(),
                'paid':dict(self.funded.counts),
                'native_136a':dict(self.native.counts),
                'auction_136b':dict(self.auction.counts)}
