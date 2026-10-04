# DELTA-A GRID-HF R1 — MT5 Mechanics / Translation Contract

## Status

**MECHANICS SPECIFICATION ONLY — NOT AN AUTHORIZED PRODUCTION EA**

This file captures deterministic MT5-translatable mechanics so the current research checkpoint is not lost. It does not authorize creation, sale, deployment, or certification of an MQL5 EA.

## 1. Architectural rule

Do **not** implement GRID-HF as a classic unlimited physical grid.

Implement it as:

1. virtual multi-scale grid event detector,
2. causal regime owner,
3. specialist router,
4. entry de-duplication/arbitration layer,
5. specialist-specific lifecycle,
6. account/risk layer.

The virtual event detector may emit many candidate events without opening multiple physical grid positions.

## 2. Tick clock

On every new XAUUSD tick:

- capture broker `time_msc` where available,
- read Bid and Ask,
- compute midpoint only for signal geometry where specified,
- never use future ticks,
- maintain all virtual-grid state causally.

Research parity uses native Dukascopy timing. Live MT5 uses the broker's actual tick stream.

## 3. Virtual grid state

Maintain an independent state object for each configured grid scale.

Suggested structure:

```
GridState
  gap_price
  anchor_price
  initialized
  last_event_time_msc
  last_cross_direction
  regime_owner
```

### Crossing rule

For each scale:

- if midpoint >= anchor + gap: emit UP crossing;
- if midpoint <= anchor - gap: emit DOWN crossing;
- emit at most one new event per observed tick per scale;
- after the event, reset that scale's anchor to the observed causal price rather than retroactively emitting every skipped intermediate grid level.

This prevents a single price jump from manufacturing many same-price pseudo-opportunities.

## 4. Candidate direction

### Continuation owner

UP crossing -> BUY candidate.
DOWN crossing -> SELL candidate.

Current leading volatile/persistent research profile:

- gap approximately $2.375,
- hold approximately 120 seconds.

### Reversion owner

UP crossing -> SELL candidate.
DOWN crossing -> BUY candidate.

Current quiet-state research scales:

- $4
- $5
- $6
- $8
- $10

The exact scale-to-lifecycle mapping is not yet translation-locked and must be verified from the next reproducibility checkpoint before executable MQL5 code.

## 5. Regime ownership

The R1 research bank used a causal native-market spread/volatility proxy with a threshold near 0.60 to route between quiet/reversion and volatile/continuation ownership.

MT5 translation requirements:

- compute the chosen proxy only from information available at the event tick,
- no future bar completion,
- no future outcome labels,
- maintain the threshold as an external parameter until neighborhood validation is finished.

The current threshold is **research provisional**.

## 6. Event de-duplication

The HF system must prevent multi-scale correlated events from becoming artificial trade inflation.

Required behavior:

- order candidate events by time,
- apply a short clock-level de-duplication/arbitration window,
- preserve one owner for materially simultaneous correlated candidate clocks,
- record rejected duplicates for parity diagnostics.

The January checkpoint reports a 1-second de-duplication stage and 29,540 unique candidate trades. The exact winner-selection policy inside that window must be explicitly reconstructed and frozen before MQL5 certification.

Until then, this is a **translation blocker**, not permission to guess.

## 7. Lifecycle

R1 uses fixed research horizons, not an unlimited grid hold.

For the leading continuation specialist:

- entry on current executable side,
- maximum lifecycle approximately 120 seconds,
- mark/exit using the opposite executable quote side.

Quiet reversion specialists use longer bounded horizons in current research. Those exact per-scale horizons remain to be formally frozen.

No Martingale.

## 8. Execution-side semantics

For live MT5:

- BUY enters at Ask and exits/marks at Bid;
- SELL enters at Bid and exits/marks at Ask;
- use actual broker spread and symbol contract details.

For Python/DELTA-comparable research only:

- signal clock remains native Dukascopy,
- execution may use `DUKAS_COINEXX_LIKE_P75`,
- current P75 implementation models approximately $0.20-$0.21 session-dependent spread.

Do not synthesize P75 quotes inside a live EA.

## 9. Cost accounting

Research parity must explicitly account for:

- spread through executable Bid/Ask,
- configured round-trip/side cost convention,
- any later verified commission,
- slippage sensitivity when added.

Do not infer profit from midpoint markout.

## 10. High-volume preservation rule

The specialist router must not improve apparent quality merely by deleting most opportunities.

R1 design objective:

- preserve approximately >=1,000 unique candidate events/day as a research floor,
- improve directional ownership/lifecycle inside that population,
- measure all rejected candidates and reasons.

This floor is a research objective, not a broker order-rate promise.

## 11. State-machine pseudocode

```
on_tick(tick):
    update_causal_market_state(tick)

    for scale in virtual_grid_scales:
        event = scale.detect_crossing(tick)
        if event:
            regime = regime_router(causal_state)
            candidate = specialist_route(event, regime)
            queue(candidate)

    unique = deduplicate_and_arbitrate(queue, short_time_window)

    for candidate in unique:
        if execution_and_risk_gate(candidate):
            open_specialist_trade(candidate)

    manage_open_specialist_lifecycles(tick)
```

## 12. Required telemetry

Every emitted candidate should log:

- event time_msc,
- grid scale,
- anchor before crossing,
- observed crossing price,
- crossing direction,
- regime state/proxy,
- specialist owner,
- proposed BUY/SELL,
- duplicate/arbitration disposition,
- executable Bid/Ask,
- spread,
- lifecycle profile,
- exit time,
- exit reason,
- gross/net PnL,
- MFE/MAE,
- concurrent-position state.

## 13. Translation blockers before production code

1. Exact R1 de-duplication winner-selection rule must be frozen.
2. Quiet-regime per-scale lifecycle mappings must be frozen.
3. Jan-Jul durability must be completed for the HF architecture.
4. Portfolio concurrency/floating-equity DD must be measured, not only event-sequence DD.
5. Session/news/event-aware structure remains deferred.
6. Coinexx-native MT5 Every tick based on real ticks certification remains separate.
7. Main DELTA is not modified by this branch.

## 14. Rollback

If later GRID-HF refinement fails, this R1 specification remains the rollback checkpoint for the high-volume virtual-grid architecture.
