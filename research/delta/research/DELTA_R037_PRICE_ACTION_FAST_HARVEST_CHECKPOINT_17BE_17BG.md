# DELTA R037 — Price-Action Fast Harvest 17BE–17BG

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR  
**Parent:** R037_IER_STAGE_A_SCREEN_CHECKPOINT_17BD  
**Surface:** native M1/M5 signals → DUKAS_COINEXX_LIKE_P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Screen three completed-bar, publicly reconstructible price-action families in one timeout-safe bounded batch. The batch was preregistered before code and used the same frozen 30-second execution for each family.

Preregistration commit: `95a7ed14925c4acba1ca19fd6db78a21c5ab33f6`

Producer:
`research/delta/experiments/delta_r037_price_action_fast_harvest_17be_17bg.py`

Producer commit:
`beb578b4f94cc0123ef817eb0d0d195e20a5b0d0`

Producer blob:
`d3d63f6ef21c57c9a1d3488766d49e4cc1025037`

Producer SHA-256:
`b4f4812734a6a094ed7f446a3615cc14864ffe0d354175e88c17572004cdcd8b`

The local execution copy matched the committed Git blob exactly.

## Sources and frozen rules

### 17BE — TBR9/21
TradingView open-source Three Bar Reversal. Source explicitly recommends M1 for short scalps and its July 2024 update adds EMA9/EMA21 trend confirmation.

Result:
**565 trades / 14 days / 267 wins / -$107.15**

Decision:
**RETIRE**

### 17BF — PCR
TradingView open-source no-input Pullback Candle price-action pattern. M1 was preregistered as a project-target adaptation.

Result:
**2,253 trades / 14 days / 963 wins / -$498.61**

Decision:
**RETIRE**

### 17BG — FAKEY
ForexFactory four-bar Fakey: Mother Bar → Inside Bar → one-side false breakout → opposite Mother-Bar breakout.

Result:
**34 trades / 11 days / 15 wins / -$4.89**

Decision:
**RETIRE**

## Interpretation

All three families passed the supply/day gate but failed the direct-economic screen. Generic completed-bar reversal geometry therefore does not provide the missing 30-second XAUUSD persistence under the frozen P75 execution.

The batch strengthens the existing negative map:
- density by itself is not edge;
- generic candle reversal frequency is not edge;
- even a naturally selective false-break pattern remained negative;
- next harvest should shift toward **continuation after controlled pause / event-defined breakout acceptance**, not additional reversal-candle permutations.

## Durability

Official compact-result SHA-256:
`42d8511ec8077c196e69b2750438b3ac0a3c55244cc1e6663ee28a3e25b8aa8b`

No threshold, timeframe, side, session, or exit rescue was performed.

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Search bias:
**completed-bar continuation after controlled pause / breakout acceptance with enough natural supply for Stage-A.**
