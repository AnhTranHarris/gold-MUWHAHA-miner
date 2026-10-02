# DELTA 005D-001 — First-Seconds Acceptance / Early Invalidation

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation only  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Window:** GOV-012 Stage-A  
**August:** not accessed

## Result

DELTA_005D isolated the initial-hold problem by leaving the original R9-style entry opportunity set intact and allowing an early invalidation only during the first 1/3/5 seconds.

The rule required all three conditions: loss of the frozen entry boundary, both 250ms and 1s tick flow flipping against the trade, and completed-S1 efficiency falling below a maintenance floor.

The best net cell was guard 5s, boundary-loss depth $0.02, maintenance efficiency floor 0.50:
- 16,830 trades;
- 7,063 winners;
- 1,310 early invalidations;
- all 1,310 invalidations were losing trades;
- net -$3,756.61 vs parent -$3,768.25;
- gross loss -$5,272.30 vs parent -$5,343.02;
- max balance drawdown $3,758.19 vs parent $3,769.83;
- net-loss improvement only 0.31%;
- gross-loss improvement 1.32%;
- drawdown improvement 0.31%;
- winner retention 96.08%;
- 5s survival deteriorated 4.89 percentage points;
- 10s survival deteriorated 2.36 percentage points.

## Matrix diagnosis

The 2D heatmaps show:

- guard duration is the largest lever, but a longer guard mainly increases early exits and destroys persistence;
- boundary-loss depth has very low leverage;
- a higher maintenance-efficiency floor increases gross-loss reduction but also destroys winners and hold survival;
- no broad parameter neighborhood produces a meaningful net/DD gain while improving initial-hold survival.

The average 5s and 10s survival deltas are negative across the grid.

## Formula-level conclusion

This rule is aligned with loss cutting but not with the owner's Entry + Initial-Hold objective.

Even though the best cell correctly identified losing positions, it did so too late or with too little saved loss to create meaningful economics, while also disrupting trades that would otherwise survive.

The result is far below the +10 percentage-point creative-escalation threshold.

## Decision

Do not run another local invalidation-threshold sweep.

The next unit is a structural discovery step: **DELTA_005E Initial-Hold Forensic Census**.

005E will observe only causal right-edge state at fixed horizons after the original R9-style entry (250ms/500ms/1s/2s/3s). Later 5s/10s survival or trade result may be used only as labels for retrospective discovery, never as candidate inputs.

The purpose is to identify which observable interactions actually distinguish durable initial holds from failures before writing another deterministic rule.

Temporary 2D matrix workbook:
https://docs.google.com/spreadsheets/d/1186BfUL6fr6imDBQ_7P2wwts7bioVfdHNrwxo449rdY/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
