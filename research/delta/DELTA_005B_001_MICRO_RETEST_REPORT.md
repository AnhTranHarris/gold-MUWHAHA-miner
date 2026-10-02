# DELTA 005B-001 — Micro-Retest / Reclaim Specialist

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Grid:** 27 causal retest/reclaim configurations  
**August:** not accessed

## Finding

The retest specialist does not recover the activity removed by DELTA_005A.

The highest-activity configuration used a $0.05 retest band, zero reclaim buffer, and 1-second timeout. It produced 13,856 trades and 6,280 wins, only 82.47% of the Stage-A parent trade count and 1,412 fewer trades than the 005A sign-flow anchor.

Of those 13,856 trades, only 299 were 005B retest entries, with 133 wins (44.48%).

The configuration reduced gross-loss magnitude 19.89% and balance drawdown 22.31% versus the Stage-A parent, but this improvement remains tightly coupled to fewer trades/wins.

## Full-grid interpretation

Across the 27 preregistered combinations:
- trade retention ranged about 74.96% to 82.47%;
- retest-sleeve win rate ranged about 39.4% to 44.5%;
- extending timeout from 1s to 3s/5s reduced activity further;
- longer delay improved headline loss metrics mainly by keeping more opportunities out of the market.

No parameter neighborhood restored the activity removed by 005A.

## Initial-hold finding

The 1/3/5/10/15-second survival curve remains effectively unchanged from the parent/005A surfaces. Retest confirmation therefore does not solve the initial-persistence problem.

## Leverage diagnosis

The weak component is the **continuation thesis for the rejected first-touch population**, not the exact retest band.

The data supports a structural change: test whether that population is better owned by a **failed-break / sweep-reversal specialist**.

## Decision

Do not continue local retest-band or timeout tuning.

Proceed to `DELTA_005C_001_FAILED_BREAK_REVERSAL`.

Temporary analysis:
https://docs.google.com/spreadsheets/d/1V-VHkj1jYPXebOtGcPVlhc81cvuqV4Q7pTl8ZzU37SM/edit?usp=drivesdk
