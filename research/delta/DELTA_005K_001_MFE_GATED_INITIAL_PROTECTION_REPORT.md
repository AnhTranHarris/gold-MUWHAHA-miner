# DELTA 005K-001 — MFE-Gated Initial Protection Before Delayed Trail

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 9  
**August:** not accessed

## Objective

005K attempted to preserve the 005H delayed-trailing survival breakthrough while repairing some of its gross-loss penalty.

The original R9 entry and $0.30 hard stop remained unchanged.

Continuous $0.03 trailing stayed delayed until +$0.30 favorable excursion.

Before that, 005K allowed one MFE-triggered stop move.

## Findings

A one-time fixed protective lock creates a clear Pareto frontier, but no tested cell dominates 005H on net.

### Best preservation of the 005H survival breakthrough

Trigger +$0.25 / lock +$0.05:
- 16,610 trades;
- 6,106 winners;
- 99.59% of 005H winners retained;
- gross-loss magnitude improves 1.81% vs 005H;
- net is 0.51% worse than 005H;
- 5s survival gives back only 1.08pp vs 005H;
- 10s gives back 1.27pp;
- 15s gives back 1.38pp.

### Best balanced gross-loss recovery

Trigger +$0.20 / lock +$0.05:
- 16,641 trades;
- 6,146 winners;
- 100.24% of 005H winner count;
- gross-loss magnitude improves 4.32% vs 005H;
- net is 0.23% worse than 005H;
- 5s survival gives back 2.70pp;
- 10s gives back 3.15pp.

### Maximum gross-loss recovery

Trigger +$0.15 / lock +$0.05:
- 100.75% of 005H winners;
- gross-loss magnitude improves 6.91% vs 005H;
- but 5s/10s survival give back roughly 4.79pp / 5.55pp.

## Leverage diagnosis

The later the one-time protection trigger, the more of the 005H persistence breakthrough survives.

The +$0.05 lock consistently preserves winner count better than the tested -$0.10 and $0.00 locks.

However, every cell remains worse than the pure 005H +$0.30 delayed-trailing cell on net.

Therefore one fixed trigger plus one fixed lock is not a sufficiently expressive protection formula.

## Decision

005K is not promoted as a replacement for 005H.

It proves that path-conditioned protection can recover some gross loss without necessarily destroying winner count, but the mechanism must become **multi-stage** rather than one-time.

Next unit:
`DELTA_005L_MULTI_STAGE_INITIAL_PROTECTION`

The next experiment should test a small number of explicitly designed protection ladders rather than another dense parameter grid.

Temporary 2D matrix workbook:
https://docs.google.com/spreadsheets/d/1GmA0TwTeWQibZqFpQOh1p7LoaIdRA3mEIbb-wK7qKB0/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
