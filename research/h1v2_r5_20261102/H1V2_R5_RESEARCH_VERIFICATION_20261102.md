# H1V2 R5 — Fitted quote-mark excitation and asymmetric entry-selection continuation

**Research state:** 2026-11-02, source-exact research-only, intentionally overfit Jan/Feb/Jun/Jul with a separately *unseen July* falsification. **Not an MT5 build, not a trading approval, and not demonstrated 80% prospective accuracy.**

## Frozen source lineage

- Existing source audit: `R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md`, unchanged. Repaired R9/V2 parent `997dfdbd06157faa426c143874ad84277971570e`, H1V2 original `edce573d9c53b743dc5de1b0d741c81370af52c1`, R2 `0a6f860bf2b3e265922af55bd2547e4970037101`, R4 latest `469f5bff1ee9158c7048c80bccf289cce90feb82`. New R5 independent branch from exactly R4 latest SHA. No original EA, TickExactActivePath, R9 exit, v2 trained model, or original H1V2 label output modified.
- Raw original Dukascopy Jan/Feb/Jun/Jul complete gzip monthly SHA-256 verified against original `h1v2_freeze.PINNED` in `extract_targets()`. This round used the prior 60k uniformly drawn 250ms candidate timestamps and 120k independent BUY/SELL classes; **not all 15.4M candidates**. The stored R2 label taxonomy is WRONG / NEUTRAL / WEAK_GOOD / STRONG_GOOD, with STRONG requiring first executable +$0.10 within 3s before -$0.10 adverse, original R9 final exact quote-side net >=$0.10, spread <=$1.00. The 3s strong class is more stringent than original 30s H1V2.
- As-of mark features are original R4 6 quote-revision marks (bid up/down, ask up/down, both up/down) with exact equal-ms ordinal state, past-only 250ms/1s/5s decays. **They are not actual executed trade or level-II order-flow marks.**

## New distinct experimental mechanism: FITTED six-mark excitation

Previous R4 had only manually defined exponential mark counts, not a fitted process. R5 fits six separate nonnegative one-step Poisson conditional-intensity heads via L-BFGS-B and exact analytic derivatives. Predict 1s future counts of *each* mark using only preceding 250ms/1s/5s decayed counts (18 regressors) plus intercept. Same-ms future row ordinal j>decision index is a label, never a feature. Fit only January/February, evaluate June/July untouched. Compare **constant-rate null**, **self-only excitation**, and **all cross marks**. Explicitly a *discrete-time linear-intensity quote-mark model*, NOT continuous-time Hawkes likelihood, and no claim of stationary branching matrix/spectral-radius test.

| July genuine held-out quote-mark forecast | Mean Poisson NLL per mark target (lower is better) |
|---|---:|
| Constant unconditional rate | 1.154458 |
| Six independent mark self-excitation models | 0.976531 |
| Six-mark self/cross-excitation, fitted | **0.962442** |

With fitted coefficients fixed from Jan/Feb, a within-UTC-hour past-feature permutation worsened July loss **0.962442 → 1.091238** and June **1.037616 → 1.179123**, supporting useful ordered observed event-history information over session-hour mixture alone. These losses score future quote revisions, **not** strict BUY/SELL entry outcomes.

## New causal side-independent asymmetric entry experiments

Held-out July trained Jan/Feb/June on existing as-of geometry / original R2 independent BUY/SELL labels. Action enters only if one side has sufficient positive evidence and rejects wrong/neutral, otherwise WAIT. Strict nonoverlap execution and monthly turnover **not** assessed here; all figures are independently labeled decisions from 15k source-month samples.

| July withheld classifier | Strictly correct / 150 top-ranked | WRONG | Weak-good | Neutral | Strict rate |
|---|---:|---:|---:|---:|---:|
| Previous R4 ordered-mark baseline | 2/150 | 125 | 8 | 15 | 1.33% |
| R5 combined R4 ordered marks plus fitted six-mark future-rate prediction as an **as-of derived feature** | 6/150 | 120 | 11 | 13 | 4.00% |
| R5 factorized head: P(any strong 3s opportunity) × conditional P(SELL versus BUY) | 8/150 | 131 | 11 | 0 | **5.33%** |

At the same 150 timestamps chosen by R5 factorized head, **only 19** had either direction strictly strong even with hindsight knowledge of the correct side. An otherwise perfect direction-only oracle could therefore achieve at most 12.67% strict correctness *on those particular chosen timestamps*. At the R5 combined model's 150 timestamps this same timestamp-conditional ceiling was **11/150 = 7.33%**. **Main bottleneck is opportunity/timing rejection, not merely flipping BUY/SELL.** The approximate improvements from 2 to 8 positives are small-count diagnostics, not evidence of statistically reliable transfer.

Neither 95% Wilson confidence interval nor the required >=80% correctness with >=150 qualified calibration choices was achieved by any July-withheld mechanism. NO entry policy qualifies. Favorable-session or intensity time-of-day data do not rescue this failure.

## Intentionally contaminated all-four-month high-capacity fit (user authorized)

A separate 85-round, 63-leaf 4-class LightGBM uses Jan, Feb, June **and July hindsight classes during training** and scores the same rows. Its top-1% selected samples were:

| Resubstitution month | Strong / 150 selected | Wrong | Weak | Strict TRAINING precision |
|---|---:|---:|---:|---:|
| January | 148 | 0 | 2 | 98.67% |
| February | 149 | 0 | 1 | 99.33% |
| June | 150 | 0 | 0 | 100.00% |
| July | 146 | 1 | 3 | 97.33% |
| **Total** | **593/600** | **1** | **6** | **98.83%** |

All four months satisfy >=80% strict *on the 600 deliberately TRAINED top-ranked sampled rows*, NOT on all original R9 SYNTH trade dates and NOT on a fresh chronological split. Top 5% performance already decays sharply: 68.13% Jan, 72.13% Feb, 83.20% June, 46.40% July, showing extreme skew toward a memorized narrow tail, not usable throughput. **The 94,150 monthly-floor-summed trade volume cannot be established from 600 sampled oracle-labeled admissions**, and no realized PnL/backtest is inferred. R4 already exhibited 100% top-1% train memorization; R5 does not reinterpret this as breakthrough predictive ability.

The very large planned 320-round / 127-leaf all-four fit exceeded the finite execution budget; that non-completed variant is an abandoned computational branch, not a positive or negative statistical result. The 85-round 63-leaf completed variant is independently stored with model bytes and receipts.

## Three research cycles and audited conclusions

1. **Causal 1s mark prediction:** cross excitation improves held-out mark likelihood over null/self-only and within-hour shuffled null; measure mark prediction only. New real additive mechanism, QUOTE_FORECAST_GAIN.
2. **Execution-side asymmetry under July withdrawal:** 2-stage factorization scores slightly better top-ranked strict examples than previous R4 but still fails extremely; as-of opportunity rejection and side classification must improve. ENTRY_DIRECTION_REJECT_FAIL.
3. **Four-month deliberately overfit teacher:** 593/600 strict training successes at top1%, 1 wrong; training-overfit proof, not evidence of foresight or 80%-of-SYNTH count. HINDSIGHT_MEMORIZATION_CONFIRMED.

## Validation and continuation

- **32 tests passed** combined across original H1V2, R2, R3, R4, new R5; R5 same-ms and arbitrary future quote mutation tests demonstrate as-of intensity features are not affected by future quote paths. Raw month hashes match original `PINNED`. All R5 outputs `R5_...` are additive; existing source and labels unchanged.
- Fresh correct/slippage-adjusted on-policy trade volume, Coinexx feed source agreement, full 4-month market-trade labels, Hawkes continuous-time maximum likelihood, stable fitted Hawkes kernel and MQL5 compilation remain **unperformed**.
- No reason to rerun previous R3 112-grid failed motifs or R4 marked 4-class failed trainings. Priority for R6: genuinely predictive quote **opportunity/timing** information independent of direction, with a *strictly past-only* dynamically segmented survival head (quote gaps, burst deceleration, arrival surprise), source-domain robustness, and session-specific boundary controls. Hold July out, then optional all-four in-sample memorize; do not fit July and later call it held out.

**Full prior kit links:** H1V2 original https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view ; R2 https://drive.google.com/file/d/11vsLhtdkDUfdEF34Q7zPYqpIJibu-aPV/view ; R3 https://drive.google.com/file/d/17oxTABUOMNq7Zc8nFpsbVpYJZ8xx75B4/view . Original 4-month raw tick folder https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV . Separate R4 full ZIP source SHA256 `df2d7044eb06f4bd79fb09dd981a748fe01d4226276a74e413f41d9186d6049d`; R5 depends on its restored local content or same repo files, not on conversation memory.
