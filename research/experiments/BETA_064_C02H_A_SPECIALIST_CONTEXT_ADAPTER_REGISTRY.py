"""
BETA064 C02H-A specialist-specific context-adapter registry.

Research-only. No checkpoint mutation. No MQL5 authorization.
Adapters are evaluated only at the parent proposal timestamp from already-completed causal state.
They do not create standalone Entry clocks.
"""

SPECIALIST_CONTEXT_ADAPTERS = {
    "E5_VWAP_RECLAIM": {
        "status": "RESEARCH_POSITIVE",
        "role": "PARENT_ADMISSION_CONTEXT",
        "features": [
            "bollinger_keltner_squeeze_on",
            "bollinger_keltner_squeeze_ratio",
            "bars_since_squeeze_release",
            "adx14",
            "di_spread",
            "ema50_slope",
        ],
        "observed_auc_delta": 0.047727,
    },
    "E6_VALUE_REVERSION": {
        "status": "RESEARCH_POSITIVE_HIGH_PRIORITY",
        "role": "PARENT_ADMISSION_CONTEXT",
        "features": [
            "hurst_5m",
            "hurst_15m",
            "hurst_1h",
            "entropy_5m",
            "entropy_15m",
            "entropy_1h",
            "efficiency_5m",
            "efficiency_15m",
            "efficiency_1h",
            "variance_ratio_4_15m",
            "variance_ratio_12_15m",
            "autocorr1_15m",
        ],
        "observed_auc_delta": 0.064087,
        "boundary": "DO_NOT_USE_AS_STANDALONE_E6_CLOCK",
    },
    "E7_SWEEP_RECLAIM": {
        "status": "RESEARCH_POSITIVE",
        "role": "PARENT_ADMISSION_CONTEXT",
        "features": [
            "completed_m1_heikin_ashi_side",
            "completed_m1_heikin_ashi_body_fraction",
            "completed_m1_heikin_ashi_no_opposite_wick",
            "completed_m1_heikin_ashi_alignment_with_side",
        ],
        "observed_auc_delta": 0.028559,
        "execution_rule": "REAL_BID_ASK_ONLY",
    },
    "E9_LEVEL_BREAK": {
        "status": "RESEARCH_POSITIVE",
        "role": "PARENT_ADMISSION_CONTEXT",
        "features": [
            "completed_m1_heikin_ashi_state",
            "bollinger_keltner_squeeze_state",
        ],
        "observed_auc_delta_ha": 0.019748,
        "observed_auc_delta_squeeze": 0.015642,
        "execution_rule": "REAL_BID_ASK_ONLY",
    },
    "E10_COMPRESSION_RELEASE": {
        "status": "NEGATIVE_CONTROL_KEEP_EXISTING_MICRO",
        "role": "NO_NEW_ADAPTER",
        "rejected": [
            "bollinger_keltner_squeeze_state",
            "heikin_ashi_state",
            "fibonacci_location",
            "hurst_entropy_bundle",
        ],
        "reason": "New overlays reduced held-out discrimination.",
    },
    "E12_FAILED_EXPANSION": {
        "status": "RESEARCH_POSITIVE_HIGH_PRIORITY",
        "role": "PARENT_ADMISSION_CONTEXT",
        "features": [
            "bollinger_keltner_squeeze_on",
            "bollinger_keltner_squeeze_ratio",
            "bars_since_squeeze_release",
            "fibonacci_location_secondary",
        ],
        "observed_auc_delta_squeeze": 0.075596,
        "observed_auc_delta_fibonacci": 0.012900,
    },
}

REJECTED_STANDALONE_ENTRY_FAMILIES = [
    "E17_FIB_STRUCTURAL_PULLBACK",
    "E18_HEIKIN_ASHI_TREND_RESTART",
    "E19_KALMAN_PULLBACK_RECOVERY",
    "E20_DONCHIAN_ADX_BREAKOUT",
    "E21_ABCD_HARMONIC_REVERSAL",
    "E21_GARTLEY_HARMONIC_REVERSAL",
]

GLOBAL_RULES = [
    "Frozen Major Checkpoint 02 keeps first ownership.",
    "C02G session derivative authority matrix remains authoritative.",
    "Adapter state must be available at the parent proposal timestamp.",
    "No delayed post-signal confirmation.",
    "No synthetic Heikin-Ashi execution prices.",
    "New additions must independently satisfy held-out survivability and path-value requirements.",
    "August remains sealed.",
    "No Alpha/GAMMA dependency.",
]
