"""
BETA064 Checkpoint-02G derivative-state reconstruction specification.

RESEARCH ONLY.
Major Checkpoint 02 is immutable.
Alpha/GAMMA are prohibited dependencies.
Hold->Exit is outside scope.
August is sealed.

This file freezes the mathematical derivative contract and the session authority
matrix recovered from C02G. It is NOT a claim that the transient C02G trainer
was preserved byte-for-byte. A rerun must reproduce the committed C02G result
tables before extending the architecture.
"""

from dataclasses import dataclass
from typing import Literal

DerivativeOrder = Literal[
    "NONE",
    "D1_5S",
    "D2_5S",
    "D3_5S",
    "D3_PLUS_1S_MICRO",
]

DERIVATIVE_AUTHORITY_MATRIX: dict[str, DerivativeOrder] = {
    "AUSTRALIA": "D3_5S",
    "ASIA": "D2_5S",
    "MIDEAST": "D3_PLUS_1S_MICRO",
    "EUROPE": "NONE",
    "UK": "D1_5S",
    "NY": "D3_PLUS_1S_MICRO",
}

# Parent/state fields that may feed derivative packets.
DERIVATIVE_STATE_FAMILIES = (
    "price_displacement_or_return",
    "path_efficiency",
    "spread_or_friction",
    "tick_activity_or_intensity",
    "quote_pressure",
    "quote_volume_imbalance_proxy",
    "session_or_vwap_value_displacement",
)

@dataclass(frozen=True)
class DerivativePacket:
    session: str
    order: DerivativeOrder
    d1_5s: dict[str, float]
    d2_5s: dict[str, float]
    d3_5s: dict[str, float]
    d1_1s: dict[str, float] | None = None
    d2_1s: dict[str, float] | None = None
    d3_1s: dict[str, float] | None = None

def d1(x_t: float, x_tm1: float) -> float:
    return x_t - x_tm1

def d2(x_t: float, x_tm1: float, x_tm2: float) -> float:
    return (x_t - x_tm1) - (x_tm1 - x_tm2)

def d3(x_t: float, x_tm1: float, x_tm2: float, x_tm3: float) -> float:
    d2_t = (x_t - x_tm1) - (x_tm1 - x_tm2)
    d2_tm1 = (x_tm1 - x_tm2) - (x_tm2 - x_tm3)
    return d2_t - d2_tm1

CAUSALITY_RULES = (
    "5s bucket [t,t+5s) is observable only at t+5s",
    "1s micro bucket is observable only after that second completes",
    "no future tick/bar may enter derivative state",
    "derivative packet is evaluated at parent proposal time",
    "do not delay entry waiting for a derivative confirmation",
)

RESEARCH_ONLY_DESCENDANTS = {
    "AUSTRALIA": "E6.D3",
    "ASIA": "E6.D2",
    "MIDEAST": "E6.D3mu",
    "EUROPE": "E6.parent",
    "UK": "E6.D1",
    "NY": "E6.D3mu",
}

PROHIBITED = (
    "standalone derivative entry authority without new validation",
    "post-signal derivative confirmation delay",
    "universal derivative order across all sessions",
    "Alpha dependency",
    "GAMMA dependency",
    "August access",
)
