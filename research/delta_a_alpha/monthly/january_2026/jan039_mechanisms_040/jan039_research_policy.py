"""JAN039 January-fitted *research policy* for future Delta-A-alpha V1 adapters.

This module does NOT originate events, decide market regimes, authorize live orders,
or implement L0-L7. It consumes original V1 permissions and *already funded* counts.
No month, weekday, year, price hindsight, or R9 outcomes are permitted as signals.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

# IDs belong to the frozen JAN037/038 source-proposal tape; future V1 router
# must explicitly map source identities. Never infer them from generic indicators.
PHASE_EXCLUSIONS: frozenset[tuple[int, int]] = frozenset({
    (25, 0), (25, 5), (26, 1), (26, 3), (26, 5), (27, 1),
    (21, 1), (21, 2), (21, 5), (3, 1), (3, 3), (3, 4),
    (3, 5), (4, 2), (4, 4), (5, 0), (5, 4), (6, 0),
    (6, 2), (4, 0),
})

@dataclass(frozen=True)
class Params:
    lot: float = 0.01
    spread_max_usd: float = 3.0
    max_open: int = 512
    per_tick_max: int = 1
    per_utc_second_max: int = 3
    watchdog_max: int = 8
    watchdog_per_cell_max: int = 4
    s26_max: int = 432
    s27_p0_max: int = 224
    s27_p5_max: int = 128
    wd_successful_child_unlock: int = 2
    wd_scout_budget_per_cell: int = 1
    # These are *historical high-account exposure settings*, NOT $100 deployable.
    research_balance_usd: float = 100_000.0
    research_margin_leverage: int = 500


@dataclass(frozen=True)
class CompletedBar:
    end_ms: int
    close: float
    high: float
    low: float


@dataclass(frozen=True)
class BootstrapContext:
    quote_ms: int
    first_valid_quote_ms: int
    quote_valid: bool
    broker_connected: bool
    complete_htf: Mapping[str, CompletedBar]
    session_known: bool
    grid_anchor_initialized: bool
    risk_broker_verified: bool


def bootstrap_status(state: BootstrapContext) -> tuple[bool, tuple[str, ...]]:
    """300 seconds measured from FIRST VALID tradable broker quote, not wall T0.

    Preexisting historical bars may be hydrated at once. Nothing forces waiting
    five minutes and nothing fabricates completed bars when market is closed.
    """
    failed = []
    if not state.quote_valid or state.quote_ms < state.first_valid_quote_ms:
        failed.append('valid_quote')
    if not state.broker_connected:
        failed.append('broker_connection')
    if not state.session_known:
        failed.append('session_dst')
    if not state.grid_anchor_initialized:
        failed.append('v1_grid_anchor')
    if not state.risk_broker_verified:
        failed.append('broker_margin_symbol_and_risk')
    for name in ('H4', 'H1', 'M15', 'M5'):
        bar = state.complete_htf.get(name)
        if bar is None or bar.end_ms > state.quote_ms or bar.high < bar.low:
            failed.append(f'completed_{name}')
    return not failed, tuple(failed)


def quote_start_deadline_exceeded(state: BootstrapContext) -> bool:
    return state.quote_valid and (state.quote_ms - state.first_valid_quote_ms > 300_000)


def phase_of_utc_hour(timestamp_ms: int) -> int:
    """Six 10-min UTC subphases. Session membership handled by upstream V1 DST adapter."""
    return (timestamp_ms // 600_000) % 6


@dataclass(frozen=True)
class AdmissionSnapshot:
    timestamp_ms: int
    source_id: int
    direction: int
    spread_usd: float
    # mid(t)-mid(t-20s) measured using historical last-at-or-before quote.
    signed_impulse_20s: float
    v1_completed_htf_permission: bool
    v1_session_and_geometry_permission: bool
    broker_can_accept_order: bool
    global_open: int
    direction_open: int
    per_tick_submitted: int
    per_second_submitted: int
    watchdog_open: int
    watchdog_same_cell_side_open: int
    s26_open: int
    s27_open_in_entry_phase: int


def admission(s: AdmissionSnapshot, p: Params = Params()) -> tuple[bool, str]:
    """Research admission checks; L7 real margin/stop-out remains external and mandatory.

    A denied Watchdog proposal must be propagated to the original parent genealogy
    engine. This method may NEVER credit outcomes of rejected candidate children.
    """
    if not s.v1_completed_htf_permission or not s.v1_session_and_geometry_permission:
        return False, 'V1_STRUCTURAL_PERMISSION'
    if not s.broker_can_accept_order:
        return False, 'BROKER_MARGIN_EXECUTION_GATE'
    if s.direction not in (-1, 1):
        return False, 'INVALID_SIDE'
    if (s.source_id, phase_of_utc_hour(s.timestamp_ms)) in PHASE_EXCLUSIONS:
        return False, 'JAN039_EXPERIMENTAL_PHASE_MASK'
    if s.source_id >= 17 and s.direction * s.signed_impulse_20s < 0.0:
        return False, 'HISTORICAL_20S_IMPULSE_PERMISSION'
    if s.spread_usd > p.spread_max_usd or s.spread_usd < 0:
        return False, 'SPREAD'
    if s.global_open >= p.max_open or s.direction_open >= p.max_open:
        return False, 'GLOBAL_OR_SIDE_CAP'
    if s.per_tick_submitted >= p.per_tick_max or s.per_second_submitted >= p.per_utc_second_max:
        return False, 'ORDER_RATE'
    if s.source_id == 0 and (s.watchdog_open >= p.watchdog_max or
                             s.watchdog_same_cell_side_open >= p.watchdog_per_cell_max):
        return False, 'WATCHDOG_CAP'
    if s.source_id == 26 and s.s26_open >= p.s26_max:
        return False, 'S26_CAP'
    phase = phase_of_utc_hour(s.timestamp_ms)
    if s.source_id == 27 and phase == 0 and s.s27_open_in_entry_phase >= p.s27_p0_max:
        return False, 'S27_PHASE_0_CAP'
    if s.source_id == 27 and phase == 5 and s.s27_open_in_entry_phase >= p.s27_p5_max:
        return False, 'S27_PHASE_5_CAP'
    return True, 'ADMISSIBLE_SUBJECT_TO_V1_PARENT_AND_L7_EXECUTION'


def first_executable_profit_take(source_id: int, utc_ms: int, original_is_short: bool) -> float | None:
    """USD cash threshold on the fixed 0.01 research lot; no new TP on other routes.

    In JAN039's frozen replay this refinement applied only to original S26/S27
    short candidates that survived the original proposal/spread/phase mask.
    """
    if not original_is_short:
        return None
    if source_id == 26:
        return 35.0
    if source_id != 27:
        return None
    return {0: 60.0, 2: 50.0, 3: 50.0, 4: 35.0}.get(phase_of_utc_hour(utc_ms))


@dataclass(frozen=True)
class ObservableMarketFingerprint:
    """Market-state features for later correlation, never a January calendar selector."""
    completed_m5_range_usd: float
    completed_m15_range_usd: float
    completed_h1_range_usd: float
    completed_h4_range_usd: float
    preceding_10m_tick_count: int
    preceding_10m_abs_mid_range_usd: float
    preceding_10m_spread_mean_usd: float
    current_spread_usd: float
    signed_mid_impulse_20s_usd: float
    current_session: str
    utc_phase_10m: int
    trend_phase: str
    funded_net_directional_exposure: int
    funded_floating_heat_usd: float


def january_like_adaptation_approved(*, correlation_calibrated: bool,
                                      prior_month_regression_passed: bool,
                                      forward_validation_passed: bool) -> bool:
    """Fail closed: January-fitted settings are not auto-enabled by calendar or hunch."""
    return correlation_calibrated and prior_month_regression_passed and forward_validation_passed