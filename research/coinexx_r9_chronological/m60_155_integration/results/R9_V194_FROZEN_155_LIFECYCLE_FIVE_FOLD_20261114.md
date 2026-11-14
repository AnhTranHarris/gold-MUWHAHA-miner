# R9 v1.94 — Original high-AUC model connected to the R9 trade lifecycle

2026-11-14. **FIVE CHRONOLOGICAL CASH-CALIBRATION FOLDS COMPLETED. NOT LIVE CERTIFIED. NO EA SOURCE CHANGES.**

## Original development log and source-exact provenance

Read the original MT5_EXPAND high-AUC development logs R9_M60_JanSep_Training_AUC_Audit_20261113.md, R9_M60_FullUniverse_AUC_Ceiling_Audit_20261113.md and R9_M60_QuoteOnly_PressureProxy_20261113_RESULTS.md; model archive R9_M60_JanSep_FullTraining_155Features_20261113.zip, saved five 95-tree LightGBM direct classifiers; original 9 monthly 145-col full cache, 77-col event cache, 23-col quote-intensity cache, and 303,934-entry original signed close ledger. All are original, existing frozen cache ZIPs, not rebuilt tick data.

Exactly 155 original fields, float32: 14 original R9 context, 25 selected HFT, 77 causal event-time, 23 CUSUM/quote intensity, 11 original Brownian analytical, 5 action metadata. Only ORIGINAL R9 side selected. Exact original source ordinal, entry millisecond, side and signed executable-side entry/exit quote PnL matched the original ledger across all 303,934 entries. All five source-model hashes verified before loading. All five original-direction P5 ROC-AUCs reproduced their archived fold receipts.

The ORIGINAL model label is a hypothetical favorable-first FIVE-SECOND barrier event. It does NOT predict R9 original stop/trailing realized after-cost cash, best holding horizon, new rearm entries, live server fills or true portfolio performance.

## Five chronological training/evaluation rounds

Small economic cash head: regularized deterministic logistic SGD with training-only winsorization/normalization, 14 original R9 causal entry context features plus the original frozen 155-feature model's P5 score. Matched 14-context-only head tests incremental P5 information. Train Jan–Apr to evaluate May, expand previous-month training through Jan–Aug to evaluate Sep. The full 155-model is NOT retrained; its saved primary score is heldout on the test month but IN-SAMPLE on cash-head TRAIN rows. This limits calibration reliability.

Explicit hypothetical economic scenario: fixed 0.01 lot, K=1.00 account currency for a $1 XAUUSD quote-price movement, C=0.20 additional roundtrip cash charge beyond spread already included in BUY Ask->Bid / SELL Bid->Ask. Original R9 signed cash is observed from original ledger price quotes with this hypothetical conversion, not actual broker statement.

| Test | Frozen ORIGINAL-side 5s target AUC | SAME P5 score, original trade cash-win AUC | 14 R9 context cash AUC | 14 context + P5 cash AUC | Original trades |
|---|---:|---:|---:|---:|---:|
| May | 0.70508 | 0.52393 | 0.52843 | 0.52913 | 31,615 |
| June | 0.71411 | 0.53380 | 0.53629 | 0.53774 | 33,946 |
| July | 0.73893 | 0.53604 | 0.53627 | 0.53827 | 32,536 |
| Aug | 0.73453 | 0.54259 | 0.53767 | 0.53936 | 31,214 |
| Sep | 0.72321 | 0.53434 | 0.52801 | 0.53114 | 33,001 |
| Equal-month mean | **0.72317** | **0.53414** | **0.53333** | **0.53513** | **162,312** |

Mean incremental original P5 feature gain over 14 causal R9 context variables: **+0.00179 ROC-AUC** across cash-head tests; not a demonstrated profitable trading advantage.

Descriptive within-month P5 probability-decile groups (NOT viable train-only cutoffs): pooled bottom 10%, 16,233 original trades, 14.25% after-cost winners, mean -0.41136 hypothetical account cash/trade; pooled top 10%, 16,234 original trades, 20.26% after-cost winners, mean -0.40483/trade. **Even the highest-P5 decile is substantially cash-negative under actual ORIGINAL R9 stop/trail behavior.** Win rate rankings differ from cash expectation.

## “How much AUC holds?” Original-exit survivor-conditioned diagnostic

The entry-time P5 score was never retrained at the later timestamps. Among original positions STILL OPEN at each indicated age, its ROC-AUC for ultimately ending ORIGINAL R9 trades with net-cash gain was:

| Original R9 age survived | Matching original R9 May–Sep positions | Pooled original entry P5 AUC vs eventual original-exit net cash win |
|---|---:|---:|
| 0 seconds | 162,312 | 0.53549 |
| 1 second | 137,598 | 0.54678 |
| 3 seconds | 92,157 | 0.54641 |
| 5 seconds | 64,893 | 0.54581 |
| 10 seconds | 31,167 | 0.54457 |
| 15 seconds | 17,181 | 0.54959 |
| 20 seconds | 10,261 | 0.54912 |

**Survivor-bias warning:** these are selected risk sets under the original stops/trailing, not trained new landmark models, not an answer to “would HOLD outperform EXIT NOW”, and not evidence of p5 directional continuation alpha 10 or 20s after entry.

## Execution, risk and preservation

- Source-exact score-to-original-entry-to-original-close research association and small fivefold original-policy cash-head training is COMPLETE.
- Actual alternative adaptive holding/exit simulation is NOT completed by this experiment; the original R9 trade entry/exit/rearm stream was frozen, not rerouted.
- Source feature archives are pinned to ORIGINAL R9 entry ordinals; modified exits may create new entry moments with NO trained source-exact score. Missing values must not be imputed from future or nearby original entries; genuine as-of online feature production is required before model-directed live trading.
- Live MQL5 standalone v1.94 compiled checkpoint at commit 813baf96f2b381be5fc7896aac8b08a966114948 remains unchanged. Its default model mode=1 SHADOW, not model-directed exits, and its exact 155-feature live online scoring producer is not complete. Critical R9 v1.90 rollback at 8729a6345655a7b4ea31facc81982004ee2b8921 is untouched.
- Coinexx ticklogger does not provide original trade server fills, final commissions, currency conversion or all-account governor state; K and C are explicit economic assumptions, not verified brokerage data.
- Jan–Sep were previously researched repeatedly; these historical folds are chronological retrospective checks, not pristine post-September OOS certification.
- No original Coinexx raw tick archive was read or duplicated in this particular integration experiment; original frozen source-derived inputs were joined in memory. Do not call this a new full causal on-policy MT5 replay.
- Training evidence shows weak cash discrimination. Do not turn on the entry veto, force additional runner holds or adjust account-gross-loss governor from these AUCs alone.

## Reproduction (existing ZIPs only)

From this GitHub branch, run the existing Python integration script lifecycle_calibration.py with source-dir pointing at the original frozen ZIPs, cash-per-one-xau-price-dollar 1.0, extra-roundtrip-cash-cost 0.20, and an output file for ONE small scorecard JSON. The script verifies original input schema, exact original model SHA, original R9 entry/exit source ordinal and source fold AUC, trains the small head five times and writes only the compact resulting scorecard. No 72M-tick rebuild.

**Verdict: cash AUC weak.** Original high AUC survives unchanged for its original target, but it does not transfer strongly to actual after-cost R9 trade wins. The next justified step is to train and test a POLICY-SPECIFIC conditional hold-versus-exit net-cash advantage using actual as-of liquidation Bid/Ask at the decision landmark, before using the score to control live R9 positions.
