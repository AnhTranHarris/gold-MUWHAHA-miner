# DELTA 005C-001 — Failed-Break Reversal Screen

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Window:** Stage-A GOV-012  
**August:** not accessed

## Summary

DELTA_005C tested whether first-touch opportunities rejected by the mild 005A continuation owner become useful when treated as opposite-side failed-break reversals.

The reversal sleeve is materially more promising than the 005B retest continuation sleeve, but it is not a complete solution.

At the highest-activity geometry (failure depth $0.00, opposite-flow threshold 0.00, timeout 1s), the composite retained 93.78% of 005A-anchor trades and 93.84% of winners. Net-loss magnitude improved 6.85%, gross-loss magnitude 6.42%, and drawdown 6.85%.

The cleanest reversal-rate geometry (depth $0.05, opposite-flow 0.20, timeout 1s) produced 518 reversal trades with a 48.26% win rate while retaining 92.08% of parent activity.

The strongest loss/risk geometry (depth $0.05, opposite-flow 0.20, timeout 5s) improved net-loss magnitude 16.13%, gross loss 14.82%, and drawdown 16.12%, but retained only 86.12% of trades and 86.86% of winners.

## Matrix diagnosis

Timeout is the strongest parameter lever: longer failure windows capture more reversal entries and improve loss metrics, but also suppress direct continuation activity.

Failure depth has medium leverage: deeper $0.05 failure produces somewhat cleaner economics with fewer reversals.

Opposite-flow threshold has low leverage. Raising it from 0 to 0.20 does not create a dramatic improvement.

Reversal-sleeve win rate remains roughly 45.5–48.3%. This is better than the original REAL-like directionality but far below the desired high-quality state.

## Initial-hold diagnosis

5s and 10s survival improve only by tenths of a percentage point across the grid.

Therefore entry rerouting has now been tested through:
- direct tick-flow continuation;
- micro-retest/reclaim continuation;
- failed-break reversal.

None materially repairs the first-seconds persistence problem.

## Decision

Preserve 005C as a complementary reversal specialist candidate.

Stop expanding entry filters for the next bounded unit.

The next high-leverage intervention is an explicit **initial-hold acceptance / early-invalidation state** applied after entry while the mature R9-style hold/exit/high-profit objective remains frozen.

Temporary 2D matrix analysis:
https://docs.google.com/spreadsheets/d/1q8MVbzpIuQQYvx3S4UAQMIUmLzR7sEF0cuMpUeG3a5Q/edit?usp=drivesdk
