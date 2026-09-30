"""
BETA064 Checkpoint-02E derivative-child research registry.

Research only.
Major Checkpoint 02 remains immutable.
Derivative children inherit a parent thesis and MAY NOT originate trades alone.
Alpha/GAMMA are prohibited dependencies.
HOLD->EXIT remains deferred.
"""

DERIVATIVE_CHILD_POLICY = {
    "standalone_entry_authority": False,
    "requires_valid_parent_thesis": True,
    "requires_session_context": True,
    "causal_completed_state_only": True,
    "future_information": "labels_only",
    "coverage_utility_enabled": "RESEARCH_ONLY",
    "august": "SEALED",
}

DERIVATIVE_ORDERS = {
    "D1": "velocity / first difference",
    "D2": "acceleration / second difference",
    "D3": "jerk / third difference",
}

GLOBAL_EVIDENCE = {
    "mean_lomo_auc_base": 0.647149,
    "mean_lomo_auc_D1": 0.670813,
    "mean_lomo_auc_D2": 0.663357,
    "mean_lomo_auc_D3": 0.664049,
    "global_preference": "D1",
}

STABLE_SESSION_ADAPTERS = {
    "MIDEAST": {"preferred_order": "D2", "status": "PROMISING"},
    "NY": {"preferred_order": "D1", "status": "PROMISING"},
    "UK": {"preferred_order": "D3", "status": "PROMISING"},
    "AUSTRALIA": {"preferred_order": "D2", "status": "OBSERVATIONAL_NOT_FROZEN"},
    "ASIA": {"preferred_order": None, "status": "ORDER_SELECTION_UNSTABLE"},
    "EUROPE": {"preferred_order": None, "status": "ORDER_SELECTION_UNSTABLE"},
}

PARENT_DERIVATIVE_CHILDREN = {
    "E6_VALUE_REVERSION": {
        "primary": "D1",
        "session_overrides": {"MIDEAST": "D2", "UK": "D3", "NY": "D1"},
        "status": "PRIORITY_RESEARCH_CHILD",
    },
    "E9_LEVEL_BREAK": {
        "primary": "D1",
        "status": "PROMISING_RESEARCH_CHILD",
    },
    "E10_COMPRESSION_RELEASE": {
        "primary": "D3",
        "status": "PROMISING_RESEARCH_CHILD",
    },
    "E12_FAILED_EXPANSION": {
        "primary": "D3",
        "status": "PROMISING_RESEARCH_CHILD",
    },
    "E5_VWAP_RECLAIM": {
        "primary": None,
        "status": "DERIVATIVES_HURT__KEEP_PARENT",
    },
    "E7_SWEEP_RECLAIM": {
        "primary": None,
        "status": "DERIVATIVES_HURT__KEEP_PARENT",
    },
    "E11_KINETIC_IGNITION": {
        "primary": "D1",
        "status": "QUALITY_INFO_ONLY__DO_NOT_EXPAND_SATURATED_DESK",
    },
}

META_ADMISSION_EVIDENCE = {
    "parent": "BETA064_C02C",
    "before_trades": 5519,
    "before_weighted_survivability": 0.882044,
    "after_trades": 5094,
    "after_weighted_survivability": 0.892030,
    "retention": 0.9230,
    "rejected": 425,
    "february_after_survivability": 0.87143,
    "interpretation": "SURVIVABILITY_RESERVE_NOT_OPPORTUNITY_EXPANSION",
}

COVERAGE_UTILITY = {
    "formula": "p_survive * deficit_weight * novelty_weight * execution_feasibility",
    "production_authority": False,
    "rule": "Use derivative quality reserve only to admit independently validated under-covered opportunities; never globally loosen quality gates.",
}

PROHIBITED_DEPENDENCIES = ["alpha", "gamma"]
