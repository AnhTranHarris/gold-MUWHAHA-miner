"""Source causal research-only staging adapter; no MT5 position opening or execution.
As-of clocks: F234 emitted t0; F331 rescues only F234-rejected at t0+5s;
F330 original 5s cancellation of existing accepted signal; F337 pending source veto
at t0+15s. Never call F337 at t0 or use future class truth at decision.

External F332 178D source-as-of 5s/10s/15s builder and F335 124D
source-as-of original t0 builder are provided separately and SHA-locked.
This adapter only combines already causal model scores and states; it does not
know class labels, future original 30–32s outcomes or native MT5 filled prices.
"""
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Literal

class Decision(str,Enum):
    CANCEL="CANCEL"; PENDING="PENDING"; KEEP="KEEP"; RECOVER="RECOVER"; UNAVAILABLE="UNAVAILABLE"

@dataclass(frozen=True)
class ScoreCuts:
    class_risk_q850:float
    class_risk_q900:float
    class_risk_q950:float
    t0_guard_q45:float
    t0_guard_q75:float
    rescue_correct_q900:float
    def __post_init__(self):
        assert all(isfinite(float(x)) and 0<=x<=1 for x in self.__dict__.values())
        assert self.class_risk_q850<=self.class_risk_q900<=self.class_risk_q950
        assert self.t0_guard_q45<=self.t0_guard_q75

@dataclass(frozen=True)
class OriginalEvent:
    t0_ms:int
    original_f234_keep:bool

@dataclass(frozen=True)
class PendingState:
    event:OriginalEvent
    after5:Decision

def decide_at_5s(event:OriginalEvent, now_ms:int, source_quote_asof_ms:int,
                  f330_cancellation:bool, f331_correct_score:float|None,
                  cuts:ScoreCuts)->PendingState:
    """Only source observed by t0+5000; no future original label in signature."""
    assert now_ms>=event.t0_ms+5000, "5-second decision is not available at t0"
    assert source_quote_asof_ms<=now_ms
    if event.original_f234_keep:
        return PendingState(event,Decision.CANCEL if f330_cancellation else Decision.PENDING)
    if f331_correct_score is None:
        return PendingState(event,Decision.UNAVAILABLE)
    assert 0<=f331_correct_score<=1
    return PendingState(event,Decision.RECOVER if f331_correct_score>=cuts.rescue_correct_q900 else Decision.CANCEL)

def decide_at_15s(state:PendingState, now_ms:int, source_quote_asof_ms:int,
                   risk_prob_wrong_or_neutral:float|None,t0_guard_prob_wrong:float|None,
                   cuts:ScoreCuts)->Decision:
    """R6 frozen three-tier veto. F331 rescued events are already decided at t+5.
    Score probabilities were produced from causal source inputs only; this
    adapter enforces clock ordering but upstream source data must be audited.
    """
    if state.after5!=Decision.PENDING: return state.after5
    assert now_ms>=state.event.t0_ms+15000, "15-second data unavailable at t0/t+5"
    assert source_quote_asof_ms<=now_ms
    if risk_prob_wrong_or_neutral is None or t0_guard_prob_wrong is None: return Decision.UNAVAILABLE
    r=float(risk_prob_wrong_or_neutral);g=float(t0_guard_prob_wrong)
    assert 0<=r<=1 and 0<=g<=1
    veto=(r>=cuts.class_risk_q950 or
         (r>=cuts.class_risk_q900 and g>=cuts.t0_guard_q45) or
         (r>=cuts.class_risk_q850 and g>=cuts.t0_guard_q75))
    return Decision.CANCEL if veto else Decision.KEEP

def cuts_from_fit(f332:dict,f335:dict,f331:dict)->ScoreCuts:
    c=f332['cuts_training_prediction_only'];g=f335['cutoffs_training_only'];rc=f331['cutoffs']
    return ScoreCuts(c['fit_q850'],c['fit_q900'],c['fit_q950'],g['45'],g['75'],rc['fit_q900'])
