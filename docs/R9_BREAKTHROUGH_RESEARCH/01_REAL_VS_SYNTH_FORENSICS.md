# 01 — R9 REAL vs SYNTH Forensics

**Status:** reconstructed from project evidence. Foundation for every later R10 decision.

## Evidence

R9 SYNTH Jan-Jul 2026:
- net ≈ +$309,122.85
- gross loss ≈ -$16,238.66
- 219,342 trades
- PF ≈ 20.04
- win rate ≈ 87.14%
- average hold ≈ 16 s

R9 REAL:
- net ≈ -$50,285.28
- gross loss ≈ -$80,465.51
- 236,647 trades
- PF ≈ 0.375
- win rate ≈ 43.26%
- average hold ≈ 5 s

The REAL test had **more ticks and more trades**. Failure therefore was not insufficient opportunity.

## Breakthrough

Generated ticks exhibit much more orderly short-horizon persistence. REAL ticks contain adverse snapback, churn and less favorable sequencing after an impulse.

The correct research target became:

`event -> observe state -> select action -> monetize favorable excursion quickly`

rather than:

`breakout -> assume persistence`

## Implementation consequence

R10 must:
1. preserve causal tick ordering;
2. use completed information only;
3. distinguish event detection from action selection;
4. track MFE/MAE live;
5. optimize REAL-path loss conversion and harvest efficiency.

Community cross-check:
- MQL5 MAE/MFE excursion analysis: https://www.mql5.com/en/articles/23245
- MQL5 competing-risks exit analysis: https://www.mql5.com/en/articles/24106

These sources support the measurement framework, not the R10 profit claims.
