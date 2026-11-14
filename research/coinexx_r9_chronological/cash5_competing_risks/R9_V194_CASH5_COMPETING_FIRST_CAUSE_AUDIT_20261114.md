# R9 v1.94 — Frozen 155-score conditional five-second cash first-cause study

**Date:** 2026-11-14. **Classification:** Coinexx quote-only, original-entry, retrospective, shadow-only; NO EA change or trade-profit certification.

## 1. Source preservation and exact research question

- Existing original R9 v1.94 owner-compiled standalone checkpoint and v1.90 rollback remain unchanged.
- Original frozen 155-feature five-second LightGBM models are reused as-is; all five model ZIP payload SHA256s checked before research scoring.
- Existing `pred_fold_05`–`pred_fold_09` are **genuinely out-of-fold P5 predictions for their respective evaluation months** from the previous original-strengthening experiment. Their original-R9-side AUC was verified against each saved fold receipt.
- The existing `micro_2026_05`–`micro_2026_09` arrays were produced by the earlier SHA-verified one-pass original Coinexx quote extractor. This study **does not re-read, reconstruct, split or export any of the original 72 million quotes**.
- Original frozen R9 completed-trade ledger, source month hash, counts, side/session labels and five-second favorable/censor labels were cross-checked against preexisting receipt and saved fold arrays.
- The label is **first event in the next five seconds from ORIGINAL R9 entry**, using executable BUY Ask→Bid and SELL Bid→Ask; it is NOT the actual filled R9 stop/trail/timeout outcome or a hold-versus-exit advantage.

## 2. Competing price-event definitions and illustrative economics

For original entry side `s ∈ {+1,-1}`, entry executable price `E`, exit-side quote `L(t)`, hypothetical `K=1.00 account-currency unit / $1 XAU quoted price at 0.01 lot`, hypothetical additional roundtrip fee `C=0.20` beyond bid–ask spread:

`Pi(t) = K*s*(L(t)-E) - C`.

- `Y=1`: **+0.10 net account units first** (favorable continuation).
- `Y=2`: **−0.65 net account units first** (adverse first passage; not necessarily a classical reversal pattern).
- `Y=0`: neither threshold observed within five seconds.
- `Y=-1`: right-censored because the source quote gap exceeded 2.5 seconds.
- Stop/target ties use the original research source first-cause precedence. Missing gap observations are **excluded** from the complete-case classifier score; no fabricated completion or censor time.

For fixed sample start state `X_entry` and mutually exclusive causes define `P_+(5|X)`, `P_-(5|X)` and `P_0(5|X)`; **all three must sum to 1**. These are interval competing-event probabilities, *not a continuously updated 1s/3s conditional hazard* and *not policy-specific optimal-stopping Q-values*.

## 3. Chronological scoring protocol

Original P5 model is frozen. A 3-class regularized logistic layer uses ORIGINAL R9 at-entry features: source spread, completed M5 ATR, signed original S1 displacement, directional efficiency, S1 range, preceding quote gap, entry minute second, rearm index, side and session. The treatment model additionally receives frozen P5 log-odds.

**No in-sample P5 calibration training:** May is the first historical OOS P5 source, used to fit the first cash head; test June. Expand training through June for July, through July for August, and through August for September. Thus **four** fully earlier-out-of-fold P5→cash training/evaluation rounds, not an invented fifth fold. All input clipping/standardization parameters are fitted only on earlier labeled months; current test labels never enter the fit. All Jan–Sep calendar periods have been examined previously and are not pristine prospective OOS.

For comparability, the context-only and context+P5 heads use the same class label, same examples and same fixed regularization. Metrics: favorable-vs-rest ROC-AUC, adverse-vs-rest ROC-AUC, 3-class Brier score (`sum_k (p_k-y_k)^2` per sample, lower is better), 3-class log-loss, and empirical event counts. Brier alone combines resolution and reliability, not pure calibration.

## 4. Four chronological evaluation results

| Eval month | Original P5 AUC (own label) | Favorable AUC context | + frozen P5 | Increment | Adverse AUC context | + frozen P5 | Three-class Brier delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06 | 0.714114 | 0.634730 | 0.639799 | +0.005070 | 0.634557 | 0.637893 | -0.003316 |
| 07 | 0.738934 | 0.664132 | 0.671568 | +0.007436 | 0.632326 | 0.639548 | -0.004730 |
| 08 | 0.734531 | 0.656531 | 0.663842 | +0.007311 | 0.633375 | 0.637510 | -0.003547 |
| 09 | 0.723210 | 0.645959 | 0.655038 | +0.009079 | 0.625236 | 0.628343 | -0.002834 |

**Equal-month means:**

- **130,697 original R9 evaluation positions** from June–September; 1,862 quote-gap censored. Modeling scores use the remaining complete cases.
- Favorable-first AUC **0.650338 → 0.657562**, increment **+0.007224**.
- Adverse-first AUC **0.631374 → 0.635823**, increment **+0.004450**.
- Mean three-class Brier change **-0.003607** and three-class log-loss change **-0.005427**; lower is better. Brier improved in 4/4 test months.

## 5. Source-day paired bootstrap — conditional historical uncertainty

- 200 paired resamples of **source-entry calendar days within each evaluated month**, averaging four monthly AUC/Brier differences. Frozen models were not re-fitted in each resample (so this interval excludes model-estimation uncertainty). Historical discovery exposure is not corrected.
- Favorable AUC increment 95% paired source-day percentile interval: **[+0.006242, +0.008489]**.
- Adverse AUC increment 95% interval: **[+0.003881, +0.005094]**.
- Three-class Brier increment interval: **[-0.003970, -0.003300]**.

These conditional intervals do not demonstrate unseen future-month stability or trading cash efficacy.

## 6. Cash first cause / five-second survival diagnosis

Across May–September original R9 opportunities, 162,312 entries included 2,161 quote-gap censored records. Of 160,151 uncensored labels; source-day risk-set calculations use `cash_hit_ms` only where defined.

- At ENTRY for uncensored May–Sep examples: 16.04% favorable-first by five seconds; 40.53% adverse-first; the rest had neither event within five seconds.
- Among completed-case quote paths with NO first event by 1 second, the remaining-by-5s historical incidences are approximately **15.12% favorable** and **32.67% adverse**.
- Among paths with no first event by 3 seconds, remaining-by-5s incidences are approximately **9.00% favorable** and **16.68% adverse**.

**Do not call these live conditional hazard predictions:** no new as-of quote-state was injected at 1s or 3s, existing R9 position may have closed before those quote landmarks, and gap-censored risk-set times were unavailable. These are retrospective price-path survivor descriptions only.

## 7. Does the stronger cash-risk score make ORIGINAL R9 profitable?

NO. The context+P5 probability head improves five-second first-event discrimination, **but even its top-ranked 10% favorable-minus-adverse trade opportunities have negative original R9 exit net P&L** under the same hypothetical account-currency conversion and cost.

| Month | Highest 10% favorable−adverse score: original R9 mean net cash | All original R9 mean net cash |
|---|---:|---:|
| 06 | -0.40286 | -0.40758 |
| 07 | -0.40641 | -0.39523 |
| 08 | -0.40407 | -0.40747 |
| 09 | -0.40259 | -0.40578 |

**July is the counterexample:** the top-ranked 10% of predicted short-term cash-first-event opportunities were worse on average than the month as a whole. Do not use these monthly top-decile cutoffs as live thresholds: they were defined retrospectively using all scores in their evaluation month and would require training-only thresholds to be deployable.

Neither a positive modeled first-passage event nor its predicted probability is an actual realized stop/trail/timeout profit. Lower throughput can only be justified by verified higher net profit per remaining trade and by full rearm/portfolio simulation.

## 8. Mathematical extension required for real holding versus exiting

For `EXIT_NOW`, evaluate current fill-side liquidation cash `Pi_now(t)` including calibrated costs. For `HOLD`, action-specific probability of stop, favorable event, timeout, rejection/censor and conditional final net payoff is required. A risk-protected finite-horizon value-of-information objective is:

`ΔQ(t,z) = E[Pi_final_net | HOLD, z, existing stop] - Pi_now(t) - λ*CVaR_95(loss | HOLD,z) - η*foregone-next-R9-opportunity-cash`,

with conditional training from **earlier ON-POLICY replay** and current as-of quote state. The current entry-timestamp 3-class estimator **cannot directly supply** this ΔQ because (a) it has no landmark mark-to-market price, (b) neither-event cash payout is unknown, and (c) original R9 stops/occupancy/rearms differ from hypothetical hold-to-5s barrier paths.

Test the following narrowly **before** any MQL5 EA change:

1. On an already-verified original Coinexx tick replayer, collect exact Bid/Ask liquidation cash and stop distance at 1s and 3s while the ORIGINAL position remains open; record first outcome at later five seconds using actual original stop/rearm or explicit separate counterfactual replay. Missing quote or missing score fails closed to baseline.
2. Fit policy-specific `Q_EXIT`, `Q_HOLD`, `Q_TIGHTEN` on earlier chronological dates with original model P5 score held immutable. Account gross-loss capacity and stop/freeze constraints remain hard barriers.
3. Simulate full original R9 entry/hold/exit/rearm (not frozen-positions shadow labels), ask if actual mean modeled net account cash/hour improves with >=95% trade retention, <=30sec mean hold, no worse gross loss/CVaR/drawdown. Use only Coinexx source; no Dukascopy substitutes or true executed-volume claims.
4. Verify Coinexx `OrderCalcProfit`, commission/slippage and live model packet latency. Native M1 iADX/EMA/iStdDev from completed Bid bars may be tested only with paired ON/OFF evidence; high-resolution price+spread observations are primary on a 5-second horizon.

## Reproduction and preservation

Run `python competing_cash5.py --root EXISTING_RESEARCH_SOURCE_DIR --output scorecard.json` with the original saved model ZIP + R9 ledger ZIP + the small preexisting `r9_auc_strength_work/cache/micro_2026_{mm}.npz` and `pred_fold_{mm}.npz` for May–Sep. Then `python robustness.py --root ... --output robustness.json --bootstrap 200`. Scripts do NOT touch original raw Coinexx gzip or write any raw dataset. All earlier source archived hashes are rechecked; source csv original row/entry parity was established by the upstream saved quote extractor.

**No production upgrade approved.** The existing compiled v1.94 source at commit `813baf96f2b381be5fc7896aac8b08a966114948` and critical v1.90 rollback `8729a6345655a7b4ea31facc81982004ee2b8921` remain unchanged. This new cash-first-cause model adds modest predictive value but has not delivered positive realized returns.

## Literature/method reference
- Aalen–Johansen and cause-specific hazards explain first-event competing risks. https://pmc.ncbi.nlm.nih.gov/articles/PMC13007359/
- Multi-class Brier and log-loss evaluate probabilistic forecasts, not standalone trading profitability. https://scikit-learn.org/stable/modules/calibration
- Account-currency P&L must be validated using the actual broker/symbol/lot via MT5 OrderCalcProfit. https://www.mql5.com/en/docs/trading/ordercalcprofit