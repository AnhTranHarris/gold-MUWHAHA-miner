"""
BETA064-C02-S1 session authority layer.

Research-only child of Major Checkpoint 01.
Checkpoint-01 remains immutable.
Hold+Exit remains deferred.
August remains sealed.
"""

from dataclasses import dataclass

BASE_SURVIVAL_FLOOR = 0.88
BASE_ECONOMIC_FLOOR = 0.30

SESSION_BLEND_WEIGHT = 0.75
SESSION_ECONOMIC_FLOOR = 0.08

# Conservative research floors selected for the gap-fill child.
SESSION_SURVIVAL_FLOORS = {
    "AUSTRALIA": 0.920,
    "ASIA":      0.900,
    "MIDEAST":   0.915,
    "EUROPE":    0.910,
    "UK":        0.925,
    "NY":        0.925,
}

# Only these frozen Entry specialists are permitted to receive additive
# session authority. E1/E3/E4/E8 remain under the Major Checkpoint-01
# router only until they earn stronger session evidence.
SESSION_OVERRIDE_SPECIALISTS = {
    "E5_VWAP_RECLAIM",
    "E6_VALUE_REVERSION",
    "E7_SWEEP_RECLAIM",
    "E9_LEVEL_BREAK",
    "E10_COMPRESSION_RELEASE",
    "E11_KINETIC_IGNITION",
    "E12_FAILED_EXPANSION",
}

@dataclass(frozen=True)
class SessionDesk:
    name: str
    timezone: str
    open_hour_local: int
    close_hour_local: int
    status: str = "ACTIVE_RESEARCH_AUTHORITY"

SESSION_DESKS = {
    "AUSTRALIA": SessionDesk("AUSTRALIA", "Australia/Sydney", 8, 17),
    "ASIA":      SessionDesk("ASIA",      "Asia/Tokyo",       9, 18),
    "MIDEAST":   SessionDesk("MIDEAST",   "Asia/Dubai",       8, 17),
    "EUROPE":    SessionDesk("EUROPE",    "Europe/Berlin",    8, 17),
    "UK":        SessionDesk("UK",        "Europe/London",    8, 17),
    "NY":        SessionDesk("NY",        "America/New_York", 8, 17),
}

# The four major FX liquidity-center sessions are externally documented.
# MIDEAST is intentionally an engineered Dubai regional liquidity window,
# not claimed as a universally standardized FX session.
PUBLIC_METHOD_REFERENCES = (
    "https://www.oanda.com/us-en/skills-and-insights/education/trading-asset-classes/forex/when-is-the-best-time-for-forex-trading/",
    "https://www.ig.com/uk/trading-strategies/when-is-the-forex-market-open-and-when-should-you-trading-in-the-191106",
)

def blended_session_probability(base_probability: float, session_probability: float) -> float:
    """Blend frozen Checkpoint-01 opinion with the active regional desk."""
    w = SESSION_BLEND_WEIGHT
    return (1.0 - w) * base_probability + w * session_probability

def session_entry_score(
    base_survival: float,
    base_first_passage: float,
    session_survival: float,
    session_first_passage: float,
) -> tuple[float, float, float]:
    """Return blended survival, blended first-passage probability, economic score."""
    ps = blended_session_probability(base_survival, session_survival)
    pw = blended_session_probability(base_first_passage, session_first_passage)
    return ps, pw, ps * pw

def can_session_override(
    specialist: str,
    authority: str,
    blended_survival: float,
    blended_entry_score: float,
) -> bool:
    """
    Additive authority only.

    This function must never delete or replace a valid frozen Checkpoint-01
    position. It only decides whether a rejected frozen candidate may be
    considered for an otherwise-idle account gap.
    """
    if specialist not in SESSION_OVERRIDE_SPECIALISTS:
        return False
    floor = SESSION_SURVIVAL_FLOORS.get(authority)
    if floor is None:
        return False
    return (
        blended_survival >= floor
        and blended_entry_score >= SESSION_ECONOMIC_FLOOR
    )

def gap_is_free(candidate_start_ms: int, candidate_end_ms: int, frozen_intervals) -> bool:
    """
    True only when the entire candidate lifecycle fits between frozen
    Checkpoint-01 reserved intervals. Prevents an earlier session trade from
    suppressing a later frozen baseline position.
    """
    for start_ms, end_ms in frozen_intervals:
        if candidate_start_ms < end_ms and candidate_end_ms > start_ms:
            return False
    return True

RESEARCH_GATES = {
    "major_checkpoint_01_preserved": True,
    "monthly_entry_hold_survival_target": 0.85,
    "session_child_safety_margin": 0.87,
    "hold_exit_optimization": False,
    "august": "SEALED",
    "mql5_promotion": False,
}
