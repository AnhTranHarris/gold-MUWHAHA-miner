"""R03 six competing causally timed XAUUSD specialist signal sources.
NOT a profitable strategy claim; independently tested P&L belongs to the source-pinned
native-tick research archive. The production signal arbiter remains the sole place
where a broker/account margin, position and risk decision is made.

Sources: archived original R9 event model plus reconstructed community hypotheses.
Only completely closed bars are consumed. All rolling levels use prices that
precede the current completed S5 bar. QWAP is quote-event volume proxy, NOT VWAP.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import isfinite

from htf_ticklab.bars import Bar
from htf_ticklab.feeds import Quote
from htf_ticklab.signal_bus import AccountView, SignalIntent


@dataclass(frozen=True)
class SixExpertParameters:
    source_id: str = "r03_six_specialists"
    lots: float = 0.01
    min_m5_atr: float = 1.5
    max_spread: float = 0.65
    min_move: float = 0.20
    min_s5_efficiency: float = 0.45
    impulse_fraction_of_atr: float = 0.035
    qwap_cross_fraction_of_atr: float = 0.02
    min_stop: float = 0.65
    max_stop: float = 1.5
    atr_stop_fraction: float = 0.10
    reward_multiple: float = 1.3

    def __post_init__(self):
        if (not self.source_id or self.lots <= 0 or self.min_m5_atr < 0 or
            self.max_spread <= 0 or self.min_move <= 0 or
            not 0 < self.min_s5_efficiency <= 1 or self.min_stop <= 0 or
            self.max_stop < self.min_stop or self.atr_stop_fraction <= 0 or
            self.reward_multiple <= 0):
            raise ValueError("invalid six-expert research parameters")


class SixSpecialists:
    """One signal source, six independent hypothesis generators.

    The central SharedSignalArbiter determines *which* request wins. It is not
    permissible to add hypothetical six-source profits or bypass shared margin.
    This source does not manage live broker stops, scale-in, or timed exits.
    """
    def __init__(self, params: SixExpertParameters | None = None):
        self.p = params or SixExpertParameters()
        self.s5 = deque(maxlen=120)  # 10m 5-second history
        self.rsi = 50.0
        self._m1_last = None
        self._gain = 0.0
        self._loss = 0.0
        self._m1_count = 0
        self._atr = None
        self._m5_last = None
        self._m5_count = 0
        self._last_qwap = None
        self._h1_last = None
        self._h1_direction = 0
        self.feature_events = 0

    @staticmethod
    def _mid_close(b: Bar) -> float:
        return (b.bid_close + b.ask_close) * .5

    @staticmethod
    def _mid_hi(b: Bar) -> float:
        # Bid-only structure avoids combining highs from different quote events.
        return b.bid_high

    @staticmethod
    def _mid_lo(b: Bar) -> float:
        return b.bid_low

    def _update_regimes(self, bar: Bar) -> None:
        if bar.seconds == 60:
            v = self._mid_close(bar)
            if self._m1_last is not None:
                diff = v - self._m1_last
                alpha = 1. / 14.
                self._gain = (1 - alpha) * self._gain + alpha * max(0., diff)
                self._loss = (1 - alpha) * self._loss + alpha * max(0., -diff)
                self._m1_count += 1
                if self._m1_count >= 14 and self._gain + self._loss > 1e-12:
                    self.rsi = 100. * self._gain / (self._gain + self._loss)
            self._m1_last = v
        elif bar.seconds == 300:
            h, l = self._mid_hi(bar), self._mid_lo(bar)
            prev = self._m5_last
            true_range = max(h - l, abs(h - prev), abs(l - prev)) if prev is not None else h - l
            self._atr = true_range if self._atr is None else (13. * self._atr + true_range) / 14.
            self._m5_last = self._mid_close(bar)
            self._m5_count += 1
        elif bar.seconds == 3600:
            v = self._mid_close(bar)
            if self._h1_last is not None:
                self._h1_direction = 1 if v > self._h1_last else (-1 if v < self._h1_last else 0)
            self._h1_last = v

    def _intent(self, q: Quote, side: int, priority: int, reason: str) -> SignalIntent:
        assert self._atr is not None
        stop = min(self.p.max_stop, max(self.p.min_stop, self._atr * self.p.atr_stop_fraction))
        return SignalIntent(
            source_id=self.p.source_id, observed_ms=q.ms, side=side, lots=self.p.lots,
            stop_distance=stop, target_distance=stop * self.p.reward_multiple,
            priority=priority, reason=reason)

    def on_bar(self, bar: Bar, quote: Quote, account: AccountView):
        if bar.end_ms > quote.ms:
            raise ValueError("future or incomplete bar")
        if bar.seconds != 5:
            self._update_regimes(bar)
            return ()
        if quote.ms - bar.end_ms > 2500:
            # A 5s bar can become available only after a long gap. Never route
            # a stale microstructure event as a current execution signal.
            self.s5.clear()
            return ()
        if self.s5 and bar.start_ms - self.s5[-1][4] > 5500:
            self.s5.clear()
        # Levels obtained solely from previous COMPLETED 5-second bars.
        old = list(self.s5)
        current = self._mid_close(bar)
        high = self._mid_hi(bar)
        low = self._mid_lo(bar)
        weighted = sum(v[0] * v[3] for v in old[-60:])
        weight = sum(v[3] for v in old[-60:])
        qwap = weighted / weight if weight else None
        prior_qwap = self._last_qwap
        self._last_qwap = qwap
        self.s5.append((current, high, low, bar.ticks, bar.start_ms))
        if (self._atr is None or self._m5_count < 14 or self._m1_count < 14 or
            len(old) < 12 or account.position_side or account.pending_entry or
            quote.ask - quote.bid > self.p.max_spread or self._atr < self.p.min_m5_atr):
            return ()
        self.feature_events += 1
        p = self.p
        last = old[-1][0]
        three_ago = old[-3][0]
        momentum = current - three_ago
        high60 = max(x[1] for x in old[-12:])
        low60 = min(x[2] for x in old[-12:])
        span60 = high60 - low60
        spread = quote.ask - quote.bid
        if span60 <= 0 or spread > 0.13 * self._atr:
            return ()
        proximity = (current - low60) / span60
        direction = 1 if momentum > 0 else (-1 if momentum < 0 else 0)
        proposals = []
        def propose(side, priority, label):
            proposals.append(self._intent(quote, side, priority, label))

        # 1. Pulse continuation: movement, efficiency, magnitude vs M5 regime.
        five_move = (bar.bid_close + bar.ask_close - bar.bid_open - bar.ask_open) * .5
        if abs(five_move) > max(p.min_move, p.impulse_fraction_of_atr * self._atr):
            same_direction = (five_move * momentum > 0)
            bar_eff = abs(five_move) / max(.001, bar.bid_high - bar.bid_low)
            if same_direction and bar_eff >= p.min_s5_efficiency:
                propose(1 if five_move > 0 else -1, 20, "pulse_continuation")

        # 2. Stop-pool sweep AND fast reclaim using *previous* minute geometry.
        if low < low60 and current > low60 + p.min_move and self.rsi < 55:
            propose(1, 30, "sweep_reclaim_low")
        if high > high60 and current < high60 - p.min_move and self.rsi > 45:
            propose(-1, 30, "sweep_reclaim_high")

        # 3. Fibonacci structural retracement — older 5-minute high/low, no pivot future confirmation.
        if len(old) >= 60:
            struct_hi = max(v[1] for v in old[-60:])
            struct_lo = min(v[2] for v in old[-60:])
            sz = struct_hi - struct_lo
            if sz > p.min_move:
                level382 = struct_lo + .382 * sz
                level618 = struct_lo + .618 * sz
                band = max(p.min_move, .025 * self._atr)
                if abs(current - level382) <= band and momentum > p.min_move and self.rsi > 48:
                    propose(1, 15, "fib_382_reclaim")
                if abs(current - level618) <= band and momentum < -p.min_move and self.rsi < 52:
                    propose(-1, 15, "fib_618_reject")

        # 4. Anchored QWAP acceptance: prior quote-count weighted anchor cross, not traded-volume VWAP.
        if qwap is not None and prior_qwap is not None:
            band = p.qwap_cross_fraction_of_atr * self._atr
            if last < prior_qwap - band and current > qwap + band:
                propose(1, 23, "qwap_accept_above")
            if last > prior_qwap + band and current < qwap - band:
                propose(-1, 23, "qwap_accept_below")

        # 5. RSI exhaustion/kinetic reversal: no global trend veto.
        if self.rsi < 33 and direction > 0 and proximity < .25:
            propose(1, 18, "rsi_reclaim_exhaustion")
        if self.rsi > 67 and direction < 0 and proximity > .75:
            propose(-1, 18, "rsi_reject_exhaustion")

        # 6. ATR-volatility release from a prior ten-S5-bar compression zone.
        if len(old) >= 12:
            narrow = max(v[1] for v in old[-10:]) - min(v[2] for v in old[-10:])
            release = max(p.min_move, .06 * self._atr)
            if narrow < .12 * self._atr and abs(five_move) > release:
                propose(1 if five_move > 0 else -1, 25, "atr_compression_release")

        # H1 agreement adjusts priority rather than vetoing either direction.
        if self._h1_direction:
            proposals = [SignalIntent(
                source_id=z.source_id, observed_ms=z.observed_ms, side=z.side,
                lots=z.lots, stop_distance=z.stop_distance,
                target_distance=z.target_distance,
                priority=z.priority + (2 if z.side == self._h1_direction else -1),
                kind=z.kind, reason=z.reason) for z in proposals]
        return tuple(proposals)

    def on_tick(self, quote: Quote, account: AccountView):
        # Execution is managed by the shared arbiter and existing Replay.
        return ()