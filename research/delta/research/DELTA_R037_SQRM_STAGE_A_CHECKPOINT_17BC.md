# DELTA R037 — Squeeze Release Momentum — Checkpoint 17BC

**Status:** COMPLETE / ADEQUATE SUPPLY / ECONOMIC FAIL / RETIRED  
**Parent:** R037_CORB_STAGE_A_SCREEN_CHECKPOINT_17BB  
**August:** SEALED | **MQL5:** NOT AUTHORIZED

One classic M1 BB/KC squeeze-release profile was tested: 20-period Bollinger 2.0, Keltner 20/1.5 using true-range mean, release when prior completed bar is squeezed and current completed bar is not, direction from the standard detrended 20-bar linear-regression momentum endpoint.

No length/multiplier/timeframe/duration/momentum-threshold/session/side/exit tuning.

## Result
- squeeze bars: **3,284**
- release signals/trades: **445**
- distinct days: **13**
- long / short: **219 / 226**
- wins: **210**
- GP / GL: **+$45.09 / -$127.59**
- direct net: **-$86.95**
- exits: **423 STOP / 22 MAX_HOLD**

## Decision
**RETIRE_SQRM_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

High event density is not the bottleneck; post-entry persistence remains the bottleneck.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
