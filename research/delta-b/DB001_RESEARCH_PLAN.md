# DB001 — Grid Layer 1 Research Plan

Status: **PREREGISTERED RESEARCH PLAN**

## Objective

Build the smallest adaptive intrinsic-time grid kernel capable of identifying economically meaningful XAUUSD movement while remaining causal, cost-aware, session-aware, and medium/high-news-aware.

DB001 deliberately excludes Volume Profile, RSI, specialist routing, ML ensembles, and production MQL5.

## DB001A — Executable Movement Quantum

Construct `Q_t` from only information observable at time `t`.

Candidate components:

- current quoted spread
- rolling spread percentile
- explicit commission equivalent
- conservative slippage allowance
- rolling robust absolute midpoint movement
- tick-direction switching rate
- tick-arrival intensity
- short-horizon directional efficiency

The first experiment must compare a small bounded family, not an unconstrained optimizer:

### Q-A — Cost + Robust Noise
```
Q = max(kc * friction, kn * median_abs_mid_change)
```

### Q-B — Cost + Quantile Noise
```
Q = max(kc * friction, quantile(abs_mid_change, p))
```

### Q-C — Cost + Path Noise
```
Q = max(kc * friction, kn * path_noise)
```

where `path_noise` increases when gross movement is high but net displacement is low.

Initial coefficients must be tested in broad neighborhoods and reported as surfaces, not cherry-picked winners.

## DB001B — Session State

Clock-derived causal sessions:

- ASIA
- LONDON_OPEN_TRANSITION
- LONDON
- LONDON_NY_OVERLAP
- NEW_YORK
- ROLLOVER_OFFSESSION

Requirements:

- explicit timezone basis
- explicit DST behavior
- no historical-profit label in session classification
- session can alter bounded Q/hysteresis parameters, not direction

Primary question:

> Does session-conditioned grid adaptation reduce false event generation and after-cost toxic entries without destroying opportunity density?

## DB001C — Scheduled Medium/High Event State

Economic calendar events with importance MEDIUM or HIGH create an observable phase state.

Initial phase family:

- normal
- pre-event
- release
- post-event discovery
- post-event stabilization

Medium and high importance may use different bounded windows and adaptation strengths.

The calendar label may change grid operating conditions. It may not imply expected release direction.

Primary question:

> Can event-aware elasticity reduce spread/noise-driven false lattice transitions while preserving genuine post-release expansion opportunities?

## DB001D — Unscheduled Shock State

Causal shock score from observable market data only.

Potential components:

- spread percentile acceleration
- tick-rate acceleration
- realized micro-volatility jump
- burst of 1Q/2Q intrinsic events
- abrupt directional-efficiency change

The score may alter grid elasticity and entry authority. It must not be described as identifying the underlying news.

## DB001E — Nested Intrinsic Lattice

Scales:

- L0 = Q
- L1 = 2Q
- L2 = 4Q
- L3 = 8Q

Each scale tracks:

- direction
- running extreme
- last directional-change confirmation
- overshoot size
- event age
- reversal count
- residence/cross count
- session/event context snapshot

No order is opened merely because a directional-change event occurs.

## DB001F — Grid State Classifier

Exactly five primary states:

1. TRANSIT
2. ROTATION
3. ESCAPE
4. FAILED_ESCAPE_RECLAIM
5. CHURN_SHOCK

First implementation should be deterministic and transparent.

If thresholds cannot be made stable across broad neighborhoods, the state definition fails and is revised before adding a higher layer.

## DB001G — Economic Diagnostic Replay

Compare the exact R9 REAL opportunity/trade population against grid diagnostics where reconstructible.

Measure:

- retained trade/opportunity count
- net profit
- gross profit
- gross loss
- max balance/equity drawdown
- monthly PnL Jan-Jul
- trade duration
- loss clusters
- session/event attribution
- state attribution
- after-cost excursion distributions
- $100/$500/$1k/$10k chronological capital overlays when economically meaningful

The grid is not allowed to "win" by deleting nearly all trades.

## DB001H — Internal Breakthrough Hurdle

Research target, not automatic promotion:

- approximately >=30% R9 REAL gross-loss reduction
- approximately >=30% R9 REAL max-drawdown reduction
- meaningful high-frequency/scalping opportunity density retained
- seven-month economics improved or materially de-risked
- no hidden leverage increase
- no martingale/adverse scaling

If Grid Layer 1 cannot meet a meaningful threshold, diagnose the specific unresolved question before adding Volume Profile.

## Falsification Conditions

DB001 Grid Layer 1 is rejected or reworked if:

- performance depends on future information
- Q collapses into unstable month-specific tuning
- session/news adaptation simply suppresses most trading
- results depend on midpoint fills
- spread/commission treatment is inconsistent
- false-boundary churn remains a dominant loss source
- high-frequency event density is destroyed
- robustness exists only at a single parameter point
- performance improvement is mostly from hidden exposure changes

## Freeze Deliverables

A successful Grid Layer 1 freeze requires:

- exact deterministic Python producer
- independent QA
- feature/state timing specification
- event ledger schema
- Jan-Jul result ledger
- parameter-neighborhood report
- session/event attribution report
- capital overlay report
- exact source hashes
- reconstruction manifest
- MT5 translation contract
- human-readable research report

Only after those deliverables are durable may DELTA-B begin Volume Profile Layer 2.
