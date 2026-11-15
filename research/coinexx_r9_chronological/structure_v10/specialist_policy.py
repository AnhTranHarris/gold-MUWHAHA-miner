"""V10 hypothesis router: pattern-specific ENTRY and LIFECYCLE ADVICE ONLY.

Deterministic labels are not probabilities and NOT trading instructions. No
entry permission, lot sizing, governor changes or broker methods exist here.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SpecialistPlan:
    specialist: str
    proposal: str
    side: int
    entry_ms: int
    structural_stop: Optional[float]
    nearby_obstacle: Optional[float]
    thesis: str
    reliability: str = "UNVALIDATED_RESEARCH"


@dataclass(frozen=True)
class LifecycleReview:
    action: str
    reason: str
    specialist: str
    structural_stop: Optional[float]


class HierarchicalPolicy:
    """No universal trade veto: each pattern has its own interpretation.

    Input observation must be emitted by the causal structure engine as-of
    the current source tick. The policy never receives future outcomes.
    """
    def propose(self,snap,side,bid,ask):
        if side not in (-1,1) or bid<=0 or ask<bid:
            raise ValueError("Invalid executable-side candidate")
        support, resistance=snap.support,snap.resistance
        observed=bid if side>0 else ask
        protection=(support[0] if side>0 and support else
                    resistance[1] if side<0 and resistance else None)
        obstacle=(resistance[0] if side>0 and resistance else
                  support[1] if side<0 and support else None)
        if snap.pattern=="UNKNOWN_STALE":
            return SpecialistPlan("DATA_QUALITY","WAIT",side,snap.time_msc,
                                  None,None,"stale quote not an eligible pattern")
        if snap.breakout_side==side and snap.breakout_phase=="PROBE":
            return SpecialistPlan("BREAKOUT_INITIATION","WAIT_CONFIRM",side,
                                  snap.time_msc,protection,obstacle,
                                  "first penetration not yet accepted")
        if snap.breakout_side==side and snap.breakout_phase=="ACCEPTED":
            return SpecialistPlan("BREAKOUT_ACCEPTANCE","STRUCTURAL_CANDIDATE",
                                  side,snap.time_msc,protection,obstacle,
                                  "two separate completed source seconds accept frozen boundary")
        if snap.breakout_side==side and snap.breakout_phase=="RETEST":
            return SpecialistPlan("BREAKOUT_RETEST","WAIT_REJECTION",side,
                                  snap.time_msc,protection,obstacle,
                                  "accepted breakout now retests frozen boundary")
        if snap.breakout_side==side and snap.breakout_phase=="RETEST_CONFIRMED":
            return SpecialistPlan("BREAKOUT_RETEST","STRUCTURAL_CANDIDATE",
                                  side,snap.time_msc,protection,obstacle,
                                  "executable-side continuation after observed retest")
        if snap.breakout_side==side and snap.breakout_phase=="FAILED":
            return SpecialistPlan("FALSE_BREAK_DEFENSE","AVOID_UNTIL_NEW_SETUP",
                                  side,snap.time_msc,protection,obstacle,
                                  "price crossed back through frozen zone")
        if (snap.pattern=="REVERSAL_CONFIRMED" and
                snap.micro_direction==side):
            return SpecialistPlan("STRUCTURAL_REVERSAL","STRUCTURAL_CANDIDATE",
                                  side,snap.time_msc,protection,obstacle,
                                  "confirmed short swing topology plus recent regime shift")
        if snap.parent_direction==side and snap.micro_direction==side:
            return SpecialistPlan("TREND_CONTINUATION","STRUCTURAL_CANDIDATE",
                                  side,snap.time_msc,protection,obstacle,
                                  "micro and parent trend agree")
        if snap.parent_direction==-side and snap.micro_direction==side:
            return SpecialistPlan("NESTED_COUNTERTREND","WAIT_PARENT_RESOLUTION",
                                  side,snap.time_msc,protection,obstacle,
                                  "micro direction opposes confirmed parent direction")
        if snap.pattern=="CONSOLIDATION":
            # A range-boundary touch alone does NOT establish rejection.
            if protection is not None and abs(observed-protection) <= (
                (support[1]-support[0])*2 if side>0 and support else
                (resistance[1]-resistance[0])*2 if resistance else 0):
                return SpecialistPlan("RANGE_BOUNDARY","WAIT_REJECTION",side,
                                      snap.time_msc,protection,obstacle,
                                      "close to confirmed zone; rejection not yet demonstrated")
            return SpecialistPlan("RANGE_INTERIOR","OBSERVE_ONLY",side,
                                  snap.time_msc,protection,obstacle,
                                  "inside consolidation without boundary rejection")
        return SpecialistPlan("UNRESOLVED","OBSERVE_ONLY",side,snap.time_msc,
                              protection,obstacle,"no specialist evidence")

    def review(self,plan,snap,side,bid,ask):
        if side not in (-1,1) or plan.side!=side:
            raise ValueError("Thesis position side mismatch")
        if snap.pattern=="UNKNOWN_STALE":
            return LifecycleReview("RISK_REVIEW","quote gap or stale structure",
                                   plan.specialist,plan.structural_stop)
        exit_quote=bid if side>0 else ask
        if plan.structural_stop is not None:
            breached=(exit_quote<plan.structural_stop if side>0
                      else exit_quote>plan.structural_stop)
            if breached:
                return LifecycleReview("THESIS_INVALIDATED",
                      "crossed frozen structural invalidation boundary",
                      plan.specialist,plan.structural_stop)
        if snap.breakout_phase=="FAILED" and snap.breakout_side==side:
            return LifecycleReview("THESIS_INVALIDATED",
                    "breakout failed back through observed boundary",
                    plan.specialist,plan.structural_stop)
        if (snap.parent_direction==-side and snap.micro_direction==-side and
            plan.specialist in ("TREND_CONTINUATION","BREAKOUT_ACCEPTANCE",
                                "BREAKOUT_RETEST")):
            return LifecycleReview("DEFEND","parent and micro directions oppose thesis",
                                   plan.specialist,plan.structural_stop)
        if snap.pattern in ("REVERSAL_CANDIDATE","REVERSAL_CONFIRMED") and snap.micro_direction==-side:
            return LifecycleReview("DEFEND","recent opposite directional change",
                                   plan.specialist,plan.structural_stop)
        return LifecycleReview("HOLD_OBSERVE","no currently confirmed structural invalidation",
                               plan.specialist,plan.structural_stop)
