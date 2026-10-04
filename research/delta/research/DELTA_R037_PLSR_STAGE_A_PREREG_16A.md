# DELTA R037 — Previous-Liquidity Sweep/Reclaim (PLSR) Stage-A Preregistration — Checkpoint 16A

**Status:** PREREGISTERED / COMPUTE NOT YET RUN  
**Family:** R037-PLSR-v1  
**Parent:** 15B-retired SORB research lane -> frozen 14A surrogate parent for integration control  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this family

SORB C04 added activity on Stage A but failed pristine later-January validation. It is retired with no rescue tuning.

PLSR changes the event geometry completely. A level is inherited from the **fully completed previous active UTC day**, price must first sweep beyond that fixed prior-day high/low, and only a causal completed-bar reclaim may propose the opposite-side entry.

This is failed-expansion/reclaim logic, not current-session opening-range breakout continuation.

## Public reconstruction basis

- TradingView open-source Sweep Reclaim Retest: PDH/PDL -> sweep -> reclaim -> optional confirmation.
- TradingView open-source AG Pro Previous Day Sweep & Reclaim: prior-day extreme sweep followed by reclaim inside.
- TradingView open-source PDH/PDL Liquidity Sweep Detector: intraday-accurate prior-day levels.
- TradingView open-source XAUUSD/XAGUSD Liquidity Sweep Mean Reversion: Gold-specific wick-through / close-back-inside grammar.
- Reddit gold discussions are treated only as qualitative support for waiting for reclaim/structure rather than blind sweep entry.

No public performance number is imported.

## Frozen level semantics

For each UTC day, use the most recent earlier UTC day containing canonical ticks:
- PDH = maximum Bid of that completed day.
- PDL = minimum Bid of that completed day.
- no prior active day available -> no event.
- Bid must trade strictly beyond the level; a touch is not a sweep.
- PDH and PDL each own at most one consumed event per current UTC day.
- an un-reclaimed sweep expires at UTC day end.

## Frozen configurations

1. **R037-PLSR-C01_PDH_PDL_S5_RECLAIM** — first completed S5 close back inside; propose at first following tick if still inside.
2. **R037-PLSR-C02_PDH_PDL_S5_RECLAIM_CONFIRM1** — S5 reclaim plus exactly one immediately following directional S5 confirmation bar.
3. **R037-PLSR-C03_PDH_PDL_S15_RECLAIM** — first completed S15 close back inside; propose at first following tick if still inside.

PDH sweep proposes SELL; PDL sweep proposes BUY.

No excursion threshold, ATR threshold, EMA, VWAP, FVG, or parameter grid is authorized in 16A.

## Integration

Parent retains same-tick priority. One position at a time. A blocked/collided PLSR event is consumed and never deferred. No PLSR post-exit rearm exists.

Accepted PLSR entries use the frozen R9 lifecycle: $0.30 stop, +$0.10 trail activation, $0.03 trail distance, 30-second maximum hold, 0.01 lot and frozen commission/executable-side semantics.

## Stage-A advance gate

Minimum 8 proposals, 4 distinct days, 5 incremental accepted entries; combined trade count cannot fall; net may not worsen by more than $2; balance/equity DD deterioration must remain <=1%; a strong pass requires nonnegative incremental net.

No threshold/config changes after observing results.

## Next

Strong survivor -> later-January independent validation frozen before exposure.

No survivor -> retire PLSR v1 and harvest the next independent entry source.
