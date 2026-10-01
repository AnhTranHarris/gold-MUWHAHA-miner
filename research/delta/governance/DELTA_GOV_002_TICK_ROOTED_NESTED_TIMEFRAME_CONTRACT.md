# DELTA GOV-002 — Tick-Rooted Nested Timeframe Contract

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY  
**Scope:** All DELTA Python backtests, research features, parity fixtures, and any eventual MT5 EA derived from DELTA.

## 1. Authoritative source

The ordered tick stream is the authoritative market chronology.

Every candle used by DELTA is reconstructed from tick data for accuracy. Prebuilt candles may be used only as an external comparison surface, never as the authoritative source when the canonical tick stream is available.

## 2. Nested analytical hierarchy

DELTA uses the following nested timeframe concept:

```text
TICKS
  -> 0.25 second
  -> 1 second
  -> 5 seconds
  -> 15 seconds
  -> 30 seconds
  -> 45 seconds
  -> 1 minute
  -> standard MT5 timeframes through 1 day
```

This sequence defines the analytical hierarchy from microstructure to progressively slower market state.

It does **not** require DELTA to construct a higher candle from the immediately preceding candle. For accuracy, each timeframe is canonically rebuilt directly from the same ordered tick stream.

Therefore:

`CANDLE(timeframe) = AGGREGATE(authoritative_ticks, timeframe_boundary_rule)`

for every supported timeframe.

## 3. Required DELTA timeframe set

Custom sub-minute research timeframes:
- 250 milliseconds / 0.25 second
- 1 second
- 5 seconds
- 15 seconds
- 30 seconds
- 45 seconds

Standard MT5 periods through D1:
- M1
- M2
- M3
- M4
- M5
- M6
- M10
- M12
- M15
- M20
- M30
- H1
- H2
- H3
- H4
- H6
- H8
- H12
- D1

W1 and MN1 are outside the present DELTA scope unless the owner later expands the research horizon.

## 4. Candle boundary rule

Every fixed-duration candle uses a left-closed, right-open interval:

`[bar_start, bar_end)`

A tick exactly at `bar_end` belongs to the next candle.

All time boundaries must use integer time units. Floating-point timestamp arithmetic is prohibited for candle assignment.

Same-timestamp ticks retain deterministic source order.

## 5. Visibility and causality

A completed candle becomes available to trading logic only at its right edge.

A strategy decision at time `t` may use:
- completed candles whose `bar_end <= t`;
- explicitly defined intrabar state built only from ticks observed through `t`.

It may not use the eventual high, low, close, volume, indicator value, or any other future property of a candle that has not closed.

This rule applies identically in Python and MT5.

## 6. Price surfaces

Where BID/ASK ticks are available, each candle must preserve at minimum:
- BID open, high, low, close;
- ASK open, high, low, close;
- first tick timestamp;
- last tick timestamp;
- first source ordinal;
- last source ordinal;
- tick count.

Midpoint OHLC may be derived for research, but midpoint is not an executable market price and must not silently replace BID/ASK in fill or exit logic.

## 7. Empty intervals

DELTA does not invent ticks.

If an interval contains no source tick:
- the canonical interval is empty;
- no synthetic executable OHLC is created;
- a carry-forward display/state representation may be used only if explicitly declared by the research unit and must remain distinguishable from an observed candle.

## 8. Direct tick reconstruction invariant

Every supported timeframe must be reproducible independently from the authoritative tick stream.

For a given source file, timestamp convention, and boundary rule, repeated construction must produce identical candles.

The required QA identity is:

`rebuild_from_ticks(timeframe, run_A) == rebuild_from_ticks(timeframe, run_B)`

for:
- boundaries;
- BID OHLC;
- ASK OHLC;
- tick count;
- first/last tick identity.

## 9. Cross-timeframe consistency

Although every candle is built directly from ticks, DELTA treats the hierarchy as nested state.

Research may compare:
- microstructure state against slower context;
- agreement and disagreement between horizons;
- entry timing across fast and slow state;
- hold persistence across horizons;
- exit/harvest state across horizons;
- volatility, trend, compression, expansion, reversal, and regime persistence.

No higher timeframe may overwrite or reinterpret the tick chronology used by a lower timeframe.

## 10. Python-to-MT5 parity

Any eventual DELTA MT5 candidate must reproduce the Python candle engine's:
- tick ordering;
- boundary clock;
- timeframe definitions;
- bar-open/bar-close rules;
- BID/ASK OHLC;
- empty-interval behavior;
- completed-bar visibility;
- same-timestamp ordering.

Parity fixtures must include:
- ticks immediately before and on timeframe boundaries;
- multiple ticks sharing one timestamp;
- sparse/no-tick intervals;
- rollover across minute, hour, and day boundaries;
- representative 250ms, second, minute, hour, and D1 bars.

A candle-parity mismatch blocks MT5 promotion.

## 11. Research governance

This contract is foundational DELTA methodology.

A research unit may add a new timeframe, but it must preregister its exact duration and boundary rule.

A research unit may not silently change:
- timestamp normalization;
- candle boundaries;
- empty-interval behavior;
- BID/ASK aggregation;
- completed-bar visibility.

Any such change requires an explicit methodological amendment before comparison with prior DELTA results.
