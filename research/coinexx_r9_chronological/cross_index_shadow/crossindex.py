"""Research-only causal cross-index feature adapter for Gold MUWHAHAHA R9.

This does NOT synthesize an order book, infer filled trades, or fit a predictor.
External data must be merged in (available_ms, source_ordinal) order *before*
requesting the gold-tick feature snapshot. All timestamps are UTC milliseconds.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite, log
from typing import Literal

SYMBOLS = ('US100', 'US500', 'US30', 'JP225', 'EU50', 'DE40', 'FR40', 'UK100')
# Do not mistake three correlated U.S. equity indexes for three independent venues.
REGION = {**{k: 'US' for k in ('US100', 'US500', 'US30')},
          'JP225': 'JAPAN',
          **{k: 'EUROPE' for k in ('EU50', 'DE40', 'FR40', 'UK100')}}
HORIZONS_MS = (1000, 5000, 15000, 30000, 60000, 300000)


@dataclass(frozen=True)
class IndexObservation:
    symbol: str
    source_ms: int
    available_ms: int
    price: float
    kind: Literal['quote', 'bar']
    bar_end_ms: int | None = None
    duration_ms: int = 0
    # No claimed exchange order-book size or executed-volume imbalance.


class CausalCrossIndexPanel:
    """Causally joins independently timestamped index observations to R9 ticks.

    Strict contract: an index observation is not a feature until the next gold
    tick strictly *after* its availability time. No same-timestamp tie optimism.
    An unobserved index stays missing, not zero and not filled from the future.
    """

    def __init__(self, *, max_age_ms: int = 3000,
                 max_history_ms: int = 600000,
                 bar_release_delay_ms: int = 1000):
        if max_age_ms <= 0 or max_history_ms <= max(HORIZONS_MS):
            raise ValueError('invalid freshness/history contract')
        if bar_release_delay_ms < 0:
            raise ValueError('negative bar release delay')
        self.max_age_ms = max_age_ms
        self.max_history_ms = max_history_ms
        self.bar_release_delay_ms = bar_release_delay_ms
        self._history = {name: deque() for name in SYMBOLS}
        self._last_available_ms: int | None = None
        self._last_gold_ms: int | None = None

    def observe(self, obs: IndexObservation) -> None:
        if obs.symbol not in self._history:
            raise ValueError(f'unapproved symbol: {obs.symbol}')
        if obs.source_ms < 0 or obs.available_ms < obs.source_ms:
            raise ValueError('invalid source/publication time')
        if self._last_available_ms is not None and obs.available_ms < self._last_available_ms:
            raise ValueError('cross-feed updates must be source-ordinal stable and availability ordered')
        if self._last_gold_ms is not None and obs.available_ms < self._last_gold_ms:
            raise ValueError('late index data cannot be inserted into completed gold chronology')
        if not isfinite(obs.price) or obs.price <= 0:
            raise ValueError('invalid index price')
        if obs.kind == 'bar':
            if obs.bar_end_ms is None or obs.duration_ms <= 0:
                raise ValueError('bar needs explicit ending and resolution')
            if obs.source_ms + obs.duration_ms != obs.bar_end_ms:
                raise ValueError('bar start/end mismatch')
            if obs.available_ms < obs.bar_end_ms + self.bar_release_delay_ms:
                raise ValueError('unclosed or not-yet-published OHLC bar')
        elif obs.kind != 'quote' or obs.bar_end_ms is not None or obs.duration_ms != 0:
            raise ValueError('quote/bar schema mismatch')
        series = self._history[obs.symbol]
        if series and obs.available_ms < series[-1].available_ms:
            raise ValueError('per-symbol chronological inversion')
        series.append(obs)
        self._last_available_ms = obs.available_ms
        cutoff = obs.available_ms - self.max_history_ms
        while len(series) > 1 and series[1].available_ms < cutoff:
            series.popleft()

    def snapshot(self, gold_ms: int) -> dict[str, float | int | None]:
        if self._last_gold_ms is not None and gold_ms < self._last_gold_ms:
            raise ValueError('gold chronology inverted')
        if self._last_available_ms is not None and gold_ms <= self._last_available_ms:
            raise ValueError('index update at/future of gold tick: strict causality required')
        self._last_gold_ms = gold_ms
        out: dict[str, float | int | None] = {'gold_time_msc': gold_ms}
        for symbol, q in self._history.items():
            p = f'{symbol.lower()}_'
            latest = q[-1] if q else None
            age = gold_ms - latest.available_ms if latest else None
            valid = latest is not None and age is not None and age <= self.max_age_ms
            out[p+'available'] = int(valid)
            out[p+'age_ms'] = age if latest else None
            for horizon in HORIZONS_MS:
                k = p+f'logret_{horizon}ms'
                out[k] = None
                if not valid:
                    continue
                # A 1m bar cannot create a 1s/5s/15s/30s quote-level signal.
                if latest.kind == 'bar' and latest.duration_ms > horizon:
                    continue
                # Require a genuinely observed earlier endpoint with bounded
                # source age: do not interpolate a missing history interval.
                earlier = None
                target = latest.available_ms - horizon
                for row in reversed(q):
                    if row.available_ms <= target:
                        earlier = row
                        break
                if earlier is None:
                    continue
                if earlier.kind == 'bar' and earlier.duration_ms > horizon:
                    continue
                # Do not span stale observations / market closures.
                if latest.available_ms - earlier.available_ms > horizon + self.max_age_ms:
                    continue
                out[k] = log(latest.price / earlier.price)
        return out


def ex_ante_factor(snapshot: dict[str, float | int | None], *,
                    horizon_ms: int, train_vol: dict[str, float],
                    train_weights: dict[str, float]) -> dict[str, float | int | None]:
    """Vol-adjusted index composite with frozen TRAIN-ONLY weights and scales.

    It cannot infer whether index pressure is bullish or bearish for gold.
    That mapping must be estimated on past gold first-passage outcomes.
    """
    if horizon_ms not in HORIZONS_MS:
        raise ValueError('unsupported horizon')
    numerator = denominator = 0.0
    active = 0
    covered_regions: set[str] = set()
    for symbol in SYMBOLS:
        k = f'{symbol.lower()}_logret_{horizon_ms}ms'
        r = snapshot.get(k)
        vol = train_vol.get(symbol)
        weight = train_weights.get(symbol, 0.0)
        if r is None or vol is None or not isfinite(vol) or vol <= 0:
            continue
        if not isfinite(weight) or not isfinite(r):
            raise ValueError('invalid frozen factor parameters')
        numerator += weight * max(-6., min(6., r / vol))
        denominator += abs(weight)
        active += 1
        covered_regions.add(REGION[symbol])
    # Presence from two correlated U.S. symbols is NOT regional diversification.
    diversified = len(covered_regions) >= 2 and denominator > 0
    return {'factor': numerator / denominator if diversified else None,
            'observed_count': active, 'observed_regions': len(covered_regions),
            'has_diversified_factor': int(diversified)}
