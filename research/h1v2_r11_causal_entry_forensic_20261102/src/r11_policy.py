"""R11 research-only eligibility-first BUY/SELL/WAIT action gate.

Never treats raw ranking scores as calibrated trade probabilities. All gates
fail closed if no separately trained, validated, signed source-specific
evidence is provided. This code places no orders and does no backtest.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ActionEvidence:
    side: str
    p_correct_lower:float
    p_bad_upper:float
    expected_net_lower:float
    cvar_loss_upper:float
    independent_blocks:int
    source_verified:bool=False
    model_verified:bool=False
    calibrated_chronologically:bool=False

@dataclass(frozen=True)
class AdmissionPolicy:
    min_correct_lower:float=.80
    max_bad_upper:float=.20
    min_net_lower:float=0.0
    max_cvar_loss_upper:float=.40
    min_independent_blocks:int=30
    max_spread:float=1.50

def eligible(e:ActionEvidence, p:AdmissionPolicy, spread:float, quote_epoch_ready:bool)->bool:
    if e.side not in ("BUY","SELL"):return False
    if not all((e.source_verified,e.model_verified,e.calibrated_chronologically,quote_epoch_ready)):return False
    vals=(spread,e.p_correct_lower,e.p_bad_upper,e.expected_net_lower,e.cvar_loss_upper)
    if not all(isfinite(x) for x in vals):return False
    if spread<0 or spread>p.max_spread or e.independent_blocks<p.min_independent_blocks:return False
    return (e.p_correct_lower>=p.min_correct_lower
            and e.p_bad_upper<=p.max_bad_upper
            and e.expected_net_lower>p.min_net_lower
            and e.cvar_loss_upper<=p.max_cvar_loss_upper)

def decide(buy:ActionEvidence|None,sell:ActionEvidence|None,spread:float,
           quote_epoch_ready:bool, policy:AdmissionPolicy=AdmissionPolicy())->str:
    """Qualify EACH action before comparison, never 'select one then reject'."""
    ready=[e for e in (buy,sell) if e is not None and eligible(e,policy,spread,quote_epoch_ready)]
    if not ready:return "WAIT"
    if len({e.side for e in ready})!=len(ready):raise ValueError("duplicate directional evidence")
    # Only positive conservative net qualified sides. Equal value -> WAIT.
    if len(ready)==2 and abs(ready[0].expected_net_lower-ready[1].expected_net_lower)<=1e-12:
        return "WAIT"
    return max(ready,key=lambda e:e.expected_net_lower).side
