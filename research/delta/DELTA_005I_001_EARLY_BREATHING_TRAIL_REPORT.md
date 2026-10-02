# DELTA 005I-001 — Early Breathing Trail Distance

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 20  
**August:** not accessed

## Result

005I kept the original +$0.10 trail activation and widened only the early trail distance for a bounded first-seconds window, then reverted to the original $0.03 trail.

The high-retention region is very mild:
- 5s window / $0.05 early trail;
- 16,791 trades;
- 7,208 winners;
- 98.05% winner retention;
- net -$3,759.73;
- gross loss -$5,355.44;
- +0.98pp 5s survival;
- effectively no 10s survival improvement.

The high-survival region is too destructive:
- 10s window / $0.20 early trail;
- +9.45pp 5s survival;
- +8.05pp 10s survival;
- only 76.36% winner retention.

## Leverage conclusion

Early trail distance is lower leverage than the trail-activation threshold discovered by 005H.

Global widening can create breathing room, but only long/wide settings materially change survival, and those settings destroy too many eventual winners.

Therefore another local distance sweep is not justified.

## Next structural recombination

Use the 005E accepted-consolidation state to decide **which trades receive looser early protection**.

Candidate concept:
- universal short observation/grace period;
- if the trade reaches an accepted-consolidation state, grant a temporary looser trail/activation;
- otherwise restore original R9 protection quickly;
- after the initial window, all trades revert to original R9 mature lifecycle.

This is DELTA_005J.

Temporary matrix workbook:
https://docs.google.com/spreadsheets/d/1Q0QvgdOX5Nx96YdnLeS9XaAosz7U_kBwx4hMXYdk2Ck/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
