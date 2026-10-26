# F401 — causal marked L1 quote information, Stage 0 (UNSCORED)

This is an **original new research-stage implementation**, not the completed F401 experiment and not a deployable strategy. It does not alter any frozen baseline or original source. Its as-of clock is deliberately conservative: **every quote in the original event's current second is excluded**, avoiding ambiguity in same-millisecond tick ordering. No post-t0 filter can undo the original R9 market-order fill at t0.

## Predeclared Stage 1 information screen (requires original raw source tapes)

* Input: all eight original Coinexx/Dukascopy `.csv.gz` tapes Jan/Feb/Jun/Jul, exact unchanged F395 source-index masks and truth labels, F398 H1023 wrong-head frozen scores, and (if recovered) F400 score streams. Enforce all source filenames and byte SHA-256 against `F386_S04_S05_SOURCE_DEPENDENCY_PINS.json` before use. Use Coinexx broker UTC minus 120 minutes for Jan/Feb and minus 180 minutes for Jun/Jul; Dukascopy unchanged. Original `t0`, index, side and three-class 30–32-second label immutably retained. Labels enter other features only once matured 33,001 milliseconds; this stage uses **no** live label-memory feature.
* Independent L1 native quote marks: bid-only, ask-only, joint revisions, signed bid/ask moves, price unchanged, native quote count. 2/10/30/120/300s causal observation horizons. Bayesian online Poisson change-point posterior on **completed five-second source bins**, and completed M1/M5/M15/H1 price structure. These are quote revisions, **not** trades, volume or L2 order flow.
* Stage 1 baseline versus full: LogisticRegression regularized baseline with F398 frozen 74D wrong-head score, UTC-session, side and frozen F395 decision-mask; full adds only Stage 0 quote features. Use SAME original-event survivor set in both, FIT Jan earliest 70% plus Feb earliest 60%, FEB 60–80% CAL and 80–100% VAL with a 40s embargo on each chronological boundary. Never use June/July to fit or tune. Opposite-vs-neutral and correct guardian separately only if wrong/nonwrong signal shows conditional information.
* Falsification: matched **exact UTC hour×side×source broker** permutation of novel quote features, at least **199 seeds**, restricted to the SAME split and no cross-timestamp feature inference. Score incremental VAL log-loss reduction relative to the frozen-score-only baseline, compare placebo distribution, require positive CAL and VAL uplift and corrected permutation p<=.01 per broker before training expensive specialists. No nuisance refitting on VAL or selected-month OOS. Report effect size, negative controls and sample coverage. A simple AUC improvement alone does not promote.
* Stage 2 if novelty survives: protected-good asymmetric independent opposite, neutral and correct guards, frozen CAL thresholds; require **>=250 additional bad veto AND >=20:1 bad-to-good incremental veto in BOTH FEB CAL and VAL**, then original eight-cell event-index result masks, full 4,178 R9 hourly/daily/weekly/monthly quotas. Parent F395 fitted-era shadow veto is *not* causal t0 deployable because its ancestry includes t+15 observation; distinguish source-diagnostic from an actually causally executable new order policy.
* Stage 3 separately: actual new ASK/BID market-order entries, observable fill after latency, source quote spread, slippage, commissions, overlapping signals, net P&L and $100/$200 joint-capital margin/drawdown. No profit claim from 30–32s midpoint labels. True prospective untouched validation remains needed. Do not recycle F398–F400 threshold searches.

## Run bounded extraction once original archived quotes are present

`python f401_preorder_marked_information.py --approved-source-archive F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip --broker coinexx --month 01 --quote-file XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz --output F401_coinexx_01.npz`

`python -m unittest -v test_f401_preorder_causality.py`

## Dependencies and blocked inputs

Stage 0 code needs NumPy, SciPy, Pandas. Frozen F395 historical masks and F398 frozen score models were recovered as local source ZIPs. The **original eight raw tick tapes are not in this local workspace**, and the F400 experiment archive is not verified in MT5_EXPAND/01. Do not claim that Stage 1/Stage 2 has run. Keep this local research-stage work outside `/02`; save a complete ZIP + manifest in `/01` only after successful connector upload and readback.

## Run incremental novelty screen once original Jan/Feb source features are verified

`python f401_incremental_information_screen.py --f395-archive F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip --f398-archive F398_R01_MCX07_SOURCE_EXACT_RESEARCH_ONLY_20261025.zip --features-dir . --permutations 199 --out F401_STAGE1_UNAPPROVED_SCORES.json`

An emitted Stage 1 result is source-label informativeness only. No classification performance may be published without actual input tapes, SHA verification, original event identity comparisons, frozen model scoring, CAL/VAL log-loss, and exact-hour/side placebo. The F400 head archive is unavailable and **cannot be represented as having been controlled**.