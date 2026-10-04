# DELTA-A GRID-HF R2 HARD CHECKPOINT — MT5 Mechanics / Translation Contract

## Status

**MECHANICS SPECIFICATION ONLY — NOT AN AUTHORIZED PRODUCTION EA**

This contract supersedes the earlier R1 mechanics checkpoint. It captures the current GRID-HF R2 Refinement 02 state so later MT5 translation does not depend on chat reconstruction.

## 1. Architectural rule

Do **not** implement GRID-HF as a conventional unlimited physical grid.

The intended architecture is:

1. virtual multi-scale grid event detector,
2. causal feature/state engine,
3. directional specialist router,
4. deterministic de-duplication/arbitration,
5. specialist-specific bounded lifecycle,
6. broker execution layer,
7. portfolio/risk wrapper.

Virtual events may be numerous. A virtual crossing does not automatically imply a physical grid basket.

## 2. Tick clock

On each XAUUSD tick:

- use broker `time_msc` where available,
- read current Bid and Ask,
- compute midpoint only where signal geometry requires it,
- never use future ticks or incomplete future bars,
- update all event/router state causally.

Research parity uses native Dukascopy timing. Live MT5 uses the broker's actual tick stream.

## 3. Virtual grid state

Maintain independent state per configured scale.

Suggested structure:

```
GridState
  gap_price
  anchor_price
  initialized
  last_event_time_msc
  last_cross_direction
```

Crossing semantics:

- midpoint >= anchor + gap -> UP event,
- midpoint <= anchor - gap -> DOWN event,
- at most one new event per observed tick per scale,
- after an event, reset that scale's anchor to the observed causal price.

Do not backfill intermediate skipped levels from a large price jump.

## 4. Candidate-event de-duplication

Hard-checkpoint rule:

- combine eligible virtual events chronologically,
- retain the first eligible event inside a rolling **1-second** cluster,
- do not use future PnL to select the winner,
- log all suppressed duplicates.

January hard-checkpoint result after this rule: **39,253 retained events**.

## 5. Required causal features

The R2 router uses only as-of-event information:

- native quoted spread,
- crossing direction,
- grid/source scale,
- signed 15-second momentum,
- signed 60-second momentum,
- signed 60-second efficiency (signed movement divided by causal local range),
- previous retained-event direction,
- previous retained-event reclaim fraction,
- previous retained-event extension fraction,
- 10-second cross-scale agreement score.

Exact feature implementation must be parity-tested against the research producer before production certification.

## 6. Frozen router

### 6.1 Volatile branch

If native Dukascopy spread > **$0.90**:

- owner: **CONTINUATION**
- lifecycle: **180 seconds**

### 6.2 Quiet $2.25-$2.50 family

Use signed 60-second momentum relative to crossing direction.

- threshold center: **2.9**
- above threshold -> continuation / **1800 seconds**
- below threshold -> reversion / **600 seconds**

### 6.3 Quiet $2.375 family

Use signed 15-second momentum relative to crossing direction.

- threshold center: **3.9**
- above threshold -> continuation / **1800 seconds**
- below threshold -> reversion / **900 seconds**

### 6.4 Quiet $2.75-$3.00 family

Use prior retained-event causal reclaim fraction.

- threshold center: **0.73**
- above threshold -> continuation / **1200 seconds**
- below threshold -> reversion / **900 seconds**

### 6.5 Quiet $3.50-$5.00 and $10.00 families

- reversion / **1200 seconds**

### 6.6 Quiet $6.00-$8.00 family

Use signed 60-second efficiency.

- threshold center: **0.82**
- above threshold -> continuation / **300 seconds**
- below threshold -> reversion / **900 seconds**

## 7. Global overrides

### 7.1 Failed-reclaim persistence

If the prior retained event is same-direction and:

- prior reclaim fraction <= **0.50**
- prior extension fraction >= **1.50**

then:

- continuation / **600 seconds**

### 7.2 Immediate multi-scale agreement

Compute the causal agreement score using the prior/current 10-second multi-scale state.

- score >= **9** -> continuation / **180 seconds**
- score <= **-9** -> reversion / **600 seconds**

Override ordering must match the authoritative research producer when that producer is frozen for Jan-Jul replay.

## 8. Direction semantics

Continuation:

- UP crossing -> BUY
- DOWN crossing -> SELL

Reversion:

- UP crossing -> SELL
- DOWN crossing -> BUY

## 9. Lifecycle semantics

All R2 lifecycles are bounded time horizons.

At lifecycle expiration:

- BUY marks/exits at executable Bid,
- SELL marks/exits at executable Ask.

No unlimited recovery cycle is implied by GRID-HF R2.

## 10. Research execution surface

Python/DELTA-comparable research:

- signal clock: native Dukascopy,
- execution surface: `DUKAS_COINEXX_LIKE_P75`,
- session-dependent modeled spread remains approximately $0.20-$0.21 under the current DELTA P75 implementation.

Live MT5:

- use actual broker Bid/Ask,
- use verified commission/slippage/contract details,
- do **not** synthesize P75 quotes.

## 11. Hard-checkpoint metrics

January:

- retained events: **39,253**
- net: **+$12,239.46**
- average/event: **+$0.31181**
- PF: **1.05976**
- positive outcomes: **~50.30%**
- closed-event-sequence DD: **~$2,057.60**
- early-half net: **+$203.37**
- late-half net: **+$12,036.09**
- positive week buckets: **5/5**

These metrics are research parity targets, not production promises.

## 12. Session semantics

No hard session gate is part of the hard checkpoint.

January session diagnostics were all positive:

- off-session,
- London-only,
- London/NY overlap,
- NY-only.

London/NY overlap was strongest. A later session-aware router may change lifecycle, ownership confidence, or risk, but must be justified out of sample.

## 13. Prop-firm semantics

Prop-firm constraints are a separate wrapper. They must not redefine the alpha signal.

A later wrapper may enforce:

- daily loss ceiling,
- trailing/overall drawdown,
- maximum concurrent exposure,
- news restrictions,
- overnight/weekend rules,
- broker/firm trading-hour rules,
- account-specific lot scaling.

## 14. Required telemetry

Log every retained event:

- event `time_msc`,
- source/grid scale,
- anchor before crossing,
- crossing price,
- crossing direction,
- native spread,
- momentum/efficiency features,
- prior reclaim/extension state,
- agreement score,
- chosen specialist owner,
- lifecycle,
- duplicate/arbitration disposition,
- executable entry Bid/Ask,
- exit time and reason,
- gross/net PnL,
- MFE/MAE,
- concurrent open-trade state.

## 15. Translation blockers

Before production MQL5:

1. freeze the authoritative research producer implementing this exact router,
2. complete unchanged February-July replay,
3. measure overlapping-portfolio floating-equity DD,
4. validate Coinexx broker-native tick execution,
5. decide session/news/event routing only from out-of-sample evidence,
6. define any prop-firm wrapper independently,
7. obtain explicit owner authorization for production MQL5.

## 16. Rollback

The authoritative rollback checkpoint is:

`DELTA_A_GRID_HF_R2_HARD_CHECKPOINT.md`

If later refinement fails, restore this router and metrics rather than an intermediate experiment.
