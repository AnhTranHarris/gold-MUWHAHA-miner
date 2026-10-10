"""DAA033 C2D3-J: source-exact JAN038/FEB042 entry-known inputs.

Complete original executable authorities:
 - JAN039/JAN038_SELECTED_EXACT.json::signal_gating_source_phase_pairs
 - FEB042/prepare.py:: qsp, imp20, phase, excluded expressions

This is a strictly preceding ENTRY FEATURE transport / optional JAN038 phase
filter, not original S17..S28 event generation, not physical admission, not
FEB045 quality-pocket filtering, not source-ledger exit/PnL reproduction.
"""
from __future__ import annotations
import hashlib
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

TEN_MIN_MS = 600_000
IMPACT_LOOKBACK_MS = 20_000
JAN038_SOURCE_SHA256 = '643103c0c1a260e7ca9a1a9b2c8653c8afcaea5eba513c605a3aca05cbfecb4d'

@dataclass(frozen=True, slots=True)
class OriginalEntryContext:
    timestamp_ms: int
    phase10: int
    spread_usd: float
    raw_impulse20_usd: float
    source_id: int
    excluded_by_jan038: bool
    prior_observation_ms: int

class OriginalJAN038FEB042Online:
    """One-quote-at-a-time original left-search 20-second input state.

    Uses observed genuine Bid/Ask, NOT STMR synthetic research quotes;
    no future observations, month name, day label, or rolling hindsight P/L.
    The original source arrays may contain MANY offers on one physical tick.
    Caller records each original source offer separately after on_quote.
    """
    def __init__(self, source_rules: str | Path):
        file=Path(source_rules)
        content=file.read_bytes()
        if hashlib.sha256(content).hexdigest()!=JAN038_SOURCE_SHA256:
            raise ValueError('Original JAN038 whole-file SHA256 mismatch')
        source=json.loads(content)
        rows=source['signal_gating_source_phase_pairs']
        self.excluded_pairs=frozenset((int(a),int(b)) for a,b in rows)
        self._recent=deque()
        self._now=-1
        self._ask=0
        self._bid=0
        self._mid_twice=0
        self.observed_quotes=0
        self.discarded_quotes=0

    def on_quote(self, timestamp_ms: int, ask_raw: int, bid_raw: int) -> None:
        if timestamp_ms<self._now:
            raise ValueError('Original FEB042 Bid/Ask chronology cannot run backwards')
        if ask_raw<bid_raw or bid_raw<=0:
            raise ValueError('Non-executable Bid/Ask quote')
        dq=self._recent
        boundary=timestamp_ms-IMPACT_LOOKBACK_MS
        while dq and dq[0][0]<boundary:
            dq.popleft()
            self.discarded_quotes+=1
        self._now=int(timestamp_ms)
        self._ask=int(ask_raw)
        self._bid=int(bid_raw)
        self._mid_twice=self._ask+self._bid
        dq.append((int(timestamp_ms),self._mid_twice))
        self.observed_quotes+=1

    def context_for(self, source_id:int) -> OriginalEntryContext:
        if self._now<0:
            raise ValueError('Source offer before first genuinely observed tick')
        # JAN038 exclusion is NOT FEB044/045 source quality; keep separate.
        phase=(self._now//TEN_MIN_MS)%6
        earlier_t,earlier_mid2=self._recent[0]
        return OriginalEntryContext(
            timestamp_ms=self._now,
            phase10=phase,
            spread_usd=(self._ask-self._bid)/1000.0,
            raw_impulse20_usd=(self._mid_twice-earlier_mid2)/2000.0,
            source_id=int(source_id),
            excluded_by_jan038=(int(source_id),phase) in self.excluded_pairs,
            prior_observation_ms=earlier_t)
