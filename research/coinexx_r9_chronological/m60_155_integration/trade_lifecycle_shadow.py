"""Position-scoped R9 v1.94 lifecycle score monitor — explicitly SHADOW ONLY.

Attach the archived original-entry 155-feature LightGBM P5 to the ORIGINAL
R9 trade and carry that immutable entry score forward through its lifecycle.
Use only currently received executable Bid/Ask quotes for observable PnL.
No model-score interpolation at non-original R9 entry moments, no volume
assumptions, no executed order-flow data, no alternative exit orders.

This is a self-contained monitor: callers may integrate it with the EXISTING
chronological R9 replay engine and its trade ledger. It is NOT a replacement
for the exact tick engine and does not alter entries, stops, holds, or rearms.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass
class R9LifecycleShadow:
    entry_ordinal: int
    entry_time_msc: int
    side: int
    entry_price_cents: int
    cash_per_xau_quote_dollar: float
    extra_roundtrip_cash: float
    frozen_entry_p5: float | None = None
    calibrated_original_exit_cash_win_probability: float | None = None

    def __post_init__(self):
        if self.entry_ordinal < 1 or self.entry_time_msc < 0:
            raise ValueError("Original immutable source entry ordinal/time required")
        if self.side not in (-1, 1) or self.entry_price_cents <= 0:
            raise ValueError("Original signed executable entry quote required")
        if not (isfinite(self.cash_per_xau_quote_dollar) and
                self.cash_per_xau_quote_dollar > 0 and
                isfinite(self.extra_roundtrip_cash) and
                self.extra_roundtrip_cash >= 0):
            raise ValueError("Positive cash conversion and nonnegative extra cost required")
        for p in (self.frozen_entry_p5,
                  self.calibrated_original_exit_cash_win_probability):
            if p is not None and (not isfinite(p) or not 0 <= p <= 1):
                raise ValueError("No future-filled or invalid model probability")
        self.last_ordinal = self.entry_ordinal
        self.last_time_msc = self.entry_time_msc
        self.max_favorable_cash = float("-inf")
        self.max_adverse_cash = float("inf")
        self.latest_liquidation_cash = None
        self.closing_cash = None
        self.close_ordinal = None
        self.close_time_msc = None
        self.quote_count = 0
        self.active = True

    def quote_cash(self, bid_cents: int, ask_cents: int) -> float:
        if bid_cents <= 0 or ask_cents < bid_cents:
            raise ValueError("Bad executable Coinexx quote")
        liquidation = bid_cents if self.side == 1 else ask_cents
        signed_cents = self.side * (liquidation - self.entry_price_cents)
        return (signed_cents / 100.0 * self.cash_per_xau_quote_dollar
                - self.extra_roundtrip_cash)

    def observe(self, ordinal: int, time_msc: int, bid_cents: int,
                ask_cents: int) -> float:
        if not self.active:
            raise ValueError("Cannot inspect position after original exit")
        if ordinal < self.last_ordinal or time_msc < self.last_time_msc:
            raise ValueError("Source ordinals and times must remain causal")
        cash = self.quote_cash(bid_cents, ask_cents)
        self.last_ordinal = ordinal
        self.last_time_msc = time_msc
        self.latest_liquidation_cash = cash
        self.max_favorable_cash = max(self.max_favorable_cash, cash)
        self.max_adverse_cash = min(self.max_adverse_cash, cash)
        self.quote_count += 1
        return cash

    def close(self, ordinal: int, time_msc: int, exit_price_cents: int) -> dict:
        """Record only externally observed ORIGINAL R9 exit, NEVER request one."""
        if not self.active:
            raise ValueError("Duplicate close")
        if ordinal < self.last_ordinal or time_msc < self.last_time_msc:
            raise ValueError("Original R9 exit cannot precede observed quote")
        if exit_price_cents <= 0:
            raise ValueError("No fabricated exit fill")
        self.closing_cash = (
            self.side * (exit_price_cents - self.entry_price_cents) / 100.0
            * self.cash_per_xau_quote_dollar - self.extra_roundtrip_cash)
        self.active = False
        self.close_ordinal = ordinal
        self.close_time_msc = time_msc
        return {
            "entry_ordinal": self.entry_ordinal,
            "entry_time_msc": self.entry_time_msc,
            "exit_ordinal": ordinal,
            "exit_time_msc": time_msc,
            "original_r9_hold_ms": time_msc - self.entry_time_msc,
            "frozen_original_entry_p5": self.frozen_entry_p5,
            "shadow_cash_win_probability_for_original_exit": (
                self.calibrated_original_exit_cash_win_probability),
            "observed_quote_count": self.quote_count,
            "max_favorable_marked_cash": (
                self.max_favorable_cash if self.quote_count else None),
            "max_adverse_marked_cash": (
                self.max_adverse_cash if self.quote_count else None),
            "original_exit_cash_assumed": self.closing_cash,
            "original_exit_net_positive": self.closing_cash > 0,
            "classification": "RESEARCH_ONLY_ORIGINAL_R9_QUOTE_SIDE_NO_BROKER_FILLS",
        }
