# BETA077 — Expanding-Window Structural Meta Router

**Status:** PREREGISTERED / NOT TESTED  
**Primary setup:** BETA076 M5 FIRST_RETEST, fixed 900-second hold  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA076 decisively rejected trading every M5 first retest. BETA077 keeps that causal opportunity generator but separates **setup detection** from **economic admission**.

January is the only seed month. The first 70% of January executable events fits three bounded heads: realized-PnL regression, profitability classification, and hurdle expected value. The last 30% of January chooses one model head and one score/EV threshold. That model family and threshold are then frozen.

February through July are replayed sequentially. Before each month, the model is refit on all completed events from prior months only. It then predicts the entire new month without any within-month label update. At month end, that month's completed outcomes may enter the next refit. This is expanding-window adaptation, not same-period optimization.

Features are generic causal state only: side, retest tolerance, retest age, confirmed M5 level age, M1 ATR, actual entry spread, UTC cyclic time, and weekday cyclic terms. Time is a predictive feature rather than a hand-coded session veto.

The forward human-QA gate requires at least 200 Feb-Jul one-position trades, positive aggregate net, PF > 1, positive average, and at least 4 of 6 positive forward months. Jan-Jul are historically inspected elsewhere and are therefore robustness data, not pristine OOS. August remains sealed for a later blind gate.

Methodologically, this follows walk-forward/meta-labeling principles: construct the primary signal first, train the take/skip decision only on past completed outcomes, and include execution cost in the realized label.