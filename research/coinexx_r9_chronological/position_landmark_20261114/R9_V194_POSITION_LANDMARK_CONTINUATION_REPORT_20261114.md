# R9 v1.94 — position-level 1s / 3s cash continuation versus liquidation

**Date:** 14 November 2026. **Research verdict: NO EXIT PROMOTION.** Original MQL5 v1.94 and R9 v1.90 rollback unchanged.

## Source, parity and causal observation

- Source: ORIGINAL Coinexx XAUUSD Bid/Ask monthly compressed source January–September 2026. Only **May–September** were scanned for this position-level test, reading the original archives without reconstructing or uploading a new tick library. Input SHA-256, row count, original R9 entry and exit source ordinal, millisecond timestamps, side and executable quote prices all matched prior frozen ledger receipts.
- The May–September source-backed original R9 position universe contains **162,312** completed original Python R9 trades. This is *not* a report of executed live MT5 deals; the historical Python R9 control differs from v1.94 account governor/OnTimer and does not observe broker fills.
- At each position age 1s and 3s, select **the first actually observed quote at or after the landmark** and strictly BEFORE the ORIGINAL observed exit ordinal. Reject first quotes arriving >500ms after milestone and prior quote interarrival gaps >2500ms; do not interpolate price to exactly 1s/3s.
- Position state uses only original quote history up to that time. Reconstruct original 30-cent initial stop and its 10-cent activation/3-cent monotonically tightened trailing level. Store real liquidation-side Bid for BUY / Ask for SELL, stop distance, spread, quote-event rate, signed 1s quote drift, volatility, MFE/MAE and immutable **original-direction frozen 155-feature P5 model** value. No future feature data.
- The original five R9-direction fold models had their actual SHA-256 checked and their original own-target AUC reproduced within 1e-6 in source code before using P5 on each month. No new five-second classifier was trained.

## Economic definition, target mismatch, and unidentifiable rearm value

With side s=+1 BUY / −1 SELL, fill E=BUY Ask/SELL Bid, current liquidation L=BUY Bid/SELL Ask, and K/C explicit illustrative account cash assumptions:

\[\Pi_t^{net}=K s(L_t-E)-C,\qquad Y_t=\Pi_{original\ R9\ exit}^{net}-\Pi_{exit\ now,t}^{net}.\]

The **fixed per-trade C cancels in Y**, so Y is an observed additional quote-side cash payoff from original R9 continuing instead of hypothetically exiting at that observed landmark. This is a valid paired observation on an ORIGINAL-policy surviving position, but it does **not** establish a realizable alternative-account equity curve. Exiting early changes the opposite-direction rearm and future entry universe; the frozen ledger cannot identify that counterfactual.

\[\widehat{\Delta Q}_t =\underbrace{\widehat{E}[Y_t\mid X_t]}_{\text{earlier-fold predicted original-policy increment}}-\lambda\underbrace{\widehat{CVaR}_{95}(-Y_t\mid X_t)}_{\text{earlier-period risk bucket}}-\eta C_{rearm}.\]

The rearm-opportunity cash term **is not identified** by a frozen original-policy ledger; numerical sensitivity below sets eta=0 and discloses it. This is neither a broker-validated Q-value nor an on-policy early-exit optimization. CVaR estimates come from training-only eight risk buckets of original-policy continuation residuals; no action-specific counterfactual hazard is established.

## Observed position-level comparison (original R9 survivors only)

| Month | Alive & observable at 1s | Hold-minus-exit at 1s | Alive & observable at 3s | Hold-minus-exit at 3s |
|---|---:|---:|---:|---:|
| 05 | 23,372 | -0.01579 | 14,568 | -0.01534 |
| 06 | 25,374 | +0.00943 | 15,636 | +0.01298 |
| 07 | 25,102 | +0.00460 | 17,147 | +0.00238 |
| 08 | 23,177 | -0.00241 | 14,977 | -0.00425 |
| 09 | 24,895 | -0.00243 | 16,012 | -0.00268 |

**Totals:** 121,920 observed 1s survivors and 78,340 observed 3s survivors. These groups differ and cannot be treated as all 162,312 entries.

## Four expanding chronological cash-value evaluations: May trained; June, July, August and September tested

Small, matched, fixed regularized **Ridge** head estimates original-policy cash advantage from causal quote/position context, with or without adding frozen entry-time P5. Same source positions, same target, train-only input clipping/normalization and training-only target winsorization for both heads. Original P5 for every month was itself trained on earlier months and source-verified. No model-tuning search was conducted.

| Landmark | Test month | Positions | AUC context | AUC + frozen P5 | Delta AUC | Estimated CVaR (cash) |
|---|---|---:|---:|---:|---:|---:|
| 1s | 06 | 25,374 | 0.48088 | 0.48667 | +0.00579 | 0.675 |
| 1s | 07 | 25,102 | 0.54115 | 0.53518 | -0.00597 | 0.687 |
| 1s | 08 | 23,177 | 0.53955 | 0.53119 | -0.00836 | 0.668 |
| 1s | 09 | 24,895 | 0.53119 | 0.52724 | -0.00396 | 0.672 |
| 3s | 06 | 15,636 | 0.49413 | 0.50206 | +0.00793 | 0.671 |
| 3s | 07 | 17,147 | 0.51652 | 0.51339 | -0.00314 | 0.682 |
| 3s | 08 | 14,977 | 0.49190 | 0.49368 | +0.00178 | 0.663 |
| 3s | 09 | 16,012 | 0.51858 | 0.50889 | -0.00969 | 0.668 |

| Landmark | Mean AUC context | Mean AUC + P5 | AUC difference | Mean observed hold-minus-exit | Source-day 95% bootstrap interval (cash) | P5 incremental AUC 95% day interval |
|---|---:|---:|---:|---:|---|---|
| 1s | 0.52319 | 0.52007 | -0.00312 | +0.00230 | [-0.00090, +0.00489] | [-0.00570, -0.00076] |
| 3s | 0.50528 | 0.50450 | -0.00078 | +0.00211 | [-0.00076, +0.00563] | [-0.00328, +0.00183] |

**Economic inference:** The original P5 model improved 5-second FIRST-CAUSE event prediction previously, but its incremental value for predicting whether **continuing under the original stop policy** beats immediate liquidation at 1s/3s is negative on mean AUC across these four later evaluation months. The mean observed original-policy HOLD advantage is near zero and its paired source-day interval includes zero. Do not confuse the two AUC labels.

## Risk/throughput sensitivity (eta=0 only)

- The training-bucket conditional left-tail CVaR of continuation *relative to exiting now* is about **0.66–0.69 cash units** for these historical survivor populations, much greater than the approximately 0.002 mean observed HOLD advantage.
- Under a research score ΔQ = predicted mean original-policy HOLD advantage − 0.10 × training-only CVaR, the model predicts **almost no** surviving positions should HOLD; with a penalty of 0.25 it selects **zero** in all June–September folds. This would change exit behavior radically and is not an acceptable high-volume trade strategy without a complete independent on-policy rearm/governor simulation.
- Because next rearm opportunity cash is not observed under counterfactual early exit, η cannot be fit from these frozen original exits. η=0 is a neutral declared scenario, **not a certified bound** when the original follow-on trading edge may itself be negative.
- Model cash-currency conversion K=1 cash unit for 1 XAUUSD quoted-dollar move at 0.01 lots and additional C=.20 full round-trip are illustrative. Exit costs, fills, price gaps, broker stop/freeze and account governor are not verifiable from quote-only data.

## Conclusion and next controlled gate

**No production promotion:** The frozen approved high AUC is preserved; original-position landmark estimates do not support a reliably positive, risk-adjusted hold-versus-exit policy, nor have they improved realized net P&L/hour. No trading mode or portfolio loss governor has been changed.
If the owner wants an actionable alternate EXIT NOW policy, the **single next gate** is original-chronology ON-POLICY execution that retriggers subsequent entries/rearms under the same feed and tracks account gross-loss capacity. Reuse the existing R9 simulator; do not build another tick engine, rebuild feature caches or tune a large indicator sweep. A model score is missing for entries created by altered exits: fail safe to original state rather than impute future feature vectors.

## Reproduction (read-only originals, compact temporary landmark snapshots)

1. Extract source-backed snapshots from original Coinexx gz / frozen archives with `continuation_landmarks.py` (original monthly source hashes and full ordinal/price matching enforced). This writes only ~8 MB of temporary small landmark arrays; **no tick source rebuilt**.
2. Fit four chronological folds with `train_continuation_value.py` (train May to preceding month, test next month June–September). Do not refit the frozen P5 model.
3. `day_bootstrap.py` resamples existing source-entry days 200 times within each evaluation month, holding model fits fixed; historical, conditional confidence intervals are not prospective guarantees.
4. `test_landmark.py` has five passing synthetic invariant tests for executable cash, non-future price access, protective stop geometry, original-position survival, train-only risk and feature ablation.

Original exact compiled R9 v1.94 commit `813baf96f2b381be5fc7896aac8b08a966114948`, exact v1.90 rollback commit `8729a6345655a7b4ea31facc81982004ee2b8921`. Both remain unchanged.
