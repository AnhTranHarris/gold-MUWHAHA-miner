"""Research-only R9 15-second basket and causal 15/30-second midquote breakouts.

Preserves unmodified source-exact R9 position/SL/trade/ATR/S1 control engine.
Only basket reset, short-horizon breakout trigger and basket-local rearms change.
No L2, real volume, look-ahead, new tick library or claimed 155-model scores.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from on_policy_cash_replay import ManagedR9, ResearchCash, QuoteRegime


@dataclass(frozen=True)
class BasketSpec:
    basket_seconds: int = 15
    breakout_seconds: int = 15
    minimum_mid_displacement_cents: int = 10
    breakout_extra_cents: int = 1
    minimum_completed_seconds: int = 4
    max_completed_second_age: int = 2

    def __post_init__(self):
        if self.basket_seconds != 15:
            raise ValueError('Research basket must be 15 seconds')
        if self.breakout_seconds not in (15, 30):
            raise ValueError('Only predeclared 15s/30s breakouts')
        if self.minimum_mid_displacement_cents <= 0 or self.breakout_extra_cents < 0:
            raise ValueError('Midquote distances must be finite nonnegative integer cents')
        if self.minimum_completed_seconds < 4 or self.max_completed_second_age > 2 or self.max_completed_second_age < 0:
            raise ValueError('Invalid completed-bar observation requirements')


class QuarterBasketMixin:
    """Use exact R9 market context; only entry/basket-specific methods differ.

    R9 baseline ``cycle_minute`` retains the NATIVE 60s value for inherited
    reconcile mechanics; ``basket_start`` tracks the independent 15s state.
    No score from the old candidate universe is imputed for new basket entries.
    """
    def __init__(self, *args, basket_spec: BasketSpec, **kwargs):
        super().__init__(*args, **kwargs)
        self.basket_spec = basket_spec
        self.basket_start: Optional[int] = None
        self.anchor_mid2 = 0
        self._last_entry_basket = None
        self._last_close_basket = None
        self._closed_entry_basket = None
        self._cached_second = None
        self._cached_breakout = None
        self._basket_entry_counts = {}

    def _start_minute_cycle(self, t: Tick):
        self.cycle_minute = t.time_s - t.time_s % 60
        basket = t.time_s - t.time_s % self.basket_spec.basket_seconds
        if basket == self.basket_start:
            return
        self.basket_start = basket
        self.anchor_mid2 = t.bid_u + t.ask_u
        self.rearms = 0
        self.pending_mode = 2
        self.cycle_buy_u = 0  # Not used; midpoint thresholds are dynamic.
        self.cycle_sell_u = 0
        self._cached_second = None
        self._cached_breakout = None
        self.stats['15sec_basket_starts'] += 1

    def _breakout_levels(self, t: Tick):
        """Completed Bid/Ask second CLOSE midpoints (not future/current bar)."""
        if self._cached_second == t.time_s:
            return self._cached_breakout
        self._cached_second = t.time_s
        now = t.time_s
        h = self.basket_spec.breakout_seconds
        # second_builder from ORIGINAL R9; no parallel resampling.
        points = [b for b in self.micro if 0 < now - b.second <= h]
        if (len(points) < self.basket_spec.minimum_completed_seconds or
            not points or now - points[-1].second > self.basket_spec.max_completed_second_age):
            self._cached_breakout = None
            return None
        # Sum two simultaneously-observed CLOSE quotes; never add unrelated
        # intrasecond ASK high to BID high to fabricate a midpoint extreme.
        high2 = max(b.bid_close_u + b.ask_close_u for b in points)
        low2 = min(b.bid_close_u + b.ask_close_u for b in points)
        self._cached_breakout = (high2, low2)
        return self._cached_breakout

    def _process_entries(self, t: Tick):
        if self.pending_mode == 0:
            return
        if getattr(self, 'account', None) is not None:
            if self.cash.governor and (self.account.day_lock or self.account.permanent_lock):
                self.reasons['governor_blocks_entry'] += 1
                return
        if not self._gate(t):
            return
        levels = self._breakout_levels(t)
        if levels is None:
            self.stats['missing_completed_breakout_window'] += 1
            return
        high2, low2 = levels
        mid2 = t.bid_u + t.ask_u
        delta2 = 2 * self.basket_spec.minimum_mid_displacement_cents
        buffer2 = 2 * self.basket_spec.breakout_extra_cents
        up = mid2 >= self.anchor_mid2 + delta2 and mid2 >= high2 + buffer2
        down = mid2 <= self.anchor_mid2 - delta2 and mid2 <= low2 - buffer2
        side = 0
        if self.pending_mode in (2, 1) and up:
            side = 1
        elif self.pending_mode in (2, -1) and down:
            side = -1
        if side == 0:
            self.stats['no_mid_breakout'] += 1
            return
        if not self._quality(side):
            self.stats['gate_s1'] += 1
            return
        self._open_trade(t, side)

    def _open_trade(self, t: Tick, side: int):
        before = self.position
        super()._open_trade(t, side)
        if self.position is not None and self.position is not before:
            self._last_entry_basket = self.basket_start
            self.entries[-1]['basket_start_second'] = self.basket_start
            self.entries[-1]['breakout_seconds'] = self.basket_spec.breakout_seconds
            self.stats['15sec_basket_entries'] += 1
            self._basket_entry_counts[self.basket_start] = self._basket_entry_counts.get(self.basket_start,0)+1

    def _record_close(self, t: Tick, reason: str, exit_u: int):
        if self.position is not None:
            self._closed_entry_basket = self._last_entry_basket
            self._last_close_basket = t.time_s - t.time_s % 15
        super()._record_close(t, reason, exit_u)

    def _arm_opposite_after_exit(self):
        # Do not accidentally override the newly reset basket with a stale
        # opposite rearm from a position entered in a previous 15s basket.
        if (self._closed_entry_basket == self.basket_start ==
            self._last_close_basket):
            super()._arm_opposite_after_exit()
            self.stats['15sec_opposite_rearms'] += 1
        else:
            self.stats['15sec_cross_basket_exit_no_rearm'] += 1
            # Keep the newest basket's fresh both-side pending state.
            if self.pending_mode == 0:
                self.pending_mode = 2


class QuarterBasketBaseline(QuarterBasketMixin, R9HybridGateBaseline):
    def __init__(self, cfg: R9Config, basket_spec: BasketSpec):
        super().__init__(cfg, basket_spec=basket_spec)


class QuarterBasketCash(QuarterBasketMixin, ManagedR9):
    def __init__(self, cfg: R9Config, cash: ResearchCash, mode: str,
                 basket_spec: BasketSpec, regime: QuoteRegime | None = None,
                 original_score_map: dict | None = None):
        super().__init__(cfg, cash, mode, regime, original_score_map,
                         basket_spec=basket_spec)