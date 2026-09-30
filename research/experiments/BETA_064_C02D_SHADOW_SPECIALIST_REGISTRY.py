"""
BETA064 Checkpoint-02D shadow specialist registry.
Research-only. Major Checkpoint 02 is immutable.
Alpha/GAMMA are explicitly prohibited dependencies.
"""

SHADOW_SPECIALISTS = {
    "E13_ABSORPTION_DIVERGENCE_REVERSAL": {
        "status": "PROBATIONARY_SHADOW_GAPFILL_ONLY",
        "mechanism": "extreme + activity + quote-pressure divergence + low-friction reversal",
        "research_gate": {
            "friction_max": 0.09,
            "tick_z_min": 1.00,
            "eff60_min": 0.50,
            "r900_side_vs_atr300_min": -0.50,
        },
        "horizon_seconds": 120,
        "hold_checkpoint_seconds": 15,
        "may_own_position": False,
        "notes": "Observed idle-gap tail promising; not LOMO-certified, so no production admission."
    },
    "E14_SESSION_SWEEP_MSS": {
        "status": "SHADOW_ONLY",
        "mechanism": "confirmed extreme sweep/reclaim followed by causal micro structure shift",
        "horizon_seconds": 180,
        "hold_checkpoint_seconds": 20,
        "may_own_position": False,
    },
    "E15_COMPRESSION_SWEEP_RECLAIM": {
        "status": "SHADOW_ONLY",
        "mechanism": "compressed range then failed boundary sweep and reclaim",
        "horizon_seconds": 120,
        "hold_checkpoint_seconds": 15,
        "may_own_position": False,
    },
    "E16_SPREAD_CONTRACTION_IGNITION": {
        "status": "SHADOW_ONLY",
        "mechanism": "spread contraction plus activity/volatility expansion and directional efficiency",
        "horizon_seconds": 120,
        "hold_checkpoint_seconds": 15,
        "may_own_position": False,
    },
}

OPPORTUNITY_ROUTER_RESEARCH = {
    "formula": "survivability * deficit_weight * novelty_weight * execution_feasibility",
    "production_enabled": False,
    "purpose": "prioritize safe opportunities in under-covered state cells without expanding saturated E11-like capacity",
}

PROHIBITED_DEPENDENCIES = ["alpha", "gamma"]
