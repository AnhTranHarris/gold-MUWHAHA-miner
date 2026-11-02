# R9 v2 — Source-exact ordered first-30-second hindsight teacher training

**STRICT ENTRY-SURVIVABILITY RESULT: FAIL. No trained policy approved, no v2 execution changes promoted.**

## First-event laboratory labels

Post-entry actual real-tick quote sequence was replayed for all 2,481,012 previously executed baseline entries. At the earliest executable quote after entry, classify favorable event when exiting at bid (BUY) or ask (SELL) would produce net +$0.10 or better (including the existing $0.02 fee); classify an adverse event when executable liquidation quote moves at least $0.10 against the liquidation-side quote at entry (spread separately accounted for). Both prices are observed from actual source ticks, in original chronological event order even when timestamps are equal. An accepted teacher-positive example must encounter favorable event first AND the recorded R9-style close must realize positive net within <=30 seconds. If neither event occurs, mark neutral; all other cases, including late market-open timeout, are not success. This is a research-specific $0.10 adverse diagnostic, **not** the broker initial stop of $0.30 plus spread. The original R9 holding/exits remain unchanged.

## Full source-month first-event label availability (no sampling)

| Source | Month | Baseline entries | Strict favorable-first successful | Strict supply rate | 85% SYNTH floor |
|---|---|---:|---:|---:|---:|
| coinexx | 01 | 414,938 | 112,072 | 27.01% | 23,783 |
| coinexx | 02 | 477,916 | 138,041 | 28.88% | 28,495 |
| coinexx | 06 | 387,283 | 102,390 | 26.44% | 27,031 |
| coinexx | 07 | 312,856 | 78,332 | 25.04% | 20,725 |
| dukascopy | 01 | 238,644 | 33,218 | 13.92% | 23,783 |
| dukascopy | 02 | 236,293 | 33,737 | 14.28% | 28,495 |
| dukascopy | 06 | 235,139 | 35,318 | 15.02% | 27,031 |
| dukascopy | 07 | 177,943 | 20,552 | 11.55% | 20,725 |

All eight sources have mathematically sufficient strict favorable-first winners for >=80% of their separate monthly trade-count floors. However, Dukascopy July has 20,552 strict good candidates versus a 20,725 minimum count; an oracle restricted to **100% good entries** would need 173 extra trades, although a permitted 80%-survival policy could include some non-successes. This is a hindsight supply ceiling, not causal predictability.

## Chronological student with ordered first-event labels

The exact same 89 causal runtime features and LightGBM/Hawkes-style quote-signature student were re-trained; model thresholds were calibrated only on dates before a separate check window in each source-month. SYNTH teacher marker was offline sample weight (+5% only for true real-tick positives), not runtime input. 9 historical NP false-class quantiles searched, and no calibration choice produced both >=80% strict favorable-first positive outcomes AND positive P&L. Chosen negative diagnostic thresholds are not approved and represent tiny filtered subsets only.

| Source | Month | Diagnostic filtered count (check dates) | Strict first-event winrate | Diagnostic net | Check days clearing 80% |
|---|---|---:|---:|---:|---:|
| coinexx | 01 | 541 | 43.07% | $-57.62 | 0/10 |
| coinexx | 02 | 58 | 46.55% | $-3.36 | 0/8 |
| coinexx | 06 | 81 | 48.15% | $-9.17 | 1/11 |
| coinexx | 07 | 137 | 46.72% | $-20.08 | 1/12 |
| dukascopy | 01 | 440 | 25.45% | $-301.93 | 0/10 |
| dukascopy | 02 | 13 | 46.15% | $-7.97 | 2/8 |
| dukascopy | 06 | 151 | 35.10% | $-70.68 | 0/11 |
| dukascopy | 07 | 286 | 29.02% | $-169.74 | 0/12 |

## Final four-month retrospective source-specific fit: optimistic 85%-volume analysis

Final students were trained on **all** January, February, June, July real outcomes. For each month an unrealizable ex-post threshold picked the model top scores equal to exactly 85% of R9 SYNTH. This is only a *training-set discriminability ceiling*, not deployable trade performance.

| Source | Month | Trade quota | Strict good-first percentage, in-sample top scores | Modeled net | Days passing 80% | Weeks passing 80% |
|---|---|---:|---:|---:|---:|---:|
| coinexx | 01 | 23,783 | 47.53% | $-3,458.58 | 0/26 | 0/5 |
| coinexx | 02 | 28,495 | 46.91% | $-3,470.62 | 1/24 | 0/5 |
| coinexx | 06 | 27,031 | 46.36% | $-5,345.50 | 0/27 | 0/6 |
| coinexx | 07 | 20,725 | 44.38% | $-3,853.76 | 0/28 | 0/5 |
| dukascopy | 01 | 23,783 | 33.12% | $-13,589.78 | 1/26 | 0/5 |
| dukascopy | 02 | 28,495 | 29.64% | $-22,210.80 | 0/24 | 0/5 |
| dukascopy | 06 | 27,031 | 33.17% | $-14,376.68 | 0/26 | 0/5 |
| dukascopy | 07 | 20,725 | 28.61% | $-12,374.75 | 0/27 | 0/5 |

## Scientific verdict and required build direction

No model passes the 80% daily, 80% weekly, 80% monthly success plus 85% SYNTH volume and positive-profit mandate on both sources. Even ex-post in-sample top-score quota ranking cannot achieve 80%, strongly indicating the current candidate-direction selection and 89 features do not resolve enough event ordering at this trade frequency. Causal student time-fold predictions have weaker discrimination still. This experiment is recorded and rejected, not forgotten or mislabeled as acceptable.

**Critical remaining issue:** A veto on the old, high-volume baseline-ledger entries is an off-policy candidate subset; skipped positions create opportunity for other live entries. Therefore all scored filtered subsets are diagnostic only until the frozen trained classifier is connected to the real-tick, single-position chronological streaming runner with consistent BUY/SELL/WAIT and the complete sources rerun. The next architecture experiment must learn opportunity timing and opposing direction jointly, not merely veto the preselected lane direction, and must include source-specific cost realism.

Full unabridged source scripts, trade and feature research datasets, ten baseline fit models, ten ordered fit models, all per-source/month results, full synthetic teacher source and byte-exact parent source pins are preserved separately; original v2 and high-volume branches are not changed.
