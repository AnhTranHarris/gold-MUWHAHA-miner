# DELTA-A GRID-HF R2 REFINEMENT 02 — HARD CHECKPOINT

**Checkpoint date:** 2026-10-04  
**Lineage:** DELTA-A  
**Branch:** `delta-A`  
**Status:** **HARD CHECKPOINT / RESEARCH ONLY / NOT MT5 PRODUCTION AUTHORIZED**

This file is the authoritative rollback record for the current GRID-HF research system. Future experiments may branch from this checkpoint, but a failed refinement must be able to return to this state without reconstructing it from chat history.

## Isolation

- Main `delta` is not modified.
- August 2026 remains sealed.
- No production MQL5 EA is authorized.
- No prop-firm/session/news restriction is promoted into alpha at this checkpoint.

## Frozen January event clock

- unique events: **39,253**
- approximate event density: **1,354/day**
- de-duplication: chronological first eligible event inside a rolling **1-second** cluster
- future payoff used in de-duplication: **NO**
- signal clock: native ordered Dukascopy XAUUSD ticks
- research execution: `DUKAS_COINEXX_LIKE_P75`

## Frozen router

### Volatile branch

If native Dukascopy spread > **$0.90**:

- owner: **CONTINUATION**
- lifecycle: **180 seconds**

### Quiet $2.25-$2.50 family

Feature: signed 60-second momentum relative to crossing direction.

- threshold neighborhood center: **2.9**
- above: continuation / **1800s**
- below: reversion / **600s**

### Quiet $2.375 family

Feature: signed 15-second momentum relative to crossing direction.

- threshold neighborhood center: **3.9**
- above: continuation / **1800s**
- below: reversion / **900s**

### Quiet $2.75-$3.00 family

Feature: prior retained-event causal reclaim fraction.

- threshold neighborhood center: **0.73**
- above: continuation / **1200s**
- below: reversion / **900s**

### Quiet $3.50-$5.00 and $10.00 families

- reversion / **1200s**

### Quiet $6.00-$8.00 family

Feature: signed 60-second efficiency.

- threshold neighborhood center: **0.82**
- above: continuation / **300s**
- below: reversion / **900s**

### Failed-reclaim persistence override

If previous retained event is same-direction AND:

- reclaim fraction <= **0.50**
- extension fraction >= **1.50**

then:

- continuation / **600s**

### Immediate multi-scale agreement override

Causal agreement window: **10 seconds**.

- score >= **9** -> continuation / **180s**
- score <= **-9** -> reversion / **600s**

## Frozen January research metrics

- events: **39,253**
- net: **+$12,239.46**
- average/event: **+$0.31181**
- PF: **1.05976**
- positive outcomes: **~50.30%**
- closed-event-sequence drawdown: **~$2,057.60**
- early-half net: **+$203.37**
- late-half net: **+$12,036.09**
- positive week buckets: **5 / 5**

Weekly net:

- W1: **+$75.52**
- W2: **+$27.45**
- W3: **+$1,172.73**
- W4: **+$1,210.91**
- W5: **+$9,752.85**

## Neighborhood evidence

A bounded adjacent sweep produced **156 qualified neighboring router configurations**. The checkpoint is therefore supported by a parameter neighborhood rather than one isolated optimum.

## Session diagnostic

All broad session buckets are positive:

- OFF_SESSION: 11,669 events / **+$1,873.78**
- LONDON_ONLY: 6,102 events / **+$920.37**
- LONDON_NY_OVERLAP: 10,200 events / **+$7,583.84**
- NY_ONLY: 11,282 events / **+$1,861.47**

Hard session exclusions are **not** frozen into alpha. Session-aware routing/lifecycle adaptation may be tested later if the pattern survives out of sample.

## R9 SYNTH reference comparison

Historical R9 SYNTH reference:

- Jan-Jul trades: **219,342**
- January entries: approximately **27,980**
- win rate: **87.14%**
- net: **+$309,122.85**
- PF: approximately **20.04**
- expected payoff: approximately **+$1.409/trade**

Current hard checkpoint:

- January events: **39,253** (~140% of R9 SYNTH January count)
- average/event: **+$0.31181** (~22% of R9 SYNTH expected payoff benchmark)
- PF: **1.05976**

Interpretation: high-frequency opportunity supply is experimentally sufficient; quality extraction remains the main gap.

## Not frozen / still blocked

The following remain research blockers:

1. unchanged February-July durability replay,
2. true overlapping-portfolio concurrency and floating-equity drawdown,
3. broker-native Coinexx MT5 validation,
4. later session/news/event-aware routing,
5. prop-firm deployment wrapper,
6. production MQL5 authorization.

## Next gate

Run this exact R2 router **unchanged** across February-July with full portfolio concurrency/equity accounting. Only cross-month residual evidence may justify promoting session-aware or news/event-aware rules.

## Rollback rule

If a later GRID-HF experiment fails its advancement gate, roll back to this checkpoint rather than to an intermediate exploratory state.
