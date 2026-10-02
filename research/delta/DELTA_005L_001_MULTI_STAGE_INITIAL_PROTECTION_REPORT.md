# DELTA 005L-001 — Multi-Stage Initial Protection

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Architectures:** 7  
**August:** not accessed

## Objective

005L tested whether staged protection sequences could preserve the 005H initial-hold breakthrough while recovering more gross loss than the one-time 005K locks.

## Result

No staged architecture dominates 005H.

### EXTENDED_BREATH

This architecture slightly improved net and survival versus 005H:
- net improvement +0.24%;
- gross-loss improvement +1.32%;
- 5s survival +2.18pp;
- 10s survival +2.07pp;
- 15s survival +1.21pp.

But winner retention fell to only 80.43% of 005H.

### EXTENDED_BALANCED

- net +0.11% vs 005H;
- gross loss +1.72%;
- 5s survival +0.56pp;
- 10s survival +0.18pp;
- winner retention 85.68%.

Still too destructive.

### EXTENDED_PROTECTIVE

- nearly flat net vs 005H;
- gross loss +3.12%;
- winner retention only 82.07%;
- survival slightly worse.

## Leverage diagnosis

The experiment confirms that repeated stop tightening can reduce loss, but it also converts a large population of recoverable 005H paths into early exits.

The more aggressive the staged protection sequence becomes, the more winner count deteriorates.

That means further stop-level ladders are the wrong next axis.

## New high-leverage axis

Public MQL5 trailing implementations expose not only activation and distance, but also **step/frequency**: how far price must advance before the trail is moved again.

R9 currently ratchets the stop whenever a new tighter $0.03 trail is available.

This frequency dimension has not yet been tested.

The next unit should keep the 005H high-leverage +$0.30 activation and $0.03 distance, but require a minimum favorable-price advance between successive trail updates.

## Decision

005L is not promoted.

Next unit:
`DELTA_005M_TRAIL_STEP_FREQUENCY`

Temporary architecture heatmap workbook:
https://docs.google.com/spreadsheets/d/1EgQDfNLrChF-ZzdG_Ou8MxsYG4nIWsvT1KBwM82xWl0/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
