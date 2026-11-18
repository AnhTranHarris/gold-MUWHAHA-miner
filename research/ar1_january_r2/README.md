# AR1 January R2 — source-exact historical account-risk observer

**Branch:** `carson/ar1-january-r2-atlas-selfproof` (isolated from owner-frozen S100 and existing R9 EA).  
**Research month:** January 2026 only. **NOT deployed, NOT a trade filter, NOT forward-tested.**

## Source authority
- **R9 SYNTH:** immutable historical trade entry/exit seconds, side, fee-inclusive booked outcomes, capital chronology, complete-cycle identities. Never use R9 synthetic intraday price paths as Coinexx ticks.
- **Coinexx REAL TickLogger:** actual January Bid/Ask millisecond quote data for open-position floating drawdown and surrounding causal market-state features. Original tick archives stay outside this public repository.
- **S100:** the already owner-frozen single-position dollar gap staircase. This study does not retune it.

## Method
1. Account-Risk Atlas R0 selects 240 historical risk witnesses spanning the 27 family reporting lines, S100 levels, protected profitable legs, recovery cycles and negative booked-loss episodes.
2. `atlas_zone_scanner.cpp` performs an optimized read-only 7,699,274-quote scan of 3,030 local market-context intervals surrounding 505 Atlas and control anchors. Surrounding context outside a trade is NOT attributed to the position's MAE or P&L.
3. `observational_policy.py` computes exact S100 gap, a serialized 12-variable January-fitted market-pressure logit, historical booked-capital-state telemetry, and real-tick pressure transitions at fractions of S100. There are no order execution methods.
4. `python_fixed_r9_coinexx_full_january_replay.py` independently reads all 21 original January TickLogger gzip inputs and tests every one of the 27,980 unchanged R9 positions. Exact quote counts, MFE, MAE, and DD agree with the preserved original C++ observation for all 27,980.
5. `atlas_acceptance_selfproof.py` audits all 240 Atlas witness rows, 270 family × level cells, actual portfolio book sums and six causal booked-loss windows.
6. `verify_formula_and_tick_state.py` independently reproduces all 27,980 numerical logistic scores and the January 9 source row 6433 quote-state transition times.

## January self-proof outcomes
- Original R9 booked net **+$41,520.82**, closing historical booked balance **$41,620.82** from $100.
- **27,980 / 27,980** original entries/exits/outcomes remain intact; **7,699,274** Coinexx quotes scanned.
- Observed 25% and 50% S100 giveback utilization thresholds: **930** and **110** positions. **Zero** observed full S100 touches. These are price-path measurements, not stop executions.
- Five held-day-out January internal folds: high S100-utilization classifier AUPRC **0.3008** versus **0.0333** event prevalence; ROC-AUC **0.8882**. These are retrospective January checks, NOT external forward validation.
- The original R9 losing-leg forecast is weak (AUPRC **0.1790** versus **0.1289** prevalence) and **must not** be used as a portfolio gate. The deterministic original booked-loss module remains usable as read-only risk telemetry.
- High market-risk scores also occur on thousands of originally profitable R9 trades. Do **not** convert the observer into an entry veto or a forced liquidation.

## Complete reproducer and environment
A **source-exact, 3.9 MB reproducibility ZIP** is preserved at:
https://drive.google.com/file/d/1fEfxObrwGaVJ41TYOrSGM_TXJtxyI93y/view

The ZIP includes the original archive basenames, source receipts, all small research tables, all Python/C++ scripts, full January result ledger and validation logs. The GitHub files have concise browsing names; the original ZIP is the authoritative runnable source and results bundle. These historical replay scripts use an `/mnt/data` research workspace containing the 21 original `R9_REAL_2026-01-*_ticks.csv.gz` files. Cloning this repo **alone** cannot reproduce the tick scan without those inputs and the earlier January R1 archive. No raw tick library has been added to GitHub.

Report and interpretation:
https://drive.google.com/file/d/142iNwSYpccWqc1JJC6NJgz7UKV8-sczQ/view

**Governance:** S100 frozen unchanged; AR1 January observational model self-tested; hypothetical profit preservation under trade-altering controls, Coinexx execution, slippage, broker realized equity and actual capital protection NOT certified. No source trade was filtered, rebooked or altered.
