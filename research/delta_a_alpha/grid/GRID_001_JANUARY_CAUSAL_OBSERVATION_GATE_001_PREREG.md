# GRID-001 January Causal Observation Gate 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_CAUSAL_OBSERVATION_GATE_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Can a grid crossing become an **observation trigger** instead of an immediate order, so that a short causal post-crossing path reveals whether the event is continuation, reclaim/mean-reversion, or ambiguous?

## Frozen environment

- Full January 2026 canonical Dukascopy XAUUSD ticks.
- `DUKAS_COINEXX_LIKE_P75`.
- Same virtual source-inspired event clock from Event-Label Lab 001.
- Fixed 0.01 economics.
- No Martingale.
- No physical multi-position grid.
- No session/news/specialist features.

## Probe rule

At event time `t0`, record modeled midpoint `m0`.

Wait a fixed causal interval `W`. At the first tick at/after `t0+W`, record `mW`.

Direction-normalized probe:

`probe = event_direction * (mW - m0) / grid_gap`

where event_direction is +1 for upward crossing and -1 for downward crossing.

Interpretation:
- `probe >= C` -> CONTINUATION;
- `probe <= -C` -> MEAN_REVERSION / RECLAIM;
- otherwise -> ABSTAIN.

Physical entry, for research accounting, occurs only at the delayed executable Bid/Ask after the probe.

## Small fixed matrix

Wait:
- 250 ms
- 1 s
- 3 s

Confirmation threshold in grid-gap units:
- 0.00
- 0.10
- 0.25

Total variants: 9.

No optimizer.

## Delayed-trade contract

For accepted events:
- fixed 0.01;
- 1-gap TP;
- 1-gap hard adverse bound;
- 5-minute maximum horizon from delayed entry;
- $0.02 round-trip commission;
- unresolved trade force-exits at the last executable quote inside the horizon.

This is still an event-level mechanism screen, not the final account-level single-owner simulator.

## Split

Reuse the frozen Event-Label Lab split:
- first 2/3 of January ticks = discovery;
- final 1/3 = internal validation.

## Required metrics

For each of 9 variants:
- accepted trades;
- acceptance percentage;
- trades/active event day;
- MR vs CONT share;
- net / gross profit / gross loss;
- PF;
- expected payoff;
- win rate;
- discovery and validation metrics separately.

## Advancement rule

The observation-gate family advances only if:
- the same broad wait/confirmation neighborhood improves both discovery and validation;
- validation PF materially exceeds always-continuation baseline PF 0.7866;
- gross loss per event falls;
- acceptance remains high enough to preserve meaningful system-wide opportunity density;
- the result is not dependent on one isolated threshold.

A positive result here authorizes a physical single-owner/drawdown simulator next.

A negative result means the next mutation must change event semantics, not fine-tune these waits.

August sealed. Main delta read-only. MQL5 unauthorized.
