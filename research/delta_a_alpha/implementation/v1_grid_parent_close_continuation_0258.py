"""GRID0258 quote-only original-parent-close MULTIGEOMETRY renewal permission.

Owner contract: R9 SYNTH=performance goals, R9 OVERFIT=retrospectively optimal
trades; months mostly unique; grid is high-volume, multi-geometry, multi-HTF,
multi-scalping and sniper. A G0 candidate cannot be confused with an order.

Frozen positive incremental source hypothesis:
  - an ALREADY SETTLED original GRID0257 H4/J179F/etc shadow parent close;
  - its ACTUAL signed source-quote net after modeled friction is >0;
  - the last FIVE genuinely COMPLETED consecutive M1 close movements in the
    original parent's trade direction total >=1.00 USD/oz;
  - admit once on the FIRST actual available quote 250-2000ms after parent
    close, if ask-bid<=0.65 USD/oz, 16-slot global capacity and one G0
    candidate per actual millisecond are respected;
  - research offline exit at first observed quote 600sec after accepted
    entry, ONE oz, 0.52 additional quote friction. NO PROTECTIVE STOP: hence
    CANNOT BE PROMOTED to funded live trading absent separate stop research.

No month identities, known future outcomes, OVERFIT scores, post-entry future
prices, fabricated fills or loss-multiplied size enter this permission.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SettledSourceParent:
    unique_parent_id: int
    closed_at_ms: int
    side: int
    settled_quote_pnl_raw: int
    last_5_completed_m1_displacement_aligned_raw: int
    last_5_m1_consecutive: bool
    quote_reconciled: bool

@dataclass(frozen=True)
class SourceOnlyRenewal:
    parent_id: int
    observed_at_ms: int
    side: int
    entry_bid_raw: int
    entry_ask_raw: int
    horizon_ms: int = 600_000
    fixed_research_qty_oz: int = 1
    source: str = 'GRID0258_CLOSED_PARENT_M1X5_EARNED_G0'

class EarnedMultigeometryRenewal0258:
    def __init__(self) -> None:
        self.parents: list[SettledSourceParent] = []
        self.seen_parent_ids: set[int] = set()
        self.used_quote_times: set[int] = set()
        self.last_quote_ms: Optional[int] = None
        self.last_parent_close_ms: Optional[int] = None
        self.accepted = 0
        self.denied = 0
        self.expired = 0

    def observe_parent_close(self, x: SettledSourceParent) -> None:
        if x.unique_parent_id in self.seen_parent_ids:
            raise ValueError('duplicate original paid-shadow source ticket')
        if (x.closed_at_ms < 0 or x.side not in (-1, 1)
                or not x.quote_reconciled):
            raise ValueError('only previously settled real source quotes count')
        if self.last_parent_close_ms is not None and x.closed_at_ms < self.last_parent_close_ms:
            raise ValueError('unordered observed parent closures')
        if self.last_quote_ms is not None and x.closed_at_ms < self.last_quote_ms:
            raise ValueError('cannot add known parent close retroactively')
        self.last_parent_close_ms = x.closed_at_ms
        self.seen_parent_ids.add(x.unique_parent_id)
        self.parents.append(x)

    def on_observed_quote(self, *, time_ms: int, bid_raw: int, ask_raw: int,
                          tradable: bool, global_active_positions: int,
                          source_h4_active: bool = True) -> tuple[SourceOnlyRenewal, ...]:
        if (time_ms < 0 or bid_raw <= 0 or ask_raw < bid_raw
                or global_active_positions < 0 or global_active_positions > 16):
            raise ValueError('invalid source quote/capacity')
        if self.last_quote_ms is not None and time_ms < self.last_quote_ms:
            raise ValueError('source quote time reversed')
        self.last_quote_ms = time_ms
        waiting: list[SettledSourceParent] = []
        emitted: list[SourceOnlyRenewal] = []
        for x in self.parents:
            age = time_ms - x.closed_at_ms
            if age < 250:
                waiting.append(x)
                continue
            if age > 2000:
                self.expired += 1
                continue
            # Never issue a live order; candidate only. One per UTC millisecond.
            valid = (x.settled_quote_pnl_raw > 0
                     and x.last_5_m1_consecutive
                     and x.last_5_completed_m1_displacement_aligned_raw >= 1000
                     and ask_raw - bid_raw <= 650
                     and global_active_positions < 16
                     and tradable and source_h4_active)
            if not valid:
                self.denied += 1
                # Already observed first eligible quote; never hunt a later quote.
                continue
            if time_ms in self.used_quote_times:
                self.denied += 1
                continue
            self.used_quote_times.add(time_ms)
            self.accepted += 1
            emitted.append(SourceOnlyRenewal(x.unique_parent_id, time_ms, x.side,
                                             bid_raw, ask_raw))
        self.parents = waiting
        return tuple(emitted)

    def stats(self) -> dict:
        return dict(stage='G0_SOURCE_RESEARCH_ONLY', accepted=self.accepted,
                    denied=self.denied, expired=self.expired,
                    trading_enabled=False, funded_broker_cash_verified=False)