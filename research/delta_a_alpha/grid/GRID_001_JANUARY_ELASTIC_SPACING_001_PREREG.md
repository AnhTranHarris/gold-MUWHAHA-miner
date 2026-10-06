# GRID-001 January Elastic Spacing 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_ELASTIC_SPACING_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Can causal volatility-normalized lattice spacing stabilize January event density and improve directional opportunity quality without collapsing throughput?

## Frozen environment

- Full January 2026 canonical Dukascopy XAUUSD ordered ticks.
- `DUKAS_COINEXX_LIKE_P75`.
- Same virtual source-inspired event-stack semantics.
- No physical positions.
- No Martingale.
- No session/news/specialist inputs.
- Shadow evaluation remains fixed: 0.01 economics, $1 TP, $1 adverse bound, 5-minute horizon, $0.02 round-trip commission.
- Same chronological discovery/validation split as Event-Label Lab 001.

## Causal volatility source

Build completed M1 bars from the modeled P75 midpoint.

For each new minute:
- compute the completed bar true range;
- maintain ATR(14) as the simple mean of the previous 14 completed M1 true ranges;
- the current incomplete M1 bar cannot affect the gap.

This is deliberately simple and reconstructible.

## Gap update contract

Base floor: $1.00.

Candidate:

`raw_gap = max($1.00, alpha * ATR14_M1)`

Then:
- clamp to [$1.00, $8.00];
- quantize to $0.25 increments;
- update at most once per completed M1 bar;
- apply 10% hysteresis: if the new gap differs by less than 10% from the active gap, retain the prior gap.

Existing virtual event anchors retain the gap that created them for their virtual one-gap reversion/removal test. New events use the current active gap.

## Small structural matrix

Only three alpha values:

- 0.25
- 0.50
- 1.00

The fixed-$1 Event-Label Lab is the baseline.

No threshold optimizer.

## Required metrics

For each alpha:
- total events;
- events/active day;
- daily event count min/median/max;
- coefficient of variation of daily event count;
- max virtual stack depth;
- median active gap;
- gap distribution;
- always-MR shadow economics;
- always-CONT shadow economics;
- impossible per-event directional oracle economics;
- discovery and validation splits separately;
- both-directions-negative percentage.

## Advancement rule

Elastic geometry is useful only if it:
1. materially reduces the fixed-$1 event-density explosion;
2. retains at least R9-scale opportunity supply after later selective routing;
3. does not materially destroy oracle opportunity quality;
4. behaves qualitatively similarly in discovery and validation;
5. shows a broad structural effect across more than one alpha.

If only one isolated alpha looks good, do not tune around it.

A successful geometry family becomes the base event clock for the next direction/recovery work.

August sealed. Main delta read-only. MQL5 unauthorized.
