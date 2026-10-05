# DELTA-A R9 GRID — Potential MT5 EA Build Specification

**Status:** Research translation contract only. No production MQL5 build is authorized by this document.

## Design objective

Translate the current pre-August grid milestone into MT5 without changing its causal logic, event density, bounded lifecycles, or portfolio-pressure behavior. The live EA must remain fast enough for XAUUSD tick processing and must not recreate a classic unlimited physical grid.

## Runtime architecture

Recommended modules:

1. `TickClock` — broker `time_msc`, Bid, Ask, spread, and session state.
2. `VirtualGridBank` — fixed set of volatility-normalized grid scales; O(1) update per scale.
3. `FeatureState` — rolling momentum, range, event-flow alignment, crossing run, previous reclaim/extension, and time-since-opposite state.
4. `BootstrapRouter` — cold-start high-frequency router used until the history-depth maturity gate is satisfied.
5. `MatureSpecialistBank` — frozen R3.4/A1 specialist ownership, source-specific lifecycle, and selective recovery logic.
6. `LifecycleManager` — bounded time exits and source-specific profit/loss management.
7. `PortfolioPressure` — gross concurrent-position cap and directional concentration gate.
8. `BrokerExecution` — real Coinexx Bid/Ask, verified stops, commission, slippage, margin, and fill handling.
9. `Telemetry` — compact event/trade ledger, daily summary, state transitions, and parity counters.

## Calendar-blind maturity transition

Start in `BOOTSTRAP`.

Become mature-eligible only when:

- at least 25 active signal days have been observed;
- at least 25,000 strategy outcomes have completed.

Do not switch immediately. Arm the transition and wait for the next market inactivity gap of at least 24 hours. Switch at the first eligible event after that gap.

## Event engine

- XAUUSD only at this milestone.
- Volatility-normalized multi-scale geometry.
- At most one new event per observed tick per scale.
- Do not backfill skipped levels after a price jump.
- De-duplication/arbitration must be deterministic and causal.
- No Martingale.
- No future bars or future labels.

## Portfolio-pressure wrapper

Current milestone research limits:

- maximum 250 simultaneously open physical research positions;
- reject a new BUY if net long-minus-short exposure is already >=225 positions;
- reject a new SELL if net short-minus-long exposure is already >=225 positions.

These counts are research-account limits, not small-account limits.

## Small-account / funded-account translation blocker

The current research account is a $100,000 diagnostic account and can reach 250 simultaneous 0.01-lot positions. That is not suitable for a $100-$500 account.

Before a small-account or prop-firm build, add an independent physical-exposure adapter that can preserve virtual specialist activity while respecting free margin, leverage, contract size, maximum physical lots, and account drawdown policy.

Possible later research includes physical-position aggregation/netting, virtual subtrade accounting with fewer broker positions, or account-size-dependent concurrency scaling. None is approved yet because each can alter execution and must be revalidated.

## Performance implementation rules

- fixed arrays/ring buffers instead of DataFrame-like structures;
- never scan full history or all historical deals on every tick;
- active-position registry indexed in memory;
- incremental rolling statistics;
- session/bar state updated only when its bucket changes;
- preallocated virtual-grid states;
- O(1) or amortized O(1) pressure gate;
- throttled/batched telemetry.

A compiled Python benchmark processed the milestone pressure-gate decisions at roughly 17 million events/second in the research environment. This is not an MT5 latency guarantee.

## Execution semantics

Research uses native Dukascopy signal timing and the `DUKAS_COINEXX_LIKE_P75` comparison surface.

Live MT5 must use actual broker Bid/Ask and verified commission, slippage, lot step, stops, margin, and fill policy. Never synthesize P75 quotes inside the EA.

## Build gates

1. explicit owner approval to write MQL5;
2. August holdout separately authorized and evaluated;
3. Python-to-MT5 signal/lifecycle parity checks;
4. Coinexx Strategy Tester `Every tick based on real ticks`;
5. account-size/margin scaling defined;
6. live-demo forward validation;
7. separate approval before funded deployment.

## Rollback

Current research rollback target: `DELTA_A_R9_GRID_MILESTONE_01`.
