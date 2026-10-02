# DELTA 005F-001 — Direct Continuation + Accepted-Consolidation Recovery

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 48  
**August:** not accessed

## Question

005F tested whether the accepted-consolidation state discovered by 005E should be used as a delayed recovery entry for opportunities that did not receive immediate sign-flow ownership.

## Result

The recovery sleeve restores activity, but its own directional quality is weak.

The highest-activity cell (500ms fallback, $1.00 S1-range ceiling, CURRENT_HELD, zero acceptance buffer) produced:
- 16,075 trades;
- 7,194 winners;
- 1,886 recovery entries;
- 770 recovery wins;
- 40.83% recovery-sleeve win rate;
- 95.68% R9-parent trade retention;
- 97.86% R9-parent winner retention;
- net -$3,480.08;
- 7.65% net-loss improvement vs R9 Stage-A;
- +0.88pp 5s survival;
- +0.15pp 10s survival.

The best net/risk cell used a much tighter $0.50 range ceiling and only admitted 133 recovery entries. Its economics are effectively the 005A sign-flow anchor with almost no meaningful recovery sleeve.

Across the matrix, broader ceilings recover more entries but recovery win rate remains roughly 39–44%.

## Why the forensic signal did not transfer directly

005E measured accepted consolidation as a state of an **already-open original entry**.

005F instead used that same state to enter a **new position later**.

Those are not equivalent experiments.

By the delayed entry time:
- entry price is different;
- part of the favorable path may already have occurred;
- spread is paid later;
- the state that predicts survival of the original position does not necessarily predict edge for a new position opened at that moment.

This translation failure explains why the forensic survival lift did not become a high-quality recovery-entry sleeve.

## Leverage diagnosis

Low leverage:
- CURRENT_HELD vs NEVER_LOST;
- $0 vs $0.05 acceptance buffer.

Medium leverage:
- fallback timing.

High trade-off:
- range ceiling. $0.50 preserves economics but recovers almost nothing; $1.00 recovers activity but at low sleeve quality.

## Decision

Do not tune the delayed recovery-entry formula further.

The next candidate should use the accepted-consolidation signal in the role it was actually discovered for: **validation of an already-open initial hold**.

DELTA_005G will preserve original entries and test a dual-state first-seconds validator:
1. immediate direct-continuation ownership; or
2. accepted-consolidation ownership at a later validation horizon.

Positions with neither ownership state may be closed early, while the mature R9 lifecycle remains unchanged for validated positions.

Temporary matrix workbook:
https://docs.google.com/spreadsheets/d/1Cv_fiMOOr6Lmn1rmbjH8RP9DPZBoKNjj5zUSxoJLpLw/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
