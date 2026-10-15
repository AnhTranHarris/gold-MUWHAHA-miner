"""January 2026 L3/L6/L7 experimental ADAPTER — explicit opt-in ONLY.

Isolates the verified M1 phase risk gate + completed M5 ATR conditioned
squeeze-exit policy without modifying the owner-frozen V1 Python engine.
Community inspiration: finite-cycle mode supervision and ATR-following exits.
Full quote-by-quote execution and physical slot constraints are in the
research simulator jan_r9_teacher_m1_phase_risk_v1.py, not in this adapter.

NOT BROKER CERTIFIED; not installed in the protected production path.
"""
from dataclasses import dataclass
from typing import Literal
from math import isfinite

@dataclass(frozen=True)
class LossGovernorConfig:
    phase_min_seconds: int = 2
    phase_max_seconds: int = 59
    spread_max_usd: float = 0.55
    signal_quote_ttl_ms: int = 15_000
    latency_floor_ms: int = 250
    max_signal_quote_drift_usd: float = 1.50
    atr_m5_high_usd: float = 7.77
    position_cap: int = 1
    lots: float = 0.01
    assumed_contract_oz: float = 100.0
    assumed_fee_cash: float = 0.20

@dataclass(frozen=True)
class ExitLifecycle:
    stop_usd: float
    target_usd: float
    trail_arm_usd: float
    trail_gap_usd: float
    max_holding_ms: int
    regime: Literal['ATR_HIGH', 'ATR_NOT_HIGH']

BASE=ExitLifecycle(7.,20.,5.,2.5,1_500_000,'ATR_NOT_HIGH')
HIGH=ExitLifecycle(7.,40.,7.,3.5,1_500_000,'ATR_HIGH')

@dataclass(frozen=True)
class CandidateDecision:
    approved: bool
    reason: str
    lifecycle: ExitLifecycle | None


def event_permission(*, signal_utc_ms:int, side:int,
                     source:str, completed_m5_atr_usd:float,
                     config:LossGovernorConfig=LossGovernorConfig())->CandidateDecision:
    """Pre-order proposal evaluation: no future minute close or R9 SYNTH outcome.

    The full tick replay uses an as-of S15 compressed-break signal. This
    adapter does not generate its own signals or authorize brokerage orders.
    """
    if source!='COMPLETED_S15_BB_KELTNER_SQUEEZE':
        return CandidateDecision(False,'SOURCE_NOT_CERTIFIED_IN_THIS_CHILD',None)
    if side not in (-1,1) or signal_utc_ms<0:
        return CandidateDecision(False,'INVALID_SIGNAL',None)
    phase=(signal_utc_ms//1000)%60
    if phase<config.phase_min_seconds or phase>config.phase_max_seconds:
        return CandidateDecision(False,'M1_OPEN_PHASE_GROSS_LOSS_SHIELD',None)
    if not isfinite(completed_m5_atr_usd):
        return CandidateDecision(False,'M5_ATR_NOT_ASOF_COMPLETE',None)
    state=HIGH if completed_m5_atr_usd>=config.atr_m5_high_usd else BASE
    return CandidateDecision(True,'JANUARY_RESEARCH_HYPOTHESIS',state)


def observable_quote_permission(*,signal_utc_ms:int,fill_quote_utc_ms:int,
                                signal_side_quote:float, candidate_side_quote:float,
                                bid:float,ask:float,
                                config:LossGovernorConfig=LossGovernorConfig())->bool:
    """Conservative quote-side condition only; physical slot must be checked by L7."""
    elapsed=fill_quote_utc_ms-signal_utc_ms
    return (config.latency_floor_ms<=elapsed<=config.signal_quote_ttl_ms
            and ask>=bid and ask-bid<=config.spread_max_usd+1e-12
            and abs(candidate_side_quote-signal_side_quote)<=config.max_signal_quote_drift_usd+1e-12)
