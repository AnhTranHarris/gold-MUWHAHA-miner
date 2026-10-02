# DELTA R002 — Direction + Hold Pre-Backtest Candidate Shortlist

**Status:** RESEARCH_ONLY / NO TESTING / NO ACTIVE CANDIDATE  
**Parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**Workbook:** DELTA Candidate Quant Harvesting Template, `07 Hypothesis Lab`, HYP-007..HYP-015  
**Drive shortlist:** https://docs.google.com/document/d/1cVb2UxZ_ROZIFNs7CDkbBfqYzJofH_tLjqaHrVXoJLI/edit  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research basis

R9 REAL already produces 236,647 Jan-Jul trades versus 219,342 SYNTH trades. The research objective is not more entry volume. The working problem is weak directional ownership and early persistence after entry across heterogeneous trend, pullback, breakout, reversal, volatility, session, and time-scale conditions.

The harvest therefore scores research families by:
- direct fit to the R9 failure hypothesis;
- causal reconstructibility;
- availability of required DELTA inputs;
- opportunity-density preservation potential;
- clean falsifiability/ablation;
- MT5 reconstructibility;
- compliance with current ENTRY + INITIAL-HOLD scope.

No performance score has been assigned.

## High-viability pretest shortlist

### HV-01 / HYP-007 — Nested Causal Direction State
Foundational direction controller separating higher structural, intermediate swing, fast execution, conflict/transition, and persistence states. Lower-timeframe disagreement remains eligible as pullback/transition context rather than blanket invalidation.

### HV-02 / HYP-008 — Breakout -> Retest -> Rebreak Specialist
Finite-state continuation entry:
`break -> observe -> retest -> rejection/rebreak -> entry`.
Directly targets R9 false/early breakout exposure.

### HV-03 / HYP-009 — Pullback -> Reclaim -> Re-Acceleration Specialist
Higher/intermediate trend may remain intact while lower-timeframe direction moves countertrend. Entry occurs only after causal reclaim/re-acceleration.

### HV-04 / HYP-010 — Intrinsic-Time Directional-Change / Overshoot Specialist
Uses raw-tick directional-change and overshoot events as an event clock. This directly challenges the assumption that fixed seconds/minutes are the only useful direction/hold state representation.

### HV-05 / HYP-013 — Quote-Pressure Initial-Hold Persistence
Post-fill PERSIST / STALL / INVALIDATE state using only available causal top-of-book/tick proxies. This is explicitly a quote-pressure proxy, not centralized true OFI.

### HV-06 / HYP-014 — Specialist-Aware Initial-Hold Hysteresis
Breakout, pullback, expansion, and failed-break entries may receive different early persistence expectations and invalidation rules. Mature exit logic remains frozen.

## Secondary high-viability specialists

### HV-07 / HYP-012 — Failed-Break Reversal Specialist
Opposite-side ownership requires an explicit failed-break/reclaim/confirmation state rather than generic R9 opposite-side rearm.

### HV-08 / HYP-011 — Compression -> Expansion Continuation Specialist
Volatility contraction inside an allowed directional state, followed by causal directional expansion.

## Architecture candidate

### HV-09 / HYP-015 — Regime Router / Multi-Entry Specialist Controller
Session + news/event + nested trend + volatility/character context chooses which specialist may own an opportunity. Do not test the router before at least two specialists are independently characterized, or causal attribution will be weak.

## Recommended research order before testing

1. Define causal nested-direction/state vocabulary.
2. Define deterministic state machines for breakout/retest, pullback/reclaim, intrinsic-time DC/overshoot, failed-break, compression/expansion.
3. Define quote-pressure and specialist-aware initial-hold state machines.
4. Use GOV-014 spreadsheet harvesting to map R9 opportunities into these states without strategy optimization.
5. Only then select bounded candidates for Stage-A preregistration and Dukascopy P75 replay.

## Combination hypotheses to retain

- COMBO-A: Nested Direction + Breakout-Retest-Rebreak + Quote-Pressure Initial Hold.
- COMBO-B: Nested Direction + Pullback-Reclaim + Specialist-Aware Initial-Hold Hysteresis.
- COMBO-C: Intrinsic-Time DC/Overshoot + Quote-Pressure Persistence.
- COMBO-D: Breakout Specialist + Failed-Break Reversal with explicit ownership transfer.
- COMBO-E: Nested Direction + Compression-Expansion + Specialist-Aware Initial Hold.

These do not activate GOV-018. Heavy synthesis remains dormant until its explicit activation conditions are met.

## Fresh public sources

- MQL5 regime-adaptive EA: https://www.mql5.com/en/articles/17781
- MQL5 breakout/reversal finite-state logic: https://www.mql5.com/en/articles/18259
- MQL5 breakout/retest confirmation logic: https://www.mql5.com/en/articles/19968
- MQL5 pullback quality: https://www.mql5.com/en/articles/23628
- MQL5 intrinsic-time directional change: https://www.mql5.com/en/articles/23814
- TradingView MTF ADX: https://www.tradingview.com/script/E5uYlnA5/
- TradingView MTF EMA reclaim: https://www.tradingview.com/script/J3cU8CvN-Elite-MTF-EMA-Reclaim-Signals-Only-With-Market-Presets/
- TradingView trend pullback: https://www.tradingview.com/script/19nw5gJS-Trend-Pullback-Signals/
- Myfxbook XAUUSD false-break/trend discussion: https://www.myfxbook.com/community/general/does-trend-following-still-work/3321121%2C1
- Oelschlager & Adam HHMM: https://arxiv.org/abs/2007.14874
- Federal Reserve EBS order-flow study: https://www.federalreserve.gov/econres/ifdp/order-flow-and-exchange-rate-dynamics-in-electronic-brokerage-system-data.htm

## Gate

- Python/tick replay: NOT STARTED
- Stage-A preregistration: NONE
- Active candidate: NONE
- Metric locks: NONE
- GOV-018 heavy synthesis: DORMANT
- August: SEALED
- MQL5: NOT AUTHORIZED
