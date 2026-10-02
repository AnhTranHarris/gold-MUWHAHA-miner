# DELTA 005M-001 — Trail Ratchet Step / Frequency

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 20  
**August:** not accessed

## Result

005M kept the 005H breakthrough mechanics fixed:
- trail activation +$0.30;
- trail distance $0.03;
- hard stop $0.30;
- max hold 30s.

Only ratchet step and minimum trail-update interval changed.

### Best net cell
- trail step $0.05
- minimum update interval 500ms
- 16,564 trades
- 6,111 winners
- winner retention 99.67% vs 005H
- net -$3,661.62
- net-loss improvement 0.29%
- gross-loss improvement 0.07%
- drawdown improvement 0.29%
- 5s survival +0.73pp
- 10s survival +0.52pp
- trail moves reduced 32.47%

### Highest-survival cell
- trail step $0.15
- minimum update interval 1000ms
- winner retention 99.30%
- net-loss improvement 0.18%
- gross-loss improvement 0.13%
- 5s survival +1.32pp
- 10s survival +1.05pp
- 15s survival +0.62pp
- trail moves reduced 41.96%

## Matrix diagnosis

Both axes behave smoothly:
- longer minimum update interval reduces ratchet churn and slightly increases survival;
- larger price step between updates also slightly increases survival;
- useful cells preserve essentially all 005H winners.

However, the economic effect is small. Net, gross loss, and drawdown improve only by fractions of a percent.

## Decision

Trail ratchet step/frequency is a valid **secondary refinement** around the 005H breakthrough, not the next primary research lever.

Do not spend another cycle fine-tuning sub-intervals or intermediate step values.

Preserve 005H as the principal Initial-Hold breakthrough and retain a moderate ratchet-frequency option for later recombination.

Holding-Trade + Exit + High-Profit remains deferred.
