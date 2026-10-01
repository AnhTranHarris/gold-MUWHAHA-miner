"""
BETA064 Major Checkpoint 03 router overlay.

Research specification only. No MQL5 implementation.
Parent: BETA_064_C02C_SESSION_E6_DEFICIT_ROUTER.py
Major Checkpoint 02 learned models and Hold model remain unchanged.

This file records the only active C02D/Checkpoint-03 routing change:
E7 and E9 child ps_b75 authority increases from 0.9145 to 0.915.
"""

BASE_PS = 0.88
BASE_ES = 0.30
PRE_PS = 0.89
PRE_ES = 0.08

DEFICIT_PS = {
    "E5_VWAP_RECLAIM": 0.9145,
    "E7_SWEEP_RECLAIM": 0.9150,
    "E9_LEVEL_BREAK": 0.9150,
    "E10_COMPRESSION_RELEASE": 0.9145,
    "E12_FAILED_EXPANSION": 0.9145,
}

FROZEN_SESSION_PS = {
    "AUSTRALIA": 0.920,
    "ASIA": 0.900,
    "MIDEAST": 0.915,
    "EUROPE": 0.910,
    "UK": 0.925,
    "NY": 0.925,
}

E6_NY = {
    "ps_b75_min": 0.920,
    "eff60_min": 0.30,
    "friction_max": 0.14,
    "session_value_z_min": -2.5,
}

E6_UK = {
    "ps_b75_min": 0.905,
    "eff60_min": 0.40,
    "eff300_max": 0.10,
    "session_value_z_min": -4.0,
}

ALLOWED_SESSION_CHILDREN = {
    "E5_VWAP_RECLAIM",
    "E6_VALUE_REVERSION",
    "E7_SWEEP_RECLAIM",
    "E9_LEVEL_BREAK",
    "E10_COMPRESSION_RELEASE",
    "E11_KINETIC_IGNITION",
    "E12_FAILED_EXPANSION",
}

SHADOW_ONLY = {
    "E13_OPENING_DRIVE_FIRST_PULLBACK",
    "E14_SWEEP_FVG_RETEST",
    "E15_REGIME_SHIFT_FIRST_PULLBACK",
    "E16_SECOND_ENTRY_TREND_PULLBACK",
}

def checkpoint03_overlay_from_c02c_selected(df):
    """Exact observed-panel reconstruction of Checkpoint 03 from C02C selection."""
    weak = (
        df.specialist.isin(["E7_SWEEP_RECLAIM", "E9_LEVEL_BREAK"])
        & (df.ps_b75 < 0.915)
    )
    return df.loc[~weak].copy()

EXPECTED = {
    "jan_jul_trades": 5469,
    "weighted_survival": 0.8838910221,
    "weighted_first_passage": 0.6081550558,
    "diagnostic_value": 5981.669,
    "lomo_months_passing_085": "7/7",
    "selected_csv_sha256": "2fe7b28280d670b915c0968e8daac5fbcf23193faf2c36b0b6f45c0e6d480cc5",
}

NON_AUTHORITY_RESEARCH = [
    "C02G derivative-state matrix",
    "C02H specialist-specific adapters",
    "E13-E16 shadow specialists",
]
