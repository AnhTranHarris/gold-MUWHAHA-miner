# DELTA 005H-001 — Initial Trailing Shield

**Status:** COMPLETE — RESEARCH BREAKTHROUGH / NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 20  
**August:** not accessed

## Control parity

The 0ms shield / $0.10 trail-activation cell reproduces the Stage-A parent:
- 16,801 trades;
- 7,351 winners;
- $1,574.77 gross profit;
- -$5,343.02 gross loss;
- -$3,768.25 net;
- $3,769.83 max balance drawdown;
- 6.712s average hold.

## Breakthrough

R9's early fixed trailing is a genuine Initial-Hold bottleneck.

The 0ms shield / $0.30 activation cell produced:
- 16,578 trades;
- 6,131 winners;
- $2,377.80 gross profit;
- -$6,050.23 gross loss;
- -$3,672.43 net;
- $3,673.59 max balance drawdown;
- 9.027s average hold;
- +11.01pp 5s survival;
- +10.69pp 10s survival;
- +8.50pp 15s survival.

The persistence gain is broad and monotonic across neighboring activation values, not an isolated lucky cell.

## Important collateral effect

Looser early trailing increases gross profit and survival, but gross loss also rises and final winning-trade count falls.

This is not evidence that the Initial-Hold discovery is false.

It shows that more trades are successfully surviving the first seconds, but the unchanged downstream R9 lifecycle often converts those longer-lived positions into later hard-stop/max-hold losses rather than harvesting the additional favorable excursion.

That is exactly the separate Holding-Trade + Exit + High-Profit problem the owner has deferred.

## Formula-level leverage

Highest leverage:
- trail activation threshold.

Secondary leverage:
- early shield duration.

Long 5s/10s shields are too blunt. They produce very large survival gains but unacceptable winner/gross-loss deterioration.

## Next refinement

DELTA_005I will keep the baseline +$0.10 activation but give the trade a wider **early trail distance** for only a short initial window, then revert to the original $0.03 trail.

This tests whether we can retain the newly discovered breathing-room benefit without permanently weakening protection.

Community provenance remains:
- https://www.mql5.com/en/articles/23882
- https://www.mql5.com/en/articles/23618
- https://www.mql5.com/en/articles/16705

Temporary matrix workbook:
https://docs.google.com/spreadsheets/d/1SWEzgzBpfgYxMyc2LMKY68qEmxqND2z-iMrlPygEF-Y/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
