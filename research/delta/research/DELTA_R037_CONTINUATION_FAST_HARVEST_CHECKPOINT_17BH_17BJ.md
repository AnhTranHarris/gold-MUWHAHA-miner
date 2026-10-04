# DELTA R037 — Controlled-Pause Continuation Fast Harvest 17BH–17BJ

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR  
**Parent:** R037_PRICE_ACTION_FAST_HARVEST_CHECKPOINT_17BE_17BG  
**Surface:** native M1/M15 signals → DUKAS_COINEXX_LIKE_P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Test whether immediate continuation **after a controlled pause** provides the missing 30-second XAUUSD persistence that generic reversal patterns did not.

The batch was preregistered before code and contained three fixed profiles:

1. **17BH — M1 Three-Bar Play continuation**
2. **17BI — M15 Inside-Bar continuation baseline**
3. **17BJ — M15 Inside-Bar continuation with source-published XAU quality filters**

Preregistration commit:
`f5d82ec9e5b07f28e737b03dc4c907ce95731bbe`

Producer:
`research/delta/experiments/delta_r037_continuation_fast_harvest_17bh_17bj.py`

Producer commit:
`a43b574f9f4253f024add1cc222f5bff79ce5e0a`

Producer blob:
`85ee4e060bc35839396d84b4ed8262a13c000061`

Producer SHA-256:
`d22810f9fa96899598402f0df8f95ab9615f0fe78c16b397b6b41a798f26a675`

The local execution copy matched the committed Git blob exactly before official compute.

## Official Stage-A results

### 17BH — Three-Bar Play M1

- signals/trades: **34**
- distinct days: **13**
- wins: **19**
- gross profit: **+$4.87**
- gross loss: **-$7.49**
- direct net: **-$2.96**
- exits: 33 STOP / 1 MAX_HOLD

Supply passes, economics fail.

### 17BI — Inside-Bar M15 baseline

- raw inside-bar patterns: **132**
- qualified baseline patterns: **132**
- expired without Mother-Bar boundary trigger: **81**
- executable trades: **51**
- distinct days: **11**
- wins: **20**
- gross profit: **+$10.26**
- gross loss: **-$16.96**
- direct net: **-$7.21**
- exits: 48 STOP / 3 MAX_HOLD

Supply passes, economics fail.

### 17BJ — Inside-Bar M15 source-published quality filters

Frozen pre-result quality filters:
- Main-Bar body >= 80% of Main-Bar range
- Inside-Bar range <= 50% of Main-Bar range
- Main-Bar range >= 0.60 x ATR14

Result:
- raw patterns: **132**
- quality-qualified: **3**
- expired: **1**
- executable trades: **2**
- distinct days: **2**
- wins: **2**
- gross profit: **+$0.12**
- gross loss: **$0.00**
- direct net: **+$0.10**

Directionally positive but far below the preregistered supply floor of 20 trades.

## Decision

**RETIRE_BATCH_NO_EXECUTABLE_SURVIVOR**

No profile earned independent later-January validation.

The result rejects the idea that a generic controlled-pause candle structure, by itself, is sufficient for 30-second persistence. The published-quality Inside-Bar context improved trade quality only by collapsing supply almost completely.

No timeframe rescue, filter sweep, pending-expiry sweep, session/side split, or exit retuning was performed.

## Synthesis

Together with 17BD and 17BE–17BG:

- raw signal density is not the missing edge;
- generic reversal geometry is not the missing edge;
- simple pause/continuation geometry is not the missing edge;
- stronger structural filters often improve apparent quality only by starving supply.

The next action is therefore **not another neighboring candlestick pattern**. It is a meta-harvest of the completed R037 Stage-A corpus to identify the highest-information surviving structural classes and untested causal feature gaps.

Compact result SHA-256:
`8528e9da6e5fef037c12398d4cfc32c9c331fee8a306d3508660900b272bd06d`

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Selection will be based on the completed 17-series empirical scorecard before another expensive screen is admitted.
