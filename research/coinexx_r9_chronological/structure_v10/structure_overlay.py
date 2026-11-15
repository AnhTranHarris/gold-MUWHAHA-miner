"""Drop-in observational subclass of the EXISTING frozen V9 router.

Every real entry and exit calls the unchanged V9 implementation. Structural
advice is diagnostics ONLY: never orders, holds, stops, governor or volume cuts.
"""
from __future__ import annotations
from collections import Counter, deque
from causal_structure import CausalMarketStructure
from specialist_policy import HierarchicalPolicy
from v9_volume_router import VolumePreservingMicroV9


class StructureShadowV10(VolumePreservingMicroV9):
    def __init__(self, cfg, cash, *args, **kwargs):
        super().__init__(cfg,cash,*args,**kwargs)
        self.structure=CausalMarketStructure()
        self.policy=HierarchicalPolicy()
        self.active_thesis=None
        self.specialist_counts=Counter()
        self.lifecycle_counts=Counter()
        self.structure_entries=Counter()
        self.structure_exit_views=Counter()
        self.structure_events=deque(maxlen=512)
        self._last_hold_view=None

    def _push_second(self,t):
        super()._push_second(t)
        self.structure.on_quote(t)

    def _open_trade(self,t,side):
        snap=self.structure.snapshot(t)
        advice=self.structure.entry_advice(snap,side)
        plan=self.policy.propose(snap,side,t.bid_u,t.ask_u)
        was=len(self.entries)
        super()._open_trade(t,side)
        if len(self.entries)==was:return
        self.structure_entries[advice]+=1
        self.specialist_counts[plan.specialist]+=1
        self.active_thesis=plan
        self.entries[-1].update({
            "v10_specialist":plan.specialist,
            "v10_specialist_proposal":plan.proposal,
            "v10_structural_stop":plan.structural_stop,
            "v10_nearby_obstacle":plan.nearby_obstacle,
            "v10_pattern":snap.pattern,"v10_regime":snap.regime,
            "v10_parent":snap.parent_direction,"v10_micro":snap.micro_direction,
            "v10_nested":snap.nested,"v10_entry_advice":advice,
            "v10_support":snap.support,"v10_resistance":snap.resistance,
            "v10_shadow_only":True,
        })
        self.structure_events.append({
            "time_msc":t.time_msc,"event":"ENTRY","side":side,
            "advice":advice,"snapshot":snap.as_record()})
        self._last_hold_view=None

    def _manage_position(self,t):
        if self.position is not None:
            snap=self.structure.snapshot(t)
            view=self.structure.hold_advice(snap,self.position.side,
                                            "entry_thesis_observed")
            if self.active_thesis is not None:
                lifecycle=self.policy.review(self.active_thesis,snap,
                                             self.position.side,t.bid_u,t.ask_u)
                view=view+"|"+lifecycle.action
            if view!=self._last_hold_view:
                self.structure_exit_views[view]+=1
                if self.active_thesis is not None:
                    self.lifecycle_counts[lifecycle.action]+=1
                self.structure_events.append({
                    "time_msc":t.time_msc,"event":"HOLD_ADVICE",
                    "advice":view,"snapshot":snap.as_record()})
                self._last_hold_view=view
        return super()._manage_position(t)

    def _record_close(self,t,reason,exit_u):
        side=self.position.side if self.position is not None else 0
        # Broker SL is checked BEFORE current tick enters the structure engine.
        seen=self.structure.now_ms
        if side:
            self.structure_events.append({
                "time_msc":t.time_msc,"event":"EXIT",
                "reason":reason,"side":side,
                "last_structure_quote_ms":seen})
        self._last_hold_view=None
        self.active_thesis=None
        return super()._record_close(t,reason,exit_u)

    def report(self):
        result=super().report()
        result["structure_v10"]={
            "mode":"SHADOW_NO_ORDER_OR_EXIT_EFFECT",
            "original_v9_on_policy":True,
            "price_source":"observed_Bid_Ask_not_trade_volume",
            "zones":len(self.structure.zones),
            "entry_advice_counts":dict(self.structure_entries),
            "specialist_counts":dict(self.specialist_counts),
            "lifecycle_action_transitions":dict(self.lifecycle_counts),
            "hold_advice_transitions":dict(self.structure_exit_views),
            "event_counters":dict(self.structure.counters),
            "diagnostic_event_count_retained":len(self.structure_events),
            "native_MQL5_parity_certified":False,
        }
        return result
