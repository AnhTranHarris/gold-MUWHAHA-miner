"""
BETA064 Checkpoint-02E session-aware derivative registry.
Research-only. No Alpha/GAMMA dependency.
Major Checkpoint 02 remains immutable.
"""

DERIVATIVE_CHILDREN = {
    "E6D2_UK_SUSTAINED_EXTREME_REVERSAL": {
        "parent": "E6_VALUE_REVERSION",
        "session": "UK",
        "status": "ACTIVE_RESEARCH_CHILD",
        "ownership": "IDLE_GAP_ONLY",
    },
    "E6D2_AUSTRALIA_SUSTAINED_EXTREME_REVERSAL": {
        "parent": "E6_VALUE_REVERSION",
        "session": "AUSTRALIA",
        "status": "ACTIVE_RESEARCH_CHILD",
        "ownership": "IDLE_GAP_ONLY",
    },
    "E6D2_ASIA_SUSTAINED_EXTREME_REVERSAL": {
        "parent": "E6_VALUE_REVERSION",
        "session": "ASIA",
        "status": "ACTIVE_RESEARCH_CHILD",
        "ownership": "IDLE_GAP_ONLY",
    },
    "E7D2_NY_SWEEP_RECLAIM_STABILIZE": {
        "parent": "E7_SWEEP_RECLAIM",
        "session": "NY",
        "status": "ACTIVE_RESEARCH_CHILD",
        "ownership": "IDLE_GAP_ONLY",
    },
}

SHADOW_ONLY = [
    "E6D2_NY",
    "E6D2_EUROPE",
    "E6D2_MIDEAST",
    "E5D2_TREND_SVWAP_RETEST",
    "E9D2_EXPANSION_BREAK_RETEST",
    "E5D3_HANDOFF_VWAP_RECLAIM",
    "E7D3_HANDOFF_SWEEP_RECLAIM",
    "E9D3_HANDOFF_BREAK_ACCEPT_RETEST",
]

COVERAGE_UTILITY = {
    "research_formula": "P_survive * (0.40 + 0.60 * P_first_passage) * deficit_weight * novelty_weight * execution_feasibility",
    "production_enabled": False,
    "rules": [
        "Parent checkpoint ownership always wins.",
        "Derivative child may act only in a chronological idle slot.",
        "Derivative child must remain distinguishable from its parent in the thesis packet.",
        "No Alpha/GAMMA dependencies.",
    ],
}
