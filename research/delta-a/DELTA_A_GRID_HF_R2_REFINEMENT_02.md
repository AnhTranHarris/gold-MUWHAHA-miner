# DELTA-A GRID-HF R2 — Refinement Checkpoint 02

## Status

**INTERIM RESEARCH BREAKTHROUGH — NOT MT5 AUTHORIZED**

Main `delta` is not modified. August remains sealed.

## Objective

Increase directional/lifecycle quality while preserving the R9-like January event population. Hard constraint: do not improve metrics by choking event supply.

## Exact event population

The R2 January event clock is deterministically reconstructed from the preserved R1 regime-bank event union using chronological first-event retention inside a rolling 1-second de-duplication window.

- unique January events: **39,253**
- approximate events/day: **1,354**
- event count is unchanged by this refinement

## Comparable prior R2 checkpoint

- net: **+$5,428.69**
- average/event: **+$0.13830**
- PF: **1.02874**
- positive outcomes: **49.89%**
- sequence DD: **~$2,878.93**
- early-half net: **+$66.99**
- positive January week buckets: **2 / 5**

## R2 Refinement 02 architecture

### Volatile branch

If native Dukascopy spread > $0.90:

- base owner: **CONTINUATION**
- base lifecycle: **180 seconds**

### Quiet branch — scale-aware routing

#### $2.25 / $2.50 micro family

Use signed 60-second momentum relative to crossing direction.

- threshold neighborhood centered near **2.9**
- above threshold: continuation / 1800 seconds
- below threshold: reversion / 600 seconds

#### $2.375 transition family

Use signed 15-second momentum relative to crossing direction.

- threshold neighborhood centered near **3.9**
- above threshold: continuation / 1800 seconds
- below threshold: reversion / 900 seconds

#### $2.75–$3.00 family

Use the prior retained event's causal reclaim fraction.

- threshold neighborhood centered near **0.73**
- larger reclaim-state value: continuation / 1200 seconds
- lower value: reversion / 900 seconds

#### $3.50–$5.00 and $10.00 family

- reversion / 1200 seconds

#### $6.00–$8.00 family

Use 60-second signed efficiency (`signed momentum / range`).

- threshold neighborhood centered near **0.82**
- above threshold: continuation / 300 seconds
- below threshold: reversion / 900 seconds

### Global failed-reclaim persistence override

When the previous retained event is same-direction, prior reclaim fraction <= **0.50**, and prior extension fraction >= **1.50**:

- continuation / 600 seconds

### Global immediate multi-scale agreement override

Using the causal 10-second cross-scale agreement score:

- score >= **9**: continuation / 180 seconds
- score <= **-9**: reversion / 600 seconds

## Leading January result

- events: **39,253**
- net: **+$12,239.46**
- average/event: **+$0.31181**
- PF: **1.05976**
- positive outcomes: **50.30%**
- closed-event-sequence DD: **~$2,057.60**
- early-half net: **+$203.37**
- late-half net: **+$12,036.09**
- positive January week buckets: **5 / 5**

Week-bucket net:

- W1: +$75.52
- W2: +$27.45
- W3: +$1,172.73
- W4: +$1,210.91
- W5: +$9,752.85

## Neighborhood robustness

A bounded nearby sweep produced **156 qualified rich-router configurations**, with many adjacent thresholds preserving positive early-half economics, >=4 positive weeks, and <=$2,500 sequence DD.

## Session diagnostic

Broad January research sessions under the selected router:

- OFF_SESSION: 11,669 events, **+$1,873.78**, +$0.161/event, PF 1.036
- LONDON_ONLY: 6,102 events, **+$920.37**, +$0.151/event, PF 1.036
- LONDON_NY_OVERLAP: 10,200 events, **+$7,583.84**, +$0.744/event, PF 1.117
- NY_ONLY: 11,282 events, **+$1,861.47**, +$0.165/event, PF 1.030

All broad sessions remain positive.

### Interpretation

A hard session-disable rule is **not justified yet**. The London/NY overlap is substantially stronger, but the other broad session buckets still contribute positive expectancy and valuable R9-scale volume.

Residual performance varies sharply by UTC hour, so later session-aware **routing/lifecycle adaptation** may be valuable. It should not initially be implemented as a blunt session gate.

## Burst/de-duplication diagnostic

Increasing the current 1-second event-spacing window generally reduced net and did not provide a sufficiently superior risk/quality tradeoff. Preserve the current **1-second deterministic de-duplication** checkpoint.

## Prop-firm / session conclusion

### Trading-session settings

**Adaptive session context: likely useful later. Hard session exclusions: not currently justified.**

### Prop-firm settings

Prop-firm rules should remain a **separate deployment/risk-policy layer**, not part of the alpha definition. Examples include daily loss limit, maximum overall drawdown, maximum concurrent exposure, news-event restrictions, weekend/overnight restrictions, and firm-specific trading-hour rules.

## R9 SYNTH comparison

Historical R9 SYNTH reference:

- Jan-Jul trades: 219,342
- January entries: approximately 27,980
- win rate: 87.14%
- expected payoff: +$1.409/trade
- PF: ~20.04

R2 Refinement 02:

- January events: 39,253 (~140% of R9 SYNTH January count)
- expected payoff: +$0.312/event (~22% of R9 SYNTH expected payoff)
- PF: 1.060

The volume problem is solved experimentally. The remaining gap is trade-quality extraction and late-month concentration.

## Remaining limitations

- The selected router is still January-harvest research.
- Profit remains heavily concentrated in W5.
- Event-sequence DD is not constrained portfolio floating-equity DD.
- Jan-Jul durability is not yet established for this R2 refinement.
- No session/news/event overlay is yet promoted.
- No production MQL5 code is authorized.

## Next recommended unit

Run this R2 architecture unchanged across Feb-Jul with full portfolio concurrency/equity accounting. Use cross-month residuals to decide whether session-aware routing is structural or January-specific.
