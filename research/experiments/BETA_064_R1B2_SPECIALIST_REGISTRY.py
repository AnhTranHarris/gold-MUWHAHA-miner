"""
BETA064-R1B2 multi-desk ENTRY->HOLD specialist registry.

Research only.
No MQL5 promotion.
August remains sealed.
"""

ENTRY_SURVIVALITY_GATE = 0.88
ENTRY_ECONOMIC_SCORE_GATE = 0.30
HOLD_TRAIN_SURVIVALITY_FLOOR = 0.80
HOLD_CONTINUATION_GATE = 0.6185642603486833

ENTRY_SPECIALISTS = {
    "E1_MACRO_TREND": {
        "role": "H4/H1/M15 structural trend and accepted displacement",
        "horizon_s": 900,
        "checkpoint_s": 60,
    },
    "E2_PULLBACK_REACCEL": {
        "role": "macro-trend pullback followed by M1/S15 reacceleration",
        "horizon_s": 300,
        "checkpoint_s": 30,
    },
    "E3_ORB": {
        "role": "London/NY opening-range break and acceptance",
        "horizon_s": 300,
        "checkpoint_s": 30,
    },
    "E4_VWAP_PULLBACK": {
        "role": "trend pullback toward quote-activity-weighted value followed by reacceleration",
        "horizon_s": 300,
        "checkpoint_s": 30,
    },
    "E5_VWAP_RECLAIM": {
        "role": "value break/reclaim transition",
        "horizon_s": 120,
        "checkpoint_s": 15,
    },
    "E6_VALUE_REVERSION": {
        "role": "statistical value reversion in rotational state",
        "horizon_s": 180,
        "checkpoint_s": 20,
    },
    "E7_SWEEP_RECLAIM": {
        "role": "liquidity sweep then reclaim/rejection",
        "horizon_s": 120,
        "checkpoint_s": 15,
    },
    "E8_LEVEL_BOUNCE": {
        "role": "higher-timeframe/key-level rejection",
        "horizon_s": 300,
        "checkpoint_s": 30,
    },
    "E9_LEVEL_BREAK": {
        "role": "accepted structural/key-level break",
        "horizon_s": 300,
        "checkpoint_s": 30,
    },
    "E10_COMPRESSION_RELEASE": {
        "role": "compression to directional expansion transition",
        "horizon_s": 120,
        "checkpoint_s": 15,
    },
    "E11_KINETIC_IGNITION": {
        "role": "tick/quote velocity, acceleration, efficiency and quote-pressure ignition",
        "horizon_s": 45,
        "checkpoint_s": 10,
    },
    "E12_FAILED_EXPANSION": {
        "role": "failed breakout/contradiction and recross",
        "horizon_s": 120,
        "checkpoint_s": 15,
    },
}

HOLD_SPECIALISTS = {
    "H1_IGNITION_CONFIRMATION": "Did the expected first impulse actually materialize after fill?",
    "H2_EXTENSION_RUNNER": "Is favorable displacement still extending with residual runway?",
    "H3_HEALTHY_PULLBACK": "Is adverse movement a normal pullback inside a valid thesis?",
    "H4_REACCELERATION": "Has directional drive resumed after pullback or stall?",
    "H5_TRANSIENT_SCALP": "Did the entry produce a transient favorable excursion without runner characteristics?",
    "H6_STALL_CHOP": "Has the trade entered high-turn, low-efficiency two-sided noise?",
    "H7_FAILED_ACCEPTANCE": "Has price invalidated the entry structure/value boundary?",
    "H8_EXHAUSTION_CLIMAX": "Has favorable extension become unstable with declining renewal and rising reversal hazard?",
}

ENTRY_MODEL_OUTPUTS = (
    "p_survive_to_specialist_checkpoint",
    "p_favorable_first_passage_before_adverse",
    "entry_score = p_survive * p_first_passage",
)

HOLD_MODEL_INPUTS = (
    "origin_entry_specialist",
    "entry_thesis",
    "MFE",
    "MAE",
    "current_excursion",
    "path_efficiency",
    "entry_recross_count",
    "new_extreme_renewal",
    "spread_evolution",
    "tick_intensity",
    "signed_quote_pressure",
    "hold_age",
)

STRICT_EXECUTION = {
    "buy_entry": "observed Ask",
    "sell_entry": "observed Bid",
    "buy_markout": "observed Bid",
    "sell_markout": "observed Ask",
    "fee_per_research_lifecycle": 0.02,
    "one_position_at_a_time": True,
    "same_source_chronology": True,
    "future_information_allowed_only_in_training_labels": True,
    "august": "SEALED",
}

RESEARCH_TARGET = {
    "entry_to_hold_survivability": 0.85,
    "safety_buffer_gate": ENTRY_SURVIVALITY_GATE,
    "do_not_game_by_zero_coverage": True,
}
