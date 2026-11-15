"""V11 research-only overlay; frozen V9/V10 execution decisions unchanged.

V10's unverified structural-stop advice is retained only as historical
diagnostic. V11 emits a separate strictly behind-entry, frozen-zone observer.
"""
from __future__ import annotations

from collections import Counter

from structure_overlay import StructureShadowV10
from structure_refinement_v11 import (
    RefinedStructure, InvalidationObserver, freeze_thesis,
)


class StructureShadowV11(StructureShadowV10):
    def __init__(self,cfg,cash,*args,**kwargs):
        super().__init__(cfg,cash,*args,**kwargs)
        self.structure=RefinedStructure()
        self.v11_thesis=None
        self.v11_invalidation=None
        self.v11_entry_profile_counts=Counter()
        self.v11_unresolved_reasons=Counter()
        self.v11_anchor_counts=Counter()
        self.v11_lifecycle_transitions=Counter()
        self._last_v11_lifecycle=None

    def _open_trade(self,t,side):
        # Parent calls the unchanged V9 opening method. No veto is possible.
        was=len(self.entries)
        super()._open_trade(t,side)
        if len(self.entries)==was:
            return
        snap=self.structure.snapshot(t)
        legacy_specialist=self.entries[-1]["v10_specialist"]
        profile=self.structure.profile(snap,side,legacy_specialist)
        frozen=freeze_thesis(self.structure,side,t)
        self.v11_thesis=frozen
        self.v11_invalidation=InvalidationObserver(frozen)
        self._last_v11_lifecycle=None
        self.v11_entry_profile_counts[profile.subtype]+=1
        self.v11_anchor_counts["valid_spatial_zone" if frozen.anchored
                               else "no_eligible_structural_zone"]+=1
        if legacy_specialist=="UNRESOLVED":
            self.v11_unresolved_reasons[profile.subtype]+=1
        self.entries[-1]["v11_profile"]=profile.record()
        self.entries[-1]["v11_frozen_thesis"]=frozen.record()
        self.entries[-1]["v11_shadow_only"]=True
        self.structure_events.append({
            "time_msc":t.time_msc,"event":"V11_ENTRY_PROFILE",
            "subtype":profile.subtype,"anchor":frozen.zone_key,
            "invalidation":frozen.invalidation_level,
            "research_only":True})

    def _manage_position(self,t):
        if self.position is not None and self.v11_invalidation is not None:
            state=self.v11_invalidation.observe(t)
            if state!=self._last_v11_lifecycle:
                self.v11_lifecycle_transitions[state]+=1
                self.structure_events.append({
                    "time_msc":t.time_msc,"event":"V11_STRUCTURE_LIFECYCLE",
                    "status":state,"frozen_zone":self.v11_thesis.zone_key,
                    "research_only":True})
                self._last_v11_lifecycle=state
        # Parent's V10 research observations continue. V9 handles the real
        # existing timed stop/cash exit, untouched by any V11 state.
        return super()._manage_position(t)

    def _record_close(self,t,reason,exit_u):
        if self.v11_invalidation is not None:
            self.structure_events.append({
                "time_msc":t.time_msc,
                "event":"V11_CLOSED_WITHOUT_EXECUTION_EFFECT",
                "v9_reason":reason,
                "v11_confirmed_structural_invalidation":
                    bool(self.v11_invalidation.confirmed)})
        self.v11_thesis=None
        self.v11_invalidation=None
        self._last_v11_lifecycle=None
        return super()._record_close(t,reason,exit_u)

    def report(self):
        result=super().report()
        now=self.structure.now_ms or 0
        result["structure_v11"]={
            "mode":"SHADOW_NO_ORDER_OR_EXIT_EFFECT",
            "baseline":"V10_original_unchanged",
            "v11_entry_subtypes":dict(self.v11_entry_profile_counts),
            "v11_unresolved_reasons":dict(self.v11_unresolved_reasons),
            "entry_zone_anchor_validity":dict(self.v11_anchor_counts),
            "v11_lifecycle_state_transitions":
                dict(self.v11_lifecycle_transitions),
            "htf_zone_count_per_frame":self.structure.bank.counts(now),
            "htf_zone_management_counters":dict(self.structure.bank.counters),
            "original_v9_decisions_modified":False,
            "native_mt5_parity_verified":False,
            "structural_recommendations_approved_to_trade":False,
        }
        return result
