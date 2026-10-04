# DELTA R037 — Source-Default Turtle Soup — Checkpoint 17AZ

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR / RETIRED  
**Parent:** R037_BOSLS_STAGE_A_SCREEN_CHECKPOINT_17AY  
**August:** SEALED | **MQL5:** NOT AUTHORIZED

## Test
One completed-M5, source-default MetaQuotes Turtle Soup profile only: 20-bar reference extreme, minimum age 4 bars, one-bar sweep window, one close back inside, reversal body required, and sweep depth >=30 native points and >=2% of the lookback range.

No default tuning, timeframe sweep, side/session rescue, overlay, or exit retuning.

## Result
- signals/trades: **23**
- distinct days: **8**
- official wins: **11**
- gross profit: **+$2.32**
- gross loss: **-$7.02**
- direct net: **-$4.93**
- exits: **22 STOP / 1 MAX_HOLD**

The source-native depth/age filters sharply reduce noise but do not produce positive executable 30-second economics.

## Integrity
- prereg `ff80d0724f7a657f2fcd4b1b9ab4c5e6b1e5aca0`
- producer `19a0e42732e2d3f759b96de1b29ed323e32b5e8d`
- blob `d22d2dd225016f3292b94bc6c93e9628be76a5fb`
- producer SHA-256 `f89012c5f8070fed507c35a1a2629f7aa2b03a912e9cb295b22ca962dd3efa14`
- result SHA-256 `1e9fbd629fb03c3403564719c69d6d544b6ddfe17881e0f72bd21687e8ba3ba6`
- exact Git blob / canonical January / chronology / hard timeout / atomic output: PASS

## Decision
**RETIRE_TSO_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
