# DELTA 005J-001 — State-Conditioned Initial Protection

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 54  
**August:** not accessed

## Objective

005J tested whether the 005H breathing-room breakthrough should be applied only to the accepted-consolidation state discovered in 005E rather than globally.

The original R9-style entry and hard stop remained unchanged.

At 1 second, positions were classified by current boundary acceptance and completed-S1 range. Accepted positions temporarily used a higher trail-activation threshold; all others retained the R9 +$0.10 activation.

## Best net region

The best net cell used:
- S1 range ceiling $1.00;
- minimum boundary acceptance $0.00;
- accepted-state activation +$0.30;
- protection end 10 seconds.

Results:
- 16,753 trades;
- 7,149 winners;
- 97.25% winner retention;
- net -$3,730.61;
- net-loss improvement 1.00%;
- gross-loss change -2.19% (worse);
- 5s survival +3.40pp;
- 10s survival +4.52pp;
- 15s survival +1.43pp.

## Best persistence region

The strongest persistence cell used the same broad state but +$0.50 activation through 10 seconds:
- 16,733 trades;
- 7,057 winners;
- 96.00% winner retention;
- net -$3,738.25;
- 5s survival +4.88pp;
- 10s survival +7.16pp;
- 15s survival +1.80pp;
- gross-loss magnitude worsened 2.85%.

## Matrix findings

Range ceiling is the largest state-selection lever.

$0.50 is too narrow to matter at system scale.

$0.75 produces modest persistence lift.

$1.00 provides the broadest useful support, roughly five thousand accepted-state classifications.

The $0 vs $0.05 boundary-acceptance buffer is low leverage and should be removed from subsequent grids.

Longer conditioned protection windows produce more persistence, but accepted-state win rate falls toward roughly 40–42% as protection is loosened.

This means accepted consolidation predicts that an original position can survive, but does not by itself identify which longer-lived positions will become final winners under the frozen downstream lifecycle.

## Decision

005J is not promoted.

It improves on global loosening by preserving activity, but best net improvement is still only ~1%, far below the creative-escalation threshold.

Do not add additional static state thresholds.

The next initial-protection experiment should condition trailing on **path evolution / favorable excursion**, not one static one-second snapshot.

Temporary 2D matrix workbook:
https://docs.google.com/spreadsheets/d/1fP3FXWAiWEs_MSy9ScmMpQbGJFIc0ls1VnT1aoF98eE/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
