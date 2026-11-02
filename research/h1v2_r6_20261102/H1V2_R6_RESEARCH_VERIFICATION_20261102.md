# H1V2 R6 — source-exact raw quote survival and opportunity timing experiment

**Status:** laboratory research completed 2026-11-02; **NO 80%-precision policy, NO on-policy real trading, NO MT5 compile**. The user explicitly authorized extreme four-month in-sample overfitting to discover what may be missing from later foresight V2. R6 adds a *strictly as-of* mechanism and independently checks transfer. It is not a new live trading strategy.

## Original science and source lineage

- Original original source audit was fully reread: `R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md`; main defects (A) lost within-second order, (B) wrong asymmetric loss, (C) old executed lane timestamps, (D) unfit Hawkes/Bayesian, (E) earlier eligibility-first bug, (F) inverted old 250ms SELL labels, (G) hardcoded path. R6 avoids the inverted SELL teacher, preserves original quote-ordinal R9 execution, and supplies only past data to the model.
- Parent repaired v2 Git SHA: `997dfdbd06157faa426c143874ad84277971570e`; original H1V2 SHA: `edce573d9c53b743dc5de1b0d741c81370af52c1`. R5 exact source parent (independent GitHub branch): `cefebf7e636d2baf2fa5c9d85af2a35e5f9ff730`. R6 isolated branch `carson/h1v2-r6-quote-survival-opportunity-20261102` started exactly from R5 parent.
- Four original Dukascopy Jan, Feb, June, July gzip source SHA-256 reverified against original `PINNED` using 32,290,648 existing original quote events. Candidate as-of arrays joined by exact source row index and epoch-ms, same-ms later quote ordinals prohibited in features. R2 independent labels and original R9 30-second exits **unchanged**.
- The sampling universe remains **15,000 candidate quote timestamps per month** (60,000 total, 120,000 independently labeled BUY/SELL actions), not full 15,401,392 250ms candidate market events. R2 strict 3-second STRONG_GOOD: entry first profitable net +$0.10 within 3s before -$0.10 adverse, R9 source-quote exit net at least $0.10 and spread <=$1.00. Class values: WRONG, NEUTRAL, WEAK_GOOD, STRONG_GOOD. No future class or price path in features.

## R6 advanced hypothesis and engineering

Previous R2-to-R5 research had shown high-density four-month in-sample memorization but almost no July-withheld strict entries. R5 revealed that the selected timestamps often have **no strong BUY or SELL even in hindsight**; choosing side alone cannot rescue the entry time. The **new R6 mechanism is an as-of quote-arrival survival regime**, not an additional OHLC grid:

1. At each original first-observed 250ms candidate quote, derive raw-ordinal windows of the last **8, 32, 128 and 512 observed quotes**. Independently retain 18 path/arrival fields per depth: quote ages, rate, gap coefficient of variation, signed true midpoint displacement as a feature only, total absolute travel, path efficiency, extrema/range, up/down revision counts, bid/ask synchronous and asynchronous revisions, lead pressure, spread instability, terminal range position, streak length.
2. Add 8 as-of instantaneous quote-state / gap-compression measures; 80 wholly new, source-ordinal, future-immune features. These are **best bid/ask quotes**, NOT actual order-book L2, market orders or market depth. Trading outcomes use original BID/ASK execution, not midpoint.
3. Refit the R5 six-mark (bid up/down, ask up/down, both up/down) Poisson cross-excitation on January + February past decay states; append its predicted future one-second *quote mark rates as as-of model outputs*, never actual future mark counts. R5 was an already-fit nonlinear-free GLM, not a continuous-time fitted Hawkes point process. R6 evaluates three opportunity→direction heads: (i) R5 fitted-mark baseline, (ii) baseline+80 raw quote-survival features, and (iii) baseline+80+5 coarse gap-surprise features. The first two share the same 115/95-round LightGBM hyperparameters; the third uses 45/35 rounds because its initial full-budget run exceeded the execution limit and is **not a hyperparameter-matched comparison**.
4. Factorize P(any STRONG_GOOD action now) and P(SELL given a strong opportunity) into independent heads; side-specific score = P(opportunity) × P(direction given opportunity). If neither qualifies a strict calibrated >80%-precision confidence gate, action=WAIT.
5. Train the 60k R6 diagnostic using Jan+Feb+June, **July withheld entirely**. Separately train Jan+Feb, attempt Wilson 95% lower >=80% June admission gate with >=150 selected events, then freeze for July; no June or July class information in that fit or its as-of inference.

## True held-out July RESULTS — independent sampled candidates, NOT nonoverlapping trades

| Candidate model | # input features | July top 1% strictly correct | July WRONG | July weak | Top-1% strict precision | If side were omniscient, strong opportunity at these 150 timestamps |
|---|---:|---:|---:|---:|---:|---:|
| R5-marked control (retrained same R6 setup) | 231 | 6/150 | 136 | 8 | **4.00%** | 23/150 |
| New R6 ordinal quote survival | 311 | **10/150** | 131 | 9 | **6.67%** | **19/150** |
| Additional R6 gap-surprise; reduced training budget | 316 | 8/150 | 134 | 8 | **5.33%** | 19/150 |

The causal quote-survival arm provides a small **positive relative point improvement** (6 vs 10 among 150), but **130+ WRONG among top 150 is catastrophic**. It has **no demonstrated 80% skew toward correct decisions**, and the 4-entry difference is not a statistically established generalizable edge. Adding coarse surprise also failed to improve over the survival arm. The R6 July top-5% strict precision was **5.73%** (43/750) vs R5 control **5.87%** (44/750), so even the relative top-1% improvement does not persist at wider admission.

**Critical honest calibration:** June is INCLUDED in the July-withheld training fit. High resubstitution top-1% June correctness (R5 control 132/150, R6 survival 138/150) is training exposure, not out-of-sample validation. When re-fitted Jan+Feb only and calibrated strictly on **unseen June**, all 3 arms failed to yield ANY Wilson-eligible threshold. July qualified admissions under these frozen gates = **ZERO**. This is independent of the deliberately overfit oracle's 513,262 hindsight opportunities and 241,459 stricter FAST3S hindsight opportunities.

## Tests and source-validity claims

- **35/35 passed** combined original H1V2 + R2 + R3 + R4 + R5 + R6 Python unit tests, including new R6 future-path corruption invariance, equal-ms later ordinal exclusion and same-aggregate different-order distinction. The original R9 execution engine was not changed. The previous original R9 ActivePath 1,916 sampled lifecycle parity checks were **not rerun in R6**; rely on original preserved source-exact receipts.
- Original Jan/Feb/Jun/Jul gzip input SHA-256s verified by `fit_survival_rejection.load_raw_asof` and stored in machine JSON results. Newly computed raw quote-as-of 60k matrices persisted as 4 compressed `.npz` files, checksum pinned in machine report. All model files and results saved in the standalone R6 recovery ZIP.
- First attempt completed two arms then timed out before third, kept the negative interim result. Final run restored the frozen two pre-trained R6 model pairs and ran the third arm with explicitly reduced complexity; no performance assigned to the unfinished high-complexity third-arm attempt.
- **No special confidence inflation** by choosing only future-confirmed winner rows for training or evaluating hindsight oracle selection. If the 80% target cannot be attained, mark fail without weakening calibration. No risk/margin/latency/realistic brokerage replay, monthly nonoverlapping policy trade count or Coinexx feed parity certified.

## Research conclusion and next distinct hypothesis

**R6_QUOTE_ARRIVAL_SURVIVAL_RELATIVE_TOP1_SMALL_GAIN, R6_MORE_GAP_SURPRISE_FAIL, R6_STRICT_JULY_GATE_NO_ADMISSIONS.** R5 confirmed quote-mark intensity forecast improves on a null but does not solve entry opportunity. R6 confirmed that adding raw-ordinal quote gap/run compression can improve a tiny top-ranked July subset (10 vs 6) but not 750 wider entries or any 80%-qualified calibrator. Do not repeat prior R3 112 failed grids, R4 standard mark classifier, R5 fitted mark GLM, or R6 low-power survival tail without a new rationale.

Next candidate innovation is explicitly source-ordinal **competing-risk survival to imminent favorable excursion vs adverse excursion** with hazard ratio head conditioned on state, variable quote-time exposure, cross-session hazard recalibration and blocked source-domain assessment. It MUST respect initial 250ms first-observed timing and cannot use oracle first-pass outcome during its own feature construction. Especially prioritize **time selection / WAIT** rather than ever more direction-side grids. Only after genuine time discrimination should a cost-aware and class-calibrated full-market one-position 250ms execution replay be considered.

## Restore

1. Restore original R9/H1V2 full dependency kit and original R2/R3/R4/R5 source-exact dependencies without rewriting them.
2. Download exact original four Dukascopy gzip files from PRIMARY Drive folder `https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV` and verify raw pinned hashes.
3. Extract this R6 recovery ZIP to `/mnt/data/h1v2_r6`; it carries source, tests, `results/R6_SURVIVAL_ASOF_{01|02|06|07}.npz`, three frozen pairs of July-withheld and June-calibration models, full machine receipt and manifests. The code uses existing local R2/R3/R4/R5 prepared source/arrays; no old 250ms inverted SELL teacher.
4. `PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src:/mnt/data/h1v2_r5/src:/mnt/data/h1v2_r6/src pytest -q /mnt/data/h1v2/tests /mnt/data/h1v2_r2/tests /mnt/data/h1v2_r3/tests /mnt/data/h1v2_r4/tests /mnt/data/h1v2_r5/tests /mnt/data/h1v2_r6/tests`.
5. Run `python /mnt/data/h1v2_r6/src/fit_survival_rejection.py` under above `PYTHONPATH`. Files with known fitted model names are reused only if their original hashes match the ZIP manifest. If retraining from scratch, delete only the R6 derived model files; never delete parent results or original source.

## Addendum: authorized four-month deliberately contaminated high-capacity training

This addendum was completed **after** and **independently from** the July-withheld negative tests above. User explicitly requested extreme overfit across Jan/Feb/June/July as an offline teacher. The model was trained on **all 60,000 sampled quote timestamps and their future outcomes across all four months**, then ranked the very same rows — therefore **every reported rate below is an in-sample resubstitution (label-exposed) result, not a forecast**. The original R9 quote-execution, R2 hard-labels, as-of 80-column R6 quote survival inputs, R5 as-of fitted mark intensities, and raw source SHA pins were not modified.

Two distinct runs with the **same original labels and as-of source features** were completed, with their frozen model pairs and full output bytes preserved:

- `R6_FOURMONTH_EXPLICIT_TRAIN_LEAKAGE`: opportunity/conditional-side 65/48 LightGBM rounds, 43/31 leaves. Training top 1% per month: Jan 140/150 correct, Feb 138/150, June 142/150, July **119/150** (only 79.33%). Its failure in the most difficult source month led to a higher-capacity **training-memorization** experiment; no model was assessed prospectively.
- `R6_FOURMONTH_SUPERCAP_EXPLICIT_TRAIN_LEAKAGE`: opportunity/conditional-side **120/90 rounds, 63/47 leaves**, still trained on all four months' hindsight classes. **Same-row top 1%: 150/150 correct and 0 wrong, 0 neutral, 0 weak per month**; four-month total **600/600 = 100.0% TRAINING precision**. This is *by construction a memorized resubstitution* and provides no forward performance claim. Nominal Wilson lower about 97.50% per month assumes independent observations, which quote rows are not; do **not** use it as deployment calibration.

| Four-month **TRAINING same-row** month | Top 1% STRONG/Wrong | Top 2.5% STRONG | Top 5% STRONG | Top 5% strict precision |
|---|---:|---:|---:|---:|
| Jan | **150/0** | 375/375 | 704/750 | 93.87% |
| Feb | **150/0** | 375/375 | 731/750 | 97.47% |
| June | **150/0** | 375/375 | 733/750 | 97.73% |
| July | **150/0** | 349/375 | 430/750 | **57.33%** |

June/July top-ranking training rows are label-exposed, not an untrained-month test. Strong classes are sparse and the contamination is profound: **this does not establish that 600 retrospective sampled selections could produce 94,150 causal nonoverlapping R9-comparable trades**. At top 5% July accuracy falls substantially. The actual R6 JanFebJune fit → genuinely July-withheld top 150 remains **10 STRONG, 131 WRONG, 9 WEAK**, with zero strict Wilson-qualified admissions after JanFeb→June calibration. The difference measures **failure of transfer**, not economic signal discovery.

All four-month resubstitution model files, 2 output JSON machine receipts, stdout logs and source script `src/overfit_survival_fourmonth.py` are in the **UPDATED complete R6 recovery ZIP**, separately from previous earlier R6 ZIP. The base R6 35/35 tests still pass. Science status: `R6_ALL4_SUPERCAP_RESUB_600_OF_600 / R6_JULY_WITHHELD_TOP150_10_OF_150 / NO_APPROVED_CAUSAL_POLICY`.
