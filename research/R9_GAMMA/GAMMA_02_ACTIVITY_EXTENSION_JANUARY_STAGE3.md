# GAMMA-02 — January Activity / Extension Quality Stage 3

**Status:** COMPLETE JANUARY DISCOVERY CHECKPOINT — NOT PROMOTED  
**Previous checkpoint:** `f6a952f5944e9d8cc4b2b793fad0d7d2001ca7d9`

## Purpose

Refine the hour-specific Stage-2 continuation specialists using two causal dimensions that do not own direction:

1. favorable displacement / stair rank from the fresh M1 anchor;
2. recent tick-participation intensity.

Completed H4/H1/M15/M5 ALIGN4 remains the direction owner.

## NY 18:00 extension-quality discovery

The high-concurrency Stage-1 result was not uniform across stair events. Exact rank instrumentation reproduced the prior cap-32 result before diagnosis.

At a $0.15 favorable stair:
- ranks 1-10: about +$370 / 2,847 trades / low expectancy;
- ranks 11-17: about +$190 / 839;
- ranks 18-32: about +$1,683 / 1,001 / PF ~1.93 / +$1.68 per trade;
- ranks 20-32: about +$1,501 / 837 / PF ~1.98;
- ranks 24-32: about +$1,050 / 553 / PF ~2.02;
- ranks 37-40 turn negative.

Thus the raw cap-32 result was largely discovering a mature extension-quality band, not proving that 32 simultaneous positions were inherently required.

## Displacement gate

Replacing arbitrary event rank with causal displacement from the fresh M1 anchor preserved the edge at much lower exposure.

Representative frontier:
- cap 4: ~+$537 / 272 / PF ~2.09 / +$1.98 per trade;
- cap 8: ~+$1,081 / 590 / PF ~2.06;
- cap 12: ~+$1,609 / 801 / PF ~2.11;
- cap 16: ~+$2,159 / 1,081 / PF ~2.10.

The quality zone migrated to roughly **$3.0-$5.2 favorable displacement**, often strongest around **$3.5-$5.2**.

## Lifecycle compression

Inside the displacement-quality zone, the NY18 specialist remained positive at R9-like short lifecycles.

Examples:
- cap 8 / 5s: ~+$842 / 903 / PF ~2.33;
- cap 12 / 10s: ~+$1,546 / 1,142 / PF ~2.30;
- cap 12 / 20s: ~+$1,675 / 934 / PF ~2.45;
- cap 16 / 12s: ~+$2,078 / 1,325 / PF ~2.50 / DD ~207;
- cap 16 / 20s: ~+$2,246 / 1,263 / PF ~2.44.

The 12-20 second zone is therefore a serious R9-SYNTH-like lifecycle candidate.

## Tick participation is useful as intensity, not direction

Rolling prior-tick counts improved several hour-specific specialists while retaining large trade populations.

### London 11:00
- unfiltered: ~+$1,439 / 1,693 / PF 2.86
- 1-second count >=2: ~+$1,479 / 1,550 / PF 3.08
- 1-second count >=3: **~+$1,552 / 1,261 / PF 3.64 / +$1.23 per trade**

### Overlap 13:30-14:00
- unfiltered: ~+$3,719 / 2,376 / PF 3.42
- 1-second count >=4: ~+$3,795 / 2,156 / PF 3.70
- 1-second count >=6: ~+$3,790 / 1,818 / PF 4.01
- 3-second count >=19: **~+$3,848 / 1,475 / PF 4.71 / +$2.61 per trade**

### Overlap 14:00-15:00
- unfiltered: ~+$5,500 / 7,693 / PF 1.80
- 3-second count >=17: ~+$5,607 / 7,134 / PF 1.86
- 3-second count >=23: **~+$5,667 / 6,058 / PF 1.97 / +$0.94 per trade**

### NY 17:00-18:00
- unfiltered: ~+$2,796 / 8,005 / PF 1.42
- 3-second count >=12: ~+$3,062 / 7,063 / PF 1.50
- 3-second count >=16: **~+$3,128 / 6,108 / PF 1.56 / +$0.51 per trade**

The thresholds form broad neighboring plateaus rather than a single isolated optimum, but all are January discovery only.

## Architecture implication

The emerging stack is:

**completed HTF direction -> hour/auction-phase specialist -> fresh M1 favorable geometry -> activity-intensity throttle -> specialist lifecycle**

Tick rate does not predict direction. It decides whether an already-directional auction is active enough to participate.

## Important integration warning

A first shared-portfolio simulator failed the required one-specialist parity test. It reset the fresh-minute anchor one tick late when activating a specialist. Its combined results are invalid and MUST NOT be used.

Next work must:
1. make each integrated one-specialist run reproduce its standalone result exactly;
2. only then enable multiple specialists under one chronological exposure pool.

## Durability

Exact result files are persisted in Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/`

- `gamma02_hourly_refinements_stage3.json`
- `gamma02_tick_activity_stage3.json`
- `gamma02_ny_hour18_rank_stage3.json`
- `gamma02_ny_hour18_displacement_stage3.json`

## Hard target

R9 SYNTH remains the hard goal. These results are mechanisms for recovering correct-direction trade density; they are not authorization to accept modest progress or to implement an overfit January portfolio.

August remains SEALED.
