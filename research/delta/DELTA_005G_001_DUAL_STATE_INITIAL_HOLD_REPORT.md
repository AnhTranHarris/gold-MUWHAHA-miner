# DELTA 005G-001 — Dual-State Initial-Hold Validator

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 48  
**August:** not accessed

## Result

005G preserved every original R9-style entry, then required a first-seconds ownership state before allowing the position to continue.

A trade could be validated by:
1. direct continuation ownership from 250ms/1000ms aligned tick flow; or
2. accepted-consolidation ownership at the validation horizon.

If neither state existed, the position closed early.

The best net cell (250ms validation, $0.50 S1-range ceiling, NEVER_LOST) produced:
- 16,895 completed trades;
- 6,408 winners;
- 13,152 direct validations;
- 33 consolidation validations;
- 2,934 early invalidations;
- net -$3,711.33;
- gross loss -$5,085.92;
- max balance drawdown $3,712.91;
- net-loss improvement only 1.51%;
- gross-loss improvement 4.81%;
- drawdown improvement 1.51%;
- winner retention 87.17%;
- 5s survival deteriorated 7.80pp;
- 10s survival deteriorated 4.12pp.

## Matrix diagnosis

Earlier validation cuts more losses but destroys substantially more winners and initial-hold survival.

Later validation preserves winners but has almost no economic effect.

Range ceiling produces the same harmful trade-off: tighter consolidation definition cuts more losses but eliminates more future winners.

CURRENT_HELD vs NEVER_LOST and $0 vs $0.05 acceptance buffers are low-leverage distinctions.

## Conclusion

The 005E forensic state is useful as a descriptive persistence state but should not be used as a hard binary keep/kill rule.

The campaign has now tested:
- entry-flow filtering;
- retest continuation;
- failed-break reversal;
- ER/flow early invalidation;
- accepted-consolidation delayed entry;
- accepted-consolidation hard hold validation.

None solves the initial-hold problem at the required magnitude.

## New leverage direction

The next candidate moves away from state gating and tests the **mechanics that may be terminating otherwise valid trades**.

R9 activates a fixed trailing stop after only +$0.10 favorable movement and trails only $0.03 behind price. Community MQL5 sources explicitly warn that tight fixed trailing can stop breakout trades before they have room to develop and show reconstructible alternatives including delayed activation, periodic trailing and ATR/volatility-adaptive trailing.

DELTA_005H will therefore test an **initial trailing shield** while leaving the mature trade/exit/high-profit phase frozen.

Temporary matrix workbook:
https://docs.google.com/spreadsheets/d/12VclDyjItrZ_OjsnCefxGUBE1PV1IwzaDsvgmyjMyxY/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
