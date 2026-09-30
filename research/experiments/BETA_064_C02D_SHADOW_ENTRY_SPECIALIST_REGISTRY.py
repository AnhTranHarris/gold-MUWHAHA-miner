"""
BETA064 Checkpoint-02D shadow Entry specialist registry.
Research-only. These specialists have NO position ownership authority.

Alpha/GAMMA are prohibited sources for this registry.
"""

SHADOW_ENTRY_SPECIALISTS = {
    "E13_OPENING_DRIVE_FIRST_PULLBACK": {
        "status": "SHADOW_ONLY",
        "mechanism": "session opening drive -> first constructive pullback -> reacceleration",
        "horizon_s": 300,
        "hold_checkpoint_s": 30,
    },
    "E14_SWEEP_FVG_RETEST": {
        "status": "SHADOW_ONLY",
        "mechanism": "confirmed sweep/reclaim -> post-sweep FVG -> first retrace confirmation",
        "horizon_s": 180,
        "hold_checkpoint_s": 20,
    },
    "E15_REGIME_SHIFT_FIRST_PULLBACK": {
        "status": "HIGH_PRIORITY_SHADOW",
        "mechanism": "causal regime/volatility break -> pullback -> retained impulse -> renewed extreme",
        "horizon_s": 300,
        "hold_checkpoint_s": 30,
    },
    "E16_SECOND_ENTRY_TREND_PULLBACK": {
        "status": "HIGH_PRIORITY_SHADOW",
        "mechanism": "trend -> pullback #1 -> attempt #1 -> pullback #2 -> renewed continuation",
        "horizon_s": 300,
        "hold_checkpoint_s": 30,
    },
}

ACTIVE_ROUTING_AUTHORITY = False
MAY_OWN_POSITION = False
MAY_CHANGE_MAJOR_CHECKPOINT_02 = False

C02D_ACTIVE_REFINEMENT = {
    "E9_LEVEL_BREAK_MIN_PS_B75": 0.915,
    "E7_SWEEP_RECLAIM_MIN_PS_B75": 0.915,
    "all_other_C02C_rules": "UNCHANGED",
}
