# H1V2 R11 — Source-Exact, Additive Entry Mechanism Research

**Research classification:** isolated causal mechanism engineering and synthetic-unit verification only; not a trading policy, not a fresh full-month fitted model, not broker execution or MT5 deployment.

**Owner instruction:** Never use this README as a substitute for the complete original sources, the entire 33k-character source forensic audit, the original four-month raw tick files, all R2–R10 scientific reports and the complete append-only Google Drive recovery ledger. This README is an *executable dependency and restoration index*, not a compressed narrative summary.

## Frozen ancestry, source and audit

- Repository: https://github.com/AnhTranHarris/gold-MUWHAHA-miner
- New branch: carson/h1v2-r11-causal-hazard-entry-contract-20261102, created from exact R10 parent `a22218b14ed387ecc0dea9ba8d867cd33c4b4ee7`.
- Original H1V2 teacher `carson/h1v2-fourmonth-hindsight-teacher-20261102`, SHA `edce573d9c53b743dc5de1b0d741c81370af52c1`, completely unchanged.
- Repaired R9 v2 v5 `carson/r9-v2-entry-asymmetry-repair-20261102`, SHA `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`, completely unchanged.
- Original R9 H1V2 hyperreject `f559f9768331bfa520f090bde02dcd108d22b661` retained, negative control.
- Primary R11 Drive folder https://drive.google.com/drive/folders/1V2G9fC665cPHFI8VXbRHwmiNy1JQy-Cy
- **FULL technical audit, all 15 defects and experimental reasoning:** https://docs.google.com/document/d/1KhPl9eZqUJZM8vh7W8n93tUQWwbLXhMhcPZDXEN909E/edit
- **APPEND-ONLY experimental ledger:** https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit
- Full proposed new-hypothesis tests: https://docs.google.com/document/d/1tv0t1bBDsnuwpGq79AzbL17kTU0xE2lmlJBiaFF7zdo/edit
- Raw exact original Python sources/test transport: https://drive.google.com/file/d/1bMkfL-K0s9rcNn1jnLSykS_SiWWwjzax/view
- Extra fitted-hazard code/test transport: https://drive.google.com/file/d/1SWq7s_6aKtlzD17OVQHlPBAIbImh9rOz/view
- Source file SHA-256: `SOURCE_EXACT_SHA256_MANIFEST.json`. All files uploaded to Github via text-exact source transportation from the raw Drive files, and fetched back to verify exact text equality.

## Why each new source module exists and what it actually does

### `src/entry_contract.py` — source-exact candidate universe

- Reimplements the frozen original teacher candidate contract, first observed quote of occupied 250ms bucket, warmup 300000ms, gap reset on gap >=300000ms, spread <=1.50.
- Adds an isolated **research-only v5 gap adapter**: gap >15000ms restarts subminute quote epoch, 300000ms new warmup. Spread configurable, not an assertion that every other full v5 runtime gate is emulated.
- `reconcile` verifies exact original teacher ordinals against reconstructed original candidates *before* filtering. Unknown new candidate ordinals or parity mismatch aborts; no future outcomes invented.
- Optional same original hindsight `schedule_oracle` recalculate on the v5-filtered labels. This is still future privileged, never an online model.
- `run_original_month` verifies source raw SHA and exact original teacher labels SHA before applying the candidate adapter. Four-month full run **NOT EXECUTED in R11 initial source checkpoint** because raw source files are on Google Drive, not the local test runtime.

### `src/event_graph.py` — event-time causal graph and corrected bid/ask quote marks

- Nine mutually exclusive quote mark types retain original six-mark taxonomy and introduce Bid-up/Ask-down spread contraction and Bid-down/Ask-up spread widening that legacy R4 marked as zero.
- True observed rolling 250ms,1s,3s,15s,30s,60s,300s time windows, not a fixed number of quote changes.
- Incremental monotone extrema queues recover high/low order and ages. Computes signed displacement, signed path efficiency, absolute mid path, range, terminal location, mean spread, all nine mark counts, two quote-leadership transitions and mixed-mark fractions. Future price/teacher outcome never included in features.
- Uses bounded quote-event memory sized to actual max 300sec occupancy with vectorized candidate output. The original 48-quote R10 grammar is an immutable control, not removed.
- Full-month 32M quote extraction not run yet. The initial 15 randomized streams x20 candidates x7 windows showed extrema-range parity with direct brute-force slicing. A future run must profile memory/CPU and compare full original source parity and gaps.

### `src/hazard_contract.py` — right-censored true first-passage targets

- Generates interval risk exposure and three first-passage causes over [0,250,1000,3000,5000,15000,30000]ms. BUY and SELL retained independently.
- Original H1V2 `first_event`, `first_event_ms`, `exit_ms`, `exit_tick_index`, `net` used **OFFLINE as labels only**. Missing source-end terminal outcomes are not relabeled as wins/losses. Original strict criterion remains separate from simple positive net.
- Replaces R10 NaN-weighted group payoff arithmetic with explicit completed, censored, wrong, neutral, strict-good, finite net sums and censored-group fail-closed safety. Historical R10 results immutable.

### `src/competing_hazard_model.py` — fit-ready discrete competing-risk student

- Builds cause-specific person-period rows from risk exposure. A partially observed censored interval *without witnessed first passage* is excluded from the no-event training class rather than mislabeled as a survivor.
- Fits independent BUY or SELL three-way survival/favorable/adverse conditional interval LightGBM when genuine source matrices are supplied. Temporal bin index is known at query time; no future price included in predictor features.
- Probability integration conserves mass: survival-to-bin multiplied by first favorable or adverse conditional hazards; outputs [BAD,NEUTRAL,GOOD] to a separate economic router.
- Current tests use synthetic causally controlled data; **no 2026 original four-month fit, no fitted model weights and no threshold or accuracy claim yet**. Preserve entirely separate validation calendar and calibration.

### `src/action_router.py` — independent eligibility-first economic arbitration

- Uses BUY and SELL independently calibrated probabilities [BAD, NEUTRAL, GOOD], Wilson-style *external* lower confidence inputs, gain/loss magnitudes, conservative extra execution costs, CVaR penalty, and spread.
- Rejects a side if its absolute correctness, bad-risk, expected net and spread gate fail. Only then compares eligible actions; a rival that already failed economics cannot veto the sole eligible side through a misleading raw probability score.
- Competing eligible actions require minimum directional separation. If neither qualifies: WAIT. No arbitrary count-fill, no retrospective optimizer in online input.
- IMPORTANT: no source-fitted calibration exists in this checkpoint. Synthetic tests of the controller are not trading tests.

### `src/cache_contract.py` — content-addressed fail-closed model identity

- Freezes model role, feature version, source file paths plus SHA-256, hyperparameters, source calendar split and content-derived contract SHA. Every saved weight file must match its own SHA and the entire exact dependency contract before reuse.
- Replaces unsafe *concept* of 'the model file already exists, reuse' from prior R6/R9. Does not patch those historical files in place. The new protections must be applied on any next fitted research checkpoint.

## Source-exact local tests and failure history

Install runtime dependencies `numpy`, `numba`, `pandas`, `scipy`, `scikit-learn`, `lightgbm`, and `pytest` as appropriate; original teacher also requires `h1v2_teacher.py` from immutable R10 ancestor.

From this research directory:

```bash
PYTHONPATH=src python -m pytest -q tests
python -m compileall -q src tests
```

Initial post-repair run: **21 passed** (local test environment). Separate randomized rolling-window extremum test: 15 independent streams, 20 candidate ordinals each, seven event-time windows, passed. This is **local test evidence**; no connected cloud CI or real source tick suite claimed.

During development, test-first failures were preserved and corrected before Github upload:
1. Numba `@njit` required an ordinary optional argument list instead of keyword-only typed signature in `candidate_quotes`. This was repaired and 5 original contract tests passed.
2. Initial independent action arbitration incorrectly vetoed the only economically eligible SELL when BUY had a numerically greater raw GOOD posterior but had failed its own calibration. Fixed by applying directional rivalry margin only if both actions independently pass; final 18 then 21 tests passed.

## Full data still required for performance qualification

Raw Dukascopy exact original tick archives Jan/Feb/June/July SHA pins are in `entry_contract.PINNED`. The original H1V2 teacher full labels must be generated/restored and verified. Then:
1. Regenerate 250ms original candidate universe; check exact ordinal identity and source hashes. Run v5-gap intersection, daily/week/month counts and original DP hindsight recomputation.
2. Produce new mixed-mark/5m causal graph, exact source parity/future mutation regression, full memory/performance profiling and source hashes.
3. Build true cause/exposure risk arrays per original H1V2 quote-side exit, test genuine censoring fractions.
4. Fit new student on frozen chronology, pre-register model hyperparams, save model weight/feature/label and per-block SHA receipts. Any failed calibration means no qualified policy.
5. Perform purged chronological validation, then truly untouched out-of-sample source and broker domain, exact one-open-position on-policy replay, realistic commissions/slippage/margin, active day/ISO week/month breakouts and risk.
6. Preserve owner R9v2 strict 85%-of-SYNTH monthly throughput, >=80% first-15s and 30s strict by every active day, week and month, positive net, account survivability. Historical H1V2's 80%-month-only is not enough.
7. No MT5/MQL5 activation until all gates pass.

## Explicit scientific verdict at code checkpoint

**SOURCE_ADD_ON_CHECKED / 21_LOCAL_TESTS_PASSED / ORIGINAL_DATA_FULL_MONTH_NOT_RUN / NEW_MODEL_NOT_TRAINED / OOS_NOT_QUALIFIED / EXECUTION_NOT_QUALIFIED / EA_UNCHANGED.**

This branch is an isolated H1V2 causal research successor, not a rewrite of prior scientific history or a live trading model.
