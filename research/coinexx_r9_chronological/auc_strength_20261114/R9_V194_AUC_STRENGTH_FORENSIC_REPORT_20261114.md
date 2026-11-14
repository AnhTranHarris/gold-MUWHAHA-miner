# Gold MUWHAHAHA Miner R9 v1.94 — bounded AUC strengthening research (14 November 2026)

**Disposition: RETAIN original approved 155-feature model. DO NOT promote the new 16-feature augmentation or five-second economic companion as a trading decision.**

## Executive result

The five frozen original LightGBM direct binary five-second models were successfully reloaded and scored on **identical original Coinexx candidate/action labels**, reproducing all five previously published pooled and original-direction ROC-AUCs to <1e-6. The original 155-feature model remains untouched. One previously untested **16-feature exact sub-500ms quote-event residual group** was added to an otherwise capacity-matched 95-tree classifier, preserving original and alternative action rows and original-signal side evaluation. It produced **no economic or predictive breakthrough**.

- Original R9 direction ROC-AUC, five-month equal-mean: **0.723175**.
- With 16 sub-500ms features, same labels/dates: **0.723153**, difference **-0.000022**.
- Increased R9-side AUC in only **2 of 5** months. Paired source-day 95% descriptive confidence intervals ALL include zero.
- Existing pooled both-action 155-feature mean AUC remains approximately **0.738513**. Pooled classifications are hypothetical BUY+SELL actions; actual R9 entry side must be evaluated separately.
- All **303,934** original entry moments were source-matched and retained for shadow evaluation; **162,312** May–September original entries held out in five chronological historical folds. **Zero actual trade routing, governor, hold or exit changes.** No realized P&L gain is demonstrated.

## Directly matched five-second original-label AUC

| Historical evaluation month | Frozen 155 R9-side AUC | Augmented 171 R9-side AUC | Delta | Day-block CI on delta |
|---|---:|---:|---:|---:|
| 05 | 0.705085 | 0.705542 | +0.000457 | -0.000891…+0.001580 |
| 06 | 0.714114 | 0.714391 | +0.000277 | -0.000479…+0.000977 |
| 07 | 0.738934 | 0.738530 | -0.000404 | -0.001564…+0.001084 |
| 08 | 0.734531 | 0.734475 | -0.000056 | -0.000759…+0.000791 |
| 09 | 0.723210 | 0.722827 | -0.000384 | -0.001015…+0.000576 |

**Statistical caution:** January–September dates have been used extensively in this project before; these folds are chronological retrospective development studies, not fresh independently untouched OOS. Day-block resampling is descriptive only and does not correct for all prior experiment selection.

## Why 10/50/250ms information is sparse

Source-ordinal-sensitive lookbacks and quote revision signs/flip fractions were computed ONCE over original **72,129,347** Coinexx rows with NO reconstructed bars or duplicate ticks. Quote hashes and original entry timestamp, direction, spread and liquidation-side price were checked against immutable receipts, using **global ONE-BASED quote ordinals across month boundaries**; equal-millisecond quotes preserved without sorting/deduplication.

Among original R9 entries, at least two quotes occurred within:
- final 10ms: **0.0105%** of entries
- final 50ms: **0.0625%**
- final 250ms: **62.35%**

Thus many 10–50ms feature values are uninformative; rapid-quote revisions may be concentrated in exceptional market conditions. This finding partly explains why the added representation failed to improve held-out AUC. It is not proof no causal sub-500ms predictor can ever work.

## Economically aligned five-second COMPANION label (different target)

A second, original-R9-side-only LightGBM was trained on the same as-of 155-feature inputs, then +16, **against a different quote-side first-cause outcome**: hypothetical K=1 account-currency unit per one $1 XAUUSD price change at 0.01 lots; EXTRA cost C=0.20/trade (spread already included through BUY Ask→Bid / SELL Bid→Ask); favorable **net +0.10** before adverse **net −0.65** within five seconds. Quote gaps >2500ms before a conclusive outcome are right-censored. These economic constants were **predeclared**, and neither K nor C is verified by historical quote-only logs. The target does NOT represent the real v1.94 trailing stop, broker execution or portfolio profit.

| Held-out month | Companion positive event rate | 155 only AUC | 155 + 16 AUC | Delta |
|---|---:|---:|---:|---:|
| 05 | 16.04% | 0.641781 | 0.642082 | +0.000301 |
| 06 | 17.91% | 0.648518 | 0.648977 | +0.000458 |
| 07 | 14.33% | 0.683845 | 0.682777 | -0.001068 |
| 08 | 16.17% | 0.671389 | 0.671307 | -0.000082 |
| 09 | 15.65% | 0.664452 | 0.664589 | +0.000137 |

Mean companion ROC-AUC: **0.661997** for 155-only versus **0.661946** for 171, incremental **-0.000051**. These are NOT directly comparable to 0.723/0.738 original-label AUC because the barrier definition and action universe differ.

The new companion does establish a separate five-second cash-event classification benchmark for *research*, not trade-profit feasibility. No threshold, stop or holding decision was promoted.

## Training-only session calibration — diagnostic, not new alpha

A regularized single-variable Platt-style calibrator was estimated ONLY from **prior months' actual held-out fold predictions** with source-native session subgroups and global fallback. May had no eligible prior held-out calibration data, so remained uncalibrated. No eval-month labels were used to fit that month's calibrator. Probability calibration does not create new directional predictability by itself.

| Month | Raw Brier | Prior-OOS calibrated Brier | Raw 10-bin ECE | Prior-OOS calibrated ECE |
|---|---:|---:|---:|---:|
| 05 | 0.045374 | 0.045374 | 0.010353 | 0.010353 |
| 06 | 0.051369 | 0.051401 | 0.003603 | 0.006182 |
| 07 | 0.037196 | 0.037220 | 0.004835 | 0.000948 |
| 08 | 0.042150 | 0.042125 | 0.004854 | 0.001306 |
| 09 | 0.038844 | 0.038797 | 0.005988 | 0.001335 |

The mean 10-bin ECE declined from **0.005927** to **0.004025**, but mean Brier changed only **0.042987 → 0.042983**, with deterioration in June and July. This supports retaining calibration diagnostics, **not** enabling a live session-specific threshold or claiming a robust probabilistic breakthrough.

## High-volume / economic disposition

- **No original R9 trades were filtered.** Historical signal coverage is 100%, but an experimental Python model's runtime has NOT been proved in MT5's event-coalescing real-time loop.
- Diagnostic high-score deciles of the ORIGINAL frozen R9 trade ledger remained net-negative under the illustrative K/C assumptions; changing a classifier score does not change original R9 entries, holds or exits.
- No after-cost gain per hour, trade or portfolio is established. Preserved original v1.94 gross-loss governor and exact compiled EA untouched. No new derived tick archives, trained 155-model replacement, model-to-order wiring or live signals.
- Original system profit remains the appropriate deployment gate. Its earlier R9 source-exact quote-side baseline was negative, even with zero additional commissions. Improving AUC by less than one ten-thousandth is economically insignificant without full-system tested utility.

## Next evidence-led direction (frozen before any new test)

1. **Retain 155-feature direct LightGBM**. Do not promote the 171 augmentation, retune dozens of threshold combinations or repeat failed 182/237/quote-pressure experiments.
2. For a next genuinely unseen Coinexx month after Sep 2026, first measure original-side AUC and P5 reliability, five-second cash-event AUC, execution cost and session stability with the frozen model and predeclared cash label. Do not change classifier based on July/August results.
3. If economic calibration is insufficient, investigate an *entry-time* continuation utility/stop-hazard model only with broker-verified K/C and strictly past-only labels, then whole-system on-policy R9 trades, rearming and gross-loss capacity. Without positive net portfolio cash and high volume, do not touch MQL5.

## Reproducibility & safety

Scripts: `micro_events.py` (original quote-stream 16-feature extractor and 5-sec cash label), `train_auc.py` (source exact 155 construction, old model AUC/hash verification, matched 171-classifier and original-side cash companion), `summarize.py` (strict previous-heldout session calibration, day-block descriptive CIs, economic diagnostics), tests `tests/test_micro_auc.py` (6 causal and protocol tests). Original development code/weight/source SHA256 pinned. Re-extract source only if necessary: pre-existing 2.1 MB nine-month temporary micro feature cache was the *only* derived input created; no new source tick archives. Models were fitted in memory. Original files reside only in the original source folder and Drive. This result report is compact, not a new training library.

**Status: NO PROMOTION / original frozen model remains best supported baseline.**