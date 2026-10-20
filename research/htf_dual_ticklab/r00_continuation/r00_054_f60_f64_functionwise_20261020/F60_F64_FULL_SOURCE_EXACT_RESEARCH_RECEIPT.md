# R00-054 F60–F64 — SOURCE-EXACT FUNCTIONWISE FILTER RESEARCH & ANTI-DRIFT CONTINUATION (2026-10-20)
**Classification:** RESEARCH-ONLY. No qualifying 71%-correct / 90%-bad causal filter found; no funded trade or MT5 execution validation. Written to preserve complete positive *and* negative evidence. Historical FILTER08 teacher is same-broker-month hindsight-fit and is NOT a tradable result.
**Authority:** full binding, append-only original owner document https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit
**Approved source:** broker-native Coinexx XAUUSD bid/ask quote feed and independent Dukascopy XAUUSD bid/ask; separate real 2026 Jan/Feb/June/July source, Coinexx UTC -120min winter / -180min summer; exact original R00-054 events and +30..32-second first-midpoint >$0.10 labels. Two brokers are NEVER blended into one funded account.
**Object:** replicate individually the observed near-lossless HISTORICAL FILTER08 behavior with distinct causal functions, sequential specialists, calibrated cooperative vetoes; preserve >=71% correct and remove >=90% incorrect **EACH** broker-month and no newly failed eligible source R9 correct/emitted hour/day/week/month. Minimize further unnecessary destruction of correct signals. Histories complete; June/July historically exposed, not blind.

## 0 — Binding lineage and state

Canonical original FILTER08: https://drive.google.com/file/d/17YePE46goX2ChbL89LLNbqS5ddYDkms_/view . Original FILTER07: https://drive.google.com/file/d/1dOUVcoK-Po_vF3TCUcCAAcWM5KNZOwo5/view . Previous F27 failure preserved in master Appendix B. Prior F29 portability, F30–F59 heterogeneous specialist attempts, and complete broker-native F39/F42 inputs are retained in their original existing paths. No test here rebuilds the established tick backtest engine.
FILTER08 source ZIP exact SHA256 `7edaddf30f3a19cafd364a270333c6f87962960233f9d10ccbfb6e2a3b23b2ad`. Eight original .npz score/truth vectors were CRC-opened from this exact ZIP; original event IDs, sides and counts checked against source RESULT_*.json in F60.
Functionwise prior F08 selected five score variants: (1) binary trained fitted correctness p; (2) quote_phase p+0.015*tanh(clip(X[:,47]+X[:,52],-6,6)); (3) structure_conflict p+0.015*tanh(clip(X[:,31]*side,-6,6)); (4) matured_feedback p+0.015*tanh(clip(X[:,87]-.5,-1,1)); (5) cooperative_3 p+0.012*(quote+structure+matured). The claim that all five were independently deployable specialist models is FALSE: overlays are perturbations of the SAME same-month fitted LightGBM teacher, not five independently validated filters. Selected eight historical policies comprise five binary, two quote_phase and one structure_conflict. Every original backtest signal remains in denominator.

## 1 — F60 FULL ORIGINAL FILTER08 IN-SAMPLE FUNCTION ORACLE AUDIT (NO PREDICTIVE CLAIM)

F60 used only the exact originally saved `FITTED_CLASSIFIER_SCORES_*.npz` score vectors, truth classes, original keep mask, and original RESULT reports. It tested one PREDECLARED universal numeric cutoff at 0.0, 0.1 ... 1.0 on each original source, with all 8 per-hour/day/week/month reference floors recomputed from existing approved R9 reference. Selecting cutoff after viewing full labels is prohibited online; even predeclaring a numerical score cut cannot cure the fitted teacher having used each test month label in training.
**Verified teacher at score>=0.50 in-sample:** total original four-month 2,574,251 original signals, 1,208,071 correct, 1,366,180 bad; correct retained **1159812 (96.00528%)**, bad rejected **1347808 (98.65523%)**; passes 71% and 90% on EACH historical broker-month, with zero newly failed R9 reference hours/days/weeks/months for every month. However this is an illegitimate forward result (same-month future label overfit). If called a live win, that would constitute scientific fraud.
Universal threshold detailed historical score frontier:

| Score >= | Correct retention | Bad rejection | Minimum broker-month good | Minimum broker-month bad | Eight-month historical numeric gate |
|---|---:|---:|---:|---:|---|
| 0.0 | 100.000% | 0.007% | 100.000% | 0.000% | NO |
| 0.1 | 100.000% | 8.873% | 100.000% | 4.037% | NO |
| 0.2 | 100.000% | 37.509% | 99.999% | 24.042% | NO |
| 0.3 | 99.983% | 70.494% | 99.945% | 55.453% | NO |
| 0.4 | 99.565% | 91.462% | 99.166% | 83.142% | NO |
| 0.5 | 96.005% | 98.655% | 94.174% | 96.651% | YES, hindsight only |
| 0.6 | 83.434% | 99.897% | 78.356% | 99.687% | YES, hindsight only |
| 0.7 | 59.249% | 99.997% | 52.720% | 99.990% | NO |
| 0.8 | 29.568% | 100.000% | 24.744% | 100.000% | NO |
| 0.9 | 6.697% | 100.000% | 5.052% | 100.000% | NO |
| 1.0 | 0.005% | 100.000% | 0.000% | 100.000% | NO |

Fixed score=0.50 all eight source/mth exact quota and retention results:

| Broker | Month | Original correct retained | Bad rejected | Newly failed eligible source R9 h/d/w/m |
|---|---|---:|---:|---|
| coinexx | 01 | 97.77147% | 96.65129% | 0/0/0/0 |
| coinexx | 02 | 96.76156% | 98.57679% | 0/0/0/0 |
| coinexx | 06 | 95.94302% | 99.36565% | 0/0/0/0 |
| coinexx | 07 | 94.17419% | 99.35343% | 0/0/0/0 |
| dukascopy | 01 | 97.41774% | 96.81490% | 0/0/0/0 |
| dukascopy | 02 | 94.39978% | 99.20624% | 0/0/0/0 |
| dukascopy | 06 | 95.59668% | 99.60407% | 0/0/0/0 |
| dukascopy | 07 | 94.97193% | 99.50314% | 0/0/0/0 |

Exact class score distribution and original wrong/opposite/neutral removal by month: `F60_ORIGINAL_ALL_8_CLASSWISE_SCORE_DISTRIBUTIONS.json`; complete 88 threshold rows: `F60_ORIGINAL_ALL_8_SCORE_THRESHOLD_CLASS_BREAKDOWN.json`; source code `f60_original_overfit_function_oracle_atlas.py`, `f60_quota_check.py`.

## 2 — F61 DISTINCT NEUTRAL / OPPOSITE CASCADE AND CORRECT-SIGNAL SHIELD

Parent: genuine F57 separately trained February-first60 quote opposite Q, HTF structural opposite S, neutral reachability N, 33s matured correctness M and joint correctness J. Quarantined source F08 teacher is NEVER an input. F61 stages: N risk then opposite Q*S concurrence, with optional correct shield (M+J). Source-local FEB last35 independent budgets (7 options), full original Feb R9 floor tests. Six predeclared functional architecture variants, per-broker February frozen masks, JunJul *strictly unchanged*. Input paths require F39 ordered source quote, F42 trailing 1s..180s source-native path, F44 source identity and F53 previously matured signal; all MQL5-portable arithmetic but model conversion/parity pending.
| Frozen candidate | Four-month June+July correct kept | Bad rejected | Neutral rejected | Opposite rejected | Stage1 bad | Stage2 incremental bad | New R9 quota misses | Pass |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| neutral_first_shield | 359488 (65.588%) | 244426 (35.772%) | 59491 | 184935 | 54399 | 190027 | 4 | False |
| neutral_structural_concurrence | 336194 (61.338%) | 275450 (40.312%) | 67856 | 207594 | 57316 | 218134 | 6 | False |
| neutral_first_hard_correct | 302034 (55.106%) | 325172 (47.589%) | 84988 | 240184 | 52759 | 272413 | 7 | False |
| opposite_first | 364981 (66.590%) | 241471 (35.340%) | 61785 | 179686 | 69984 | 171487 | 5 | False |
| neutral_reachability_first | 364981 (66.590%) | 241471 (35.340%) | 61785 | 179686 | 69984 | 171487 | 5 | False |

**Negative:** no F61 candidate meets 71%/90% AND zero R9 quota losses per month. Stage budgets that improve wrong rejections also lose too many original good events, especially after June/July regime transfer. All per broker-month scores, stage attribution, selected Feb source-specific budget, and 42-or-84 candidate policy rows retained unabridged. One predeclared family has no eligible Dukascopy Feb threshold and was therefore NOT scored as valid cross-broker. F61 runtime initially timed out during six repeated model-predictions; code was changed only to memoize the exact same fitted head outputs for faster execution. Experiment policy/thresholds unchanged.

## 3 — F63 ORIGINAL TEACHER VERSUS F44 CAUSAL FUNCTIONAL DISCRIMINATION

Exact F08 event IDs and original 3-class labels matched F44 frozen out-of-fit causal score arrays (both brokers June/July). Source event timestamp and truth vectors assert exact identity. For 8 causal heads and one historical hindsight teacher report class-wise ROC AUC for good-vs-opposite and good-vs-neutral. The 71% good retained diagnostic threshold is *chosen using evaluated month truth* solely as an upper class-ranking diagnostic; it is NOT a legitimate train/test policy, no P&L.
| Head / Original oracle | Mean correct AUC | Good vs opposite AUC | Good vs neutral AUC | Wrong reject at hindsight 71%-good budget |
|---|---:|---:|---:|---:|
| F08_SAME_MONTH_FITTED | 0.99852 | 0.99870 | 0.99790 | 99.994% |
| OOF_good | 0.51678 | 0.49992 | 0.57564 | 31.133% |
| OOF_opp_guard | 0.49152 | 0.49747 | 0.47241 | 28.001% |
| OOF_neutral_guard | 0.53021 | 0.50155 | 0.62910 | 33.066% |
| OOF_min_three | 0.51669 | 0.49992 | 0.57524 | 31.127% |
| OOF_geo_three | 0.51594 | 0.49941 | 0.57359 | 31.036% |
| OOF_weighted | 0.51447 | 0.49940 | 0.56727 | 30.833% |
| OOF_min_err | 0.49166 | 0.49750 | 0.47289 | 28.000% |
| OOF_avg_error | 0.50832 | 0.49842 | 0.54332 | 29.969% |

**Identified function-specific bottleneck:** historic teacher good-vs-opposite AUC 0.9987 and good-vs-neutral AUC 0.9979 (same-month fit, unusable). The F44 predicted correctness head good-vs-opposite AUC 0.49992, effectively no average transfer separation, while its neutral guard gives good-vs-neutral AUC 0.62910, measurable but insufficient. Multiple correlated heads cannot manufacture new information. Build independent opposite-direction source-native mechanism before adding still more arbiter complexity.

## 4 — F64 SOURCE-NATIVE MICRO/MACRO SIX PER-ERROR FUNCTION HEADS AND SEVEN COOPERATIVE POLICIES

F64 is a NEW source-native native MQL5-implementable artifact: every original F39 30 ordered quote and F42 49 trailing temporal values combined in 79-dimensional event-aligned past-only input; six causal feature families (ordered quote, temporal lag, phase acceleration, quote+phase, temporal+phase, full) each separately trained for GOOD-vs-OPPOSITE and GOOD-vs-NEUTRAL, generating twelve frozen lightweight heads. Source-specific model train is FEB first60 every fifth event; top-four max standardized mean-shift contrasting original signal label; February last35 independently calibrates seven cooperative KEEP policies and R9 full-month constraints. No label from June/July influences feature selection, training, or cutoff; no hindsight teacher input.
| F64 candidate | Correct retention JunJul | Bad rejected JunJul | Opposite removed | Neutral removed | Worst month correct kept | New R9 quota misses | Pass |
|---|---:|---:|---:|---:|---:|---:|---|
| orthogonal_and | 96.330% | 5.782% | 19627 | 19879 | 93.505% | 2 | False |
| double_failure_min | 97.177% | 4.581% | 14895 | 16406 | 95.197% | 1 | False |
| error_max | 93.574% | 8.578% | 34064 | 24547 | 90.298% | 7 | False |
| temporal_protection | 95.735% | 6.684% | 23297 | 22376 | 93.828% | 4 | False |
| micro_phase_majority | 76.650% | 26.628% | 128048 | 53899 | 66.754% | 73 | False |
| neutral_first | 96.008% | 6.191% | 21373 | 20930 | 93.521% | 2 | False |
| opposite_first | 82.947% | 21.038% | 92810 | 50942 | 73.837% | 27 | False |

**MQL5 portability:** `F64_Functionwise_MultiHead_ResearchOnly.mqh` consists of exactly the separately FEB-frozen 2-broker x 12-head coefficient/normalizer arrays and MQL5 IF-family inference arithmetic. Six source-broker/month sampled tests compare Python reference probability with independently recomputed exported MQL5 mathematics: maximum absolute difference <=1.1921e-7. This is a Python arithmetic EMULATION ONLY; native MT5 MetaEditor compile, live tick buffer synchronization and executable ONNX parity (for F57) are still REQUIRED. No live authorization. Feature input exact calculation must preserve F39 quote-index and F42 trailing millisecond timestamp alignment.
All model source coefficients, source feature indices, frozen February thresholds, all FEB candidate grids, four broker-month full performance rows, Python porting test code, and output-native `.mqh` are packed unabridged in this ZIP.

## 5 — F62 attempted but interrupted; no F62 full results claimed

F62 planned original F57 independent head AUC across Feb last35 and original June/July. Its extended full-array full-model scoring timed out after some source/month diagnostics; model-stage files never written and original F57/F44 models remain intact. F62 is **INCOMPLETE**, no AUC values from the attempted run are qualified; the source and exact partial log remain preserved in this pack for reproducibility. Next test should avoid repeated full-model inference by caching immutable per-head scores per month and computing class diagnostics from those arrays.

## 6 — Next ranked research hypothesis: opposite-side event outcomes need a genuinely new discriminant

New hypothesis H-F65 (NOT RUN): an independent source-native opposite-error **event microphase transition** function, with quote-run polarity transition duration, flow-efficiency conditioned on current spread, event phase relative to last fully known HTF pivot, and side-dependent competing hazard conditioned on past completed 33-second event labels, may provide new (nonredundant) opposite-class information. Freeze computation formula BEFORE evaluation; use parent F39/F42 arrays only if exact quote raw field subset available; train on Jan/FEB predeclared time splits, freeze on February and report every function standalone (good retention, opposite recall, neutral recall, source quota) before a staged cooperative arbiter. H-F65 claims no expected performance improvement; it must compete against original best F59 corrected-zero-quota frontier and original F61/F64. Do not tune on exposed June/July.
Do not substitute external market tapes, time-shift, delay entry, change side, alter original event set or exploit current event +30s label in inference. Account execution P&L is a separate later investor gate requiring fills, spread, slippage, margin, survivability $100/$200. No result can be called a qualified MT5 EA or profitable strategy absent those tests.

## 7 — Continuation lock: NO DRIFT, NO AMNESIA, NO SUMMARY REPLACEMENT

LATEST COMPLETE RESEARCH EXPERIMENTS: F60 original teacher oracle threshold/quota, F61 staged classification failure, F63 causal function separability audit, F64 source-native twelve head family. F62 partial/interrupted. Prior F59 best zero-quota independent structure_guarded retained 73.42% of good and rejected 27.83% of bad — negative versus 90% target. F60 hindsight teacher at 0.50 is spectacular ONLY by same-month fitted leakage. DO NOT treat it as a causal candidate. F64 training/code/parity verified but rejected.
READ FULL ORIGINAL SOURCE DOC and ORIGINAL FILTER08 SOURCE ZIP and this entire 7-section report and ALL JSON/code files before any new build. Previous assistant recaps are mere pointers. Verify GitHub/Drive HEAD and their actual SHA before stating synchronized commits. Preserve failing models/ledgers separately, never overwrite prior branches or original raw tick source. Next experiments MUST evaluate each function independently first then cooperative conditional error intersections, report entire Pareto with strict <=cut publication clocks and zero fabricated fills. Preserve all candidate failed tests, errors, source provenance. No speculative algorithm may be described as demonstrated profit or accuracy.
No automation/daily task created. Work in the current execution, never promise endless unattended research. This archive is a **research checkpoint**, NOT solution acceptance.