# Gold MUWHAHA Miner — R9 BNP–Hawkes Four-Month Development Checkpoint (2026-11-01)

**STATUS: TRAINED, TESTED, REJECTED FOR PROMOTION. NO MT5 COMPILE. NO ORDERS.**

This is a narrow, reconstructible continuation of the existing R9 HybridGate and subminute Bayesian / Neyman–Pearson / Hawkes research entry mechanisms, NOT a replacement backtest platform. Preserve all source files and all failed experiments. Source trading lineage: `8729a6345655a7b4ea31facc81982004ee2b8921`, exact original expert blob `7eecb5f1947017a01ce85b2520725de54749e523`.

## Reused environments (no new tick engine)

- `research/r9_chronological_20261101/src/r9_replay.py` is the existing source-exact Python R9 baseline with separate `coinexx`/`dukascopy` adapters. The January Coinexx validation previously achieved 31,745 exact MT5 trade-lifecycle matches out of 31,915 (99.47%), with known residuals accepted as tolerable research differences, not absolute exact simulator equivalence.
- `research/r9_subminute_bnp_hawkes_v1/entry_model.py` is the existing causal subminute feature engine, copied source-identically here as `src/entry_model.py`; clocks: tick, 250ms, 500ms, 1s, 5s, 15s, 30s, 45s. Synthetic R9 teacher never enters the live feature vector.
- Local recovery files also include the baseline R9 replay `src/r9_replay.py`. This project adds only the supervised outcome labeling, teacher extractor, optimizer and tests.
- Original source files: Coinexx monthly `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` and Dukascopy monthly `XAUUSD_DUKAS_2026_MM_ticks.csv.gz` in the user's main Drive and Dukascopy Drive. Do not create interpolated ticks.

## Fixed development data partition

2026-01: fit Jan 6/12; NP calibration Jan 20; development check Jan 27.
2026-02: fit Feb 3/10; NP calibration Feb 19; development check Feb 26.
2026-06: fit Jun 2/9; NP calibration Jun 18; development check Jun 25.
2026-07: fit Jul 2/9; NP calibration Jul 16; development check Jul 28.

The entire files of all eight source/month combinations were scanned: **64,515,445 raw ticks**, of which **11,940,461** occurred on the selected 32 source-days and were processed by the subminute engine. These are **four nonadjacent sampled days per month/source**, NOT whole-month training. Do not claim continuous full-month or blind out-of-sample validation. March/April/May and August/September have not been evaluated with this candidate.

The source calendar and input file hashes are pinned in `results/*_collection.json`, without rehosting/duplicating original huge market data. Clock normalization was verified independently: Coinexx UTC+2 in Jan/Feb, UTC+3 in Jun/Jul; Dukascopy UTC native. The SYNTH teacher uses Coinexx server-native timestamps. For Dukascopy, labels are aligned to the equivalent Coinexx native-minute timestamp. The original pre-repair teacher labels are retained only in the full recovery archive for forensic transparency.

## Causal training and full lifecycle real-tick labels

At each eligible 10-second slot: update observed quote-event Hawkes intensities and only completed subminute bars, derive bounded ATR, RSI, Bollinger, Fibonacci-position proxy, momentum/efficiency, quote-update-weighted price (not genuine trade-volume VWAP) and spread features. No M1/M15/H1/H4 geometric confirmation. Candidate features are frozen at this tick. Then, *only in the offline labeling process*, walk subsequent actual source-native bid/ask ticks using R9's nominal stop/activation/trailing/30-second maximum-hold behavior to compute a simulated trade outcome. The gap-reset and partial-day warm-up rules remain fixed. The original R9 holding/exits are NOT changed in this study.

Training label: **net forward simulated P&L > $0.10**, with assumed 0.01 lot, `1oz` effective contract, $0.30 nominal stop from entry tick's Bid/Ask, trailing activation +$0.10, trail $0.03, max hold 30s, **$0.02 fixed round-trip fees**, no financing, no fill delay, no broker stop-level widening or margin/stop-out simulator in this new label. Consequently these are optimistic *labeling* metrics, not live-account P&L or exact Coinexx MT5 equivalence. All fills use executable side of bid/ask and adverse stop crossing first.

`src/extract_synth_teacher.py` streamed the surviving R9 SYNTH MT5 XLSX and extracted **117,686 trades** across Jan/Feb/Jun/Jul; **101,896** had positive outcomes. A teacher flag represents a profitable synthetic trade in the *same Coinexx-native minute and side*. Teacher is privileged: training can upweight an already REAL-positive outcome by up to 20% when the teacher agrees; teacher never assigns success in place of real outcomes and is never in the runtime feature vector.

## Experiments and complete numbers

Single-direction candidate collection: **158,986** forward-labeled candidate rows; Coinexx **93,042**, Dukascopy **65,944**. Real forward survival-label rate (>$0.10): **23.01%**. SYNTH teacher marker rate after clock repair: **54.58%**. Sources differ enormously in typical execution spread (January sample median Coinexx $0.19, Dukascopy $0.83). An optimized entry is not allowed to silently loosen broker constraints.

The original binned shrinkage Naive Bayesian likelihood score + held-out Neyman–Pearson threshold was fitted with real labels and the optional teacher weight: **70 candidate threshold/spread/teacher trials, zero** met a positive result on both brokers.

A nonlinear two-head survival/conditional-net student (LightGBM, 12 *causal* inputs) with NP blocking was also tested: **120 variants; zero pass** on both brokers.

The architecture was then extended to paired BUY/SELL counterfactual training, permitting an offline probabilistic action competition between trend continuation and reversal. It generated **317,967** forward-labeled candidate-action rows. These counterfactual *outcomes* are available only during offline training; at inference the candidate uses only observed features, predicts scores for each permitted side, and can abstain. **36 paired-model variants; zero pass**. Best combined diagnostic on the development-check days: **1,470 overlapping-avoiding actions, -$298.40 modeled net**, Coinexx 1,465 actions / -$295.72; Dukascopy 5 actions / -$2.68. These figures are purposefully negative and not performance claims about a deployed EA.

The teacher has descriptive signal but insufficient economics: Coinexx real-labeled survival on a teacher-marked single-direction candidate was about **35.32%**, versus **20.40%** for teacher-unmarked; Dukascopy **21.85%** versus **7.26%**. Teacher-marked mean payoff was nevertheless negative on both brokers. Teacher influence is an offline statistical correlation, **not** valid synthetic hindsight at entry or a profitable strategy.

No candidate passed the binding requirement: positive development P&L on BOTH brokers with at least 20 realized nonoverlapping accepted trades per broker. There is no approved model and no entry-system promotion. The diagnostic model files `REJECTED_dev_survival_classifier.txt` and `REJECTED_dev_net_regressor.txt` are *saved for reproducibility only*, their LightGBM reload checks matched predictions exactly.

## Core anti-hindsight rules

1. Use strictly source-ordered ticks; within a timestamp preserve file order. Normalized UTC is for alignment, not to merge broker quote streams.
2. Feature state at t comes only from completed older buckets and tick observations already arrived by t. Offline training labels may examine later ticks, NEVER the runtime scorer.
3. Never mix the SYNTH R9 “Every tick” generated quote path with the real-tick execution truth. SYNTH labels appear only as weak offline teacher metadata.
4. Do not tune or backfit using March, April, May, August or September in this checkpoint. All selected January/February/June/July dates remain research/development, **not untouched OOS**.
5. No code here has been compiled into MT5 or activated; fail closed pending a validated frozen model.
6. Do not misrepresent QWAP as real-volume VWAP. Do not claim the NP alpha controls live false-positive rates under dependent market events.

## Reproduction (Python only)

```bash
python -m unittest discover -v -s tests
python src/extract_synth_teacher.py /path/to/ReportTester-871471_jan2026_jul2026_R9_ticklog_synth.xlsx results/synth_teacher_minutes.csv
for month in 01 02 06 07; do
  for source in coinexx dukascopy; do
    python src/four_month_train.py --data-root /path/to/source_ticks \
      --teacher results/synth_teacher_minutes.csv --results results \
      --month "$month" --source "$source"
    python src/four_month_train.py --data-root /path/to/source_ticks \
      --teacher results/synth_teacher_minutes.csv --results results/paired \
      --month "$month" --source "$source" --paired
  done
done
python src/four_month_train.py --teacher results/synth_teacher_minutes.csv --results results --tune-only
python src/nonlinear_student.py results
python src/nonlinear_student_paired.py results/paired
python src/save_diagnostic_models.py results/paired
```

For previously generated Dukascopy labels from the pre-repair snapshot, only: `python src/repair_teacher_clock.py results/synth_teacher_minutes.csv results/dukascopy_*_candidate_outcomes.csv.gz results/paired/dukascopy_*_candidate_outcomes.csv.gz`. This refuses repeated repair and retains original files. On a fresh run, use the corrected `four_month_train.py` and **do not** run the repair.

## Next scientific direction

The result rejects only this candidate feature/label/execution combination. The next improvement should not be a cosmetic alpha/spread sweep. Research a **forward expected-exit-survival** model with asymmetric adverse/favorable hazard, subsecond quote-response sequence and liquidity/sweep diagnostics, while retaining the full lifecycle and risk-first objective. Investigate whether R9's current tight trailing and 30-second timeout are fundamentally incompatible with real spread economics; do not change hold/exit until user directs phase two.

Caution: This archive contains all run outputs including negative trials and timestamp-repair preimages. Preserve it unmodified. The original monthly market files stay at their source Drive IDs and were hashed.
