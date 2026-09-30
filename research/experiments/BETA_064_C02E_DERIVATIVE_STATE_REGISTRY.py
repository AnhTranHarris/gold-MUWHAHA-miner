"""
BETA064 C02E derivative-state research registry.

Derivative specialists are shadow state descendants, not independent production desks.
Alpha/GAMMA dependencies are prohibited.
"""

DERIVATIVE_POLICY = {
    "max_research_depth": 2,
    "D0": "original parent specialist opportunity",
    "D1": "first causal retest/reclaim/turn/continuation transition",
    "D2": "second confirmation: stabilization/rebreak/reacceleration/persistence",
    "D3": "NO_CHAINING_AUTHORITY__RESET_AS_NEW_PARENT_EPISODE",
    "inherit": [
        "parent_specialist",
        "parent_episode_id",
        "parent_thesis",
        "side",
        "session_authority",
        "thesis_boundary",
    ],
    "executable_gate": {
        "standalone_lomo_survivability_min": 0.85,
        "portfolio_buffer_may_not_hide_bad_adds": True,
        "adequate_sample_required": True,
    },
    "ownership": {
        "max_D1_per_parent_episode": 1,
        "max_D2_per_parent_episode": 1,
        "D3_resets_episode": True,
    },
}

TESTED_D1 = [
    "E5D1_SVWAP_RECLAIM_RETEST",
    "E6D1_SESSION_VALUE_TURN",
    "E7D1_PREOPEN_SWEEP_RECLAIM",
    "E9D1_BREAK_ACCEPT_RETEST",
]

TESTED_D2 = [
    "E5D2_TREND_SVWAP_RETEST",
    "E6D2_SUSTAINED_EXTREME_REVERSAL",
    "E7D2_SWEEP_RECLAIM_STABILIZE",
    "E9D2_EXPANSION_BREAK_RETEST",
]

TESTED_D3 = [
    "E5D3_HANDOFF_VWAP_RECLAIM",
    "E7D3_HANDOFF_SWEEP_RECLAIM",
    "E9D3_HANDOFF_BREAK_ACCEPT_RETEST",
]

PRODUCTION_AUTHORITY = False
HOLD_EXIT_AUTHORITY = False
AUGUST = "SEALED"
ALPHA_GAMMA_DEPENDENCIES = []
