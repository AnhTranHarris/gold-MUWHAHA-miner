# R9 M60 — January–September aggressive joint-training audit

**Classification: RETROSPECTIVE RESEARCH ONLY. No MT5 EA promotion, no original-direction 0.75 gate pass, no 0.80 breakthrough.**

## Owner question and fixed experiment

Can previously constructed QRB/QAF, event-time trend, CUSUM, signed quote-intensity, analytical first-passage, marked-Hawkes-inspired excitation, latent-pressure estimates, and quoted-spread-resilience proxies predict R9 five-second favorable-first events more accurately when jointly trained, rather than merely appended?

- Original Coinexx XAUUSD source: 72,129,347 quote rows, Jan–Sep 2026; **303,934 original R9 entry decisions**.
- Both hypothetical sides at each R9 decision: 607,868 action records; 120 censored across nine months, resulting in 607,748 uncensored actions for final pooled training.
- Five chronological expanding folds: Jan–Apr→May; Jan–May→June; Jan–June→July; Jan–July→August; Jan–August→September. Entire held-out month scored (except frozen censor handling).
- Historical feature schema: original 155-feature direct 5s binary classifier, full 27 price-derived quote-only proxies (182), **55 predeclared cross-family features (237)**, including pressure consensus, disagreements, trend × Hawkes × pressure, QAF × quote-excitation, CUSUM × spread response, and analytical barrier interactions.
- Additional capacity-only control (182 features, identical hyperparameters) isolates the value of explicit interaction terms from simply increasing tree capacity.
- Original-direction-only specialist and frozen 50/50 blends test whether training on R9 action side gives better discrimination without changing decision moments.
- Fixed joint LightGBM settings: binary loss, 160 boosting trees, learning rate .04, max 23 leaves, min leaf 220, lambda L2=24, L1=3, max bins 63, seed 20261113. No per-month parameter optimization or target tuning in this experiment.
- Causal features use original source-ordinal quote prices and timestamps. Undefined histories remain NaN in base features; neutral cross products carry an explicit missing-60s flag. The feature generator never accesses future labels.
- **All evaluated months have been exposed in prior R9 research; this is NOT independent, fresh, prospective OOS certification.**

## Full evaluation — five-second ROC-AUC

| Evaluation month | Frozen 155 pooled | Expanded 182 pooled | Synergy 237 pooled | Frozen R9 side | Expanded 182 R9 side | Synergy 237 R9 side |
|---|---:|---:|---:|---:|---:|---:|
| 05 | 0.719757 | 0.720387 | 0.719380 | 0.705085 | 0.705218 | 0.703888 |
| 06 | 0.730416 | 0.731332 | 0.731187 | 0.714114 | 0.714132 | 0.713945 |
| 07 | 0.756060 | 0.757339 | 0.756723 | 0.738934 | 0.739732 | 0.739785 |
| 08 | 0.750072 | 0.751282 | 0.751717 | 0.734531 | 0.736109 | 0.736455 |
| 09 | 0.736258 | 0.737114 | 0.737405 | 0.723210 | 0.724691 | 0.724504 |

## Five-month mean comparison

| Model | Pooled 5s AUC | Original R9 direction AUC | Original direction AP | Original R9 months ≥0.75 |
|---|---:|---:|---:|---|
| Frozen 155 baseline | 0.738513 | 0.723175 | 0.119836 | None |
| Previous 182 append-only | 0.738317 | 0.723061 | 0.120011 | None |
| Expanded 182 capacity (control) | 0.739491 | 0.723976 | 0.120580 | None |
| All 182 + 55 explicit interaction features | 0.739282 | 0.723715 | 0.120253 | None |
| 237-feature original-R9-direction specialist | 0.735521 | 0.722588 | 0.118850 | None |
| Fixed 50/50 synergy+specialist | 0.738545 | 0.723819 | 0.120019 | None |
| Fixed 50/50 baseline+synergy | 0.739265 | 0.723847 | 0.120264 | None |

**Measured change:** expanded 182 vs frozen 155 = +0.000978 pooled AUC, +0.000801 original-direction AUC. 
**55 explicit interaction features vs 182 capacity-only** = -0.000208 pooled AUC, -0.000261 original-direction AUC. 

## What high volume means here

- All R9 entry opportunities are *scored*. No threshold or new trading logic changes the original R9 opportunity universe. This is **NOT** equal to actual new trades, on-policy order routing, broker fills, or improved account turnover.
- At 75%/50% diagnostic retention, a top-k threshold is derived from the held-out monthly score distribution solely for ranking analysis; it cannot be deployed without a training-only fixed threshold and measured test-month coverage. The complete no-selection 100% denominator is preserved.
- No new 5s quote-side terminal fills or separate commissions/slippage/occupancy simulation performed. Do not report positive after-cost profitability or live capability.

## Final all-nine-month fit

- joint: **607,748** uncensored training actions, **237** features, artifact `FULL_JanSep_joint_IN_SAMPLE_ONLY.joblib`, SHA-256 `5f29e5d43548da2f0ab740734a2dd8c89cabb68b0ad120a23c39c6c56c46e2ba`. **IN-SAMPLE TRAINING ONLY; no held-out AUC.**
- r9_specialist: **303,874** uncensored training actions, **237** features, artifact `FULL_JanSep_r9_specialist_IN_SAMPLE_ONLY.joblib`, SHA-256 `4616aeb2c0d464170428e6e97e2e4730c2c49cc1801bf5dc2a7e50237f2da52c`. **IN-SAMPLE TRAINING ONLY; no held-out AUC.**

## Interpretation and next-governor rule

- The attempt to make the proxy families enhance each other **has been executed and measured**, not merely hypothesized. More trees and deeper interactions gave only small aggregate discrimination changes; existing event-time trend and price/spread geometry remain dominant.
- Combined feature importance from a full-data model is an **in-sample attribution only**; correlated features share importance and it is not evidence of new exploitable liquidity data.
- AUC remains below 0.80 and R9 original-direction 0.75. Do not optimize further on July/August thresholds without a fresh independent later period.
- Preserve the 155 baseline and all new models separately; neither replace nor merge the deployed R9 EA. QRB/QAF research observation remains enabled in the existing source branch.
- Research gate for next phase: freeze models, measure full original R9 trade occupancy, exits, stop geometry and account-level after-cost performance; preserve a truly unseen later period for evaluation.

## Verification

- Revalidated **9** original source-month SHA256 values and **15** held-out model hashes and **60** AUC/AP metrics; **2** final model hashes.

## Descriptive Uncertainty

- `joint_vs_frozen_155`: mean delta +0.000585, descriptive day-block 95% interval [-0.000134, +0.001262]; prior exposure invalidates confirmatory inference.
- `joint_vs_capacity_182`: mean delta -0.000224, descriptive day-block 95% interval [-0.000760, +0.000285]; prior exposure invalidates confirmatory inference.
- `specialist_vs_frozen_155`: mean delta -0.000590, descriptive day-block 95% interval [-0.001528, +0.000463]; prior exposure invalidates confirmatory inference.
- `fixed_joint_specialist_vs_frozen_155`: mean delta +0.000668, descriptive day-block 95% interval [-0.000127, +0.001426]; prior exposure invalidates confirmatory inference.
- `fixed_frozen_joint_vs_frozen_155`: mean delta +0.000696, descriptive day-block 95% interval [+0.000327, +0.001045]; prior exposure invalidates confirmatory inference.

