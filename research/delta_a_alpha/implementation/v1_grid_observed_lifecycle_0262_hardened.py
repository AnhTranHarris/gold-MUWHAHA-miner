"""Hardened bid/ask trailing and target management for GRID0262 research.

No broker stop-modify ACK, freeze level, rejected order or transaction feed
is invented. This is explicit unpromoted quote sandbox state, not MT5 parity.
"""
from __future__ import annotations
from dataclasses import dataclass
from v1_grid_funded_quote_gate_0259 import Quote, OpenResearchPosition, ResearchSettlement
from v1_grid_funded_quote_gate_0262_hardened import HardenedQuoteFundingEngine

@dataclass(frozen=True)
class HardenedExitPolicy:
    source:str
    arm_raw:int
    trail_raw:int
    profit_target_raw:int|None=None
    def __post_init__(self):
        if not self.source or self.arm_raw<0 or self.trail_raw<=0 or (
            self.profit_target_raw is not None and self.profit_target_raw<=0):
            raise ValueError('invalid protective policy')

class HardenedObservedLifecycleFundingEngine(HardenedQuoteFundingEngine):
    def __init__(self,*,exit_policies:tuple[HardenedExitPolicy,...],**kwargs):
        super().__init__(**kwargs)
        if len({p.source for p in exit_policies})!=len(exit_policies):
            raise ValueError('duplicate exit source policy')
        self.policies={p.source:p for p in exit_policies}
        self.armed_ids:set[str]=set()
        self.target_closes=0
        self.trail_moves=0

    def _close(self,p:OpenResearchPosition,q:Quote,reason:str):
        super()._close(p,q,reason)
        self.armed_ids.discard(p.event_id)

    def on_observed_quote(self,q:Quote)->tuple[ResearchSettlement,...]:
        # VALIDATE *before* mutating stops or checking targets.
        self._validate_quote(q)
        if not q.broker_tradable:
            # Defers even apparently hit targets and all stops until next
            # explicitly authorized quote; price may have already reversed.
            return super().on_observed_quote(q)
        first=len(self.settlements)
        alive=[]
        for p in self.open:
            if q.utc_ms<=p.entry_ms:
                alive.append(p);continue
            policy=self.policies.get(p.source)
            if policy is None:
                alive.append(p);continue
            executable=q.bid_raw if p.side==1 else q.ask_raw
            stop_hit=(executable<=p.stop_raw if p.side==1 else executable>=p.stop_raw)
            # Safety priority: a stop or expiry is settled by superclass,
            # rather than replaced by a fabricated target in the same tick.
            if stop_hit or q.utc_ms>=p.deadline_ms:
                alive.append(p);continue
            favorable=(executable-p.entry_raw)*p.side
            if policy.profit_target_raw is not None and favorable>=policy.profit_target_raw:
                self._close(p,q,'OBSERVED_TARGET_EXIT')
                self.target_closes+=1
                continue
            if favorable>=policy.arm_raw:
                self.armed_ids.add(p.event_id)
            if p.event_id in self.armed_ids:
                proposal=executable-p.side*policy.trail_raw
                if ((p.side==1 and proposal>p.stop_raw) or
                    (p.side==-1 and proposal<p.stop_raw)):
                    p.stop_raw=proposal
                    self.trail_moves+=1
            alive.append(p)
        self.open=alive
        super().on_observed_quote(q)
        return tuple(self.settlements[first:])

    def summary(self)->dict:
        d=super().summary()
        d.update({'trailing_stop_updates_unacknowledged':self.trail_moves,
                  'observed_target_closes':self.target_closes,
                  'broker_stop_modify_ack_verified':False})
        return d
