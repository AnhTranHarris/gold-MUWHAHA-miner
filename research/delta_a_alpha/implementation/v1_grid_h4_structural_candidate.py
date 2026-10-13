"""GRID0252 completed-H4 structural grid *source*, before Vertical Grid.

R9 SYNTH is performance goal. R9 OVERFIT shows retrospective optimal trades,
not causal trade signals. Each month's market conditions are mostly unique;
this source recognizes only actually observed completed-bar state, never
calendar month labels.

Recovered from historical P5 H4 structural source specifications and audited
separately in GRID0252, January-July original Dukascopy quotes. Research-only
candidate emitter, NEVER places orders or certifies broker fills/profit.
It emits an accepted crossing at a COMPLETED minute: earliest executable
availability is on a LATER observed quote. Its ATR and frozen H4 extremes must
be provided by a causal completed-bar upstream builder, NOT current H4.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

H4_MS = 4 * 60 * 60 * 1000

@dataclass(frozen=True)
class CompletedH4StructuralSource:
    """As-of reference from the prior six fully completed H4 bars."""
    reference_asof_ms: int
    rolling_six_high_raw: int
    rolling_six_low_raw: int
    completed_atr14_raw: int
    completed_tr_to_atr: float

@dataclass(frozen=True)
class GridH4Candidate:
    signal_known_at_ms: int
    side: int
    source: str
    boundary_raw: int
    completed_h4_owner: int
    risk_atr_raw: int
    horizon_ms: int = 24*60*60*1000

class CompletedH4GridSource:
    """One first observed completed-minute breakthrough per H4 owner.

    Never calls a broker or hides future labels in its result. Later broker
    execution must compute stop=max(1.50 USD,1.5*ATR,3*observed entry spread)
    and trailing room=max(1.00 USD,ATR) from ACTUAL acknowledged fills.
    These distances are research configurations, not source admission P&L.
    """
    def __init__(self, *, atr_expansion_ceiling: float = 2.0):
        if atr_expansion_ceiling <= 0:
            raise ValueError("positive expansion ceiling required")
        self.ceiling = float(atr_expansion_ceiling)
        self.last_completed_m1_ms: Optional[int] = None
        self.last_source_owner: Optional[int] = None
        self.signals = 0
    def on_completed_m1(
        self, *,
        completed_m1_end_ms: int,
        prior_m1_close_raw: int,
        latest_m1_close_raw: int,
        h4: CompletedH4StructuralSource,
    ) -> Optional[GridH4Candidate]:
        if (self.last_completed_m1_ms is not None
                and completed_m1_end_ms <= self.last_completed_m1_ms):
            raise ValueError("completed M1 source must advance, never rewind")
        self.last_completed_m1_ms = completed_m1_end_ms
        owner = (completed_m1_end_ms - 1)//H4_MS
        if h4.reference_asof_ms > owner*H4_MS:
            raise ValueError("unfinished or future H4 reference")
        if (h4.rolling_six_low_raw <= 0
                or h4.rolling_six_high_raw <= h4.rolling_six_low_raw
                or h4.completed_atr14_raw <= 0
                or prior_m1_close_raw <= 0 or latest_m1_close_raw <= 0):
            return None
        if not (0 <= h4.completed_tr_to_atr <= self.ceiling):
            return None
        # The completed M1 ended precisely at the next tradable bar boundary,
        # hence (end-1) determines the H4 group it belonged to.
        if owner == self.last_source_owner:
            return None
        up = (prior_m1_close_raw <= h4.rolling_six_high_raw
              and latest_m1_close_raw > h4.rolling_six_high_raw
              and latest_m1_close_raw > prior_m1_close_raw)
        down = (prior_m1_close_raw >= h4.rolling_six_low_raw
                and latest_m1_close_raw < h4.rolling_six_low_raw
                and latest_m1_close_raw < prior_m1_close_raw)
        if not (up or down):
            return None
        self.last_source_owner = owner
        self.signals += 1
        return GridH4Candidate(
            signal_known_at_ms=completed_m1_end_ms,
            side=1 if up else -1,
            source="GRID0252_CAUSAL_COMPLETED_H4_DONCHIAN6",
            boundary_raw=(h4.rolling_six_high_raw if up
                          else h4.rolling_six_low_raw),
            completed_h4_owner=owner,
            risk_atr_raw=h4.completed_atr14_raw,
        )
