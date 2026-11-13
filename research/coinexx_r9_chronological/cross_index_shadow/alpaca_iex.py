"""Causal Alpaca IEX ETF quote-to-gold adapter (research only).

US-listed ETFs are *proxy instruments*, NOT native equity indices or a gold
order book. The quote timestamp is exchange/source time, not observed terminal
arrival time. A pre-registered, positive availability delay is therefore
required. Invalid quotes reset the local return segment: they do not permit
forward-filling a prior clean quote through an unreliable price interval.

A caller must feed all ETF symbols in nondecreasing (available_ms, ordinal)
order and invoke snapshot for XAUUSD at strict later gold timestamps.
"""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log

ETF_TO_INDEX = {
    'QQQ': 'US100', 'SPY': 'US500', 'DIA': 'US30',
    'EWJ': 'JAPAN_EQUITY_ETF', 'FEZ': 'EURO_STOXX_50', 'VGK': 'EUROPE_EQUITY_ETF',
}
ETF_REGION = {k: ('US' if k in ('QQQ', 'SPY', 'DIA') else ('JAPAN' if k == 'EWJ' else 'EUROPE'))
              for k in ETF_TO_INDEX}
HORIZONS_MS = (1000, 3000, 5000, 10000)


def parse_utc_milliseconds(stamp: str) -> int:
    """Parse RFC3339 UTC, preserving source order externally for same-ms rows."""
    if not stamp.endswith('Z') or 'T' not in stamp:
        raise ValueError('quotes require explicit UTC Z timestamp')
    dt = datetime.fromisoformat(stamp[:-1] + '+00:00')
    if dt.tzinfo is None:
        raise ValueError('missing time zone')
    return int(dt.timestamp() * 1000)


@dataclass(frozen=True)
class ETFQuote:
    symbol: str
    time_msc: int
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    source_ordinal: int


class CausalAlpacaIEXPanel:
    def __init__(self, *, assumed_feed_latency_ms=500,
                 max_age_ms=2000, max_spread_bps=25.0, max_window_ms=10000):
        if assumed_feed_latency_ms <= 0:
            raise ValueError('latency must be strictly positive')
        if max_age_ms <= 0 or max_window_ms < max(HORIZONS_MS):
            raise ValueError('invalid freshness/history')
        if max_spread_bps <= 0:
            raise ValueError('invalid spread gate')
        self.latency_ms = assumed_feed_latency_ms
        self.max_age_ms = max_age_ms
        self.max_spread_bps = max_spread_bps
        self.max_window_ms = max_window_ms
        self.history = {name: deque() for name in ETF_TO_INDEX}
        self.last_good = dict.fromkeys(ETF_TO_INDEX)
        self.last_bad = dict.fromkeys(ETF_TO_INDEX)
        self.stats = defaultdict(int)
        self._last_available: int | None = None
        self._last_ordinal: int | None = None
        self._last_gold: int | None = None

    def observe(self, quote: ETFQuote) -> None:
        if quote.symbol not in ETF_TO_INDEX:
            raise ValueError('not a vetted ETF proxy')
        if quote.time_msc < 0 or quote.source_ordinal < 0:
            raise ValueError('invalid source event')
        av = quote.time_msc + self.latency_ms
        if (self._last_available is not None and
            (av, quote.source_ordinal) < (self._last_available, self._last_ordinal)):
            raise ValueError('cross-feed event order inverted')
        if self._last_gold is not None and av <= self._last_gold:
            raise ValueError('late-arriving historical event cannot be inserted behind gold time')
        self._last_available, self._last_ordinal = av, quote.source_ordinal
        self.stats['received'] += 1
        ok = all(isfinite(v) and v > 0 for v in (quote.bid, quote.ask, quote.bid_size, quote.ask_size))
        ok = ok and quote.ask >= quote.bid
        spread = (10000*(quote.ask-quote.bid)/((quote.ask+quote.bid)/2)) if ok else float('inf')
        ok = ok and spread <= self.max_spread_bps
        if not ok:
            self.stats['rejected'] += 1
            self.stats['rejected_'+quote.symbol] += 1
            self.history[quote.symbol].clear()
            self.last_good[quote.symbol] = None
            self.last_bad[quote.symbol] = av
            return
        self.stats['accepted'] += 1
        mid = (quote.ask + quote.bid) / 2
        imb = (quote.bid_size - quote.ask_size) / (quote.bid_size + quote.ask_size)
        q = self.history[quote.symbol]
        q.append((av, mid, imb, spread))
        self.last_good[quote.symbol] = av
        cutoff = av-self.max_window_ms-self.max_age_ms
        while len(q)>1 and q[1][0]<cutoff:
            q.popleft()

    def snapshot(self, gold_time_msc: int) -> dict[str, float | int | None]:
        if self._last_gold is not None and gold_time_msc < self._last_gold:
            raise ValueError('gold tick order inverted')
        if self._last_available is not None and gold_time_msc <= self._last_available:
            raise ValueError('source data cannot be same/future of gold decision')
        self._last_gold = gold_time_msc
        out = {'gold_time_msc':gold_time_msc,'provider':'Alpaca','feed':'iex',
               'latency_assumption_ms':self.latency_ms}
        for sym in ETF_TO_INDEX:
            pref=sym.lower()+'_'
            q=self.history[sym]
            valid=bool(q) and 0 < gold_time_msc-q[-1][0] <= self.max_age_ms
            out[pref+'present'] = int(valid)
            out[pref+'last_age_ms'] = gold_time_msc-q[-1][0] if q else None
            out[pref+'spread_bps'] = q[-1][3] if valid else None
            out[pref+'iex_size_imbalance'] = q[-1][2] if valid else None
            for horizon in HORIZONS_MS:
                name=pref+f'logret_{horizon}ms'
                out[name]=None
                if not valid:continue
                target = q[-1][0]-horizon
                older = next((x for x in reversed(q) if x[0] <= target),None)
                if older is None or q[-1][0]-older[0]>horizon+self.max_age_ms:
                    continue
                out[name] = log(q[-1][1]/older[1])
        return out


def row_from_alpaca(symbol: str, payload: dict, ordinal:int) -> ETFQuote:
    """Provider-native quote dict (bp, ap, bs, as, t), not aggregate OHLC."""
    if any(k not in payload for k in ('bp','ap','bs','as','t')):
        raise ValueError('missing provider-native quote fields')
    return ETFQuote(symbol, parse_utc_milliseconds(payload['t']),
                    float(payload['bp']),float(payload['ap']),
                    float(payload['bs']),float(payload['as']),ordinal)
