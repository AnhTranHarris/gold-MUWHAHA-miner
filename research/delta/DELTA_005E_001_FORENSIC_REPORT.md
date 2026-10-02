# DELTA 005E-001 — Initial-Hold Causal Forensic Census

**Status:** COMPLETE DISCOVERY — NOT A CANDIDATE  
**Mode:** historical causal forensic analysis  
**Focus:** Entry + Initial-Hold  
**Stage-A ticks:** 4,205,709  
**Parent trades:** 16,801  
**Causal snapshots:** 82,774  
**August:** not accessed

## Method

The original R9-style Stage-A entry set was replayed unchanged.

For each trade still open at 0/250/500/1000/2000/3000 ms, DELTA froze only right-edge information available by that observation time. Future 5s/10s/15s survival was used only as a retrospective label.

Features included boundary acceptance, tick flow, completed-S1 efficiency/range/turns, efficiency change, causal MFE/MAE, path efficiency, aligned tick fraction, extreme renewal and session state.

All matrix bins were fixed independently of label outcomes.

## First high-leverage discovery: accepted consolidation

At 1 second, the overall open-position population had:
- 51.94% 5s survival;
- 26.41% 10s survival.

When completed-S1 range had compressed below $0.50 and the boundary had not been lost:
- support = 342;
- 5s survival = 73.39%;
- 10s survival = 48.25%;
- lift = +21.45pp / +21.84pp.

The broader $0.50–$0.75 completed-S1 range with boundary held had:
- support = 3,464;
- 5s survival = 68.24%;
- 10s survival = 39.29%.

The effect persists at 2s and 3s.

## Early cooling is not automatically failure

At 250ms, a completed-S1 efficiency decline of -0.30 to -0.10 combined with deep boundary acceptance (> $0.10) had:
- support = 481;
- 65.70% 5s survival;
- 37.84% 10s survival;
versus 44.78% / 22.76% horizon baselines.

This directly falsifies the assumption embedded in 005D that falling efficiency during the first seconds is necessarily failure.

A successful break can impulse, establish acceptance, then cool/compress.

## Flow interpretation

Several broad matrices show that negative post-entry flow can coexist with higher survival when the structural boundary remains accepted.

Therefore flow is more useful as an ownership/router input than as a universal persistence requirement.

This explains why DELTA_005A improved losses mainly by deleting activity rather than creating better initial holds.

## Recovery opportunity from the 005A-rejected pool

For trades whose entry snapshot failed immediate sign-flow confirmation, there were 5,340 observations still open at 1 second.

Overall rejected-pool survival:
- 52.53% at 5s;
- 27.43% at 10s.

Within that rejected pool:

### Range < $0.50, boundary held
- support 169;
- 71.60% 5s survival;
- 47.93% 10s survival.

### Range $0.50–$0.75, boundary held
- support 1,517;
- 69.08% 5s survival;
- 40.41% 10s survival.

This is a broad recoverable population, not a tiny lucky cell.

## Formula-level conclusion

The first meaningful Entry + Initial-Hold structure discovered by DELTA is:

**IMPULSE -> ACCEPTED BOUNDARY -> MICRO-CONSOLIDATION / COOLING**

rather than:

**IMPULSE -> CONTINUOUS HIGH FLOW / HIGH EFFICIENCY**

That changes the architecture.

## Next candidate

DELTA_005F should test specialist recombination:

1. Immediate continuation owner:
   preserve the mild 005A sign-flow entry for opportunities with immediate directional ownership.

2. Delayed accepted-consolidation owner:
   for the 005A-rejected pool, wait approximately 1 second and enter continuation only if the original boundary remains accepted and completed-S1 range has cooled into a preregistered acceptance band.

The first 005F grid should center on broad discovered regions ($0.50 / $0.75 / $1.00 range ceilings and boundary-held requirements), not optimize a single forensic cell.

Mature Holding-Trade + Exit + High-Profit remains frozen.

## Durable matrix workbook

https://docs.google.com/spreadsheets/d/1Ngbap0ordQVpEnrBdrxoatLXm9uAMexiJUUD8ZbL9lQ/edit?usp=drivesdk
