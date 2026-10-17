"""Funded pretrade budget; explicit research caps, never an approved investor policy."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ResearchBudget:
    max_loss_fraction: float
    max_margin_fraction: float
    max_daily_drawdown_fraction: float
    max_peak_drawdown_fraction: float

    def __post_init__(self):
        for val in (self.max_loss_fraction, self.max_margin_fraction,
                    self.max_daily_drawdown_fraction, self.max_peak_drawdown_fraction):
            if not isfinite(val) or not 0 < val <= 1:
                raise ValueError("research fractions must be in (0, 1]")

@dataclass(frozen=True)
class BudgetDecision:
    allowed: bool
    reason: str

class SurvivalBudget:
    """Per-funded-account UTC observation; exit orders are never gated here."""
    def __init__(self, settings: ResearchBudget):
        self.settings = settings
        self.day = None
        self.day_open_equity = 0.0
        self.peak_equity = 0.0
        self.total_latch = False
        self.daily_latch = False
        self.last_ms = None

    def review_entry(self, ms: int, equity: float, estimated_stop_loss: float,
                     required_margin: float) -> BudgetDecision:
        if self.last_ms is not None and ms < self.last_ms:
            raise ValueError("noncausal UTC event")
        if ms < 0 or not all(isfinite(x) for x in
                (equity, estimated_stop_loss, required_margin)):
            raise ValueError("nonfinite event or monetary budget")
        if estimated_stop_loss < 0 or required_margin < 0:
            raise ValueError("negative monetary requirement")
        self.last_ms = ms
        if equity <= 0:
            return BudgetDecision(False, "no_equity")
        date = ms // 86_400_000
        if date != self.day:
            self.day = date
            self.day_open_equity = equity
            self.daily_latch = False
        self.peak_equity = max(self.peak_equity, equity)
        cfg = self.settings
        if equity <= self.peak_equity * (1-cfg.max_peak_drawdown_fraction):
            self.total_latch = True
        if equity <= self.day_open_equity * (1-cfg.max_daily_drawdown_fraction):
            self.daily_latch = True
        if self.total_latch:
            return BudgetDecision(False, "peak_drawdown_latch")
        if self.daily_latch:
            return BudgetDecision(False, "daily_loss_pause")
        if estimated_stop_loss > equity*cfg.max_loss_fraction:
            return BudgetDecision(False, "minimum_lot_risk_exceeds_budget")
        if required_margin > equity*cfg.max_margin_fraction:
            return BudgetDecision(False, "margin_budget")
        return BudgetDecision(True, "entry_feasible")
