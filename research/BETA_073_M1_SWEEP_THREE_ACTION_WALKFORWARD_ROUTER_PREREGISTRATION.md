# BETA073 — M1 Sweep Three-Action Walk-Forward Router

**Status:** PREREGISTERED / FEBRUARY CLOSED UNTIL JAN CONFIG FREEZE  
**Parent:** BETA063 safe causal base  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA072 proved that a fixed M1 sweep/reclaim fade can look strong on one CAL slice and fail catastrophically in the following week. The event clock is retained; the fixed action is rejected.

## Decision problem

At each causal M1 confirmed-pivot sweep/reclaim event compare:
- **FADE_RECLAIM** — trade the reclaim/reversal side.
- **CONTINUE_SWEEP** — trade the opposite side, treating the reclaim as temporary.
- **SKIP**.

Both executable action labels use actual Bid/Ask, +300 seconds, and $0.02 round-trip fee.

## Causal state

Use only compact state available by entry:
entry spread; sweep overshoot/ATR; reclaim body fraction; reclaim close location relative to the fade side; M1 range/ATR; M5 context return/ATR; M5 trend alignment to fade; confirmed level age; side-relative 1s/5s midpoint returns; log recent 5s quote count; UTC hour sine/cosine.

No future label, later bar, R9 teacher, or BETA064 historical prediction enters features.

## Model

Fit one low-capacity LightGBM regressor for FADE after-cost value and one for CONTINUE after-cost value. Test only three small tree configurations and thresholds 0 / 0.10 / 0.20 / 0.30 USD.

The action with higher predicted value is taken only when that value exceeds the frozen threshold; otherwise SKIP.

## January walk-forward selection

Four expanding validation blocks:
1. train before Jan05 -> validate Jan05-Jan08;
2. train before Jan08 -> validate Jan08-Jan11;
3. train before Jan11 -> validate Jan11-Jan14;
4. train before Jan14 -> validate Jan14-Jan18 12UTC.

Purge at least 300 seconds between training labels and each validation boundary.

A configuration qualifies only if the combined OOF one-position replay is positive/PF>1 with >=40 trades, **at least 3 of 4 folds positive**, and median fold net positive. Select deterministic highest combined OOF net, then serialize the configuration.

## February robustness

Only after the January configuration file exists:
- fit final FADE and CONTINUE models on all Jan1-Jan18 data;
- serialize both models;
- load February;
- run the frozen router without parameter changes.

A February result with >=75 trades, positive net, PF>1 and positive average makes this a **human-facing QA candidate**, not an MT5-approved strategy.

## Human QA trace

If February passes, preserve a compact review packet with examples of TAKE-FADE, TAKE-CONTINUE and SKIP decisions showing predicted action values, state features, structural level timing, entry/exit Bid/Ask and realized P&L.

This remains historically informed research; February has been consulted elsewhere in the broader project and is not claimed as pristine OOS. August remains sealed.
