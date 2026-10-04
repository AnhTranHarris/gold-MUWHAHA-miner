# DELTA-A GRID-HF R2 — Directional Ownership Checkpoint 01

## Status

**INTERIM RESEARCH BREAKTHROUGH — NOT MT5 AUTHORIZED**

This checkpoint advances the preserved GRID-HF R1 architecture without modifying main `delta`.

## Objective

Improve directional ownership and lifecycle quality while preserving the high-volume event floor. No event is deleted by the selected router.

## Deterministic de-duplication

For R2 screening, candidate events are sorted chronologically and the first eligible event is retained inside a rolling 1-second cluster. No future payoff is used to choose the retained event.

January result under this explicit rule:

- 39,253 unique candidate events
- approximately 1,354 events/day across the observed January event span

## R1 comparable baseline under the same R2 de-dup rule

Using the inherited R1 ownership/lifecycle on the same retained event clocks:

- events: 39,253
- net: +$3,096.19
- average/event: +$0.07888
- PF: 1.01861
- positive outcome fraction: 49.293%
- closed-event-sequence DD: approximately $3,380.99

## Selected R2 router

Causal rule:

- if native Dukascopy quoted spread at the event tick is **<= $0.90**, assign **REVERSION** ownership with a **600-second** bounded lifecycle;
- if native Dukascopy quoted spread is **> $0.90**, assign **CONTINUATION** ownership with a **180-second** bounded lifecycle.

Execution economics remain on the frozen `DUKAS_COINEXX_LIKE_P75` research surface.

No event filtering is applied.

## January result

- events: **39,253**
- net: **+$5,428.69**
- average/event: **+$0.13830**
- PF: **1.02874**
- positive outcome fraction: **49.892%**
- closed-event-sequence DD: **approximately $2,878.93**
- early-January half net: **+$66.99**
- later-January half net: **+$5,361.70**

Relative to the comparable R1 baseline:

- event count: unchanged
- net: approximately **+75%**
- average/event: approximately **+75%**
- PF: improved
- sequence DD: reduced by approximately **15%**
- early January changed from negative under several static ownership rules to slightly positive

## Neighborhood evidence

Nearby thresholds around $0.90-$1.05 and continuation lifecycles around 180-300 seconds also remain positive. The selected rule is preferred because it is simpler and offers a favorable net/DD tradeoff.

## Rejected complexity

A three-regime spread/lifecycle router was screened. It did not improve the selected rule enough to justify additional state complexity.

A causal online linear owner using delayed completed outcomes was also screened. It failed to improve the static causal router robustly and is not promoted.

## Remaining limitations

- Profitability remains concentrated in late January.
- The current result is event-sequence economics, not a fully constrained overlapping portfolio.
- Jan-Jul durability is not yet established for R2.
- Session/news/event-aware structure remains deferred.
- PF remains far below historical R9 SYNTH.
- No MQL5 production code is authorized.

## Next unit

Continue GRID-HF R2 with routing families that preserve the approximately 1,000+/day event floor while improving directional ownership and reducing late-month concentration.
