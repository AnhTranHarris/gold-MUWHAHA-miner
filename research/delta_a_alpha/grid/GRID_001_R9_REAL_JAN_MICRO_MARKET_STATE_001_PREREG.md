# GRID-001 R9 REAL January Nested Micro-Market State 001 — Preregistration

**Unit:** `DAA_GRID_001_R9_REAL_JAN_MICRO_MARKET_STATE_001`  
**Status:** FROZEN BEFORE ANALYSIS

## Question

Can causal subsecond/second market state around each actual R9 REAL January signal isolate wrong-direction loss families more selectively than broad 5m/15m state?

This remains a diagnostic concentration unit. No R9 entry is changed yet.

## Source legitimacy

Dukascopy January ticks contain:
- timestamp;
- Ask;
- Bid;
- Ask volume at top of book;
- Bid volume at top of book.

No L2/L3 depth is assumed.

Public HFT code commonly uses top-of-book volume imbalance and size-weighted microprice. Delta-A-alpha clean-room reconstructs only the L1 formulas supported by the data.

## M1 — nested price trend within trend

At each R9 entry, using modeled midpoint ticks at or before entry:

Frozen horizons:
- 250 ms
- 1 second
- 5 seconds

For each horizon compute R9-side-aligned midpoint displacement.

State per horizon:
- SUPPORT: aligned displacement > 0
- OPPOSE: aligned displacement < 0
- FLAT: exactly 0

Nested price states:
- ALL_SUPPORT
- ALL_OPPOSE
- FAST_SUPPORT_SLOW_OPPOSE
- FAST_OPPOSE_SLOW_SUPPORT
- MIXED_FLAT

No magnitude threshold is fitted.

Also report directional efficiency on each horizon for description only:
`abs(net displacement) / path length`.

## M2 — legitimate L1 imbalance

Per tick:

`imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)`

At the R9 entry compute:
- current imbalance;
- tick-weighted mean imbalance over prior 1 second.

Align to R9 side:
- positive = supports R9 direction;
- negative = opposes R9 direction.

Frozen L1 states:
- BOTH_SUPPORT
- BOTH_OPPOSE
- FLIP_TO_SUPPORT: 1s mean opposes, current supports
- FLIP_TO_OPPOSE: 1s mean supports, current opposes
- MIXED_OR_ZERO

## M3 — L1 microprice

For diagnostic parity only:

`microprice = (ask * bid_volume + bid * ask_volume) / (bid_volume + ask_volume)`

Report the R9-side-aligned microprice displacement from midpoint, normalized by half-spread.

Because microprice bias is mathematically related to L1 imbalance, it is not allowed to create a separate optimized filter in this unit.

## M4 — quote-event intensity

Event-time activity is measured causally:

`rate_ratio = ticks_in_prior_1s / (ticks_in_prior_30s / 30)`

Frozen states:
- THIN: ratio < 0.5
- NORMAL: 0.5 <= ratio < 2.0
- BURST: ratio >= 2.0

If the 30-second baseline is empty, state is UNKNOWN.

## Frozen interactions

Only these families are inspected:

1. nested price state;
2. L1 imbalance state;
3. quote-intensity state;
4. nested price × L1 state;
5. nested price × frozen 5m/15m owner relation;
6. nested price × frozen owner phase.

No learned model.
No arbitrary post-hoc conjunction search.
No session/news/macroeconomic state.

## Metrics

For every family:
- trades and trade share;
- MT5 deal-level net / gross profit / gross loss / PF;
- gross-loss share of canonical January;
- gross-profit share;
- gross-loss share minus trade share;
- gross-loss share minus gross-profit share;
- discovery / validation net.

## Preferred leverage signal

A micro-state is considered structurally interesting if:
- it contains >=20% of canonical gross loss or >=20% of canonical net loss;
- it is net-negative in both discovery and validation;
- gross-loss share exceeds gross-profit share;
- and either gross-loss share materially exceeds its trade share or the state creates a clear routing asymmetry.

The unit does not authorize perfect vetoing.

## Next step if useful

A passing micro-state must face a separate **risk-admission intervention**:
- IMMEDIATE,
- SHADOW/PROVE,
- DEFER,
- or ABSTAIN.

The objective is to preserve recoverable opportunities rather than amputate a broad state.

August sealed. Main `delta` read-only. Fixed 0.01. No Martingale. MQL5 unauthorized.
