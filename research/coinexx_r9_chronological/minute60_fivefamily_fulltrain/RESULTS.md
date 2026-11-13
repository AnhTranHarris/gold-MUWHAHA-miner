# R9 M60 — Full January–September training, five-family features
**2026-11-13 | Retrospective development / full nine-month fit | No production EA changes**

## Scope and invariants
- All nine Coinexx XAUUSD monthly original gzip files SHA-256 matched prior immutable source receipt: **72,129,347 ticks**.
- The frozen R9 decision universe is **303,934** original timestamps; BUY and SELL counterfactuals make **607,868 action rows**. No opportunity filtering or change to entries, stops, target, holding horizons or first-passage labels.
- **155 causal input features** include original R9/M60 context, exact event-time nested trends, QRB, QAF, bounded CUSUM, signed quote-arrival intensities, frozen Brownian approximation and action/geometry metadata.
- Five retrospective expanding chronological evaluations: Jan–Apr→May, through Jan–Aug→Sep. All months have previously been used for development; they are **not fresh prospective OOS**.
- After the five folds, two final fits trained with *all nine months*, saved `*_IS_ONLY.joblib`. **No nine-month training-set AUC is reported as validation**.
- Compared the prior saved all-feature 45-tree hazard, a 75-tree/55k-per-bin competing-risk fit, a 95-tree direct five-second binary classifier using all labeled actions, and an untuned 50/50 probability average.
- The model budget was deliberately bounded to this comparison. No selection of winning AUC month, target, features or barriers, and no live EA integration.

## Five-second ROC-AUC, pooled hypothetical BUY and SELL at original R9 times

| Month | Prior all-five | Expanded competing hazard | Direct five-second | Fixed 50/50 | Direct on R9 original side |
|:---:|---:|---:|---:|---:|---:|
| 05 | 0.708035 | 0.715392 | 0.719757 | 0.719063 | 0.705085 |
| 06 | 0.720872 | 0.725025 | 0.730416 | 0.728881 | 0.714114 |
| 07 | 0.740711 | 0.748767 | 0.756060 | 0.754327 | 0.738934 |
| 08 | 0.739191 | 0.746581 | 0.750072 | 0.749768 | 0.734531 |
| 09 | 0.727639 | 0.731828 | 0.736258 | 0.735499 | 0.723210 |
| **Equal-month mean** | **0.727290** | **0.733519** | **0.738513** | **0.737508** | **0.723175** |

**Interpretation:** Direct classification improves pooled five-second AUC in all five old validation months and crosses 0.750 in **July (0.75606) and August (0.75007)**. This does not qualify for deployment: original-direction AUC stays below 0.750 in all months; September returns to 0.73626; both threshold-crossing months were already researched. 0.75007 is particularly marginal.

## Feature attribution / causal ablation

A *fixed identical direct-classifier objective* trained using previous event-time trend+QRB/QAF features (121 total) versus all 155 gave:
| Test month | Direct 121 features | Direct 155 features | Added 34-feature AUC difference |
|:---:|---:|---:|---:|
| 05 | 0.719099 | 0.719757 | +0.000659 |
| 06 | 0.730131 | 0.730416 | +0.000286 |
| 07 | 0.755280 | 0.756060 | +0.000780 |
| 08 | 0.748316 | 0.750072 | +0.001756 |
| 09 | 0.736288 | 0.736258 | -0.000030 |
Mean added 34-feature gain: **+0.000690**. The majority of the full-model vs earlier-baseline improvement is therefore attributable to training objective/capacity, not new CUSUM, intensity or Brownian formulas alone.

The final full-period LightGBM gain attribution emphasizes nested event-time trends (about 64%) and the earlier R9/M60 context (about 22%). Correlated-feature importance is **not causal evidence** that small-gain features are worthless; QRB/QAF, CUSUM and intensity remain present in both saved full-period models.

## Descriptive day-block uncertainty around threshold crossing

- July direct pooled AUC 95% day-block interval **[0.7435, 0.7670]**; paired improvement over frozen baseline interval [+0.0120, +0.0197].
- August direct pooled AUC 95% day-block interval **[0.7391, 0.7590]**; paired improvement interval [+0.0083, +0.0138].
- Resamples hold same-decision BUY/SELL paired by UTC trading day. 160 draws/month. These intervals describe *previously exposed* data, not model-selection-adjusted or pristine future validation. Both AUC intervals include 0.75.

## Economics and high-volume constraints
- All **162,312 May–September original candidate decision moments** remain in evaluation; 324,624 hypothetical directional actions do **not** represent broker trades.
- Expanded hazard model retained the previous strict expected-utility rule using frozen modeled price costs; it authorized **zero positive-utility entries in all five test months**. No on-policy after-cost profit or high-volume tradability is demonstrated.
- Direct five-second probabilities are **not a complete competing-risk utility model**; no stop-aware trade-selection result or fill-level profitability may be inferred from their AUC.
- Frozen label geometry and R9 decision times were intentionally **not changed** in this training stage. The requested timing/stop analysis belongs to a separate follow-up after review.

## Verification and preservation
- All nine source gzip SHA-256 hashes match the earlier immutable source receipts.
- Replayed 10 new serialized fold models; pooled AUC, original-side AUC and AP reproduce exactly to numerical tolerance. Two full Jan–Sep models reload and match stored SHA-256.
- Previous 11 priority feature tests and 15 event-hazard tests pass locally (26 total). Model data integration does not imply MQL5 compile/test.
- Production R9/QRB-QAF-enabled MT5 source is not changed by this research. New experiments are shadow-only.
- No API keys, broker credentials, raw tick logs, or massive repeated research source archives are included in this small evidence package.

## Runbook
- Inputs are existing immutable cache archives available in the primary Drive; compressed `full_derived/full_month_2026_MM.npz`, `event_2026_MM.npz` and `derived/priority_2026_MM.npz` must be restored under `input/`.
- The bundled scripts expect `ROOT=/mnt/data/r9_m60_training_20261113` and original prior research modules in `source_hazard/` and `source_priority/`, included in the ZIP; adjust paths for a different local machine.
- Dependencies: Python, numpy, scipy, scikit-learn, lightgbm, joblib, numba. Use environment limits `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2`.
- `python run_train.py --fold 4` through `--fold 8`, then `python run_train.py --full`, `python verify.py`, `python bootstrap.py`. The bundled `ablate.py` supports `--folds 4 5 6 7 8` for complete replay; the five ablation results are already preserved in `outputs/feature_group_ablation.json`.
- Full nine-month fit is research-only. **Prospective data later than September are necessary for genuinely unseen certification**; testing on the training rows would be in-sample.

**Decision:** Retain all five mechanisms. Predictive ranking improved but owner AUC 0.75 original-direction and economic/high-volume gates remain **FAILED**. Do not deploy or retune using July/August test labels.
