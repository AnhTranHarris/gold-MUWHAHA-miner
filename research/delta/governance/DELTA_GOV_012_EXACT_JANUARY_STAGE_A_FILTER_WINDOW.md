# DELTA GOV-012 — Exact January Stage-A Filter Window

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE PROSPECTIVELY  
**Scope:** Every DELTA Stage-A candidate, specialist, mechanism, model, router, execution rule, and composite screen.

## 1. Frozen window

The owner's "first 2.5 weeks of January" Stage-A research filter is defined as exactly **17.5 calendar days** from the start of January 2026, using UTC.

Scoring interval:

`[2026-01-01T00:00:00.000Z, 2026-01-18T12:00:00.000Z)`

Machine boundaries:
- start timestamp ms UTC: `1767225600000`
- end timestamp ms UTC: `1768737600000`

The interval is left-closed/right-open:
- ticks with `timestamp_ms >= 1767225600000` are eligible;
- ticks with `timestamp_ms < 1768737600000` are eligible;
- a tick exactly at `1768737600000` is excluded.

## 2. Why calendar time

This boundary is frozen from the owner's phrase "first 2.5 weeks" before any DELTA_005 candidate result is observed.

DELTA does not redefine the interval by:
- number of profitable days;
- number of losing days;
- number of trades;
- volatility;
- session count;
- first/last convenient trading day;
- candidate performance.

Weekend/holiday closures naturally contain no ticks and therefore contribute no fabricated observations.

## 3. Market closure implication

The exact end boundary occurs on Sunday, 2026-01-18 at 12:00 UTC.

Because XAUUSD is normally closed during that weekend interval, the last eligible market event will naturally be the last registered source tick before the boundary. DELTA must not move the boundary backward to Friday merely to make it look like a trading-day cutoff.

## 4. January cold-start rule

December 2025 is outside the registered DELTA development corpus.

Therefore Stage-A January uses a **cold start**:
- no December ticks;
- no pre-2026 feature warm-up;
- no hidden state imported from an earlier period;
- state accumulates causally from the first registered January tick.

This is consistent with DELTA_004's January warm-up policy.

## 5. Candidate scoring

Every DELTA_005+ Stage-A candidate manifest must record:
- this governance file;
- exact start/end ISO timestamps;
- exact start/end epoch milliseconds;
- surface used;
- candidate/version;
- producing code identity.

Candidate metrics are computed only from positions/opportunities attributable to the scoring window under the candidate's preregistered lifecycle rules.

A position may not be opened before the start boundary.

If a position is still open when no further eligible tick exists before the exclusive end boundary, DELTA uses:

`FORCE_CLOSE_AT_LAST_ELIGIBLE_EXECUTABLE_QUOTE_BEFORE_END`

The close uses the last eligible executable side:
- long positions close/mark at Bid;
- short positions close/mark at Ask.

No tick at or after the exclusive end boundary may affect Stage-A P/L, drawdown, hold time, or trade classification. This rule is identical for all Stage-A candidate versions.

## 6. Research surfaces

The default Stage-A research surface remains:

`DUKAS_COINEXX_LIKE_P75`

Required friction/robustness references remain:
- `DUKAS_COINEXX_LIKE_P50`;
- `DUKAS_COINEXX_LIKE_P90`;
- `DUKAS_NATIVE`.

This contract freezes only the time window; it does not relax any active candidate, metric-lock, activity, maintenance, causality, or clean-room rule.

## 7. Prospective revision only

The owner may revise this window later.

Unless the owner explicitly requests retrospective rescoring, a later change is prospective and does not rewrite completed candidate evidence.

## 8. August

This contract does not authorize August access. August 2026 remains sealed.
