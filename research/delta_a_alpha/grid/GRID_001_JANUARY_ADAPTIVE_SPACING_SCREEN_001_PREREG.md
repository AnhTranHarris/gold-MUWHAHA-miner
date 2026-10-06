# GRID-001 January Adaptive Spacing Screen 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_ADAPTIVE_SPACING_SCREEN_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Does the creator's fixed $1 grid over-sample January XAUUSD noise, and can a causal volatility-normalized lattice improve event quality without destroying useful opportunity density?

## Frozen environment

- Full January 2026 canonical Dukascopy XAUUSD ordered ticks.
- `DUKAS_COINEXX_LIKE_P75`.
- Same virtual source-inspired H1/48-bar event-stack semantics.
- No physical averaging.
- No Martingale.
- No loss-dependent sizing.
- No session/news/specialist features.

## Causal volatility input

Use **last completed M1 ATR(14)** computed from modeled Bid bars.

No current incomplete M1 bar is allowed in the ATR.

Gap updates only when a new completed M1 ATR becomes available.

Gap is quantized to $0.10. This acts as a basic hysteresis/noise control and prevents tick-by-tick geometry chatter.

## Structural variants

Baseline:
- fixed $1.00 gap from Event-Label Lab 001.

Adaptive families:
- A05: `gap = clamp(0.50 * ATR14_M1, $0.75, $5.00)`
- A10: `gap = clamp(1.00 * ATR14_M1, $0.75, $5.00)`
- A15: `gap = clamp(1.50 * ATR14_M1, $0.75, $5.00)`

After clamping, gap is rounded to the nearest $0.10.

No other multipliers are authorized in this unit.

## Variable-gap event semantics

For a new lattice event:
- the current causal adaptive gap determines the displacement required from the current virtual anchor;
- the event stores its own gap value;
- its virtual source-style reversion/TP pop uses that stored gap;
- later gap changes do not rewrite the geometry of an already-created event.

This follows the public adaptive-step principle that new entries/events receive new geometry while existing state is not mass-recentered.

## Dual-shadow label

Each event is evaluated as:
- mean reversion;
- continuation.

For both shadows:
- TP = event's own gap;
- adverse bound = event's own gap;
- horizon = 5 minutes;
- $0.02 round-trip commission;
- executable Bid/Ask;
- timeout force-exit at last executable quote.

## Frozen split

First 2/3 of January ticks = discovery.  
Final 1/3 = internal validation.

## Required comparison

For each spacing family:
- event count;
- events/active event day;
- gap distribution;
- always-MR metrics;
- always-CONT metrics;
- impossible direction-oracle metrics;
- both-directions-negative percentage;
- discovery/validation consistency.

## Advancement logic

Adaptive spacing is interesting if it materially improves one or more of:
- oracle expected payoff / PF;
- reduction of both-negative events;
- always-CONT or always-MR baseline quality;
- gross-loss intensity per event;
while retaining more than enough opportunity density for a future R9-scale system.

A lower event count is acceptable because the fixed $1 clock currently supplies roughly 4x+ R9 SYNTH trade velocity.

No physical execution promotion occurs from this screen alone.
